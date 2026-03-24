
import psycopg2
import os
import sys
import time
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector

# Add project root to path to allow importing from `api`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.embedding_logic import get_embedding
from api.image_embedding_logic import get_image_embedding

load_dotenv()

print("Connecting to the database...")
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
print("Database connection successful.")

# Register the vector type adapter
register_vector(conn)

cur = conn.cursor()

# Clear existing data
print("Clearing existing data...")
cur.execute("TRUNCATE TABLE products, stores RESTART IDENTITY")
print("Existing data cleared.")

stores = [
("Owino Denim House","owino", "+256772123456", "Owino Market, Kampala"),
("Vintage Kampala Styles","owino", "+256752987654", "Owino Market, Kampala"),
("StreetWear Owino","owino", "+256782555777", "Owino Market, Kampala")
]

print("Seeding stores...")
for s in stores:
    cur.execute("INSERT INTO stores(name,market,phone_number,location) VALUES(%s,%s,%s,%s)",s)
print("Stores seeded successfully.")

# Note: The image_url is now a local file path for seeding
products = [
(1,"Blue Denim Jacket","blue denim jacket",45000, "blue_denim_jacket.jpg"),
(1,"Black Denim Jacket","black street denim jacket",48000, "black_denim_jacket.jpg"),
(2,"Brown Leather Jacket","brown vintage leather jacket",65000, "brown_leather_jacket.jpg"),
(2,"Retro Windbreaker","colorful retro windbreaker",40000, "retro_windbreaker.jpg"),
(3,"Black Street Hoodie","urban black hoodie",35000, "black_hoodie.jpg"),
(3,"Cargo Pants","street cargo pants",38000, "cargo_pants.jpg")
]

print("Seeding products and generating embeddings...")
# Get the absolute path to the demo_images directory
demo_images_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'demo_images'))

for p in products:
    name = p[1]
    description = p[2]
    image_filename = p[4]
    image_path = os.path.join(demo_images_path, image_filename)

    print(f"Processing: {name}")

    # 1. Generate text embedding (as before)
    print(f"  Generating text embedding for: {name}")
    text_embedding = get_embedding(description)
    time.sleep(0.5) # Rate limit

    # 2. Generate image embedding
    print(f"  Generating image embedding for: {image_filename}")
    image_embedding = None
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            image_embedding = get_image_embedding(image_bytes)
            time.sleep(0.5) # Rate limit
    except FileNotFoundError:
        print(f"  ERROR: Image file not found at {image_path}")

    # 3. Insert into database
    if text_embedding and image_embedding:
        cur.execute(
            "INSERT INTO products(store_id,name,description,price,image_url,embedding,image_embedding) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (p[0], p[1], p[2], p[3], image_filename, text_embedding, image_embedding)
        )
        print(f"  Successfully inserted '{name}' with both embeddings.")
    else:
        print(f"  Skipping '{name}' due to missing embedding.")

conn.commit()
print("All products seeded and embeddings generated.")

cur.close()
conn.close()
print("Database connection closed.")

print("Demo data inserted")