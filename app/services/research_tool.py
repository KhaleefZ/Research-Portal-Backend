import json
import re
import logging
from typing import List, Dict, Optional
from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)
logger = logging.getLogger(__name__)

# Common financial line items and their variations
FINANCIAL_METRICS = {
    'revenue': ['revenue from operations', 'total revenue', 'revenue', 'sales', 'income from operations'],
    'gross_profit': ['gross profit', 'gross profit margin'],
    'operating_profit': ['operating profit', 'operating profit before interest', 'ebit'],
    'ebitda': ['ebitda', 'ebit + da'],
    'profit_before_tax': ['profit before tax', 'profit before tax and extraordinary items', 'pbt'],
    'profit_after_tax': ['profit after tax', 'net profit', 'net income', 'net profit after tax'],
    'total_income': ['total income', 'total revenue and income'],
    'total_expenses': ['total expenses', 'total cost of revenue'],
    'eps_basic': ['earnings per share basic', 'eps basic', 'eps - basic'],
    'eps_diluted': ['earnings per share diluted', 'eps diluted', 'eps - diluted'],
    'current_assets': ['current assets', 'total current assets'],
    'current_liabilities': ['current liabilities', 'total current liabilities'],
    'total_assets': ['total assets'],
    'total_liabilities': ['total liabilities'],
    'equity': ['total equity', 'shareholders equity', 'total shareholders funds'],
}

def run_financial_extraction(text: str) -> List[Dict]:
    """Extract financial data using hybrid approach: local parsing + Gemini fallback.
    
    1. First tries to extract tables using local regex patterns
    2. If insufficient data, uses Gemini AI for intelligent extraction
    3. Handles both digital and OCR-extracted text
    
    Args:
        text: Document text containing financial statements
        
    Returns:
        List of extracted financial records
    """
    if not text or len(text.strip()) < 100:
        logger.warning("Input text too short for extraction")
        return []
    
    # STEP 1: Try local table extraction first (fast, no API calls)
    logger.info("Step 1: Attempting local table extraction...")
    local_data = extract_tables_locally(text)
    
    if local_data and len(local_data) >= 5:
        logger.info(f"Local extraction successful: {len(local_data)} records found")
        return clean_financial_data(local_data)
    
    logger.info(f"Local extraction found {len(local_data) if local_data else 0} records. Using Gemini for comprehensive extraction...")
    
    # STEP 2: Use Gemini AI for intelligent extraction if local method insufficient
    gemini_error = None
    try:
        gemini_data = extract_with_gemini(text)
        if gemini_data:
            logger.info(f"Gemini extraction successful: {len(gemini_data)} records")
            return clean_financial_data(gemini_data)
    except Exception as e:
        gemini_error = str(e)
        logger.error(f"Gemini extraction failed: {gemini_error[:200]}")
    
    # STEP 3: If we got any data from local extraction, return it
    if local_data:
        logger.warning(f"Gemini failed, returning {len(local_data)} records from local extraction")
        return clean_financial_data(local_data)
    # If Gemini failed and no local data, propagate error info
    logger.warning("No financial data extracted from document")
    if gemini_error:
        return [{
            "Particulars": "⚠️ Gemini API Error",
            "Status": "Unable to extract financial tables due to AI service error.",
            "Details": f"Gemini error: {gemini_error[:200]}",
            "Recommendation": "Please try again later or check Gemini API status."
        }]
    return []


