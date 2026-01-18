#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "vllm>=0.8.5",
#   "psycopg2-binary",
#   "torch",
# ]
# ///

import vllm
from vllm import LLM
import psycopg2


model = LLM(
    model="Qwen/Qwen3-Embedding-0.6B", 
    max_model_len=16384,
    gpu_memory_utilization=0.85,
    enforce_eager=True 
)

search_phrase = "Content Security Policy"

outputs = model.embed([search_phrase])
embedding = outputs[0].outputs.embedding
print(f"Search Phrase Embedding shape={len(embedding)}, first 10 values={embedding[:10]}")


sql = """SELECT 
    id,
    qa_body,
    embedding <=> %s AS distance
FROM search_qa
ORDER BY embedding <=> %s ASC
LIMIT 5;"""


conn = psycopg2.connect(
    host="localhost",
    database="stackoverflow",
    user="localuser",
    password="localpassword"
)

cur = conn.cursor()
cur.execute(sql, (embedding, embedding))
rows = cur.fetchall()
for row in rows:
    qa_id = row[0]
    qa_body = row[1]
    distance = row[2]

    print(f"QA ID: {qa_id}, Distance: {distance}")
    print(f"QA Body (first 300 chars): {qa_body[:300]}")
    print("-----") 


del model
import torch
import gc
gc.collect()
torch.cuda.empty_cache()
print("Successfully delete the llm pipeline and free the GPU memory!")