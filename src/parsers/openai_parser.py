# OpenAI CSV parser

import csv
import os
from typing import List
from .base_parser import TokenDataParser
from ..core.data_models import TokenRecord, ProcessingResult, Provider


class OpenAIParser(TokenDataParser):
    """Parser for OpenAI API token usage CSV files"""
    
    def __init__(self):
        super().__init__(Provider.OPENAI)
    
    def parse_file(self, file_path: str) -> ProcessingResult:
        """
        Parse OpenAI CSV file with format:
        start_time,end_time,start_time_iso,end_time_iso,project_id,num_model_requests,user_id,api_key_id,model,batch,service_tier,input_tokens,output_tokens,...
        """
        try:
            records = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # Parse date from ISO format
                        date_str = row['start_time_iso']
                        from datetime import datetime
                        parsed_date = datetime.fromisoformat(date_str.replace('+00:00', ''))
                        
                        record = self._create_token_record(
                            date=parsed_date,
                            model=row['model'],
                            input_tokens=int(row['input_tokens']),
                            output_tokens=int(row['output_tokens']),
                            workspace=row.get('project_id')
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
                error_message=f"Error parsing OpenAI file {file_path}: {str(e)}"
            )
    
    def validate_file_format(self, file_path: str) -> bool:
        """Validate OpenAI CSV format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                
                # Check for required OpenAI columns
                required_columns = [
                    'start_time_iso',
                    'model',
                    'input_tokens',
                    'output_tokens'
                ]
                
                return all(col in headers for col in required_columns)
                
        except Exception:
            return False
