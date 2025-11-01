# Abstract base parser interface

from abc import ABC, abstractmethod
from typing import List
from ..core.data_models import TokenRecord, ProcessingResult, Provider


class TokenDataParser(ABC):
    """Abstract base class for parsing token usage data"""
    
    def __init__(self, provider: Provider):
        self.provider = provider
    
    @abstractmethod
    def parse_file(self, file_path: str) -> ProcessingResult:
        """
        Parse a single CSV file and return token records
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            ProcessingResult with parsed records
        """
        pass
    
    @abstractmethod
    def validate_file_format(self, file_path: str) -> bool:
        """
        Validate that the file matches the expected format for this provider
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            True if file format is valid for this provider
        """
        pass
    
    def get_provider(self) -> Provider:
        """Get the provider this parser handles"""
        return self.provider
    
    def _create_token_record(self, date: str, model: str, input_tokens: int, 
                           output_tokens: int, **kwargs) -> TokenRecord:
        """Create a TokenRecord with common fields"""
        from datetime import datetime
        
        # Parse date string to datetime
        if isinstance(date, str):
            try:
                parsed_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                try:
                    parsed_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    parsed_date = datetime.now()  # Fallback
        else:
            parsed_date = date
        
        return TokenRecord(
            date=parsed_date,
            model=model,
            provider=self.provider,
            input_tokens=int(input_tokens),
            output_tokens=int(output_tokens),
            total_tokens=int(input_tokens) + int(output_tokens),
            **kwargs
        )
