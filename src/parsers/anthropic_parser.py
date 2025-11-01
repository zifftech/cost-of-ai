# Anthropic CSV parser

import csv
import os
from typing import List
from .base_parser import TokenDataParser
from ..core.data_models import TokenRecord, ProcessingResult, Provider


class AnthropicParser(TokenDataParser):
    """Parser for Anthropic Claude API token usage CSV files"""
    
    def __init__(self):
        super().__init__(Provider.ANTHROPIC)
    
    def parse_file(self, file_path: str) -> ProcessingResult:
        """
        Parse Anthropic CSV file with format:
        usage_date_utc,model_version,api_key,workspace,usage_type,context_window,
        usage_input_tokens_no_cache,usage_input_tokens_cache_write_5m,
        usage_input_tokens_cache_write_1h,usage_input_tokens_cache_read,
        usage_output_tokens,web_search_count
        """
        try:
            records = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # Calculate total input tokens (no cache + cache writes + cache reads)
                        input_tokens = (
                            int(row.get('usage_input_tokens_no_cache', 0)) +
                            int(row.get('usage_input_tokens_cache_write_5m', 0)) +
                            int(row.get('usage_input_tokens_cache_write_1h', 0)) +
                            int(row.get('usage_input_tokens_cache_read', 0))
                        )
                        
                        output_tokens = int(row.get('usage_output_tokens', 0))
                        
                        record = self._create_token_record(
                            date=row['usage_date_utc'],
                            model=row['model_version'],
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            workspace=row.get('workspace'),
                            api_key=row.get('api_key')
                        )
                        
                        records.append(record)
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping invalid row in {file_path}: {e}")
                        continue
            
            return ProcessingResult(
                success=True,
                records=records,
                records_processed=len(records)
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                records=[],
                error_message=f"Error parsing Anthropic file {file_path}: {str(e)}"
            )
    
    def validate_file_format(self, file_path: str) -> bool:
        """Validate Anthropic CSV format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                
                # Check for required Anthropic columns
                required_columns = [
                    'usage_date_utc',
                    'model_version', 
                    'usage_input_tokens_no_cache',
                    'usage_output_tokens'
                ]
                
                return all(col in headers for col in required_columns)
                
        except Exception:
            return False
