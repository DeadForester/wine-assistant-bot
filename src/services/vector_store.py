import os
import io
import json
from glob import glob
import pandas as pd
from tqdm.auto import tqdm
from src.config import DATA_DIR
from src.services.openai_client import client
from src.services.tokenizer import get_tokenizer
from tqdm.auto import tqdm

tqdm.pandas()


def setup_vector_store():
    try:
        stores = client.vector_stores.list()
        for store in stores:
            print(f"Удаляем файл: {store.id} ({store.name})")
            if store.name == "rag_store":
                client.vector_stores.delete(store.id)
    except Exception as e:
        print("Не удалось очистить хранилища:", e)

    vector_store = client.vector_stores.create(name='rag_store')

    text_files = (
            glob(os.path.join(DATA_DIR, "wines.txt", "*.txt")) +
            glob(os.path.join(DATA_DIR, "regions.txt", "*.txt"))
    )

    if not text_files:
        print("⚠️ Текстовые файлы не найдены")

    df_files = pd.DataFrame({"File": text_files})
    df_files["Uploaded"] = df_files["File"].progress_apply(
        lambda f: client.files.create(file=open(f, 'rb'), purpose='assistants')
    )

    def add_to_store(file_obj):
        try:
            client.vector_stores.files.create(
                vector_store_id=vector_store.id,
                file_id=file_obj.id,
                chunking_strategy={"type": "static",
                                   "static": {"max_chunk_size_tokens": 1000, "chunk_overlap_tokens": 100}}
            )
        except Exception as e:
            if "already indexed" in str(e).lower() or "being indexed" in str(e).lower():
                print(f"Файл {file_obj.id} уже индексируется — пропускаем.")
            else:
                raise e

    _ = df_files["Uploaded"].progress_apply(add_to_store)

    table_path = os.path.join(DATA_DIR, "food_wine_table.md")
    if os.path.exists(table_path):
        with open(table_path, encoding="utf-8") as f:
            lines = f.readlines()
        header = lines[:2]
        body = lines[2:]
        tokenizer = get_tokenizer("gpt-4")  # или любой
        approx_chars_per_token = 4.5
        chunk_size_chars = int(600 * approx_chars_per_token)
        current = header.copy()
        for line in tqdm(body, desc="Чанкование таблицы"):
            current.append(line)
            if len("".join(current)) > chunk_size_chars:
                upload_chunk("".join(current))
                current = header.copy()
        if len(current) > len(header):
            upload_chunk("".join(current))

    return vector_store


def upload_chunk(chunk_text):
    f_obj = client.files.create(
        file=("table_chunk.txt", io.BytesIO(chunk_text.encode("utf-8")), "text/markdown"),
        purpose="assistants"
    )
