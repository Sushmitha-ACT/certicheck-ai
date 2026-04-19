"""Rule-based pattern detection for certificate analysis."""
import re
from datetime import datetime

VALID_DEGREES = [
    'bachelor', 'master', 'doctor', 'phd', 'mba', 'associate',
    'diploma', 'certificate', 'b.sc', 'm.sc', 'b.a', 'm.a', 'b.tech', 'm.tech'
]

SIGNATURE_KEYWORDS = ['registrar', 'dean', 'director', 'president', 'chancellor', 'provost', 'signed']

COMMON_FONTS_MISMATCH = ['arial', 'times new roman', 'comic sans', 'papyrus']

def detect_patterns(text: str) -> dict:
    """Detect suspicious patterns in extracted certificate text."""
    text_lower = text.lower()
    results = {}
    
    # Check for signature keywords
    results['has_signature'] = any(kw in text_lower for kw in SIGNATURE_KEYWORDS)
    
    # Check for valid degree terms
    results['has_valid_degree'] = any(deg in text_lower for deg in VALID_DEGREES)
    
    # Check for dates
    date_pattern = r'\b(19|20)\d{2}\b'
    dates = re.findall(date_pattern, text)
    current_year = datetime.now().year
    results['future_date'] = any(int(d) > current_year for d in dates)
    results['impossible_date'] = any(int(d) < 1800 for d in dates)
    
    # Check for grammar errors (basic)
    common_errors = ['recieved', 'acheivement', 'succesfully', 'certifacate', 'aword', 'completeion']
    results['has_grammar_errors'] = any(err in text_lower for err in common_errors)
    
    # Pixel artifact heuristic (text-based proxy)
    results['has_pixel_artifacts'] = len(re.findall(r'[^\x00-\x7F]', text)) > 20
    
    # Font inconsistency (heuristic via character mixing)
    results['font_inconsistency'] = bool(re.search(r'[A-Z]{3,}.*[a-z]{10,}.*[A-Z]{3,}', text))
    
    # Check word count (very short = suspicious)
    results['word_count'] = len(text.split())
    results['too_short'] = results['word_count'] < 20
    
    return results
