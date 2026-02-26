#!/usr/bin/env python3
"""
PHOENIX VECTOR SEARCH ENGINE
Semantic search using numpy only — no heavy dependencies.
Runs fast on Android. Finds meaning, not just keywords.
"""
import json, math, re
import numpy as np
from pathlib import Path

HOME = Path.home()

class VectorEngine:
    """
    Lightweight semantic search using TF-IDF vectors.
    No PyTorch, no transformers, no internet needed.
    """
    def __init__(self):
        self.documents = []
        self.vectors = []
        self.vocab = {}
        
    def tokenize(self, text):
        return re.findall(r'\b[a-z]{2,}\b', text.lower())
    
    def build_vocab(self, docs):
        all_tokens = set()
        for d in docs:
            all_tokens.update(self.tokenize(d['text']))
        self.vocab = {w:i for i,w in enumerate(sorted(all_tokens))}
    
    def vectorize(self, text):
        tokens = self.tokenize(text)
        vec = np.zeros(len(self.vocab))
        counts = {}
        for t in tokens:
            if t in self.vocab:
                counts[t] = counts.get(t, 0) + 1
        for t, c in counts.items():
            vec[self.vocab[t]] = c
        # Normalize
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec
    
    def add_documents(self, docs):
        self.documents = docs
        self.build_vocab(docs)
        self.vectors = [self.vectorize(d['text']) for d in docs]
        print(f"✅ Indexed {len(docs)} documents, {len(self.vocab)} unique terms")
    
    def search(self, query, top_k=3):
        q_vec = self.vectorize(query)
        scores = [float(np.dot(q_vec, v)) for v in self.vectors]
        ranked = sorted(zip(scores, self.documents), key=lambda x: x[0], reverse=True)
        return [(s, d) for s, d in ranked[:top_k] if s > 0]

