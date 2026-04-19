"""Image quality and forensic analysis utilities."""

def analyze_image_quality(file_path: str) -> dict:
    """Analyze image quality metrics for forgery detection."""
    results = {}
    
    try:
        from PIL import Image, ImageStat
        import os
        
        if not file_path.endswith('.pdf'):
            img = Image.open(file_path)
            width, height = img.size
            
            results['resolution'] = f"{width}x{height}"
            results['is_low_res'] = width < 800 or height < 600
            
            # Check for suspicious uniform regions (copy-paste artifacts)
            if img.mode in ('RGB', 'RGBA'):
                stat = ImageStat.Stat(img)
                results['mean_brightness'] = sum(stat.mean) / len(stat.mean)
                results['stddev'] = sum(stat.stddev) / len(stat.stddev)
                # Very low std deviation in a region = likely pasted content
                results['seal_resolution_low'] = results['stddev'] < 15
            else:
                results['seal_resolution_low'] = False
            
            results['file_size_kb'] = os.path.getsize(file_path) / 1024
            results['suspiciously_small'] = results['file_size_kb'] < 50
        else:
            results['seal_resolution_low'] = False
            results['is_low_res'] = False
    except Exception as e:
        results['error'] = str(e)
        results['seal_resolution_low'] = False
        results['is_low_res'] = False
    
    return results
