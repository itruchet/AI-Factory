import unittest, tempfile, sqlite3, json
from simulator import Config, Simulation, run, ARCHITECTURES
class Invariants(unittest.TestCase):
 def test_repeatability(self):
  c=Config(ideas=8);self.assertEqual(run(c),run(c))
 def test_all_organizations_terminate(self):
  for a in ARCHITECTURES:
   x=run(Config(architecture=a,ideas=8))
   self.assertEqual(x['released']+x['failed'],8)
   self.assertGreater(x['hours'],0);self.assertGreaterEqual(x['intent'],0);self.assertLessEqual(x['intent'],1)
 def test_capacity_and_independence(self):
  with tempfile.TemporaryDirectory() as d:
   path=d+'/trace.sqlite';x=run(Config(architecture='evidence_graph',ideas=12,capacity='constrained',audit_path=path))
   for f,n in json.loads(x['peak_provider']).items():self.assertLessEqual(n,{'top_A':2,'top_B':2,'middle':4,'bottom':1}[f])
   db=sqlite3.connect(path)
   for (payload,) in db.execute("SELECT output FROM jobs WHERE kind='verify' AND status='done'"):
    p=json.loads(payload)
    if 'author' in p:self.assertNotEqual(p['author'],p['reviewer'])
   self.assertEqual(db.execute("SELECT count(*) FROM jobs WHERE status IN ('ready','running')").fetchone()[0],0)
   self.assertEqual(db.execute('SELECT count(*) FROM outcomes').fetchone()[0],12)
   for (snapshot,) in db.execute('SELECT input FROM jobs WHERE started IS NOT NULL'):
    self.assertEqual(len(json.loads(snapshot)['original_intent']),8)
 def test_workload_paired(self):
  a=Simulation(Config(architecture='single_checker',ideas=8));b=Simulation(Config(architecture='packet_graph',ideas=8))
  self.assertEqual(a.workload,b.workload);a.db.close();b.db.close()
 def test_ground_truth_not_in_worker_input(self):
  with tempfile.TemporaryDirectory() as d:
   run(Config(ideas=4,audit_path=d+'/trace.sqlite'))
   db=sqlite3.connect(d+'/trace.sqlite')
   for (p,) in db.execute('SELECT input FROM jobs WHERE started IS NOT NULL'):
    self.assertNotIn('bugs',json.loads(p));self.assertNotIn('difficulty',json.loads(p))
 def test_fully_serial_resource_bound(self):
  x=run(Config(architecture='single_checker',ideas=12,mix=(6,3,3)))
  stage=json.loads(x['stage_busy'])
  director=sum(stage.get(k,0) for k in ['inquiry','council','plan','challenge','release'])
  self.assertGreaterEqual(x['hours']+1e-9,max(director,stage['verify']))
 def test_quota_terminates(self):
  x=run(Config(architecture='evidence_graph',ideas=16,capacity='quota',mix=(12,0,0)))
  self.assertEqual(x['released']+x['failed'],16)

class ElasticityInvariants(unittest.TestCase):
 def test_controller_modes_and_arrivals(self):
  for policy in ('fixed_small','full_pool','queue_autoscale','work_autoscale'):
   x=run(Config(architecture='institutions',mix=(8,8,4),ideas=16,wip=12,capacity='constrained',controller=policy,arrival_pattern='bursts',varying_difficulty=True))
   self.assertEqual(x['released']+x['failed'],16)
   self.assertGreaterEqual(x['hours'],3.)
   self.assertLessEqual(x['peak_active'],4 if policy=='fixed_small' else 9)
 def test_release_quorum_and_quota(self):
  with tempfile.TemporaryDirectory() as d:
   path=d+'/trace.sqlite';run(Config(architecture='evidence_graph',ideas=16,mix=(12,0,0),capacity='quota',audit_path=path))
   db=sqlite3.connect(path)
   for family,day,hours in db.execute('SELECT family,CAST(started/24 AS INTEGER),SUM(duration) FROM jobs WHERE started IS NOT NULL GROUP BY 1,2'):
    self.assertLessEqual(hours,{'top_A':8,'top_B':8,'middle':36,'bottom':24}[family]+1e-9)
   for (raw,) in db.execute('SELECT state FROM ideas'):
    s=json.loads(raw)
    if s['phase']=='released':
     self.assertEqual(len(s['release_authors']),2)
     self.assertEqual(len(set(s['release_authors'])),2)
     self.assertEqual(len(s['release_votes']),2)
     self.assertTrue(all(not v['missing_detected'] and not v['interface_rejections'] for v in s['release_votes']))

if __name__=='__main__':unittest.main()
