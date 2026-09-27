"""Aggregate seed-level results, conditional uncertainty, and reproducible figures."""
import json, math, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from simulator import Config,PROFILES
import dataclasses
OUT=Path(__file__).parent/'results'
NAMES={'single_checker':'Single Checker','elastic_pipeline':'Elastic pipeline','institutions':'Institutions','evidence_graph':'Evidence graph','packet_graph':'Packet graph'}
COLORS={'single_checker':'#929AA4','elastic_pipeline':'#DA9C37','institutions':'#547794','evidence_graph':'#173F5F','packet_graph':'#AF608A'}
def pool(q):
 n=len(q);mu=q.useful_week.mean();se=q.useful_week.std(ddof=1)/math.sqrt(n) if n>1 else 0;ci=t.ppf(.975,n-1)*se if n>1 else 0
 released=q.released.sum();units=(q.useful_week*q.hours/168).sum()
 return dict(runs=n,ideas=int(q.ideas.sum()),useful_mean=mu,useful_lo=mu-ci,useful_hi=mu+ci,
  release_rate=q.ideas_week.mean(),intent=(q.intent*q.released).sum()/released if released else float('nan'),
  defects=(q.defects*q.released).sum()/released if released else float('nan'),completion=released/q.ideas.sum(),
  cost_useful=q.cost.sum()/units if units else float('inf'),mean_lead=(q.lead*q.released).sum()/released if released else float('nan'),
  mean_active=q.mean_active.mean() if 'mean_active' in q else float('nan'),peak_active=q.peak_active.max() if 'peak_active' in q else float('nan'),
  end_to_end=(q.end_to_end*q.released).sum()/released if 'end_to_end' in q and released else float('nan'))
def paired(q,first='evidence_graph',second='institutions',column='architecture'):
 p=q.pivot(index='seed',columns=column,values='useful_week')[[first,second]].dropna();delta=p[first]-p[second]
 ci=t.ppf(.975,len(p)-1)*delta.std(ddof=1)/np.sqrt(len(p));rng=np.random.default_rng(417)
 ix=rng.integers(0,len(p),size=(10000,len(p)));aa=p[first].to_numpy()[ix].mean(1);bb=p[second].to_numpy()[ix].mean(1)
 lo,hi=np.quantile(aa/bb-1,[.025,.975])
 return dict(first=first,second=second,seeds=len(p),difference=delta.mean(),difference_lo=delta.mean()-ci,difference_hi=delta.mean()+ci,gain=p[first].mean()/p[second].mean()-1,gain_lo=lo,gain_hi=hi)
