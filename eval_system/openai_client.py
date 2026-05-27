import yaml
from openai import OpenAI
from pathlib import Path


def get_client() -> OpenAI:
    return OpenAI()


def load_assistant(assistant_key) -> dict:
    assistant_path = Path(f"..//assistants//{assistant_key}.yaml") 
    if not assistant_path.exists():
        return {}
  
    with open(assistant_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
    

def save_assistant(assistant_key: str, assistant_info: dict ) -> None:
    assistant_path = Path(f"..//assistants//{assistant_key}.yaml") 
    with open(assistant_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(assistant_info, f, sort_keys=False)


def generate_response(
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature=0,
    vector_store_id: str | None = None,
) -> str:
    
    client = get_client()

    tools = None

    if vector_store_id:
        tools = [
            {
                "type": "file_search",
                "vector_store_ids": [vector_store_id]
            }
        ]

    response = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_prompt,
        tools=tools,
        temperature=temperature
    )

    return response.output_text
