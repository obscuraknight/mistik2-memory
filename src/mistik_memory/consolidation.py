from __future__ import annotations
from collections import Counter, defaultdict
import re
_TOKEN=re.compile(r"[a-z0-9]+")
_STOP={"the","a","an","and","or","is","are","was","were","to","of","in","on","for","with","i","user","they","it","this","that"}
def _keywords(text): return [t for t in _TOKEN.findall((text or "").lower()) if t not in _STOP and len(t)>2]
class Consolidator:
    """Evidence-preserving consolidation over inference-valid sources only."""
    def __init__(self,general_memory): self.memory=general_memory
    def consolidate_topics(self,*,min_occurrences=3,max_topics=12):
        if type(min_occurrences) is not int or min_occurrences<2: raise ValueError("min_occurrences must be >= 2")
        sources=[]
        with self.memory.governance.read_session() as snap:
            if not snap.available: return []
            view=self.memory.core.read_view()
            if view.get("degraded"): return []
            for f in view["facts"]: sources.append((f"fact:{f['fact_id']}",f["text"]))
            for e in snap.records_for("episode"):
                if self.memory.episodic._allowed(e,snapshot=snap): sources.append((f"episode:{e['id']}",e["summary"]))
            counts=Counter();refs=defaultdict(list)
            for ref,text in sources:
                for token in set(_keywords(text)): counts[token]+=1;refs[token].append(ref)
            created=[]
            for token,count in counts.most_common(max_topics*3):
                if count<min_occurrences: continue
                cid=self.memory.semantic.remember(token,f"Consolidated topic '{token}' observed across {count} governed source records.",source_ids=refs[token],confidence=min(.95,.45+.05*count),attributes={"kind":"topic_cluster","occurrences":count})
                created.append(cid)
                if len(created)>=max_topics: break
            return created
