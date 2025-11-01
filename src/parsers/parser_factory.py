# Parser factory for creating provider-specific parsers

import os
from typing import List, Optional
from .base_parser import TokenDataParser
from .anthropic_parser import AnthropicParser
from .gemini_parser import GeminiParser
from .openai_parser import OpenAIParser
from ..core.data_models import Provider


class ParserFactory:
    """Factory for creating provider-specific parsers"""
    
    def __init__(self):
        self.parsers = {
            Provider.ANTHROPIC: AnthropicParser(),
            Provider.GEMINI: GeminiParser(),
            Provider.OPENAI: OpenAIParser()
        }
    
    def get_parser(self, provider: Provider) -> TokenDataParser:
        """Get parser for specific provider"""
        return self.parsers[provider]
    
    def detect_provider_from_filename(self, filename: str) -> Optional[Provider]:
        """Detect provider from filename patterns"""
        filename_lower = filename.lower()
        
        # Anthropic patterns
        if any(pattern in filename_lower for pattern in [
            'claude_api_tokens',
            'anthropic',
            'claude'
        ]):
            return Provider.ANTHROPIC
        
        # Gemini patterns
        if any(pattern in filename_lower for pattern in [
            'zd-inc_cost',
            'gemini',
            'google',
            'cost table',
            'zd-inc',
            'cost table,'
        ]):
            return Provider.GEMINI
        
        # OpenAI patterns
        if any(pattern in filename_lower for pattern in [
            'completions_usage',
            'openai',
            'gpt'
        ]):
            return Provider.OPENAI
        
        return None
    
    def detect_provider_from_content(self, file_path: str) -> Optional[Provider]:
        """Detect provider by examining file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read first few lines to check headers
                first_line = file.readline().strip()
                
                # Check for provider-specific headers
                if 'usage_date_utc' in first_line and 'model_version' in first_line:
                    return Provider.ANTHROPIC
                elif 'SKU description' in first_line and 'Usage amount' in first_line:
                    return Provider.GEMINI
                elif 'start_time_iso' in first_line and 'input_tokens' in first_line:
                    return Provider.OPENAI
                
        except Exception:
            pass
        
        return None
    
    def create_parser_for_file(self, file_path: str) -> Optional[TokenDataParser]:
        """Create appropriate parser for a file"""
        filename = os.path.basename(file_path)
        
        # Try filename detection first
        provider = self.detect_provider_from_filename(filename)
        
        # If filename detection fails, try content detection
        if provider is None:
            provider = self.detect_provider_from_content(file_path)
        
        if provider:
            parser = self.get_parser(provider)
            # Validate the file format
            if parser.validate_file_format(file_path):
                return parser
        
        return None
    
    def get_all_parsers(self) -> List[TokenDataParser]:
        """Get all available parsers"""
        return list(self.parsers.values())
    
    def get_supported_providers(self) -> List[Provider]:
        """Get list of supported providers"""
        return list(self.parsers.keys())
