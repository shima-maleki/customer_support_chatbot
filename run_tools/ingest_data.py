
import sys
from pathlib import Path

# Ensure the repository src/ directory is on the import path when running as a script.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from assistant.infrastructure.qdrant.service import vectorstore
from assistant.domain.document import read_all_json_files, create_documents_from_knowledge_base
from assistant.config import settings

vector_store = vectorstore()

if __name__ == "__main__":
    file_path = settings.KNOWLEDGE_DATASET_PATH
    knowledge_base = read_all_json_files(file_path)
    documents = create_documents_from_knowledge_base(knowledge_base)
    
    # Add documents
    vector_store.add_documents(documents)
