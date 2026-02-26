#!/usr/bin/env python3
"""
RAG ADVISOR — Retrieval Augmented Generation
Vector search finds relevant context → Llama3.2 answers with real knowledge
"""
import sys, json, requests
sys.path.insert(0, '/data/data/com.termux/files/home/swarm-platform')
from vector_search import build_engine, augment_prompt

AI_URL = "http://localhost:8080/v1/chat/completions"
SYSTEM = "You are the CTO advisor for Phoenix Forge built by Jason Tackett on a $60 Android. Answer based on the context provided. Be direct and concise."

engine = build_engine()
print("╔══════════════════════════════════════════╗")
print("║   PHOENIX RAG ADVISOR                    ║")
print("║   Vector Search + Llama3.2               ║")
print("╚══════════════════════════════════════════╝")
print("Type your question. Ctrl+C to exit.\n")

history = []
while True:
    try:
        query = input("You: ").strip()
        if not query: continue

        # RAG — augment with relevant context
        augmented = augment_prompt(query, engine)
        history.append({"role":"user","content":augmented})

        r = requests.post(AI_URL, json={
            "messages":[{"role":"system","content":SYSTEM}]+history,
            "max_tokens":250,
            "temperature":0.7
        }, timeout=60)

        reply = r.json()["choices"][0]["message"]["content"]
        history.append({"role":"assistant","content":reply})
        print(f"\nAdvisor: {reply}\n")

    except KeyboardInterrupt:
        print("\n✅ RAG Advisor closed")
        break
    except Exception as e:
        print(f"Error: {e}\n")
