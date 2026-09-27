"""Fresh-seed confirmation; no configuration chosen using these outcomes."""
import dataclasses, json
import pandas as pd
from simulator import Config,ARCHITECTURES,PROFILES
from experiments import execute,OUT

def confirmation_tasks():
 ts=[];base=Config(ideas=32)
 # Pre-specified references plus screening-selected top/middle candidates.
 mixes=[(12,0,0),(10,2,0),(8,4,0),(6,5,1),(6,3,3),(4,7,1),(0,12,0)]
 for arch in ('institutions','evidence_graph'):
  for cap in ('unlimited','constrained'):
   for mix in mixes:
    for s in range(24):ts.append(('mix_confirmation',cap,dataclasses.replace(base,architecture=arch,mix=mix,capacity=cap,seed=1000+s)))
 for scenario,kw in [('reference',{}),('equal_controls',{'common_controls':True}),('dense_dependencies',{'coupling':.65}),('interface_errors',{'decoherence':.22})]:
  for arch in ARCHITECTURES:
   if scenario=='equal_controls' and arch=='single_checker':continue
   for s in range(24):ts.append(('topology_confirmation',scenario,dataclasses.replace(base,architecture=arch,seed=2000+s,**kw)))
 # Does the larger-packet result merely come from the assumed context penalty?
 for penalty in (0.,2.5):
  for size in (1,2,4,8):
   for s in range(16):ts.append(('packet_confirmation','high_coupling',dataclasses.replace(base,architecture='packet_graph',coupling=.65,decoherence=.22,packet_size=size,packet_context_penalty=penalty,seed=3000+s)))
 # Correlation stress on the leading candidate, keeping all other assumptions fixed.
 for corr in (0.,.05,.18,.45):
  for s in range(24):ts.append(('correlation_confirmation',str(corr),dataclasses.replace(base,architecture='evidence_graph',mix=(10,2,0),correlation=corr,seed=4000+s)))
 return ts
if __name__=='__main__':
 (OUT/'assumptions.json').write_text(json.dumps({'config':dataclasses.asdict(Config()),'profiles':PROFILES,'notice':'Synthetic hypotheses, not Artificial Analysis measurements or verified provider limits.'},indent=2))
 execute(confirmation_tasks(),OUT/'confirmation_runs.csv',6)
