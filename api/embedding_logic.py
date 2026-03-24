import os
import numpy as np
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()

# --- Vertex AI Initialization ---
try:
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    location = os.getenv("GOOGLE_REGION", "us-central1")

    aiplatform.init(project=project_id, location=location)

    # Load the text embedding model
    embedding_model = aiplatform.TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
    print("Successfully initialized Vertex AI and loaded embedding model.")

except Exception as e:
    print(f"Error initializing Vertex AI: {e}")
    print("Please ensure you are authenticated and your GOOGLE_PROJECT_ID is set.")
    embedding_model = None

# --- Embedding Functions ---
def get_embedding(text: str) -> list[float] | None:
    """
    Generates a normalized embedding for a given text using Vertex AI.
    """
    if not embedding_model or not text:
        return None
    try:
        embeddings = embedding_model.get_embeddings([text])
        values = embeddings[0].values
        norm = np.linalg.norm(values)
        if norm == 0:
            return values
        return (values / norm).tolist()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None