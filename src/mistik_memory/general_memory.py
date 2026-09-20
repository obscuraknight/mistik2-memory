from __future__ import annotations
import os
import threading
from .episodic import EpisodicMemory
from .semantic import SemanticMemory
from .procedural import ProceduralMemory
from .consolidation import Consolidator
from .source_governance import SourceGovernance
_DEFAULT_WEIGHTS={"fact":1.0,"episode":0.9,"semantic":0.82,"procedure":0.78}
class AdaptiveRetriever:
    def __init__(self,general_memory): self.memory=general_memory;self.weights=dict(_DEFAULT_WEIGHTS);self._lock=threading.RLock()
    def feedback(self,memory_type,*,helpful:bool):
        if memory_type not in self.weights:raise ValueError("unknown memory type")
        if type(helpful) is not bool:raise ValueError("helpful must be boolean")
        with self._lock:
            self.weights[memory_type]=max(.4,min(1.4,self.weights[memory_type]+(.05 if helpful else -.05)));return self.weights[memory_type]
    def recall(self,query,*,limit=12,as_of=None):
        with self._lock:
            weights=dict(self.weights)
        with self.memory.governance.read_session() as snap:
            if not snap.available:return []
            rows=[];facts=self.memory.core.search(query,limit=max(limit,8))
            for source in ("confirmed","inferred"):
                for hit in facts.get(source,[]): rows.append({"memory_type":"fact","id":hit["fact_id"],"text":hit["text"],"source":source,"score":weights["fact"]*(hit.get("score") or 0.0),"record":hit})
            for ep in self.memory.episodic._recall(query,limit=max(limit,8),as_of=as_of,participants=None,tags=None,snapshot=snap): rows.append({"memory_type":"episode","id":ep["id"],"text":ep["summary"],"source":"episodic","score":weights["episode"]*ep["score"],"record":ep})
            for sm in self.memory.semantic._recall(query,limit=max(limit,8),snapshot=snap): rows.append({"memory_type":"semantic","id":sm["id"],"text":sm["summary"],"source":"semantic","score":weights["semantic"]*sm["score"],"record":sm})
            for pr in self.memory.procedural._recall(query,limit=max(limit,8),snapshot=snap): rows.append({"memory_type":"procedure","id":pr["id"],"text":pr["name"],"source":"procedural","score":weights["procedure"]*pr["score"],"record":pr})
            rows.sort(key=lambda r:(-r["score"],r["memory_type"],r["id"]));return rows[:max(0,int(limit))]
class GeneralMemorySystem:
    def __init__(self,core,*,external_source_resolver=None):
        self.core=core;root,_=os.path.splitext(core.data_path);master=getattr(core,"_master_key",None)
        self.governance=SourceGovernance(core,external_source_resolver=external_source_resolver)
        self.episodic=EpisodicMemory(root+"_episodes.json",master_key=master,governance=self.governance)
        self.semantic=SemanticMemory(root+"_semantic.json",master_key=master,governance=self.governance)
        self.procedural=ProceduralMemory(root+"_procedures.json",master_key=master,governance=self.governance)
        self.governance.register("episode",self.episodic);self.governance.register("semantic",self.semantic);self.governance.register("procedure",self.procedural)
        self.retriever=AdaptiveRetriever(self);self.consolidator=Consolidator(self)
    def refresh(self):
        ok=bool(self.core.refresh())
        for layer in (self.episodic,self.semantic,self.procedural):
            ok=bool(layer.store.refresh()) and ok
        return ok
    def recall(self,query,*,limit=12,as_of=None):return self.retriever.recall(query,limit=limit,as_of=as_of)
    def consolidate(self,**kwargs):return self.consolidator.consolidate_topics(**kwargs)
    def integrity(self):
        core_ok=self.core.refresh()
        core_view=self.core.read_view() if core_ok else {"degraded":True,"reason":"core refresh failed"}
        result={"core":"DEGRADED" if core_view.get("degraded") else "VALID"}
        reasons={"core":core_view.get("reason")}
        for name,layer in (("episodic",self.episodic),("semantic",self.semantic),("procedural",self.procedural)):
            layer.store.refresh()
            result[name]=layer.store.integrity
            reasons[name]=layer.store.integrity_reason
        result["reasons"]=reasons
        return result
