"""Factory organization laboratory. Python 3.10+, standard library only.
All capability, price, speed and workload values are explicit synthetic hypotheses.
SQL stores canonical idea state, jobs, input snapshots, outputs and immutable events.
No agent retains task context and no LLM controls allocation.
"""
from __future__ import annotations
import argparse, dataclasses, hashlib, heapq, json, math, sqlite3, statistics, random
from pathlib import Path

ARCHITECTURES = ('single_checker', 'elastic_pipeline', 'institutions', 'evidence_graph', 'packet_graph')
PROFILES = {
 'top': dict(score=72., tps=45., input_price=2., output_price=12., verbosity=1.4),
 'middle': dict(score=56., tps=70., input_price=.4, output_price=2., verbosity=1.),
 'bottom': dict(score=38., tps=90., input_price=.08, output_price=.25, verbosity=.8),
}
TOKENS = {'inquiry':(6000,2500), 'council':(8000,2000), 'plan':(6500,3000),
          'challenge':(7500,2200), 'code':(7000,6000), 'verify':(8500,2800), 'release':(12000,3500), 'audit':(8500,2800)}

@dataclasses.dataclass
class Config:
 architecture: str = 'institutions'
 mix: tuple = (6,3,3)
 seed: int = 0
 ideas: int = 32
 wip: int = 8
 coupling: float = .25
 decoherence: float = .10
 correlation: float = .18
 read_error: float = .025
 packet_size: int = 2
 packet_context_penalty: float = 2.5
 effort: float = 1.
 capacity: str = 'unlimited'  # unlimited, constrained, quota
 claim_policy: str = 'fifo' # fifo or self_select
 max_attempts: int = 4
 max_release_rounds: int = 2
 audit_rate: float = .10
 test_catch: float = .5
 difficulty_shift: float = 0.
 slope: float = .12
 common_controls: bool = False
 specialization: float = 0.
 repair_bonus: float = .025
 controller: str = 'full_pool'
 arrival_pattern: str = 'saturated'
 target_drain_hours: float = .5
 varying_difficulty: bool = False
 audit_path: str | None = None

