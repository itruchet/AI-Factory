"""Elastic invocation-count experiments; model selection is never delegated to an LLM."""
import dataclasses
from simulator import Config
from experiments import execute,OUT

def tasks():
 ts=[]
 for arch in ('institutions','evidence_graph'):
  for scenario,kw in [('steady',{}),('bursts',{'arrival_pattern':'bursts'}),('bursts_variable_work',{'arrival_pattern':'bursts','varying_difficulty':True}),('dense_bursts',{'arrival_pattern':'bursts','coupling':.65,'decoherence':.22})]:
   for controller in ('fixed_small','full_pool','queue_autoscale','work_autoscale'):
    for s in range(24):
     c=Config(architecture=arch,mix=(8,8,4),ideas=48,wip=12,capacity='constrained',seed=5000+s,controller=controller,**kw)
     ts.append(('elasticity',scenario,c))
 return ts
if __name__=='__main__':execute(tasks(),OUT/'elasticity_runs.csv',6)
