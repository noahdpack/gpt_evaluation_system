import time
from openai_client import get_client
from pathlib import Path
import yaml


CACHE_PATH = Path("..\\vector_store_cache.yaml")


def load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    
    with open(CACHE_PATH, "r", encoding= "utf-8") as f:
        return yaml.safe_load(f) or {}


def save_cache(cache: dict) -> None:
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(cache, f, sort_keys=False)


def upload_to_vector_store(assistant_key: str, vector_store_id: str) -> None:

    client = get_client()

    file_ids = []

    DIRECTORY = Path(f"..\\knowledge_base_files\\{assistant_key}")

    for path in DIRECTORY.rglob("*"):
        if path.is_file():
            with open(path, "rb") as f:
                uploaded_file = client.files.create(
                    file=f,
                    purpose="assistants"
            )
            
            file_ids.append(uploaded_file.id)
            print(f"Uploaded to file_ids: {path} -> {uploaded_file.id}")


    batch = client.vector_stores.file_batches.create(
        vector_store_id=vector_store_id,
        file_ids=file_ids
    )

    batch_id = batch.id
    
    while True:
        batch = client.vector_stores.file_batches.retrieve(
            vector_store_id=vector_store_id,
            batch_id=batch_id
        )

        print(f"status: {batch.status}")
        print(f"file_counts: {batch.file_counts}")

        if batch.status in ["completed", "failed", "cancelled"]:
            break

        time.sleep(5)
        
    print(f"Uploaded to vector store: {vector_store_id}") 
    print(f"File batch: {batch.id}")


def get_or_create_vector_store(assistant_key: str) -> str:

    client = get_client()

    cache = load_cache()

    if assistant_key in cache:
        vector_store_id = cache[assistant_key]["vector_store_id"]

        try:
            vector_store = client.vector_stores.retrieve(vector_store_id)

            if getattr(vector_store, "status", None) != "expired":
                print(f"Reusing vector store for {assistant_key}: {vector_store_id}")
                return vector_store_id
            
            print(f"Cache vector store expired: {vector_store_id}")

        except Exception:
            print(f"Cache vector store could not be retrieved: {vector_store_id}")


    vector_store = client.vector_stores.create(
        name=f"{assistant_key}_vector_store"
    )

    upload_to_vector_store(assistant_key=assistant_key, vector_store_id=vector_store.id)

    cache[assistant_key] = {
        "vector_store_id": f"{vector_store.id}",
        "name": f"{vector_store.name}"
    }

    save_cache(cache)

    print(f"Created new vector store for {assistant_key}: {vector_store.id}")
    return vector_store.id
