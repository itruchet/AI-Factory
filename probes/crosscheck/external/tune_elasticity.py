"""Threshold sensitivity for the proposed deterministic work-aware controller."""
from simulator import Config
from experiments import execute,OUT
if __name__=='__main__':
 tasks=[]
 for arch in ['institutions','evidence_graph']:
  for target in [.10,.25,.50,1.0]:
   for seed in range(6000,6024):
    tasks.append(('controller_sensitivity','bursts_variable_work',Config(architecture=arch,mix=(8,8,4),ideas=48,wip=12,capacity='constrained',seed=seed,controller='work_autoscale',arrival_pattern='bursts',varying_difficulty=True,target_drain_hours=target)))
  for seed in range(6000,6024):
   tasks.append(('controller_sensitivity','bursts_variable_work',Config(architecture=arch,mix=(8,8,4),ideas=48,wip=12,capacity='constrained',seed=seed,controller='full_pool',arrival_pattern='bursts',varying_difficulty=True)))
 execute(tasks,OUT/'controller_sensitivity_runs.csv',6)
