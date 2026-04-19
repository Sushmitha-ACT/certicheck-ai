"""OCR text extraction module."""

def extract_text(file_path: str) -> str:
    """Extract text from image or PDF using EasyOCR."""
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(file_path, detail=0)
        return ' '.join(results)
    except ImportError:
        pass
    
    # Fallback: pytesseract
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)
    except Exception:
        pass
    
    # PDF fallback
    if file_path.endswith('.pdf'):
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                return ' '.join(page.extract_text() or '' for page in pdf.pages)
        except Exception:
            pass
    
    return ""
