import os
import numpy as np
from typing import TYPE_CHECKING, Optional
from dotenv import load_dotenv

if TYPE_CHECKING:
    # Only for type checking; prevents runtime import errors and Pylance missing-import issues.
    from google.cloud.aiplatform.vision.models import Image as VertexImage  # type: ignore[import]
    from google.cloud.aiplatform.vision.models import MultiModalEmbeddingModel as VertexMultiModalEmbeddingModel  # type: ignore[import]
    Image = VertexImage
    MultiModalEmbeddingModel = VertexMultiModalEmbeddingModel
else:
    Image = None
    MultiModalEmbeddingModel = None

load_dotenv()

# --- Lazy Vertex AI Initialization (Image Embedding - Optional) ---
_embedding_model = None
_initialized = False

def _init_image_embedding_model():
    """Lazy initialization of Vertex AI multimodal embedding model."""
    global _embedding_model, _initialized
    
    if _initialized:
        return _embedding_model
    
    _initialized = True
    
    try:
        from google.cloud import aiplatform

        project_id = os.getenv("GOOGLE_PROJECT_ID")
        location = os.getenv("GOOGLE_REGION", "us-central1")

        if not project_id:
            print("⚠️ GOOGLE_PROJECT_ID not set; image embeddings disabled")
            return None

        aiplatform.init(project=project_id, location=location)

        # Try to import vision models; if unavailable, image embedding is disabled
        try:
            from google.cloud.aiplatform.vision.models import MultiModalEmbeddingModel, Image  # type: ignore[import]

            _embedding_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
            print("✅ Successfully initialized Vertex AI multimodal embedding model.")
            return _embedding_model

        except (ImportError, ModuleNotFoundError) as e:
            print(f"⚠️ Image embedding unavailable: vision models not found. Error: {e}")
            print("   Image search is disabled. Install google-cloud-vision if needed.")
            return None

    except Exception as e:
        print(f"⚠️ Error initializing Vertex AI: {e}")
        print("   Image embedding disabled for this session.")
        return None

# --- Image Embedding Functions ---

def get_image_embedding(image_bytes: bytes) -> list[float] | None:
    """
    Generates a normalized embedding for a given image using Vertex AI.
    """
    embedding_model = _init_image_embedding_model()
    
    if not embedding_model or not image_bytes or Image is None:
        return None
    try:
        # Load the image from bytes
        image = Image(image_bytes=image_bytes)

        # Get the embeddings
        embeddings = embedding_model.get_embeddings(
            image=image,
            contextual_text=None, # No text context for pure image similarity
            dimension=1408
        )
        
        # Normalize the image embedding
        image_embedding = embeddings.image_embedding
        norm = np.linalg.norm(image_embedding)
        if norm == 0:
            return image_embedding
        return (image_embedding / norm).tolist()
     
    except Exception as e:
        print(f"Error generating image embedding: {e}")
        return None
