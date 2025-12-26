import os
from typing import List, Dict, Any
import json
from pathlib import Path
from pydantic import BaseModel, Field

from assistant import utils
from langchain_core.documents import Document

def read_all_json_files(folder_path: str) -> List[Dict[str, Any]]:
    """
    Reads all JSON files in the specified folder and returns a list of dictionaries
    containing the filename and its parsed JSON content.

    Parameters:
        folder_path (str): Path to the folder containing JSON files.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with keys 'filename' and 'data'.
    """
    result = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            full_path = os.path.join(folder_path, filename)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                result.append(data)
            except Exception as e:
                print(f"Failed to read {filename}: {e}")

    return result

def create_documents_from_knowledge_base(knowledge_base):
    """
    Converts a list of JSON-like knowledge base entries into LangChain Document objects.
    
    Each document will have:
    - `page_content`: from the 'doc' field
    - `metadata`: 'source' field derived from the 'category' field (spaces -> underscores, '&' -> 'and')

    Args:
        knowledge_base (list): A list of lists, where each inner list contains dictionaries with
                               'doc' and 'category' keys.

    Returns:
        List[Document]: A list of LangChain Document objects with properly formatted metadata.
    """
    processed_docs = []

    for data_collection in knowledge_base:
        for doc in data_collection:
            if 'doc' in doc and 'category' in doc:
                raw_metadata = doc['category']
                cleaned_metadata = raw_metadata.replace(" ", "_").replace("&", "and")
                content = doc['doc']
                
                processed_docs.append(
                    Document(
                        page_content=content,
                        metadata={"source": cleaned_metadata}
                    )
                )
            else:
                print(f"Skipped entry due to missing keys: {doc}")
    
    return processed_docs
