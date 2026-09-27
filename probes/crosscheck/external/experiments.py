"""Reproducible experiments; all inputs are synthetic and explicitly exported."""
import csv, dataclasses, json, os, argparse, math, statistics, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from simulator import Config,run,ARCHITECTURES,PROFILES
OUT=Path(__file__).parent/'results'
def one(t):
 group,scenario,c=t;r=run(c);r.update(group=group,scenario=scenario)
 for k,v in dataclasses.asdict(c).items():
  if k not in r:r['cfg_'+k]=json.dumps(v) if isinstance(v,(dict,list,tuple)) else v
 return r

def tasks(mode):
 base=Config(ideas=20)
 if mode=='pilot':
  return [('pilot','reference',dataclasses.replace(base,architecture=a,seed=s)) for a in ARCHITECTURES for s in range(4)]
 ts=[]
 scenarios={
 'reference':{},
 'low_coupling':{'coupling':.05,'decoherence':.03},
 'high_coupling':{'coupling':.65,'decoherence':.22},
 'serial_chain':{'coupling':1.,'decoherence':.10},
 'correlated_errors':{'correlation':.45},
 'no_family_blindspots':{'correlation':0.},
 'poor_reconstruction':{'read_error':.12},
 'shared_capacity':{'capacity':'constrained'},
 'quota_capacity':{'capacity':'quota'},
 'hard_work':{'difficulty_shift':10.},
 'equal_controls':{'common_controls':True},
 'local_self_selection':{'claim_policy':'self_select'},
 'role_specialization':{'specialization':1.},
 }
 for scenario,kw in scenarios.items():
  for a in ARCHITECTURES:
   if scenario=='equal_controls' and a=='single_checker':continue
   for s in range(12):ts.append(('topology',scenario,dataclasses.replace(base,architecture=a,seed=100+s,**kw)))
 # A separate scaling experiment uses common headcount and WIP across architectures.
 for n in (3,6,9,12,20,32):
  top=max(1,round(n*.5));mid=round(n*.25);mix=(top,mid,n-top-mid)
  for cap in ('unlimited','constrained'):
   for a in ARCHITECTURES:
    for s in range(6):ts.append(('scaling',cap,dataclasses.replace(base,architecture=a,mix=mix,wip=max(2,round(.7*n)),ideas=32,seed=200+s,capacity=cap)))
 # Full simplex: 91 mixes x two substantially different organizations, same seeds.
 for a in ('institutions','evidence_graph'):
  for top in range(13):
   for mid in range(13-top):
    for s in range(3):ts.append(('mix_search','reference',dataclasses.replace(base,architecture=a,mix=(top,mid,12-top-mid),seed=300+s)))
 # Packet size trades parallelism against cross-boundary coherence and invocation length.
 for coupling,deco,name in ((.05,.03,'low'),(.25,.10,'reference'),(.65,.22,'high')):
  for size in (1,2,4,8):
   for s in range(12):ts.append(('packet_size',name,dataclasses.replace(base,architecture='packet_graph',packet_size=size,coupling=coupling,decoherence=deco,seed=400+s)))
 # Reasoning effort is independent of capability tier.
 for effort in (.5,1.,2.):
  for a in ('institutions','evidence_graph','packet_graph'):
   for s in range(8):ts.append(('effort','reference',dataclasses.replace(base,architecture=a,effort=effort,seed=500+s)))
 return ts

def execute(ts,path,workers):
 t=time.time();rows=[];handle=None;writer=None
 with ProcessPoolExecutor(max_workers=workers) as ex:
  for j,r in enumerate(ex.map(one,ts,chunksize=4)):
   rows.append(r)
   if writer is None:
    handle=open(path,'w',newline='');writer=csv.DictWriter(handle,fieldnames=list(r));writer.writeheader()
   writer.writerow(r)
   if (j+1)%20==0:handle.flush()
   if (j+1)%100==0:print(f'{j+1}/{len(ts)} complete, {time.time()-t:.1f}s',flush=True)
 if handle:handle.close()
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with open(path,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
 print(f'Saved {len(rows)} runs to {path} in {time.time()-t:.1f}s',flush=True)
 return rows

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['pilot','full'],default='pilot');p.add_argument('--workers',type=int,default=6);a=p.parse_args()
 OUT.mkdir(exist_ok=True)
 (OUT/'assumptions.json').write_text(json.dumps({'config':dataclasses.asdict(Config()),'profiles':PROFILES,'notice':'Synthetic hypotheses. Not imported Artificial Analysis measurements or verified subscription limits.'},indent=2))
 rows=execute(tasks(a.mode),OUT/(a.mode+'_runs.csv'),a.workers)
 if a.mode=='pilot':
  for ar in ARCHITECTURES:
   rr=[r for r in rows if r['architecture']==ar]
   print(ar,{k:round(statistics.mean(r[k] for r in rr),3) for k in ['ideas_week','useful_week','intent','defects','completion','cost_useful','lead']})
