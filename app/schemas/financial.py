from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class FinancialLineItem(BaseModel):
    line_item: str = Field(..., description="Standardized name of the financial metric")
    values: Dict[str, Optional[float]] = Field(..., description="Mapping of years to numeric values")
    currency: str = Field(..., description="Detected currency (e.g., USD, INR) [cite: 24]")
    unit: str = Field(..., description="Detected units (e.g., Millions, Thousands) [cite: 24]")
    source_context: str = Field(..., description="Original text snippet for verification [cite: 19]")

class ExtractionResponse(BaseModel):
    items: List[FinancialLineItem]
    is_complete: bool = Field(..., description="Flag if any major items were missing [cite: 26]")