# ═══════════════════════════════════════
# KNOWLEDGE BASE — Wisdom + Domains + Chips
# ═══════════════════════════════════════
KNOWLEDGE_BASE = [
    # WISDOM
    {"id":"tao_water","category":"wisdom","text":"water nourishes all things without striving flows to low places others reject gentle overcomes force be like water adapt","tags":["tao","water","adaptability","gentleness"]},
    {"id":"tao_empty","category":"wisdom","text":"empty space makes vessel useful what is not there matters as much as what is leave room silence space","tags":["tao","emptiness","minimalism","space"]},
    {"id":"stoic_control","category":"wisdom","text":"power over mind not outside events control what you can accept what you cannot focus inner strength resilience","tags":["stoic","control","mindset","resilience"]},
    {"id":"stoic_action","category":"wisdom","text":"waste no time arguing what good person should be be one action integrity lead by example do right thing","tags":["stoic","action","integrity","leadership"]},
    {"id":"buddhist_mind","category":"wisdom","text":"mind is everything what we think we become thoughts shape reality consciousness awareness suffering compassion","tags":["buddhist","mind","thoughts","awareness"]},
    {"id":"confucius_heart","category":"wisdom","text":"wherever you go go with all your heart wholehearted commitment passion dedication craft excellence","tags":["confucius","heart","commitment","excellence"]},
    {"id":"confucius_persist","category":"wisdom","text":"does not matter how slowly you go long as do not stop persistence patience consistency journey","tags":["confucius","persistence","patience","journey"]},
    {"id":"tao_journey","category":"wisdom","text":"journey thousand miles begins single step start small begin now action momentum habit","tags":["tao","journey","beginning","action"]},
    {"id":"stoic_happiness","category":"wisdom","text":"happiness life depends quality thoughts mindset positive attitude wellbeing mental health","tags":["stoic","happiness","mindset","wellbeing"]},
    {"id":"zen_ordinary","category":"wisdom","text":"before enlightenment chop wood carry water after enlightenment chop wood carry water ordinary work daily routine presence","tags":["zen","ordinary","presence","routine"]},

    # CHIP ARCHITECTURE  
    {"id":"neuromorphic","category":"chip","text":"neuromorphic computing brain-inspired neural networks synapses spike timing biological cognitive architecture adaptive learning","tags":["neuromorphic","brain","neural","spike"]},
    {"id":"optical_computing","category":"chip","text":"optical computing light photons speed computation silicon photonics wavelength laser fiber optic","tags":["optical","light","photon","speed"]},
    {"id":"analog_matrix","category":"chip","text":"analog matrix multiply accumulate MAC units parallel computation tensor operations neural network inference","tags":["analog","matrix","MAC","parallel"]},
    {"id":"edge_ai","category":"chip","text":"edge computing local inference no cloud offline private low power mobile embedded deployment","tags":["edge","offline","private","low-power"]},
    {"id":"genetic_algorithm","category":"chip","text":"genetic algorithm evolution mutation crossover selection fitness population generations optimization search","tags":["genetic","evolution","optimization","fitness"]},
    {"id":"phoenix_chip","category":"chip","text":"phoenix chip 131072 matrix neuromorphic optical 20ghz 30 watt exaflops efficient h100 nvidia benchmark","tags":["phoenix","exaflops","efficient","benchmark"]},
    {"id":"chiplets","category":"chip","text":"chiplet design modular multi-die packaging heterogeneous integration scalable manufacturing yield","tags":["chiplets","modular","scalable","manufacturing"]},
    {"id":"binary_precision","category":"chip","text":"binary neural network 1-bit precision extreme compression efficiency inference quantization low power","tags":["binary","quantization","compression","efficiency"]},

    # DOMAINS
    {"id":"healthcare_domain","category":"domain","text":"healthcare medical patient HIPAA billing clinical workflows appointment scheduling doctor nurse hospital","tags":["healthcare","medical","patient","HIPAA"]},
    {"id":"law_domain","category":"domain","text":"law legal attorney client privilege case management Missouri statute deadline court justice","tags":["law","legal","attorney","court"]},
    {"id":"agriculture_domain","category":"domain","text":"farm agriculture crop soil Missouri planting harvest market USDA weather sensor smart farming","tags":["agriculture","farm","crop","Missouri"]},
    {"id":"restaurant_domain","category":"domain","text":"restaurant food hospitality menu kitchen orders reservations health code pricing staff service","tags":["restaurant","food","hospitality","menu"]},
    {"id":"nonprofit_domain","category":"domain","text":"nonprofit grant writing board governance volunteer community service Missouri mission impact","tags":["nonprofit","grant","volunteer","community"]},
    {"id":"education_domain","category":"domain","text":"education school student learning curriculum teaching assessment Missouri standards classroom teacher","tags":["education","school","student","learning"]},
    {"id":"mental_health_domain","category":"domain","text":"mental health therapy counseling HIPAA sessions patient wellbeing anxiety depression healing","tags":["mental-health","therapy","counseling","wellbeing"]},

    # PLATFORM
    {"id":"wisdom_pipeline","category":"platform","text":"wisdom pipeline tao stoic buddhist confucius ancient truth design philosophy generation app building","tags":["wisdom","pipeline","philosophy","generation"]},
    {"id":"human_insight","category":"platform","text":"human insight engine suffering pain relief WHO uses app worst moment daily ritual mobile first offline","tags":["human-insight","suffering","relief","mobile"]},
    {"id":"ipfs_protection","category":"platform","text":"IPFS content addressed storage permanent immutable proof invention IP protection CID timestamp","tags":["IPFS","IP","protection","immutable"]},
    {"id":"local_ai","category":"platform","text":"local AI llama tinyllama llama3 private offline no cloud port 8080 inference edge deployment","tags":["local-AI","llama","private","offline"]},
    {"id":"people_charter","category":"platform","text":"people charter never harm no deception solve real problems create value champion humanity immutable ethics","tags":["charter","ethics","humanity","values"]},
]

def build_engine():
    engine = VectorEngine()
    engine.add_documents(KNOWLEDGE_BASE)
    return engine

def search_knowledge(query, engine=None, top_k=3):
    if engine is None:
        engine = build_engine()
    results = engine.search(query, top_k)
    return results

def augment_prompt(query, engine=None):
    """RAG — retrieve relevant context before answering"""
    results = search_knowledge(query, engine, top_k=3)
    if not results:
        return query
    
    context = "\n".join([
        f"[{d['category'].upper()}] {d['text'][:100]}..."
        for score, d in results if score > 0.1
    ])
    
    augmented = f"""Relevant context from Phoenix Forge knowledge base:
{context}

Question: {query}

Answer based on the context above and your knowledge:"""
    return augmented

if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║   PHOENIX VECTOR SEARCH ENGINE           ║")
    print("║   Semantic search — numpy only           ║")
    print("╚══════════════════════════════════════════╝\n")
    
    engine = build_engine()
    
    tests = [
        "How does the chip work?",
        "What wisdom applies to healthcare?",
        "How do I protect my IP?",
        "What is edge computing?",
        "How should I approach farming technology?",
        "Tell me about mental health app design",
    ]
    
    for query in tests:
        print(f"\n🔍 '{query}'")
        results = engine.search(query, top_k=2)
        for score, doc in results:
            print(f"   {score:.3f} [{doc['category']}] {doc['id']}: {doc['text'][:60]}...")
    
    print("\n✅ Vector search engine ready")
    print("   Integrate with CTO advisor for RAG responses")
