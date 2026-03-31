import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# --- Lazy Vertex AI Initialization ---
# Defer import until needed to avoid heavy dependency chain at module load
_embedding_model = None
_initialized = False

def _init_embedding_model():
    """Lazy initialization of Vertex AI embedding model."""
    global _embedding_model, _initialized
    
    if _initialized:
        return _embedding_model
    
    _initialized = True
    
    try:
        from google.cloud import aiplatform

        project_id = os.getenv("GOOGLE_PROJECT_ID")
        location = os.getenv("GOOGLE_REGION", "us-central1")

        aiplatform.init(project=project_id, location=location)

        # TextEmbeddingModel may not be typed in all client versions, use getattr to avoid Pylance warnings.
        TextEmbeddingModel = getattr(aiplatform, "TextEmbeddingModel", None)
        if not TextEmbeddingModel:
            raise RuntimeError("TextEmbeddingModel is not available in this google.cloud.aiplatform version")

        _embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
        print("✅ Successfully initialized Vertex AI embedding model.")
        return _embedding_model

    except Exception as e:
        print(f"⚠️ Error initializing Vertex AI: {e}")
        print("   Please ensure you are authenticated and your GOOGLE_PROJECT_ID is set.")
        _embedding_model = None
        return None

# --- Embedding Functions ---
def get_embedding(text: str) -> list[float] | None:
    """
    Generates a normalized embedding for a given text using Vertex AI.
    """
    embedding_model = _init_embedding_model()
    
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