class Simulation:
 def __init__(self, cfg):
  self.c=cfg; self.t=0.; self.seq=0; self.heap=[]; self.cost=0.; self.busy=0.; self.waste=0.
  self.capacity_block_time=0.; self.events=0; self.peak_provider={}; self.provider_active={}; self.provider_used={}
  self.next_idea=0; self.active=set(); self.completed=[]; self.max_queue=0; self.dependency_wait=0.
  self.stage_busy={};self.service_ewma={};self.target_caps={};self.peak_active=0; self.rng=random.Random(cfg.seed+881)
  self.db=sqlite3.connect(cfg.audit_path or ':memory:')
  self.db.executescript('''
   CREATE TABLE IF NOT EXISTS run(config TEXT); DELETE FROM run;
   CREATE TABLE IF NOT EXISTS ideas(id INTEGER PRIMARY KEY, state TEXT); DELETE FROM ideas;
   CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY, idea INTEGER, kind TEXT, block INTEGER,
    generation INTEGER, status TEXT, created REAL, started REAL, ended REAL, agent INTEGER,
    family TEXT, input TEXT, output TEXT, duration REAL, cost REAL); DELETE FROM jobs;
   CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, time REAL, idea INTEGER, event TEXT, payload TEXT); DELETE FROM events;
   CREATE TABLE IF NOT EXISTS outcomes(idea INTEGER PRIMARY KEY, result TEXT); DELETE FROM outcomes;
  ''')
  self.db.execute('INSERT INTO run VALUES (?)',(json.dumps(dataclasses.asdict(cfg)),))
  self.agents=[]
  for tier,n in zip(PROFILES,cfg.mix):
   for j in range(n):
    fam=('top_A' if j%2==0 else 'top_B') if tier=='top' else tier
    self.agents.append(dict(id=len(self.agents),tier=tier,family=fam,busy=False))
  assert len(self.agents)>=3 and cfg.architecture in ARCHITECTURES
  self.workload=[self.make_workload(i) for i in range(cfg.ideas)]

 def u(self,*keys):
  """Keyed randomness: workload/trials remain reproducible across scheduling orders."""
  s='|'.join(map(str,(self.c.seed,)+keys)).encode()
  return int.from_bytes(hashlib.blake2b(s,digest_size=8).digest(),'little') / 2**64
 def make_workload(self,i):
  ds=[]; deps=[]
  for r in range(8):
   z=self.u(i,'difficulty',r)
   wave_shift=(8 if (i//8)%2 else -8) if self.c.varying_difficulty else 0
   ds.append((40 if z<.4 else 56 if z<.8 else 72)+self.c.difficulty_shift+wave_shift)
   deps.append([p for p in range(r) if self.u(i,'edge',p,r)<self.c.coupling])
  arrival=(i//8)*3.0 if self.c.arrival_pattern=='bursts' else 0.
  return dict(difficulty=ds,deps=deps,arrival=arrival)
 def get(self,i): return json.loads(self.db.execute('SELECT state FROM ideas WHERE id=?',(i,)).fetchone()[0])
 def put(self,s): self.db.execute('INSERT OR REPLACE INTO ideas VALUES (?,?)',(s['id'],json.dumps(s,separators=(',',':'))))
 def log(self,i,event,payload):
  self.events+=1
  if self.c.audit_path: self.db.execute('INSERT INTO events VALUES (?,?,?,?,?)',(self.events,self.t,i,event,json.dumps(payload)))
 def add(self,s,kind,b=-1,g=0):
  self.db.execute('INSERT INTO jobs(idea,kind,block,generation,status,created) VALUES (?,?,?,?,?,?)',(s['id'],kind,b,g,'ready',self.t))
 def probability(self,a,s,r,kind,attempt=0,size=1):
  p=PROFILES[a['tier']]
  # Longer fused packets add a context burden; SQL persistence does not eliminate interpretation load.
  penalty=self.c.packet_context_penalty*(size-1)**1.2
  offsets={'top':{},'middle':{'code':5,'verify':3,'inquiry':-3,'plan':-3},'bottom':{'verify':7,'inquiry':5,'code':-5}}
  role_offset=offsets[a['tier']].get(kind,0)*self.c.specialization
  z=self.c.slope*(p['score']+role_offset-self.workload[s['id']]['difficulty'][r]-penalty+6*math.log2(self.c.effort))+math.log(3)
  base=1/(1+math.exp(-z))
  # A family-specific latent blind spot is shared across independent invocations and stages.
  blind=self.u(s['id'],'blind',r,a['family'])<self.c.correlation
  base*= .4 if blind else 1.
  return min(.995,max(.015,base+min(attempt,3)*self.c.repair_bonus))
 def pass_trial(self,a,s,r,kind,attempt=0,size=1,scale=1.):
  p=self.probability(a,s,r,kind,attempt,size)*scale
  return self.u(s['id'],kind,r,a['family'],a['id'],attempt,s['round'])<p
 def admit(self):
  while len(self.active)<self.c.wip and self.next_idea<self.c.ideas and self.workload[self.next_idea]['arrival']<=self.t:
   i=self.next_idea;self.next_idea+=1;self.active.add(i)
   s=dict(id=i,admitted=self.t,round=0,known=[],planned=[],blocks=[],phase='inquiry',frames=[],stage_authors=[],release_pending=False,release_votes=[],release_authors=[])
   k=2 if self.c.architecture in ('institutions','evidence_graph','packet_graph') or self.c.common_controls else 1
   s['k']=k
   self.put(s)
   for n in range(k):self.add(s,'inquiry',g=n)
   self.log(i,'admit',{'requirements':8})
 def capacity_ok(self,a):
  if self.c.capacity=='unlimited':return True
  f=a['family'];cap={'top_A':2,'top_B':2,'middle':4,'bottom':1}[f]
  if self.c.controller=='fixed_small':cap=min(cap,1)
  elif self.c.controller in ('queue_autoscale','work_autoscale'):cap=min(cap,self.target_caps.get(f,cap))
  if self.provider_active.get(f,0)>=cap:return False
  if self.c.capacity=='quota':
   day=int(self.t/24);limit={'top_A':8.,'top_B':8.,'middle':36.,'bottom':24.}[f]
   if self.provider_used.get((f,day),0)>=limit:return False
  return True
 def eligible(self,a,row,s):
  jid,i,kind,b,g,*_=row
  if self.c.architecture=='single_checker':
   role='director' if kind in ('inquiry','council','plan','challenge','release') else 'checker' if kind=='verify' else 'worker'
   if role=='director' and a['id']!=0:return False
   if role=='checker' and a['id']!=1:return False
   if role=='worker' and a['id']<2:return False
  if kind in ('council','challenge') and a['id']==s.get('last_author',-1):return False
  if kind in ('verify','audit') and a['id']==s['blocks'][b].get('author',-1):return False
  if kind=='audit' and a['id']==s['blocks'][b].get('reviewer',-1):return False
  if kind=='inquiry' and a['id'] in s['stage_authors']:return False
  if kind=='release' and (a['id']==s.get('last_verifier',-1) or a['id'] in s['release_authors']):return False
  return True
 def duration_cost(self,a,row,s):
  jid,i,kind,b,g,*_=row;p=PROFILES[a['tier']];inp,out=TOKENS[kind]
  if kind in ('code','verify','audit'):
   block=s['blocks'][b];n=len(block['reqs']);edges=len(block['deps'])
   inp*=1+.38*(n-1);out*=n
   if kind=='verify' and self.c.architecture in ('evidence_graph','packet_graph'):out+=900*edges
  if kind=='release' and self.c.architecture not in ('evidence_graph','packet_graph'):
   out+=900*sum(len(x['deps']) for x in s['blocks'])
  if self.c.varying_difficulty:
   reqs=s['blocks'][b]['reqs'] if b>=0 else list(range(8))
   complexity=sum(self.workload[i]['difficulty'][r] for r in reqs)/len(reqs)
   volume_scale=max(.6,min(1.8,1+(complexity-56)/40))
   inp*=volume_scale;out*=volume_scale
  out*=p['verbosity']*self.c.effort
  # Independent synthetic duration jitter; includes prefill/read latency and tools.
  jitter=.8+.4*self.u(i,'duration',kind,b,g,a['tier'])
  dur=(out/p['tps']/3600+.025+(.1 if kind=='code' else .015))*jitter
  cost=(inp*p['input_price']+out*p['output_price'])/1e6
  return dur,cost
 def schedule(self):
  progress=False
  ready=self.db.execute("SELECT id,idea,kind,block,generation,created FROM jobs WHERE status='ready' ORDER BY created,id").fetchall()
  self.max_queue=max(self.max_queue,len(ready))
  if self.c.controller in ('queue_autoscale','work_autoscale'):
   if self.c.controller=='queue_autoscale':demand=len(ready)
   else:
    work=0.
    for r in ready:
     estimate=self.service_ewma.get(r[2],.22 if r[2]=='code' else .07)
     if self.c.varying_difficulty:
      state=self.get(r[1]);rs=state['blocks'][r[3]]['reqs'] if r[3]>=0 else list(range(8))
      tags=[self.workload[r[1]]['difficulty'][req]+20*(self.u(r[1],'estimate',req)-.5) for req in rs]
      estimate*=max(.6,min(1.8,1+(sum(tags)/len(tags)-56)/40))
     work+=estimate
    demand=math.ceil(work/self.c.target_drain_hours)
   maxima={'top_A':2,'top_B':2,'middle':4,'bottom':1}
   self.target_caps={f:max(1,min(cap,math.ceil(demand*cap/9))) for f,cap in maxima.items()}
  # Rotate agent order: no fixed tier receives first claim in a shared pool.
  free=[a for a in self.agents if not a['busy'] and self.capacity_ok(a)]
  self.rng.shuffle(free)
  for a in free:
   if not self.capacity_ok(a):continue
   if not ready:break
   choices=[]
   for row in ready:
    if self.c.architecture=='single_checker':
     role='director' if row[2] in ('inquiry','council','plan','challenge','release') else 'checker' if row[2]=='verify' else 'worker'
     if (a['id']==0 and role!='director') or (a['id']==1 and role!='checker') or (a['id']>=2 and role!='worker'):continue
    s=self.get(row[1])
    if self.eligible(a,row,s):
     score=0.
     if self.c.claim_policy=='self_select':
      rs=s['blocks'][row[3]]['reqs'] if row[3]>=0 else list(range(8))
      # Local claims use noisy published complexity estimates, never latent blind spots.
      estimates=[self.workload[s['id']]['difficulty'][r]+20*(self.u(s['id'],'estimate',r)-.5) for r in rs]
      prob=sum(1/(1+math.exp(-(self.c.slope*(PROFILES[a['tier']]['score']-d)+math.log(3)))) for d in estimates)/len(rs)
      # Published local preference, not centralized assignment; aging prevents starvation.
      duration,cost=self.duration_cost(a,row,s)
      score=prob/(duration*(1+10*cost)) + .2*(self.t-row[5])
     if self.c.controller=='work_autoscale':
      # Published queue rule: evidence debt, downstream release and age, no model intelligence ranking.
      score+= {'release':5,'audit':4,'verify':4,'challenge':3,'council':3,'plan':2,'code':1,'inquiry':1}[row[2]]+.75*(self.t-row[5])
      if row[3]>=0:score+=.1*sum(row[3] in x['deps'] for x in s['blocks'])
     choices.append((score,row,s))
     if self.c.claim_policy=='fifo' and self.c.controller!='work_autoscale':break
   if not choices:continue
   _,row,s=max(choices,key=lambda x:x[0]);ready.remove(row)
   jid,i,kind,b,g,created=row
   duration,cost=self.duration_cost(a,row,s)
   if self.c.capacity=='quota':
    f=a['family'];limit={'top_A':8.,'top_B':8.,'middle':36.,'bottom':24.}[f]
    if self.provider_used.get((f,int(self.t/24)),0)+duration>limit:continue
   snap={'original_intent':list(range(8)),'known':s['known'],'planned':s['planned'],'round':s['round']}
   if b>=0:
    block=s['blocks'][b];snap['dependencies']={str(x):s['blocks'][x]['generation'] for x in block['deps']}
    snap['requirements']=block['reqs']
   if kind=='inquiry':s['stage_authors'].append(a['id']);self.put(s)
   if kind=='release':s['release_authors'].append(a['id']);self.put(s)
   self.db.execute("UPDATE jobs SET status='running',started=?,agent=?,family=?,input=?,duration=?,cost=? WHERE id=?",(self.t,a['id'],a['family'],json.dumps(snap),duration,cost,jid))
   a['busy']=True;f=a['family'];self.provider_active[f]=self.provider_active.get(f,0)+1
   self.peak_provider[f]=max(self.peak_provider.get(f,0),self.provider_active[f]);self.peak_active=max(self.peak_active,sum(self.provider_active.values()))
   self.provider_used[(f,int(self.t/24))]=self.provider_used.get((f,int(self.t/24)),0)+duration
   self.cost+=cost;self.busy+=duration;self.stage_busy[kind]=self.stage_busy.get(kind,0)+duration
   self.seq+=1;heapq.heappush(self.heap,(self.t+duration,self.seq,jid))
   self.log(i,'claim',{'job':jid,'kind':kind,'agent':a['id'],'family':f,'snapshot':snap})
   progress=True
  return progress
 def init_blocks(self,s):
  size=self.c.packet_size if self.c.architecture=='packet_graph' else 1
  planned=sorted(s['planned']);groups=[planned[j:j+size] for j in range(0,len(planned),size)]
  mapping={r:b for b,rs in enumerate(groups) for r in rs};blocks=[]
  for b,rs in enumerate(groups):
   deps=sorted({mapping[p] for r in rs for p in self.workload[s['id']]['deps'][r] if p in mapping and mapping[p]!=b})
   blocks.append(dict(reqs=rs,deps=deps,status='waiting',generation=0,attempts=0,bugs=[],interfaces=[],author=-1,snapshot={},audited=False))
  s['blocks']=blocks;s['phase']='work';s['release_pending']=False;s['release_votes']=[];s['release_authors']=[]
 def refresh(self,s):
  if s['phase']!='work':return
  mesh=self.c.architecture in ('evidence_graph','packet_graph')
  bs=s['blocks']
  for b,x in enumerate(bs):
   if x['status']=='waiting' and all(bs[d]['status']=='verified' if mesh else bs[d]['status'] in ('built','verify_queued','audit_queued','verified') for d in x['deps']):
    x['status']='code_queued';self.add(s,'code',b,x['generation'])
  barrier=self.c.architecture=='institutions'
  can_verify=not barrier or all(x['status'] in ('built','verify_queued','audit_queued','verified') for x in bs)
  if can_verify:
   for b,x in enumerate(bs):
    if x['status']=='built':x['status']='verify_queued';self.add(s,'verify',b,x['generation'])
  collective=self.c.architecture in ('institutions','evidence_graph','packet_graph') or self.c.common_controls
  if collective:
   for b,x in enumerate(bs):
    if x['status']=='verified' and not x['audited'] and self.u(s['id'],'audit_sample',b)<self.c.audit_rate:
     x['status']='audit_queued';self.add(s,'audit',b,x['generation'])
  if all(x['status']=='verified' for x in bs) and not s['release_pending']:
   s['release_pending']=True;s['release_votes']=[];s['release_authors']=[]
   for v in range(2 if collective else 1):self.add(s,'release',g=s['round']*2+v)
 def invalidate(self,s,b,reason):
  bs=s['blocks'];affected={b}
  for j in range(b+1,len(bs)):
   if any(d in affected for d in bs[j]['deps']):affected.add(j)
  for j in sorted(affected):
   x=bs[j]
   if j==b or x['status']!='waiting':
    x['generation']+=1;x['status']='waiting';x['bugs']=[];x['interfaces']=[];x['audited']=False
    self.db.execute("UPDATE jobs SET status='cancelled' WHERE idea=? AND block=? AND status='ready'",(s['id'],j))
  self.log(s['id'],'invalidate',{'blocks':sorted(affected),'reason':reason})
  s['release_pending']=False
 def finish_idea(self,s,failed=False):
  w=self.workload[s['id']];bugs=set();interfaces=[]
  for x in s['blocks']:bugs.update(x['bugs']);interfaces.extend(x['interfaces'])
  correct=[];planned=set(s['planned'])
  bad_targets={int(e.split(':')[1]) for e in interfaces}
  for r in range(8):correct.append(r in planned and r not in bugs and r not in bad_targets and all(correct[p] for p in w['deps'][r]))
  result=dict(idea=s['id'],released=not failed,end_to_end=self.t-self.workload[s['id']]['arrival'],lead=self.t-s['admitted'],intent=len(planned)/8 if not failed else 0.,
    useful=sum(correct)/8 if not failed else 0.,defects=len(bugs)+len(interfaces) if not failed else 0,
    perfect=bool(all(correct) and not failed),finish=self.t,attempts=sum(x['attempts'] for x in s['blocks']))
  self.completed.append(result);self.active.remove(s['id']);s['phase']='failed' if failed else 'released'
  self.db.execute('INSERT INTO outcomes VALUES (?,?)',(s['id'],json.dumps(result)))
  self.db.execute("UPDATE jobs SET status='cancelled' WHERE idea=? AND status='ready'",(s['id'],))
  self.log(s['id'],s['phase'],result)
 def complete(self,jid):
  row=self.db.execute('SELECT id,idea,kind,block,generation,agent,input,duration FROM jobs WHERE id=?',(jid,)).fetchone()
  _,i,kind,b,g,aid,snapshot,duration=row;a=self.agents[aid];a['busy']=False;self.provider_active[a['family']]-=1
  self.service_ewma[kind]=.8*self.service_ewma.get(kind,duration)+.2*duration
  s=self.get(i);snap=json.loads(snapshot);output={}
  if s['phase'] in ('failed','released') or (b>=0 and s['blocks'][b]['generation']!=g):
   self.waste+=duration;output={'discarded':'obsolete generation or terminated idea'}
  elif kind=='inquiry':
   found=[r for r in range(8) if self.pass_trial(a,s,r,'inquiry',g)]
   s['frames'].append(found);s['known']=sorted(set(s['known'])|set(found));output={'found':found}
   if len(s['frames'])==s['k']:
    s['last_author']=aid
    self.add(s,'council' if self.c.architecture=='institutions' or self.c.common_controls else 'plan')
  elif kind=='council':
   found=[r for r in range(8) if self.pass_trial(a,s,r,'council',scale=.55)]
   s['known']=sorted(set(s['known'])|set(found));s['last_author']=aid;self.add(s,'plan');output={'additional_evidence':found}
  elif kind=='plan':
   s['planned']=[r for r in s['known'] if self.pass_trial(a,s,r,'plan',scale=1.10)]
   s['last_author']=aid;output={'mapped':s['planned']}
   if self.c.architecture in ('institutions','evidence_graph','packet_graph') or self.c.common_controls:self.add(s,'challenge')
   else:self.init_blocks(s)
  elif kind=='challenge':
   recovered=[r for r in range(8) if r not in s['planned'] and self.pass_trial(a,s,r,'challenge',scale=.85)]
   s['planned']=sorted(set(s['planned'])|set(recovered));s['known']=sorted(set(s['known'])|set(recovered));self.init_blocks(s);output={'recovered':recovered}
  elif kind=='code':
   x=s['blocks'][b];x['attempts']+=1;x['author']=aid;x['family']=a['family'];x['snapshot']=snap.get('dependencies',{})
   x['bugs']=[r for r in x['reqs'] if not self.pass_trial(a,s,r,'code',x['attempts'],len(x['reqs'])) or self.u(i,'read',r,aid,x['attempts'])<self.c.read_error]
   interfaces=[]
   for r in x['reqs']:
    for p in self.workload[i]['deps'][r]:
     if p not in x['reqs'] and any(p in s['blocks'][d]['reqs'] for d in x['deps']):
      prob=self.c.decoherence*(1.25-.5*self.probability(a,s,r,'code'))
      if self.u(i,'interface',p,r,aid,x['attempts'])<prob:interfaces.append(f'{p}:{r}')
   x['interfaces']=interfaces
   detected=[r for r in x['bugs'] if self.u(i,'test',r,aid,x['attempts'])<self.c.test_catch]
   output={'artifact':{'requirements':x['reqs'],'version':g},'tests_failed':bool(detected)}
   if detected:
    if x['attempts']>=self.c.max_attempts:self.finish_idea(s,True)
    else:self.invalidate(s,b,'tests')
   else:x['status']='built'
  elif kind in ('verify','audit'):
   x=s['blocks'][b];x['reviewer' if kind=='verify' else 'auditor']=aid;s['last_verifier']=aid
   stale=any(s['blocks'][int(d)]['generation']!=v for d,v in x['snapshot'].items())
   caught=[r for r in x['bugs'] if self.pass_trial(a,s,r,kind,x['attempts'],len(x['reqs']),scale=.95)]
   crossed=[]
   if self.c.architecture in ('evidence_graph','packet_graph'):
    crossed=[e for e in x['interfaces'] if self.pass_trial(a,s,int(e.split(':')[1]),'interface_verify',x['attempts'],scale=.95)]
   output={'reviewer':aid,'author':x['author'],'rejected':bool(stale or caught or crossed),'stale':stale}
   if stale or caught or crossed:
    if x['attempts']>=self.c.max_attempts:self.finish_idea(s,True)
    else:self.invalidate(s,b,'verification')
   else:
    x['status']='verified'
    if kind=='audit':x['audited']=True
  elif kind=='release':
   missing=[r for r in range(8) if r not in s['planned'] and self.pass_trial(a,s,r,'intent_check',s['round'],scale=.85)]
   crossed=[]
   for bi,x in enumerate(s['blocks']):
    for e in x['interfaces']:
     if self.pass_trial(a,s,int(e.split(':')[1]),'release_interface',x['attempts'],scale=.8):crossed.append(bi)
   output={'missing_detected':missing,'interface_rejections':sorted(set(crossed))}
   s['release_votes'].append(output)
   collective=self.c.architecture in ('institutions','evidence_graph','packet_graph') or self.c.common_controls
   if len(s['release_votes'])==(2 if collective else 1):
    missing=sorted({r for vote in s['release_votes'] for r in vote['missing_detected']})
    crossed=sorted({bi for vote in s['release_votes'] for bi in vote['interface_rejections']})
    if missing or crossed:
     if s['round']>=self.c.max_release_rounds:self.finish_idea(s,True)
     else:
      s['round']+=1
      if missing:
       s['planned']=sorted(set(s['planned'])|set(missing));self.init_blocks(s)
       self.log(i,'intent_reopen',{'recovered':missing})
      else:
       for bi in crossed:self.invalidate(s,bi,'release_interface')
    else:self.finish_idea(s)
  self.refresh(s);self.put(s)
  self.db.execute("UPDATE jobs SET status='done',ended=?,output=? WHERE id=?",(self.t,json.dumps(output),jid))
  self.log(i,'complete',{'job':jid,'kind':kind,'output':output})
 def run(self):
  self.admit()
  while len(self.completed)<self.c.ideas or self.heap:
   self.schedule()
   next_arrival=self.workload[self.next_idea]['arrival'] if self.next_idea<self.c.ideas and len(self.active)<self.c.wip else float('inf')
   if next_arrival>self.t and next_arrival<(self.heap[0][0] if self.heap else float('inf')):
    self.t=next_arrival;self.admit();continue
   if self.heap:
    t,_,jid=heapq.heappop(self.heap);self.t=t;self.complete(jid);self.admit()
   elif self.c.capacity=='quota' and self.active:
    self.t=(int(self.t/24)+1)*24
   elif self.active:raise RuntimeError('deadlock '+str(self.c)+' '+str(self.db.execute("SELECT idea,kind,status FROM jobs WHERE status='ready'").fetchall()))
   else:break
   if self.t>100000 or self.seq>30000:raise RuntimeError('runaway '+str(self.c)+' '+str([self.get(i) for i in self.active]))
  release=[x for x in self.completed if x['released']];n=len(release);hours=self.t
  lead=sorted(x['lead'] for x in release)
  waits=self.db.execute("SELECT kind,AVG(started-created) FROM jobs WHERE started IS NOT NULL GROUP BY kind").fetchall()
  stats=dict(architecture=self.c.architecture,mix='/'.join(map(str,self.c.mix)),seed=self.c.seed,ideas=self.c.ideas,
    released=n,failed=self.c.ideas-n,hours=hours,ideas_week=n*168/hours,useful_week=sum(x['useful'] for x in self.completed)*168/hours,
    perfect_week=sum(x['perfect'] for x in self.completed)*168/hours,intent=statistics.mean(x['intent'] for x in release) if n else 0,
    defects=statistics.mean(x['defects'] for x in release) if n else 0,completion=n/self.c.ideas,
    lead=statistics.mean(lead) if lead else float('nan'),p95_lead=lead[min(len(lead)-1,int(.95*len(lead)))] if lead else float('nan'),
    cost=self.cost,cost_idea=self.cost/n if n else float('inf'),cost_useful=self.cost/sum(x['useful'] for x in self.completed) if sum(x['useful'] for x in self.completed) else float('inf'),
    peak_active=self.peak_active,mean_active=self.busy/hours,end_to_end=statistics.mean(x['end_to_end'] for x in release) if n else float('nan'),utilization=self.busy/(len(self.agents)*hours),waste_fraction=self.waste/self.busy,max_queue=self.max_queue,
    attempts=sum(x['attempts'] for x in self.completed),jobs=self.db.execute('SELECT count(*) FROM jobs').fetchone()[0],
    peak_provider=json.dumps(self.peak_provider),stage_busy=json.dumps(self.stage_busy),stage_wait=json.dumps(dict(waits)))
  self.db.commit();self.db.close();return stats

def run(cfg):return Simulation(cfg).run()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--architecture',default='institutions',choices=ARCHITECTURES);p.add_argument('--mix',default='6,3,3');p.add_argument('--seed',type=int,default=0);p.add_argument('--ideas',type=int,default=32);p.add_argument('--audit',default=None);a=p.parse_args()
 print(json.dumps(run(Config(architecture=a.architecture,mix=tuple(map(int,a.mix.split(','))),seed=a.seed,ideas=a.ideas,audit_path=a.audit)),indent=2))
