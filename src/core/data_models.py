# Core data models for token impact estimation system

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class Provider(Enum):
    """AI model providers"""
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OPENAI = "openai"


@dataclass
class TokenRecord:
    """Individual token usage record"""
    date: datetime
    model: str
    provider: Provider
    input_tokens: int
    output_tokens: int
    total_tokens: int
    workspace: Optional[str] = None
    api_key: Optional[str] = None
    
    def __post_init__(self):
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens


@dataclass
class MonthlyAggregation:
    """Aggregated token usage data for a month"""
    year: int
    month: int
    provider: Provider
    model_tokens: Dict[str, int]  # model -> total_tokens
    total_tokens: int
    
    def __post_init__(self):
        if self.total_tokens == 0:
            self.total_tokens = sum(self.model_tokens.values())


@dataclass
class ImpactMetrics:
    """Environmental impact metrics"""
    kwh: float
    co2_kg: float
    water_liters: float
    cost_usd: Optional[float] = None
    
    def __post_init__(self):
        # Validate metrics are positive
        if self.kwh < 0 or self.co2_kg < 0 or self.water_liters < 0:
            raise ValueError("Impact metrics must be positive")


@dataclass
class ProcessingResult:
    """Result of processing token data"""
    success: bool
    records: List[TokenRecord]
    error_message: Optional[str] = None
    records_processed: int = 0
    
    def __post_init__(self):
        if self.success and self.records_processed == 0:
            self.records_processed = len(self.records)


@dataclass
class SystemConfiguration:
    """System configuration settings"""
    input_directory: str = "data/input"
    output_directory: str = "data/output"
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.input_directory:
            errors.append("Input directory is required")
        
        if not os.path.exists(self.input_directory):
            errors.append(f"Input directory does not exist: {self.input_directory}")
        
        if not os.path.exists(self.output_directory):
            try:
                os.makedirs(self.output_directory, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")
        
        return errors


@dataclass
class ReportConfiguration:
    """Report generation configuration"""
    include_charts: bool = True
    chart_format: str = "html"  # html, json
    include_raw_data: bool = True
    output_formats: List[str] = None
    
    def __post_init__(self):
        if self.output_formats is None:
            self.output_formats = ["html", "json", "csv"]
