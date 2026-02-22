import re
from typing import List

def clean_numeric_value(value_str: str) -> float:
    """
    Cleans strings like '$1,200.50M' into float 1200.50.
    """
    if not value_str or value_str.lower() in ["n/a", "none", "-"]:
        return 0.0
    
    # Remove currency symbols and commas [cite: 24]
    clean_str = re.sub(r'[^\d.]', '', value_str)
    try:
        return float(clean_str)
    except ValueError:
        return 0.0

def standardize_label(label: str) -> str:
    """
    Maps various document terms to a standard schema[cite: 20].
    """
    mapping = {
        "operating costs": "Operating Expenses",
        "cost of sales": "Cost of Goods Sold",
        "total turnover": "Total Revenue",
        "net profit": "Net Income"
    }
    return mapping.get(label.lower().strip(), label)

def detect_year(text: str) -> List[str]:
    """
    Extracts potential years (2020-2029) from headers[cite: 25].
    """
    return re.findall(r'202[0-9]', text)