def extract_tables_locally(text: str) -> List[Dict]:
    """Extract financial tables using regex patterns and heuristics."""
    records = []
    clean_text = clean_ocr_text(text)
    
    # Pattern: Line item followed by spaces and number
    pattern = r'([A-Za-z\s\-/&()]+?)\s+([\d,]+(?:\.\d+)?)\s+(?:Crores|Millions|Cr|Rs)?'
    
    for match in re.finditer(pattern, clean_text):
        line_item = clean_metric_name(match.group(1).strip())
        value_str = match.group(2).replace(',', '')
        
        # Filter by quality
        if len(line_item) < 10 or len(line_item) > 70:  # Too short or too long
            continue
        
        if not is_financial_metric(line_item):
            continue
        
        try:
            value = float(value_str)
            if value > 0 and value < 10000000:  # Reasonable range
                records.append({
                    'line_item': line_item,
                    'value': value,
                    'unit': 'Crores',
                    'period': extract_period_from_text(text)
                })
        except ValueError:
            continue
    
    # IMPORTANT: Look for key financial metrics explicitly
    key_patterns = [
        (r'Revenue\s+(?:from\s+)?Operations?\s*[\:\-=]?\s*Cr\.\s*([\d,]+)', 'Revenue from Operations'),
        (r'Total\s+Income\s*[\:\-=]?\s*Cr\.\s*([\d,]+)', 'Total Income'),
        (r'Profit\s+Before\s+Tax\s*[\:\-=]?\s*Cr\.\s*([\d,]+)', 'Profit Before Tax'),
        (r'(?:Profit\s+After\s+Tax|Net\s+Profit)\s*[\:\-=]?\s*Cr\.\s*([\d,]+)', 'Net Profit'),
        (r'EBITDA\s*[\:\-=]?\s*([\d,]+)', 'EBITDA'),
    ]
    
    for pattern_str, metric_name in key_patterns:
        for match in re.finditer(pattern_str, clean_text, re.IGNORECASE):
            try:
                value = float(match.group(1).replace(',', ''))
                if value > 0 and not any(r['line_item'] == metric_name for r in records):
                    records.append({
                        'line_item': metric_name,
                        'value': value,
                        'unit': 'Crores',
                        'period': extract_period_from_text(text)
                    })
            except (ValueError, IndexError):
                continue
    
    # Deduplicate: keep highest value for each metric
    seen = {}
    for rec in records:
        key = rec['line_item'].lower()
        if key not in seen or rec['value'] > seen[key]['value']:
            seen[key] = rec
    
    return list(seen.values())


def clean_metric_name(raw: str) -> str:
    """Remove OCR crud from metric names."""
    # Remove common OCR artifacts and formatting
    text = raw.strip()
    
    # Remove leading/trailing letters that are OCR artifacts
    text = re.sub(r'^[^A-Z]*', '', text)  # Remove junk before first capital letter
    text = re.sub(r'[^a-zA-Z0-9\s\-/&()]*$', '', text)  # Remove trailing junk
    
    # Fix spacing around keywords
    text = re.sub(r'\s+', ' ', text)
    
    # Remove very short fragments
    if len(text) < 8:
        return ''
    
    return text.strip()


def clean_ocr_text(text: str) -> str:
    """Clean common OCR artifacts and formatting issues."""
    # Remove page markers
    text = re.sub(r'--- (START|END) OF PAGE \d+ .*? ---', '', text, flags=re.IGNORECASE)
    
    # Fix specific OCR confusions for Indian financial statements
    replacements = [
        (r'Seqment', 'Segment'),
        (r'segement', 'Segment'),
        (r'Thesl', 'These'),
        (r'Consoli', 'Consolidated'),
        (r'Consolliated', 'Consolidated'),
        (r'Unauditea', 'Unaudited'),
        (r'Unauditled', 'Unaudited'),
        (r'materia ', 'material '),  # Common OCR misread
        (r'\bW\s+expenses\b', 'Raw material expenses'),  # OCR artifact for common section headers
        (r'avv', 'own'),  # Common OCR artifact
        (r'aai', ''),  # OCR garbage
        (r'aaiai', ''),
        (r'\[', '('),  # Replace brackets
        (r'\]', ')'),
        (r'\|', '/'),  # Replace pipes with forward slash
        (r'aa', ''),  # Common OCR artifact
        (r'ss', 's'),  # Double s
        (r'ii', 'i'),  # Double i
    ]
    
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def is_financial_metric(line_item: str) -> bool:
    """Check if line item contains financial keywords."""
    keywords = [
        'revenue', 'income', 'profit', 'loss', 'expense', 'cost',
        'ebitda', 'ebit', 'eps', 'assets', 'liabilities', 'equity',
        'dividend', 'tax', 'interest', 'cash', 'deposit'
    ]
    
    line_lower = line_item.lower()
    return any(kw in line_lower for kw in keywords)


