import os
from dotenv import load_dotenv
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
load_dotenv()

# Set Tesseract Path
pytesseract.pytesseract.tesseract_cmd =os.getenv('TESSERACT_PATH')


def extract_text(file,input_path, lang='eng'):
    
    if input_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        image = Image.open(file)
        text = pytesseract.image_to_string(image, lang=lang)
    elif input_path.lower().endswith('.pdf'):
        pdf_bytes = file.read()
        images = convert_from_bytes(pdf_bytes, dpi=300, poppler_path=os.getenv('POPPLER_PATH'))
        pdf_text = []
        for page_num, image in enumerate(images, start=1):
            page_text = pytesseract.image_to_string(image, lang=lang)
            pdf_text.append(f"Page {page_num}:\n{page_text}")
        text = "\n".join(pdf_text)
    else:
        raise ValueError("Unsupported file format. Use an image (png, jpg, etc.) or a PDF.")

    return text

