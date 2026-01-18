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

documents = "Content Security Policy"


model = LLM(
    model="Qwen/Qwen3-Embedding-0.6B", 
    max_model_len=16384,
    gpu_memory_utilization=0.85,
    enforce_eager=True 
)

sql = """
SELECT 
    parent_posts.id,
    parent_posts.title,
    COUNT(child_posts.id) AS num_answers,
    parent_posts.body AS parent_body,
    STRING_AGG(child_posts.body, '------- \n\n -------' ORDER BY child_posts.id) AS all_answers
FROM public.posts AS parent_posts
INNER JOIN public.posts AS child_posts
    ON child_posts.parentid = parent_posts.id
GROUP BY parent_posts.id, parent_posts.title, parent_posts.body
ORDER BY parent_posts.id DESC
LIMIT 50;
"""

conn = psycopg2.connect(
    host="localhost",
    database="stackoverflow",
    user="localuser",
    password="localpassword"
)
cur = conn.cursor()
cur.execute(sql)
rows = cur.fetchall()
for row in rows:
    post_id = row[0]
    title = row[1]

    num_answers = row[2]
    parent_body = row[3]
    all_answers = row[4]

    combined_text = f"Title: {title}\n\nBody: {parent_body}\n\nAnswers:\n{all_answers}"
    print(combined_text[:300])

    outputs = model.embed([combined_text])
    embedding = outputs[0].outputs.embedding
    print(f"Post ID {post_id}: Embedding shape={len(embedding)}, first 10 values={embedding[:10]}")

    insert_sql = """
    INSERT INTO search_qa (id, qa_body, embedding)
    VALUES (%s, %s, %s);
    """
    cur.execute(insert_sql, (post_id, combined_text, embedding))
    conn.commit()
cur.close()
conn.close()


del model
import torch
import gc
gc.collect()
torch.cuda.empty_cache()
print("Successfully delete the llm pipeline and free the GPU memory!")