def standardize_metric_name(raw_name: str) -> str:
    """Convert various naming to standard format."""
    name_lower = raw_name.lower().strip()
    
    # Clean up OCR artifacts further
    name_lower = re.sub(r'[^\w\s]', '', name_lower).strip()
    
    # Direct mapping of common variations
    mappings = {
        'revenue from operations': ['revenue', 'revenue from operations', 'total revenue from operations', 'operating revenue'],
        'total income': ['total income', 'total revenue and other income'],
        'profit before tax': ['profit before tax', 'pbt', 'profit before tax and extraordinaryitems'],
        'profit after tax': ['profit after tax', 'net profit', 'net income', 'pat', 'profit after tax'],
        'operating profit': ['operating profit', 'ebit', 'operating profit'],
        'ebitda': ['ebitda', 'ebit and da'],
        'earnings per share': ['eps', 'earnings per share', 'eps basic', 'earnings per share basic'],
        'current assets': ['current assets', 'total current assets'],
        'current liabilities': ['current liabilities', 'total current liabilities'],
    }
    
    # Check for matching metric
    for standard, variations in mappings.items():
        for variation in variations:
            if variation in name_lower:
                return standard.title()
    
    # If no match, return cleaned version (title case, max 50 chars)
    return raw_name.strip()[:50].title() if raw_name.strip() else 'Unknown Metric'


def extract_period_from_text(text: str) -> str:
    """Extract financial period (quarter/year) from text."""
    # Patterns for different period formats
    patterns = [
        r'(?:Q[1-4]|Quarter\s+[1-4])\s+(?:FY|20\d{2})',  # Q1 FY2025
        r'(?:March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+20\d{2}',
        r'\d{1,2}[/-](?:Dec|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov)[/-]20\d{2}',
        r'(?:Q[1-4])\s+20\d{2}',
        r'20\d{2}(?:-20\d{2})?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    return 'Unknown Period'


def extract_from_aligned_tables(text: str, period: str) -> List[Dict]:
    """Extract from aligned table structures in OCR text."""
    records = []
    
    # Look for lines with multiple numbers (table rows)
    # Example: "Item1    12345   67890   11111"
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # Find lines with metrics and multiple numbers
        if any(metric in line.lower() for metrics in FINANCIAL_METRICS.values() for metric in metrics):
            # Extract all numbers from this line
            numbers = re.findall(r'[\d,]+(?:\.\d+)?', line)
            
            if numbers:
                # Extract the most recent/relevant value
                value_str = numbers[-1].replace(',', '')
                try:
                    value = float(value_str)
                    metric_name = re.sub(r'[\d,\.\s]+', '', line).strip()
                    
                    if metric_name and value > 0:
                        records.append({
                            'line_item': standardize_metric_name(metric_name),
                            'value': value,
                            'unit': 'Crores',
                            'period': period
                        })
                except ValueError:
                    continue
    
    return records


def extract_with_gemini(text: str) -> Optional[List[Dict]]:
    """Use Gemini AI for intelligent financial data extraction.
    
    This is called as fallback when local extraction insufficient.
    """
    is_ocr_text = "[OCR]" in text
    
    prompt = f"""You are a Financial Analyst. Extract financial data from this statement.

RESPONSE FORMAT: Return ONLY a JSON array. No explanations.
[{{"line_item": "Revenue from Operations", "value": 118927, "unit": "Crores", "period": "Q4 2025"}}]

OCR TEXT: {"Yes - handle artifacts like '11 1897'→'111897'" if is_ocr_text else "No"}

Extract these metrics if present:
- Revenue from Operations / Revenue / Total Revenue
- Total Income
- Net Profit / Profit After Tax
- Profit Before Tax / Operating Profit
- EBITDA
- EPS (Basic) / EPS (Diluted)
- Current Assets / Liabilities
- Other key metrics visible

TEXT:
{text[:3000]}"""  # Limit to first 3000 chars to save tokens
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        res_text = response.text.strip()
        
        # Extract JSON array from response
        json_match = re.search(r'\[.*\]', res_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        return json.loads(res_text)
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)[:100]}")
        return None


def clean_financial_data(data: List[Dict]) -> List[Dict]:
    """Validate and clean extracted financial data."""
    cleaned = []
    seen = set()
    
    for item in data:
        if not isinstance(item, dict):
            continue
        
        try:
            required = ['line_item', 'value', 'unit', 'period']
            if not all(k in item for k in required):
                continue
            
            value = item['value']
            if not isinstance(value, (int, float)):
                value = float(str(value).replace(',', ''))
            
            if value < 0:
                continue
            
            line_item = str(item['line_item']).strip()
            unit = str(item['unit']).strip() or 'Crores'
            period = str(item['period']).strip() or 'Unknown'
            
            # Skip duplicates
            key = (line_item, unit)
            if key in seen:
                continue
            seen.add(key)
            
            cleaned.append({
                'line_item': line_item,
                'value': round(value, 2),
                'unit': unit,
                'period': period
            })
        except Exception as e:
            logger.debug(f"Skipping invalid record: {e}")
            continue
    
    return cleaned
