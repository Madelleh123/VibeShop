
from fastapi import FastAPI, UploadFile
from .search_logic import search_products

app = FastAPI()

@app.get("/")
def root():
    return {"message": "VibeShop Assistant Running"}


@app.post("/webhook")
async def whatsapp_webhook(file: UploadFile):

    # Step 1: Read image bytes from upload
    image_bytes = await file.read()

    if not image_bytes:
        return {"message": "No image file received."}

    # Step 2: Search database using image similarity
    # For this demo, we are hardcoding store_id=1 as per CTO guidance.
    store_id_for_demo = 1
    results, top_distance = search_products(image_bytes, store_id_for_demo)

    # Step 3: Formulate response based on search quality
    message = "Here are the best visual matches we found for you:"
    
    # We define "close" as a cosine distance < 0.4 (a tighter threshold for visual search).
    # This threshold is a starting point and can be tuned.
    if top_distance == -1 or top_distance > 0.4:
        message = "We couldn’t find an exact visual match, but here are some similar items."

    return {
        "message": message,
        "matches": results
    }