import os
import io
from glob import glob
from typing import List
from openai import OpenAI
from tqdm.auto import tqdm

from config import DATA_DIR, FOLDER_ID, API_KEY, BASE_URL
from util import get_tokenizer

client = OpenAI(base_url=BASE_URL, api_key=API_KEY, project=FOLDER_ID)

def create_vector_store(name: str = "rag_store"):
    stores = client.vector_stores.list()
    for store in stores.data:
        if store.name == name:
            client.vector_stores.delete(store.id)
    return client.vector_stores.create(name=name)

def upload_text_files(vector_store_id: str):
    text_files = (
        glob(os.path.join(DATA_DIR, "wines.txt", "*.txt")) +
        glob(os.path.join(DATA_DIR, "regions.txt", "*.txt"))
    )
    if not text_files:
        return

    uploaded_files = []
    for f_path in tqdm(text_files, desc="Uploading text files"):
        with open(f_path, 'rb') as f:
            file_obj = client.files.create(file=f, purpose='assistants')
            uploaded_files.append(file_obj)

    for file_obj in tqdm(uploaded_files, desc="Indexing files"):
        try:
            client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_obj.id,
                chunking_strategy={
                    "type": "static",
                    "static": {"max_chunk_size_tokens": 1000, "chunk_overlap_tokens": 100}
                }
            )
        except Exception as e:
            msg = str(e).lower()
            if "already indexed" not in msg and "being indexed" not in msg:
                raise

def upload_food_wine_table(vector_store_id: str, chunk_size_tokens: int = 600):
    table_path = os.path.join(DATA_DIR, "food_wine_table.md")
    if not os.path.exists(table_path):
        return

    with open(table_path, encoding="utf-8") as f:
        lines = f.readlines()

    header = lines[:2]
    body = lines[2:]
    tokenizer = get_tokenizer("gpt-4")
    approx_chars_per_token = 4.5
    chunk_size_chars = int(chunk_size_tokens * approx_chars_per_token)

    current = header.copy()
    for line in tqdm(body, desc="Chunking food-wine table"):
        current.append(line)
        if len("".join(current)) > chunk_size_chars:
            _upload_chunk(vector_store_id, "".join(current))
            current = header.copy()

    if len(current) > len(header):
        _upload_chunk(vector_store_id, "".join(current))

def _upload_chunk(vector_store_id: str, text: str):
    f_obj = client.files.create(
        file=("table_chunk.txt", io.BytesIO(text.encode("utf-8")), "text/markdown"),
        purpose="assistants"
    )
    try:
        client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=f_obj.id,
            chunking_strategy={
                "type": "static",
                "static": {"max_chunk_size_tokens": 1000, "chunk_overlap_tokens": 100}
            }
        )
    except Exception as e:
        msg = str(e).lower()
        if "already indexed" not in msg and "being indexed" not in msg:
            raise