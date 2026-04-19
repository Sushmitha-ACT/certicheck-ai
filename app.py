"""
CertiCheck AI Microservice
Flask-based certificate authenticity analyzer
Uses EasyOCR + rule-based + Claude AI detection
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import anthropic
from utils.ocr_extractor import extract_text
from utils.pattern_detector import detect_patterns
from utils.image_analyzer import analyze_image_quality

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def rule_based_analysis(text: str, file_path: str) -> dict:
    """Fast rule-based pre-screening before AI analysis."""
    issues = []
    
    patterns = detect_patterns(text)
    
    FAKE_INSTITUTIONS = [
        'global university', 'world university', 'international institute of excellence',
        'universal college', 'online degree university', 'diploma mill'
    ]
    text_lower = text.lower()
    for fake in FAKE_INSTITUTIONS:
        if fake in text_lower:
            issues.append({'issue': 'Suspicious institution name', 'detail': f'Institution name matches known diploma mill patterns: "{fake}"', 'severity': 'high'})
    
    if patterns.get('has_pixel_artifacts'):
        issues.append({'issue': 'Image tampering detected', 'detail': 'Pixel artifacts suggest text was digitally edited onto the document.', 'severity': 'high'})
    
    if patterns.get('font_inconsistency'):
        issues.append({'issue': 'Font inconsistency', 'detail': 'Multiple unrelated font families detected, suggesting content was pasted from different sources.', 'severity': 'medium'})
    
    img_quality = analyze_image_quality(file_path)
    if img_quality.get('seal_resolution_low'):
        issues.append({'issue': 'Low-resolution seal', 'detail': 'Official seal appears low-resolution compared to document background, suggesting it was copied from another source.', 'severity': 'high'})
    
    if not patterns.get('has_signature'):
        issues.append({'issue': 'Missing signature', 'detail': 'No authorized signatory signature detected in expected document areas.', 'severity': 'medium'})
    
    if patterns.get('future_date') or patterns.get('impossible_date'):
        issues.append({'issue': 'Invalid date detected', 'detail': 'Certificate date is either in the future or predates the institution\'s founding.', 'severity': 'high'})
    
    return {'rule_issues': issues, 'extracted_text': text}


def ai_analysis(file_path: str, rule_result: dict, mime_type: str) -> dict:
    """Deep AI analysis using Claude."""
    
    system_prompt = """You are a forensic document expert specializing in certificate authentication. 
    Analyze the provided certificate and return ONLY valid JSON:
    {
      "status": "REAL"|"FAKE"|"SUSPICIOUS",
      "confidence": <50-98>,
      "reasons": [{"issue": "string", "detail": "string", "severity": "high"|"medium"|"low"}],
      "institution": "string",
      "riskLevel": "Low"|"Medium"|"High"|"Critical",
      "report": "2-3 paragraph forensic analysis"
    }"""
    
    content = []
    
    # Include image if available
    if mime_type.startswith('image/') and os.path.exists(file_path):
        import base64
        with open(file_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode()
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": mime_type, "data": img_data}
        })
    
    pre_analysis = ""
    if rule_result['rule_issues']:
        issues_text = "\n".join([f"- {i['issue']}: {i['detail']}" for i in rule_result['rule_issues']])
        pre_analysis = f"\n\nPre-screening found these issues:\n{issues_text}"
    
    content.append({
        "type": "text",
        "text": f"Analyze this certificate for authenticity.{pre_analysis}\n\nExtracted text:\n{rule_result['extracted_text'][:2000]}"
    })
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": content}]
    )
    
    return json.loads(response.content[0].text.strip())


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'CertiCheck AI'})


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400
    
    # Save temporarily
    file_path = os.path.join(UPLOAD_FOLDER, f"temp_{file.filename}")
    file.save(file_path)
    mime_type = file.content_type or 'image/jpeg'
    
    try:
        # Step 1: OCR text extraction
        extracted_text = extract_text(file_path)
        
        # Step 2: Rule-based pre-screening
        rule_result = rule_based_analysis(extracted_text, file_path)
        
        # Step 3: AI deep analysis
        result = ai_analysis(file_path, rule_result, mime_type)
        
        # Merge rule-based issues with AI findings
        all_reasons = result.get('reasons', []) + rule_result['rule_issues']
        seen = set()
        unique_reasons = []
        for r in all_reasons:
            key = r['issue'].lower()
            if key not in seen:
                seen.add(key)
                unique_reasons.append(r)
        
        result['reasons'] = unique_reasons[:8]  # Cap at 8 findings
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