def main():
 frames=[pd.read_csv(OUT/f) for f in ['full_runs.csv','confirmation_runs.csv','elasticity_runs.csv','controller_sensitivity_runs.csv']]
 x=pd.concat(frames,ignore_index=True)
 for k,v in [('cfg_packet_context_penalty',2.5),('cfg_controller','full_pool'),('cfg_target_drain_hours',.5)]:
  x[k]=x[k].fillna(v)
 keys=['group','scenario','architecture','mix','cfg_packet_size','cfg_effort','cfg_packet_context_penalty','cfg_controller','cfg_target_drain_hours']
 rows=[]
 for key,q in x.groupby(keys,dropna=False,sort=False):rows.append(dict(zip(keys,key))|pool(q))
 summary=pd.DataFrame(rows);summary.to_csv(OUT/'summary.csv',index=False)
 comparisons=[]
 for scenario in ['reference','equal_controls','dense_dependencies','interface_errors']:
  q=x[(x.group=='topology_confirmation')&(x.scenario==scenario)]
  comparisons.append({'scenario':scenario}|paired(q))
 for architecture in ['institutions','evidence_graph']:
  for scenario in ['steady','bursts','bursts_variable_work','dense_bursts']:
   q=x[(x.group=='elasticity')&(x.scenario==scenario)&(x.architecture==architecture)]
   for policy in ['full_pool','queue_autoscale','work_autoscale']:
    comparisons.append({'scenario':scenario,'architecture':architecture}|paired(q,policy,'fixed_small','cfg_controller'))
   comparisons.append({'scenario':scenario,'architecture':architecture}|paired(q,'work_autoscale','full_pool','cfg_controller'))
 for architecture in ['institutions','evidence_graph']:
  q=x[(x.group=='controller_sensitivity')&(x.architecture==architecture)].copy()
  q['treatment']=q.apply(lambda r:'full_pool' if r.cfg_controller=='full_pool' else 'work_'+str(r.cfg_target_drain_hours),axis=1)
  for target in [.1,.25,.5,1.]:comparisons.append({'scenario':'controller_threshold','architecture':architecture,'target':target}|paired(q,'work_'+str(target),'full_pool','treatment'))
 pd.DataFrame(comparisons).to_csv(OUT/'paired_comparisons.csv',index=False)
 # Sampling uncertainty in the conditional quality constraints for shortlisted mixes.
 qr=[];rng=np.random.default_rng(174)
 for key,q in x[x.group=='mix_confirmation'].groupby(['scenario','architecture','mix']):
  idx=rng.integers(0,len(q),size=(5000,len(q)));n=q.released.to_numpy();intent=q.intent.to_numpy();defects=q.defects.to_numpy()
  den=n[idx].sum(1);ii=(intent[idx]*n[idx]).sum(1)/den;dd=(defects[idx]*n[idx]).sum(1)/den
  rec=dict(zip(['scenario','architecture','mix'],key))|pool(q)
  rec.update(intent_lo=np.quantile(ii,.025),intent_hi=np.quantile(ii,.975),defects_lo=np.quantile(dd,.025),defects_hi=np.quantile(dd,.975))
  rec['passes_point_floors']=rec['intent']>=.97 and rec['defects']<=.25
  rec['passes_conservative_floors']=rec['intent_lo']>=.97 and rec['defects_hi']<=.25
  qr.append(rec)
 pd.DataFrame(qr).to_csv(OUT/'mix_quality_intervals.csv',index=False)
 (OUT/'assumptions.json').write_text(json.dumps({'config':dataclasses.asdict(Config()),'profiles':PROFILES,'notice':'All numerical input parameters synthetic. No Artificial Analysis snapshot or live provider-limit measurements used.'},indent=2))
 counts=x.groupby('group').agg(runs=('seed','size'),ideas=('ideas','sum')).to_dict('index')
 (OUT/'run_counts.json').write_text(json.dumps(counts,indent=2))
 # Standalone scientific figure; source values available in summary.csv.
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#283442','text.color':'#283442'})
 fig,ax=plt.subplots(2,2,figsize=(13.6,9.4));fig.subplots_adjust(left=.09,right=.97,top=.86,bottom=.12,wspace=.31,hspace=.48)
 fig.suptitle('Factory simulation: structure, elasticity and coherence',x=.09,y=.975,ha='left',fontsize=21,fontweight='bold')
 fig.text(.09,.923,'Synthetic structural experiments • SQL state • Stateless agents • Independent evidence • 95% seed-level intervals',fontsize=11)
 q=summary[(summary.group=='topology_confirmation')&(summary.scenario=='equal_controls')].set_index('architecture')
 order=['institutions','elastic_pipeline','evidence_graph','packet_graph'];a=ax[0,0]
 vals=[q.loc[v,'useful_mean'] for v in order];err=[q.loc[v,'useful_hi']-q.loc[v,'useful_mean'] for v in order]
 a.barh(range(4),vals,xerr=err,color=[COLORS[v] for v in order],capsize=3)
 a.set_yticks(range(4),[NAMES[v] for v in order]);a.invert_yaxis();a.set_xlim(left=0);a.set_xlabel('Useful idea-equivalents / synthetic week');a.set_title('Same controls; different work topology',loc='left',fontweight='bold',pad=12)
 q=summary[(summary.group=='elasticity')&(summary.scenario=='bursts_variable_work')&(summary.architecture=='evidence_graph')].set_index('cfg_controller')
 order=['fixed_small','full_pool','queue_autoscale','work_autoscale'];a=ax[0,1]
 vals=[q.loc[v,'useful_mean'] for v in order];err=[q.loc[v,'useful_hi']-q.loc[v,'useful_mean'] for v in order]
 a.barh(range(4),vals,xerr=err,color=['#929AA4','#547794','#DA9C37','#173F5F'],capsize=3)
 a.set_yticks(range(4),['4-slot ceiling','9-slot shared pool','Queue autoscale','Work autoscale']);a.invert_yaxis();a.set_xlim(left=0);a.set_xlabel('Useful idea-equivalents / synthetic week');a.set_title('Elastic invocations; variable burst workload',loc='left',fontweight='bold',pad=12)
 q=summary[summary.group=='packet_confirmation'];a=ax[1,0]
 for pen,color,marker,label in [(0.,'#DA9C37','o','No added packet context penalty'),(2.5,'#173F5F','s','Context penalty applied')]:
  z=q[q.cfg_packet_context_penalty==pen].sort_values('cfg_packet_size');a.errorbar(z.cfg_packet_size,z.useful_mean,yerr=z.useful_hi-z.useful_mean,color=color,marker=marker,capsize=3,label=label)
 a.set_xticks([1,2,4,8]);a.set_ylim(bottom=0);a.set_xlabel('Requirements per invocation');a.set_ylabel('Useful idea-equivalents / synthetic week');a.set_title('Larger packets: fewer interfaces, harder calls',loc='left',fontweight='bold',pad=12);a.legend(frameon=False,fontsize=9)
 q=summary[summary.group=='correlation_confirmation'].copy();q['c']=q.scenario.astype(float);q=q.sort_values('c');a=ax[1,1]
 a.errorbar(q.c,q.useful_mean,yerr=q.useful_hi-q.useful_mean,color='#173F5F',marker='o',capsize=3)
 a.set_ylim(bottom=0);a.set_xticks([0,.05,.18,.45],['0%','5%','18%','45%']);a.set_xlabel('Latent family blind-spot probability');a.set_ylabel('Useful idea-equivalents / synthetic week');a.set_title('More agents do not remove shared mistakes',loc='left',fontweight='bold',pad=12)
 for a in ax.flat:a.grid(axis='x' if a in ax[0,:] else 'y',alpha=.15);a.set_axisbelow(True)
 fig.text(.09,.035,'Conditional simulation results, not production forecasts. Price, skill and capacity inputs are hypotheses.\nQuality floors are assessed separately; a throughput winner is not automatically safe to deploy.',fontsize=10,color='#576474')
 fig.savefig(OUT/'factory_findings.png',dpi=180);plt.close(fig)
 print(json.dumps(counts,indent=2));print('Paired comparisons',json.dumps(comparisons[:4],indent=2))
if __name__=='__main__':main()
