
Download the stackoverflow data dump from [user settings](https://stackoverflow.com/users/preferences/). 

Unzip the import to a folder. 

Bring up the postgres container

```bash
docker compose up -d pgstackoverflow
``` 

Run the pgimport container to import the data from the mapped folder. This could take a while. 

```bash
docker compose up sodata-pgimport
```

Use some of the scripts in [scripts.sql](scripts.sql) to explore the data. 

Run the `CREATE TABLE` script to create an empty table for vector embeddings.

Run the [generate_embeddings.py](generate_embeddings.py) script to populate the embeddings table. This makes use of the Qwen/Qwen3-Embedding-0.6B model and vllm to generate embeddings for just a small sample of question and answer pairs from the dataset. 

```bash
uv run generate_embeddings.py
```

