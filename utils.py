import re
from datetime import datetime

def clean_text(text):
    """Clean text by removing extra whitespace and special characters"""
    if not text:
        return ""
    
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s.,$%\-/]', '', text)
    
    return text

def is_numeric(text):
    """Check if text represents a numeric value"""
    try:
        float(text.replace('$', '').replace('%', '').replace(',', ''))
        return True
    except ValueError:
        return False

def parse_date(date_str):
    """Attempt to parse various date formats"""
    try:
        # Try common date formats
        for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%b %d, %Y', '%B %d, %Y', '%Y'):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try quarter format (Q1 2023)
        if date_str.startswith('Q'):
            quarter = int(date_str[1])
            year = int(date_str[3:])
            return datetime(year, (quarter-1)*3 + 1, 1)
        
        return None
    except:
        return None