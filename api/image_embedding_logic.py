import os
import numpy as np
from google.cloud import aiplatform
from google.cloud.aiplatform.vision.models import Image, MultiModalEmbeddingModel
from dotenv import load_dotenv

load_dotenv()

# --- Vertex AI Initialization ---
try:
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    location = os.getenv("GOOGLE_REGION", "us-central1")

    aiplatform.init(project=project_id, location=location)

    # Load the multimodal embedding model
    embedding_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
    print("Successfully initialized Vertex AI and loaded multimodal embedding model.")

except Exception as e:
    print(f"Error initializing Vertex AI: {e}")
    print("Please ensure you are authenticated and your GOOGLE_PROJECT_ID is set.")
    embedding_model = None

# --- Image Embedding Functions ---

def get_image_embedding(image_bytes: bytes) -> list[float] | None:
    """
    Generates a normalized embedding for a given image using Vertex AI.
    """
    if not embedding_model or not image_bytes:
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