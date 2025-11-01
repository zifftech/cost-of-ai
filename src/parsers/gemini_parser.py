# Gemini CSV parser

import csv
import os
from typing import List
from .base_parser import TokenDataParser
from ..core.data_models import TokenRecord, ProcessingResult, Provider


class GeminiParser(TokenDataParser):
    """Parser for Gemini API token usage CSV files"""
    
    def __init__(self):
        super().__init__(Provider.GEMINI)
    
    def parse_file(self, file_path: str) -> ProcessingResult:
        """
        Parse Gemini CSV file with format:
        Billing account name,Billing account ID,Project name,Project ID,Project hierarchy,Service description,Service ID,SKU description,SKU ID,Consumption model description,Credit type,Cost type,Usage start date,Usage end date,Usage amount,Usage unit,Unrounded Cost ($),Cost ($)
        """
        try:
            records = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # Extract model from SKU Description
                        sku_description = row.get('SKU Description', '')
                        model = self._extract_model_from_sku(sku_description)
                        
                        # Parse usage amount (remove commas)
                        usage_amount = row.get('Usage amount', '0').replace(',', '')
                        tokens = int(usage_amount) if usage_amount.isdigit() else 0
                        
                        # Parse date
                        usage_date = row.get('Usage start date', '')
                        
                        if tokens > 0:  # Only process rows with actual token usage
                            record = self._create_token_record(
                                date=usage_date,
                                model=model,
                                input_tokens=tokens // 2,  # Split roughly
                                output_tokens=tokens // 2,
                                workspace=row.get('Project ID')
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
                error_message=f"Error parsing Gemini file {file_path}: {str(e)}"
            )
    
    def _extract_model_from_sku(self, sku_description: str) -> str:
        """Extract model name from SKU description"""
        # Common Gemini model patterns in SKU descriptions
        if 'gemini-2.5-pro' in sku_description.lower():
            return 'gemini-2.5-pro'
        elif 'gemini-2.5-flash' in sku_description.lower():
            return 'gemini-2.5-flash'
        elif 'gemini-2.0-flash' in sku_description.lower():
            return 'gemini-2.0-flash'
        elif 'gemini-1.5-pro' in sku_description.lower():
            return 'gemini-1.5-pro'
        elif 'gemini-1.5-flash' in sku_description.lower():
            return 'gemini-1.5-flash'
        elif 'gemini-pro' in sku_description.lower():
            return 'gemini-pro'
        else:
            return 'gemini-unknown'
    
    def validate_file_format(self, file_path: str) -> bool:
        """Validate Gemini CSV format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                
                # Check for required Gemini columns
                required_columns = [
                    'SKU description',
                    'Usage amount',
                    'Usage start date'
                ]
                
                return all(col in headers for col in required_columns)
                
        except Exception:
            return False
