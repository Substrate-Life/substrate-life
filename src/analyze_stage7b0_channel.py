"""Independent fail-closed reducer for retained Stage 7B0 evidence.

The producer emits observations only. This module reconstructs ledger equations,
account/event totals, registered block predictions, and global gates. Malformed,
omitted, contradictory, or wrong-fixture evidence is INVALID; complete evidence
that misses a registered mechanism prediction is FAIL.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import re

from stage7b0_channel import (
    BLOCK_CHECK_KEYS, BLOCK_IDS, GATE_IDS, PROGRAM_SPEC_SHA256, PROTOCOL_SHA256,
)

_EXPECTED_ARMS={"A":("LOW","HIGH"),"B":("LOW","HIGH"),"C":("LOW","HIGH"),"D1":("fixture",),"D2":("fixture",),"E1":("LOW","HIGH"),"E2":("LOW","HIGH")}
_EXPECTED_FIXTURES={}
for arm in ("LOW","HIGH"):
    _EXPECTED_FIXTURES[("A",arm)]={"memory_pool":8192,"parent_id":"parent","opening_S":100,"opening_R":0,"seed":42,"generation_tick":0,"packet_id":1,"packet_budget":300,"max_reducible":192,"child_id":"child"}
    _EXPECTED_FIXTURES[("B",arm)]={"capacity":4,"founders":1,"founder_id":"org-0","founder_S":100,"founder_R":0,"memory_pool":8192,"seed":42,"packet_rate":2,"buffer_depth":4,"packet_budget":300,"hazard_rate":0,"corpse_ttl":2,"ticks":[0,1]}
    _EXPECTED_FIXTURES[("C",arm)]={"memory_pool":8192,"parent_id":"parent","opening_S":100,"opening_R":0,"seed":42,"packets":[{"generation_tick":0,"packet_id":1,"budget":10},{"generation_tick":1,"packet_id":2,"budget":300}],"max_reducible":192,"child_id":"child"}
    _EXPECTED_FIXTURES[("E1",arm)]={"memory_pool":8192,"parent_id":"parent","opening_S":100,"opening_R":0,"seed":42,"generation_tick":0,"packet_id":1,"packet_budget":300,"partial_extent":20,"complete_extent":64}
    _EXPECTED_FIXTURES[("E2",arm)]={"memory_pool":8192,"parent_id":"parent","opening_S":100,"opening_R":0,"seed":43,"generation_tick":0,"packet_id":1,"packet_budget":300,"failed_reversal_extent":80,"child_id":"child"}
for block,labels in (("D1",{"org-0":"LOW","org-1":"HIGH"}),("D2",{"org-0":"HIGH","org-1":"LOW"})):
    _EXPECTED_FIXTURES[(block,"fixture")]={"capacity":2,"founders":2,"founder_ids":["org-0","org-1"],"founder_S":100,"founder_R":0,"labels":labels,"memory_pool":8192,"seed":42,"packet_rate":1,"buffer_depth":2,"packet_budget":300,"hazard_rate":0,"corpse_ttl":2,"ticks":[0,1,2,3]}
_EXPECTED_CP={
 "A":("INITIAL","POST_FORAGE","POST_ALLOC","POST_COPY","POST_DIVIDE","FINAL"),
 "B":("INITIAL","POST_PACKET_ARRIVAL","POST_ADMISSION","POST_MEMBER","TICK_COMPLETE","POST_PACKET_ARRIVAL","POST_ADMISSION","POST_MEMBER","POST_ADMISSION","POST_MEMBER","TICK_COMPLETE"),
 "C":("INITIAL","POST_FORAGE","POST_ALLOC","POST_FORAGE","POST_ALLOC","POST_COPY","POST_DIVIDE","FINAL"),
 "D1":("INITIAL",)+("POST_PACKET_ARRIVAL","POST_REJECTION","POST_MEMBER","POST_MEMBER","TICK_COMPLETE")*4,
 "D2":("INITIAL",)+("POST_PACKET_ARRIVAL","POST_REJECTION","POST_MEMBER","POST_MEMBER","TICK_COMPLETE")*4,
 "E1":("INITIAL","POST_FORAGE","POST_REVERSAL","POST_REVERSAL","FINAL"),
 "E2":("INITIAL","POST_FORAGE","POST_ALLOC","POST_COPY","POST_DIVIDE","POST_REVERSAL","FINAL")}
def _d_transitions():
 return [x for tick in range(4) for x in ((tick,"org-0","FORAGE_RLE","SUCCESS"),(tick,"org-0","ALLOC_OFFSPRING","SUCCESS"),(tick,"org-0","COPY_BLOCK","SUCCESS"),(tick,"org-0","DIVIDE","REJECTED_NO_VACANCY"),(tick,"org-1","READ_EMPTY","NO_PACKET"))]
_EXPECTED_TRANS={
 "A":[(None,"parent","FORAGE_RLE","SUCCESS"),(None,"parent","ALLOC_OFFSPRING","SUCCESS"),(None,"parent","COPY_BLOCK","SUCCESS"),(None,"parent","DIVIDE","SUCCESS")],
 "B":[(0,"org-0",op,"SUCCESS") for op in ("FORAGE_RLE","ALLOC_OFFSPRING","COPY_BLOCK","DIVIDE")]+[(1,actor,op,"SUCCESS") for actor in ("org-0","org-1") for op in ("FORAGE_RLE","ALLOC_OFFSPRING","COPY_BLOCK","DIVIDE")],
 "C":[(None,"parent","FORAGE_RLE","SUCCESS"),(None,"parent","ALLOC_OFFSPRING","R_INSUFFICIENT"),(None,"parent","FORAGE_RLE","SUCCESS"),(None,"parent","ALLOC_OFFSPRING","SUCCESS"),(None,"parent","COPY_BLOCK","SUCCESS"),(None,"parent","DIVIDE","SUCCESS")],
 "D1":_d_transitions(),"D2":_d_transitions(),
 "E1":[(None,"parent","FORAGE_RLE","SUCCESS"),(None,"parent","REVERSE_RLE_20","SUCCESS"),(None,"parent","REVERSE_RLE_64","SUCCESS")],
 "E2":[(None,"parent","FORAGE_RLE","SUCCESS"),(None,"parent","ALLOC_OFFSPRING","SUCCESS"),(None,"parent","COPY_BLOCK","SUCCESS"),(None,"parent","DIVIDE","SUCCESS"),(None,"parent","REVERSE_RLE_80","REVERSAL_ACCOUNT_UNAVAILABLE")]}
_GATE_REQ={
 "realised_treatment":tuple((b,"realised_treatment") for b in BLOCK_IDS),
 "programme_identity":tuple((b,"programme_identity") for b in BLOCK_IDS),
 "allocation_identity":tuple((b,"allocation_identity") for b in BLOCK_IDS),
 "direct_debit_isolation":tuple((b,"direct_debit_isolation") for b in ("A","B","C","D1","D2","E2")),
 "reversal_provenance":(("E1","partial_and_complete_reversal"),("E2","spent_credit_atomic_failure")),
 "recovery":(("C","registered_recovery"),),"lifecycle":(("B","two_generation_sequence"),),
 "topology":(("D1","shared_source_topology"),("D2","shared_source_topology"),("_cross","label_permutation")),
 "closure":tuple((b,"all_checkpoints_closed") for b in BLOCK_IDS),
 "no_hidden_gate":tuple((b,"no_hidden_gate") for b in BLOCK_IDS)}
_FORBIDDEN={"fitness","selection_coefficient","p_value","p-value","ess","optimum","invasion_growth","reproductive_value"}
_HEX64=re.compile(r"^[0-9a-f]{64}$")

def _exact(value, keys, where):
 if not isinstance(value,dict) or set(value)!=set(keys): raise ValueError(f"{where} keys differ")
def _scan(value,where="artifact"):
 if isinstance(value,dict):
  for k,v in value.items():
   if str(k).lower() in _FORBIDDEN: raise ValueError(f"prohibited field {where}:{k}")
   _scan(v,f"{where}.{k}")
 elif isinstance(value,list):
  for i,v in enumerate(value): _scan(v,f"{where}[{i}]")
def _r(value,where="rational"):
 if isinstance(value,bool): raise ValueError(f"boolean rational at {where}")
 if isinstance(value,int): return Fraction(value)
 if not isinstance(value,dict) or set(value)!={"numerator","denominator"}: raise ValueError(f"malformed rational at {where}")
 if not isinstance(value["numerator"],int) or not isinstance(value["denominator"],int) or value["denominator"]==0: raise ValueError(f"malformed rational at {where}")
 return Fraction(value["numerator"],value["denominator"])

def _participant_hash(a,t,d):
 return hashlib.sha256(json.dumps({"A":a,"D":d,"T":t},sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _validate_participant(item,where):
 _exact(item,{"role","organism_id","treatment_label","A","T","D","heritable_state_sha256"},where)
 label=item["treatment_label"]; expected_a={"LOW":102,"HIGH":204}.get(label)
 if (item["A"],item["T"],item["D"])!=(expected_a,128,255): raise ValueError(f"realised treatment mismatch at {where}")
 if item["heritable_state_sha256"]!=_participant_hash(item["A"],item["T"],item["D"]): raise ValueError(f"heritable hash mismatch at {where}")
def _pkey(item): return (item["role"],item["organism_id"],item["treatment_label"])

def _expected_packet_ids(block,index):
 if block=="B": return list(range(1,(0,2,2,2,2,4,4,4,4,4,4)[index]+1))
 if block in {"D1","D2"}: return [] if index==0 else list(range(1,((index-1)//5)+2))
 if block=="C": return [1,2]
 return [1]
def _expected_cp_participants(block,arm,index):
 if block in {"A","C","E1","E2"}:
  label=arm; values=[("parent","parent",label)]
  birth_at={"A":4,"C":6,"E1":999,"E2":4}[block]
  if index>=birth_at: values.append(("descendant","child",label))
  return values
 if block=="B":
  count=(1,1,2,2,2,2,3,3,4,4,4)[index]
  return [("founder" if i==0 else "descendant",f"org-{i}",arm) for i in range(count)]
 labels=_EXPECTED_FIXTURES[(block,"fixture")]["labels"]
 return [("founder",oid,label) for oid,label in labels.items()]

def _validate_reserve(axis,where):
 if not isinstance(axis,dict) or axis.get("kind") not in {"isolated","population"}: raise ValueError(f"reserve absent at {where}")
 if axis["kind"]=="isolated":
  keys={"kind","opening_S","opening_R","current_S","current_R","committed","destroyed","gross_income","reversed_income","C_S","C_R","lhs","rhs","closed"}; _exact(axis,keys,where)
  lhs=_r(axis["current_S"])+_r(axis["current_R"])+_r(axis["committed"])+_r(axis["destroyed"])
  rhs=_r(axis["opening_S"])+_r(axis["opening_R"])+_r(axis["gross_income"])-_r(axis["reversed_income"])-_r(axis["C_S"])-_r(axis["C_R"])
 else:
  keys={"kind","opening_energy","live_reserves","destroyed","gross_income","reversed_income","costs","lhs","rhs","closed"}; _exact(axis,keys,where)
  lhs=_r(axis["live_reserves"])+_r(axis["destroyed"])
  rhs=_r(axis["opening_energy"])+_r(axis["gross_income"])-_r(axis["reversed_income"])-_r(axis["costs"])
 if _r(axis["lhs"])!=lhs or _r(axis["rhs"])!=rhs: raise ValueError(f"reserve components contradict lhs/rhs at {where}")
 closed=lhs==rhs
 if axis["closed"] is not closed: raise ValueError(f"reserve closed flag contradicts equation at {where}")
 return closed
def _validate_packet(packet,where):
 _exact(packet,{"packet_id","kind","initial_budget","budget_remaining","drawn_S","drawn_R","lhs","rhs","closed"},where)
 if packet["kind"] not in {"captured","unread"} or not isinstance(packet["packet_id"],int): raise ValueError(f"bad packet identity at {where}")
 initial=_r(packet["initial_budget"]); remaining=_r(packet["budget_remaining"]); ds=_r(packet["drawn_S"]); dr=_r(packet["drawn_R"])
 lhs=remaining+ds+dr
 if _r(packet["lhs"])!=lhs or _r(packet["rhs"])!=initial: raise ValueError(f"packet components contradict lhs/rhs at {where}")
 if packet["kind"]=="unread" and (ds!=0 or dr!=0 or remaining!=initial): raise ValueError(f"unread packet contains a draw at {where}")
 closed=lhs==initial
 if packet["closed"] is not closed: raise ValueError(f"packet closed flag contradicts equation at {where}")
 return closed
def _validate_memory(memory,where):
 _exact(memory,{"initial_pool","totals","ownership","lhs","rhs","closed"},where); _exact(memory["totals"],{"free_pool","somatic_active","gestation","corpse_reserved"},where+".totals")
 _exact(memory["ownership"],{"somatic_active","gestation","corpse_reserved"},where+".ownership")
 for bucket in memory["ownership"].values():
  if not isinstance(bucket,dict) or any(not isinstance(k,str) or not isinstance(v,int) or v<0 for k,v in bucket.items()): raise ValueError(f"invalid memory ownership at {where}")
 for name in ("somatic_active","gestation","corpse_reserved"):
  if sum(memory["ownership"][name].values())!=memory["totals"][name]: raise ValueError(f"memory ownership detached from totals at {where}:{name}")
 lhs=sum(memory["totals"].values()); rhs=memory["initial_pool"]
 if any(not isinstance(v,int) or v<0 for v in memory["totals"].values()) or not isinstance(rhs,int): raise ValueError(f"invalid memory components at {where}")
 if memory["lhs"]!=lhs or memory["rhs"]!=rhs: raise ValueError(f"memory components contradict lhs/rhs at {where}")
 closed=lhs==rhs
 if memory["closed"] is not closed: raise ValueError(f"memory closed flag contradicts equation at {where}")
 return closed
def _validate_census(census,where):
 _exact(census,{"founders","admitted_births","hazard_removals","lhs","rhs","closed"},where)
 lhs=census["founders"]+census["admitted_births"]-census["hazard_removals"]; rhs=census["rhs"]
 if census["lhs"]!=lhs: raise ValueError(f"census components contradict lhs at {where}")
 closed=lhs==rhs
 if census["closed"] is not closed: raise ValueError(f"census closed flag contradicts equation at {where}")
 return closed

def _validate_population_event(event,where):
 if not isinstance(event,dict): raise ValueError(f"malformed population event at {where}")
 kind=event.get("event")
 keys={
  "packet_capture_failed":{"tick","phase","event","organism_id"},
  "birth_rejected_no_vacancy":{"tick","phase","event","parent_id"},
  "birth_admitted":{"tick","phase","event","parent_id","child_id","provision"},
 }.get(kind)
 if keys is None: raise ValueError(f"unregistered population event at {where}:{kind}")
 _exact(event,keys,where)
 if not isinstance(event["tick"],int) or event["phase"]!={"packet_capture_failed":"packet_capture","birth_rejected_no_vacancy":"admission","birth_admitted":"admission"}[kind]: raise ValueError(f"bad population event metadata at {where}")
 if "provision" in event: _r(event["provision"],where+".provision")

def _validate_checkpoint(cp,block,arm,index):
 _exact(cp,{"name","detail","reserve","packets","memory","census","participants","accounts","population_events","evictions","closed"},f"{block}.{arm}.cp{index}")
 if cp["name"]!=_EXPECTED_CP[block][index] or not isinstance(cp["detail"],str): raise ValueError(f"checkpoint identity mismatch {block}.{arm}.{index}")
 if cp["evictions"]!=0: raise ValueError(f"packet eviction at {block}.{arm}.{index}")
 ids=[p.get("packet_id") for p in cp["packets"]]
 if ids!=_expected_packet_ids(block,index): raise ValueError(f"packet evidence incomplete at {block}.{arm}.{index}: {ids}")
 reserve=_validate_reserve(cp["reserve"],f"{block}.{arm}.{index}.reserve")
 packets=[_validate_packet(p,f"{block}.{arm}.{index}.packet") for p in cp["packets"]]
 memory=_validate_memory(cp["memory"],f"{block}.{arm}.{index}.memory")
 population=block in {"B","D1","D2"}
 census=_validate_census(cp["census"],f"{block}.{arm}.{index}.census") if population else True
 if not population and cp["census"] is not None: raise ValueError(f"isolated census at {block}.{arm}.{index}")
 observed=[]
 for j,item in enumerate(cp["participants"]): _validate_participant(item,f"{block}.{arm}.{index}.participant{j}"); observed.append(_pkey(item))
 if observed!=_expected_cp_participants(block,arm,index): raise ValueError(f"checkpoint participants mismatch {block}.{arm}.{index}")
 participant_ids=[item["organism_id"] for item in cp["participants"]]
 ownership=cp["memory"]["ownership"]
 if set(ownership["somatic_active"])!=set(participant_ids) or ownership["corpse_reserved"]!={}: raise ValueError(f"memory ownership/participants mismatch {block}.{arm}.{index}")
 expected_gestation={}
 if (block=="A" and index in {2,3}) or (block=="C" and index in {4,5}) or (block=="E2" and index in {2,3}): expected_gestation={"parent":64}
 if ownership["gestation"]!=expected_gestation: raise ValueError(f"gestation ownership mismatch {block}.{arm}.{index}")
 account_data=[]
 for j,state in enumerate(cp["accounts"]): account_data.append((state,_validate_state(state,f"{block}.{arm}.{index}.account{j}")))
 account_ids=[state["participant"]["organism_id"] for state,_ in account_data]
 if account_ids!=[item["organism_id"] for item in cp["participants"] if item["role"]!="descendant" or population]:
  raise ValueError(f"checkpoint account/participant mismatch {block}.{arm}.{index}")
 if population:
  if not isinstance(cp["population_events"],list): raise ValueError(f"population event prefix absent {block}.{arm}.{index}")
  for j,event in enumerate(cp["population_events"]): _validate_population_event(event,f"{block}.{arm}.{index}.population_event{j}")
  births=[e for e in cp["population_events"] if e.get("event")=="birth_admitted"]
  deaths=[e for e in cp["population_events"] if e.get("event")=="hazard_death"]
  if len(births)!=cp["census"]["admitted_births"] or len(deaths)!=cp["census"]["hazard_removals"]: raise ValueError(f"census detached from population events {block}.{arm}.{index}")
  if any(e.get("child_id") not in participant_ids for e in births): raise ValueError(f"admitted child missing from participants {block}.{arm}.{index}")
  if _r(cp["reserve"]["live_reserves"])!=sum((_r(s["S"])+_r(s["R"]) for s,_ in account_data),Fraction(0)): raise ValueError(f"population live reserves detached from accounts {block}.{arm}.{index}")
  if _r(cp["reserve"]["gross_income"])!=sum((_r(s["gross_income"]) for s,_ in account_data),Fraction(0)): raise ValueError(f"population gross detached from events {block}.{arm}.{index}")
  if _r(cp["reserve"]["reversed_income"])!=sum((_r(s["reversed_income"]) for s,_ in account_data),Fraction(0)): raise ValueError(f"population reversal detached from events {block}.{arm}.{index}")
  if _r(cp["reserve"]["costs"])!=sum((_r(s["C_S"])+_r(s["C_R"]) for s,_ in account_data),Fraction(0)): raise ValueError(f"population costs detached from events {block}.{arm}.{index}")
  if cp["census"]["rhs"]!=len(cp["participants"]): raise ValueError(f"census detached from participants {block}.{arm}.{index}")
 else:
  if cp["population_events"]!=[]: raise ValueError(f"isolated checkpoint has population events {block}.{arm}.{index}")
  state=account_data[0][0]
  mapping={"current_S":"S","current_R":"R","committed":"committed","destroyed":"destroyed","gross_income":"gross_income","reversed_income":"reversed_income","C_S":"C_S","C_R":"C_R"}
  if any(_r(cp["reserve"][axis])!=_r(state[field]) for axis,field in mapping.items()): raise ValueError(f"isolated reserve detached from account {block}.{arm}.{index}")
 packet_totals={}
 for state,_ in account_data:
  for event in state["events"]:
   if event.get("event")=="draw":
    total=packet_totals.setdefault(event["packet_id"],[Fraction(0),Fraction(0)]); total[0]+=_r(event["delta_s"]); total[1]+=_r(event["delta_r"])
   elif event.get("event")=="partial_reversal":
    total=packet_totals.setdefault(event["packet_id"],[Fraction(0),Fraction(0)]); total[0]-=_r(event["debit_s"]); total[1]-=_r(event["debit_r"])
 for packet in cp["packets"]:
  expected=packet_totals.get(packet["packet_id"],[Fraction(0),Fraction(0)])
  if (_r(packet["drawn_S"]),_r(packet["drawn_R"]))!=tuple(expected): raise ValueError(f"packet state detached from account events {block}.{arm}.{index}")
 closed=reserve and all(packets) and memory and census
 if cp["closed"] is not closed: raise ValueError(f"aggregate closure flag contradiction {block}.{arm}.{index}")
 return closed

def _validate_account_event(event,where):
 kind=event.get("event") if isinstance(event,dict) else None
 base={
  "charge_s":{"event","s","r","reason","amount"},
  "charge_r":{"event","s","r","reason","amount"},
  "r_insufficient":{"event","s","r","reason","required"},
  "draw":{"event","s","r","packet_id","quantity","delta_s","delta_r","input_bytes","output_bytes","transform"},
  "gestation_allocated":{"event","s","r","bytes","owner"},
  "copy_complete":{"event","s","r","instructions"},
  "provision_committed":{"event","s","r","child_id","provision"},
  "divide_rejected_no_vacancy":{"event","s","r"},
  "partial_reversal":{"event","s","r","packet_id","quantity","debit_s","debit_r","input_bytes","output_bytes","transform"},
  "reversal_failed":{"event","s","r","packet_id","quantity","debit_s","debit_r","input_bytes","output_bytes","transform","reason"},
 }.get(kind)
 if base is None: raise ValueError(f"unknown account event at {where}:{kind}")
 timed={"tick","actor"}.issubset(event)
 if ("tick" in event)!=("actor" in event): raise ValueError(f"partial scheduler metadata at {where}")
 _exact(event,base|({"tick","actor"} if timed else set()),where)
 for name in ("s","r","amount","required","quantity","delta_s","delta_r","provision","debit_s","debit_r"):
  if name in event: _r(event[name],where+"."+name)
 if timed and (not isinstance(event["tick"],int) or not isinstance(event["actor"],str)): raise ValueError(f"bad scheduler metadata at {where}")

def _validate_state(state,where):
 _exact(state,{"participant","S","R","C_S","C_R","gross_income","reversed_income","committed","destroyed","child","events"},where); _validate_participant(state["participant"],where+".participant")
 for name in ("S","R","C_S","C_R","gross_income","reversed_income","committed","destroyed"): _r(state[name],where+"."+name)
 if state["child"] is not None:
  _exact(state["child"],{"organism_id","S","R","A","T","D"},where+".child"); _r(state["child"]["S"]); _r(state["child"]["R"])
  participant=state["participant"]
  if (state["child"]["A"],state["child"]["T"],state["child"]["D"])!=(participant["A"],participant["T"],participant["D"]): raise ValueError(f"child traits differ from parent at {where}")
 if not isinstance(state["events"],list): raise ValueError(f"events absent at {where}")
 for i,event in enumerate(state["events"]):
  _validate_account_event(event,where+f".event{i}")
 draws=[e for e in state["events"] if e.get("event")=="draw"]
 gross=sum((_r(e["quantity"],where+".draw") for e in draws),Fraction(0))
 reversed_total=sum((_r(e["quantity"],where+".reverse") for e in state["events"] if e.get("event")=="partial_reversal"),Fraction(0))
 cs=sum((_r(e["amount"],where+".charge_s") for e in state["events"] if e.get("event")=="charge_s"),Fraction(0))
 cr=sum((_r(e["amount"],where+".charge_r") for e in state["events"] if e.get("event")=="charge_r"),Fraction(0))
 committed=sum((_r(e["provision"],where+".provision") for e in state["events"] if e.get("event")=="provision_committed"),Fraction(0))
 account_consistent=(_r(state["gross_income"]),_r(state["reversed_income"]),_r(state["C_S"]),_r(state["C_R"]),_r(state["committed"]))==(gross,reversed_total,cs,cr,committed)
 label=state["participant"]["treatment_label"]; alpha=Fraction(2,5) if label=="LOW" else Fraction(4,5)
 allocation=all(_r(e["delta_r"])==alpha*_r(e["quantity"]) and _r(e["delta_s"])+_r(e["delta_r"])==_r(e["quantity"]) for e in draws)
 s_reason=lambda reason: (reason=="READ" or reason=="READ_EMPTY" or reason.endswith(":dispatch") or reason.startswith("ordinary_upkeep:") or reason.startswith("TRANSFORM_COMPRESS_") or reason.startswith("TRANSFORM_EXPAND_"))
 r_reason=lambda reason: (reason.endswith(":work") or reason.startswith("gestation_upkeep:"))
 direct=account_consistent and _r(state["destroyed"])==0 and all(
  (e.get("event")!="charge_s" or s_reason(str(e.get("reason",""))))
  and (e.get("event")!="charge_r" or r_reason(str(e.get("reason",""))))
  for e in state["events"]
 )
 return {"draws":draws,"allocation":allocation,"direct":direct,"events":state["events"]}

def _replay_account(state,opening_s,opening_r):
 s,r=opening_s,opening_r; valid=True
 for event in state["events"]:
  kind=event["event"]
  if kind=="draw": s+=_r(event["delta_s"]); r+=_r(event["delta_r"])
  elif kind=="charge_s": s-=_r(event["amount"])
  elif kind=="charge_r": r-=_r(event["amount"])
  elif kind=="provision_committed": r-=_r(event["provision"])
  elif kind=="partial_reversal": s-=_r(event["debit_s"]); r-=_r(event["debit_r"])
  valid &= (_r(event["s"])==s and _r(event["r"])==r)
 return valid and (_r(state["S"])==s and _r(state["R"])==r)

def _event_tuples(events,name,fields): return [tuple(e.get(f) for f in fields) for e in events if e.get("event")==name]
def _rv(value): return [_r(v) for v in value]
def _draw_signature(states):
 return {s["participant"]["organism_id"]:[(e["packet_id"],_r(e["quantity"]),_r(e["delta_s"]),_r(e["delta_r"])) for e in d["draws"]] for s,d in states}

def _transitions_from_raw(block,states,population_events):
 found=[]
 for state,_ in states:
  default_actor=state["participant"]["organism_id"]
  for event in state["events"]:
   kind=event["event"]; tick=event.get("tick"); actor=event.get("actor",default_actor)
   item=None
   if kind=="draw": item=(tick,actor,"FORAGE_RLE","SUCCESS")
   elif kind=="r_insufficient" and str(event.get("reason","")).startswith("ALLOC_OFFSPRING"):
    item=(tick,actor,"ALLOC_OFFSPRING","R_INSUFFICIENT")
   elif kind=="gestation_allocated": item=(tick,actor,"ALLOC_OFFSPRING","SUCCESS")
   elif kind=="copy_complete": item=(tick,actor,"COPY_BLOCK","SUCCESS")
   elif kind=="provision_committed": item=(tick,actor,"DIVIDE","SUCCESS")
   elif kind=="divide_rejected_no_vacancy": item=(tick,actor,"DIVIDE","REJECTED_NO_VACANCY")
   elif kind=="partial_reversal": item=(tick,actor,f"REVERSE_RLE_{event['input_bytes']}","SUCCESS")
   elif kind=="reversal_failed": item=(tick,actor,f"REVERSE_RLE_{event['input_bytes']}",event["reason"])
   if item is not None: found.append(item)
 for event in population_events:
  if event.get("event")=="packet_capture_failed": found.append((event["tick"],event["organism_id"],"READ_EMPTY","NO_PACKET"))
 if block in {"B","D1","D2"}:
  rank={"FORAGE_RLE":0,"ALLOC_OFFSPRING":1,"COPY_BLOCK":2,"DIVIDE":3,"READ_EMPTY":4}
  found.sort(key=lambda x:(x[0],int(x[1].split("-")[-1]),rank[x[2]]))
 return found

def _validate_memory_history(cps,history,where):
 if not isinstance(history,list) or not history: raise ValueError(f"memory history absent at {where}")
 normalized=[]; expected_pool=cps[0]["memory"]["initial_pool"]
 for i,record in enumerate(history):
  _exact(record,{"operation","free_pool","somatic_active","gestation","corpse_reserved","ownership"},f"{where}.memory_history{i}")
  if not isinstance(record["operation"],str): raise ValueError(f"invalid memory operation at {where}.{i}")
  totals={name:record[name] for name in ("free_pool","somatic_active","gestation","corpse_reserved")}
  observed=sum(totals.values())
  _validate_memory({"initial_pool":expected_pool,"totals":totals,"ownership":record["ownership"],"lhs":observed,"rhs":expected_pool,"closed":observed==expected_pool},f"{where}.memory_history{i}")
  normalized.append((totals,record["ownership"]))
 cursor=0
 for i,cp in enumerate(cps):
  target=(cp["memory"]["totals"],cp["memory"]["ownership"])
  match=next((j for j in range(cursor,len(normalized)) if normalized[j]==target),None)
  if match is None: raise ValueError(f"checkpoint memory not found in mutation history at {where}.{i}")
  cursor=match

def _derive_arm(block,arm,data):
 _exact(data,{"identity","fixture","checkpoints","transitions","terminal"},f"{block}.{arm}")
 if data["fixture"]!=_EXPECTED_FIXTURES[(block,arm)]: raise ValueError(f"fixture mismatch {block}.{arm}")
 identity=data["identity"]; _exact(identity,{"programme_sha256","initial_participants","terminal_participants"},f"{block}.{arm}.identity")
 if identity["programme_sha256"]!=PROGRAM_SPEC_SHA256: raise ValueError(f"programme hash mismatch {block}.{arm}")
 for phase in ("initial_participants","terminal_participants"):
  for i,item in enumerate(identity[phase]): _validate_participant(item,f"{block}.{arm}.{phase}.{i}")
 cps=data["checkpoints"]
 if not isinstance(cps,list) or len(cps)!=len(_EXPECTED_CP[block]): raise ValueError(f"checkpoint count mismatch {block}.{arm}")
 if identity["initial_participants"]!=cps[0]["participants"] or identity["terminal_participants"]!=cps[-1]["participants"]: raise ValueError(f"identity snapshots differ from checkpoint participants {block}.{arm}")
 closure=all(_validate_checkpoint(cp,block,arm,i) for i,cp in enumerate(cps))
 if block in {"B","D1","D2"}:
  previous=[]
  for i,cp in enumerate(cps):
   current=cp["population_events"]
   if current[:len(previous)]!=previous: raise ValueError(f"population event history is not append-only {block}.{arm}.{i}")
   previous=current
 transitions=data["transitions"]
 if not isinstance(transitions,list): raise ValueError(f"transitions absent {block}.{arm}")
 observed=[]
 for i,t in enumerate(transitions): _exact(t,{"tick","actor","operation","result"},f"{block}.{arm}.transition{i}"); observed.append((t["tick"],t["actor"],t["operation"],t["result"]))
 terminal=data["terminal"]
 expected_terminal_keys={
  "A":{"compressed_bytes","parent_S","parent_R","child_S","child_R","organisms","memory_history"},
  "B":{"tick_trace","population_events","final_buffer_ids","final_census","organisms","memory_history"},
  "C":{"first_state","first_failure_event","no_first_gestation","parent_S","parent_R","child_S","organisms","memory_history"},
  "D1":{"tick_trace","population_events","capture_owner_ids","capture_labels","packet_ids","final_census","organisms","memory_history"},
  "D2":{"tick_trace","population_events","capture_owner_ids","capture_labels","packet_ids","final_census","organisms","memory_history"},
  "E1":{"state_after_20","state_after_64","parent_S","parent_R","organisms","memory_history"},
  "E2":{"before_reversal","after_reversal","failure_event","organisms","memory_history"}}[block]
 _exact(terminal,expected_terminal_keys,f"{block}.{arm}.terminal")
 states=[]
 for i,state in enumerate(terminal["organisms"]): states.append((state,_validate_state(state,f"{block}.{arm}.state{i}")))
 if terminal["organisms"]!=cps[-1]["accounts"]: raise ValueError(f"terminal accounts differ from FINAL checkpoint {block}.{arm}")
 _validate_memory_history(cps,terminal["memory_history"],f"{block}.{arm}")
 if block in {"B","D1","D2"} and terminal["population_events"]!=cps[-1]["population_events"]: raise ValueError(f"terminal population events differ from FINAL checkpoint {block}.{arm}")
 openings={}
 for cp in cps:
  for state in cp["accounts"]:
   organism_id=state["participant"]["organism_id"]
   if organism_id not in openings:
    if state["events"]!=[]: raise ValueError(f"account first appears after events at {block}.{arm}:{organism_id}")
    openings[organism_id]=(_r(state["S"]),_r(state["R"]))
 replayed=all(_replay_account(state,*openings[state["participant"]["organism_id"]]) for state,_ in states)
 terminal_keys=[_pkey(s["participant"]) for s,_ in states]
 identity_terminal_keys=[_pkey(p) for p in identity["terminal_participants"]]
 if not terminal_keys or any(key not in identity_terminal_keys for key in terminal_keys): raise ValueError(f"terminal account holder absent from identity evidence {block}.{arm}")
 descendants={p["organism_id"]:p for p in identity["terminal_participants"] if p["role"]=="descendant"}
 for state,_ in states:
  child=state["child"]
  if child is not None:
   measured=descendants.get(child["organism_id"])
   if measured is None or (child["A"],child["T"],child["D"])!=(measured["A"],measured["T"],measured["D"]): raise ValueError(f"child identity not measured at {block}.{arm}")
 # Every terminal participant must first appear with its hash in a checkpoint no later than its first scheduled event.
 seen={}
 for i,cp in enumerate(cps):
  for part in cp["participants"]: seen.setdefault(part["organism_id"],i)
 if set(seen)!={p["organism_id"] for p in identity["terminal_participants"]}: raise ValueError(f"pre-event participant identity missing {block}.{arm}")
 checks={name:True for name in BLOCK_CHECK_KEYS[block]}
 population_events=terminal["population_events"] if block in {"B","D1","D2"} else []
 reconstructed_transitions=_transitions_from_raw(block,states,population_events)
 checks["programme_identity"]=observed==_EXPECTED_TRANS[block] and reconstructed_transitions==_EXPECTED_TRANS[block]
 checks["all_checkpoints_closed"]=closure
 checks["allocation_identity"]=all(d["allocation"] for _,d in states)
 if "direct_debit_isolation" in checks: checks["direct_debit_isolation"]=replayed and all(d["direct"] for _,d in states)

 sig=_draw_signature(states)
 label=arm if arm in {"LOW","HIGH"} else _EXPECTED_FIXTURES[(block,arm)]["labels"]["org-0"]
 split=(Fraction(315,4),Fraction(105,2)) if label=="LOW" else (Fraction(105,4),Fraction(105))
 full=lambda pid:(pid,Fraction(525,4),split[0],split[1])
 if block=="A":
  expected={"LOW":(Fraction(413,10),Fraction(26432,1275),Fraction(6271,40)),"HIGH":(Fraction(469,5),Fraction(60032,1275),Fraction(4171,40))}[arm]
  state=states[0][0]; rw=split[1]-_r(state["C_R"])
  checks["allocation_identity"] &= terminal["compressed_bytes"]==172 and sig=={"parent":[full(1)]}
  checks["direct_debit_isolation"] &= _r(state["C_S"])==Fraction(879,40) and _r(state["C_R"])==Fraction(56,5)
  checks["no_hidden_gate"]=(rw==expected[0] and _r(terminal["child_S"])==expected[1] and _r(terminal["child_R"])==0 and _r(terminal["parent_S"])==expected[2] and state["child"] is not None)
 elif block=="B":
  checks["allocation_identity"] &= sig=={"org-0":[full(1),full(2)],"org-1":[full(3)],"org-2":[],"org-3":[]}
  events=terminal["population_events"]; births=_event_tuples(events,"birth_admitted",("tick","parent_id","child_id"))
  traces=terminal["tick_trace"]
  checks["two_generation_sequence"]=(births==[(0,"org-0","org-1"),(1,"org-0","org-2"),(1,"org-1","org-3")] and [t["snapshot"]["packet_arrivals"] for t in traces]==[[1,2],[3,4]] and [t["snapshot"]["scheduler_snapshot"] for t in traces]==[["org-0"],["org-0","org-1"]] and terminal["final_buffer_ids"]==[4] and terminal["final_census"]==4)
  checks["no_hidden_gate"]=(not any(e.get("event") in {"hazard_death","somatic_stall","birth_rejected_no_vacancy"} for e in events) and traces[-1]["snapshot"]["admitted_births"]==2)
 elif block=="C":
  low_split=(Fraction(21,8),Fraction(7,4)) if arm=="LOW" else (Fraction(7,8),Fraction(7,2))
  expected_state=(Fraction(6671,80),Fraction(7,4)) if arm=="LOW" else (Fraction(6531,80),Fraction(7,2))
  checks["allocation_identity"] &= sig=={"parent":[(1,Fraction(35,8),low_split[0],low_split[1]),full(2)]}
  failure=terminal["first_failure_event"]
  checks["registered_recovery"]=(failure is not None and failure.get("event")=="r_insufficient" and failure.get("reason")=="ALLOC_OFFSPRING:work" and _rv([terminal["first_state"]["S"],terminal["first_state"]["R"]])==list(expected_state) and terminal["no_first_gestation"] is True and states[0][0]["child"] is not None)
  checks["no_hidden_gate"]=(states[0][0]["child"] is not None and _r(states[0][0]["child"]["R"])==0 and len(sig["parent"])==2)
 elif block in {"D1","D2"}:
  checks["allocation_identity"] &= sig=={"org-0":[full(i) for i in range(1,5)],"org-1":[]}
  events=terminal["population_events"]
  misses=_event_tuples(events,"packet_capture_failed",("tick","organism_id")); rejects=_event_tuples(events,"birth_rejected_no_vacancy",("tick","parent_id"))
  checks["shared_source_topology"]=(misses==[(i,"org-1") for i in range(4)] and rejects==[(i,"org-0") for i in range(4)] and terminal["packet_ids"]==[1,2,3,4] and terminal["capture_owner_ids"]==["org-0"]*4 and terminal["capture_labels"]==[label]*4 and all(t["snapshot"]["packet_arrivals"]==[i+1] for i,t in enumerate(terminal["tick_trace"])))
  checks["no_hidden_gate"]=(terminal["final_census"]==2 and all(t["snapshot"]["admitted_births"]==0 for t in terminal["tick_trace"]) and not _event_tuples(events,"birth_admitted",("child_id",)))
 elif block=="E1":
  checks["allocation_identity"] &= sig=={"parent":[full(1)]}
  exp20=(Fraction(200),Fraction(60),Fraction(40)) if arm=="LOW" else (Fraction(200),Fraction(20),Fraction(80))
  checks["partial_and_complete_reversal"]=_rv(terminal["state_after_20"])==list(exp20) and _rv(terminal["state_after_64"])==[Fraction(300),Fraction(0),Fraction(0)]
  checks["no_hidden_gate"]=_r(states[0][0]["reversed_income"])==Fraction(525,4)
 elif block=="E2":
  checks["allocation_identity"] &= sig=={"parent":[full(1)]}
  before=_rv(terminal["before_reversal"]); after=_rv(terminal["after_reversal"]); failure=terminal["failure_event"]
  expected_r=Fraction(52451,2550) if arm=="LOW" else Fraction(59563,1275)
  expected_packet=[Fraction(675,4),Fraction(315,4),Fraction(105,2)] if arm=="LOW" else [Fraction(675,4),Fraction(105,4),Fraction(105)]
  checks["spent_credit_atomic_failure"]=(before[1]==expected_r and before[2:]==expected_packet and after[1:]==before[1:] and before[0]-after[0]==Fraction(859,160) and failure.get("event")=="reversal_failed" and failure.get("reason")=="REVERSAL_ACCOUNT_UNAVAILABLE")
  checks["no_hidden_gate"]=checks["spent_credit_atomic_failure"]
 checks["no_hidden_gate"] &= replayed
 return checks

def analyze_artifact(artifact,expected_manifest_sha256):
 _scan(artifact); _exact(artifact,{"scope","selection_assay_run","mutation_enabled","mutation_rng_draws","protocol_sha256","programme_specification_sha256","freeze_manifest_sha256","blocks"},"raw artifact")
 if not _HEX64.fullmatch(expected_manifest_sha256): raise ValueError("invalid expected manifest digest")
 if artifact["freeze_manifest_sha256"]!=expected_manifest_sha256: raise ValueError("artifact is not bound to authorized manifest digest")
 if artifact["scope"]!="Stage 7B0 scripted fixed-state mechanism verification" or artifact["selection_assay_run"] is not False or artifact["mutation_enabled"] is not False or artifact["mutation_rng_draws"]!=0: raise ValueError("scope mismatch")
 if artifact["protocol_sha256"]!=PROTOCOL_SHA256 or artifact["programme_specification_sha256"]!=PROGRAM_SPEC_SHA256: raise ValueError("source identity mismatch")

 if not isinstance(artifact["blocks"],dict) or tuple(artifact["blocks"])!=BLOCK_IDS: raise ValueError("block set/order mismatch")
 block_results={}
 for block in BLOCK_IDS:
  _exact(artifact["blocks"][block],{"raw"},f"block {block}"); raw=artifact["blocks"][block]["raw"]; _exact(raw,{"arms"},f"block {block}.raw")
  if tuple(raw["arms"])!=_EXPECTED_ARMS[block]: raise ValueError(f"arm set/order mismatch {block}")
  arm_checks=[_derive_arm(block,arm,data) for arm,data in raw["arms"].items()]
  checks={name:all(item[name] for item in arm_checks) for name in BLOCK_CHECK_KEYS[block]}
  block_results[block]={"checks":checks,"result":"PASS" if all(checks.values()) else "FAIL","reasons":[k for k,v in checks.items() if not v]}
 d1=block_results["D1"]["checks"]["shared_source_topology"]; d2=block_results["D2"]["checks"]["shared_source_topology"]
 cross={"label_permutation":d1 and d2}
 gates={}
 for gate in GATE_IDS:
  evidence=[]; passed=True
  for block,check in _GATE_REQ[gate]:
   value=cross[check] if block=="_cross" else block_results[block]["checks"][check]
   evidence.append({"block":block,"check":check,"passed":value}); passed &= value
  gates[gate]={"classification":"PASS" if passed else "FAIL","passed":passed,"reason":"all registered evidence passed" if passed else "one or more registered checks failed","evidence":evidence}
 decision="PASS" if all(g["passed"] for g in gates.values()) else "FAIL"
 return {"decision":decision,"block_results":block_results,"cross_checks":cross,"gates":gates}

def _raw_from_completed(payload):
 return {k:payload[k] for k in ("scope","selection_assay_run","mutation_enabled","mutation_rng_draws","protocol_sha256","programme_specification_sha256","freeze_manifest_sha256","blocks")}

def validate_attempt_artifact(payload,expected_manifest_sha256):
 _scan(payload)
 if not _HEX64.fullmatch(expected_manifest_sha256): raise ValueError("invalid expected manifest digest")
 common={"artifact_version","run_status","decision","scope","selection_assay_run","mutation_enabled","mutation_rng_draws","protocol_sha256","programme_specification_sha256","freeze_manifest_sha256","blocks","analysis"}
 _exact(payload,common,"deterministic artifact")
 if payload["artifact_version"]!=1 or payload["run_status"]!="COMPLETED" or payload["freeze_manifest_sha256"]!=expected_manifest_sha256: raise ValueError("deterministic artifact identity mismatch")
 if payload["scope"]!="Stage 7B0 scripted fixed-state mechanism verification" or payload["selection_assay_run"] is not False or payload["mutation_enabled"] is not False or payload["mutation_rng_draws"]!=0 or payload["protocol_sha256"]!=PROTOCOL_SHA256 or payload["programme_specification_sha256"]!=PROGRAM_SPEC_SHA256: raise ValueError("artifact scope/source mismatch")
 derived=analyze_artifact(_raw_from_completed(payload),expected_manifest_sha256)
 if payload["decision"]!=derived["decision"] or payload["analysis"]!=derived: raise ValueError("analysis is not the independent reduction")
