import fitz  # PyMuPDF
import json
import os

PDF_FILE = "Encyclopedia_of_Mythical_Creatures.pdf"
OUTPUT_FILE = "creatures.json"
IMAGE_DIR = "images"

os.makedirs(IMAGE_DIR, exist_ok=True)

doc = fitz.open(PDF_FILE)
creatures = []

for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text("text").strip()

    if len(text) < 100:
        continue

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    name = lines[0] if lines else "Unknown"
    origin = lines[1] if len(lines) > 1 else ""
    subtitle = lines[2] if len(lines) > 2 else ""

    image_path = None

    images = page.get_images(full=True)
    if images:
        xref = images[0][0]
        pix = fitz.Pixmap(doc, xref)

        if pix.alpha:
            pix = fitz.Pixmap(fitz.csRGB, pix)

        filename = f"{name.replace(' ', '_').lower()}.png"
        image_path = os.path.join(IMAGE_DIR, filename)

        pix.save(image_path)

    creatures.append({
        "name": name,
        "origin": origin,
        "subtitle": subtitle,
        "story": text,
        "image": image_path,
        "page": page_num + 1
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(creatures, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(creatures)} creatures.")
