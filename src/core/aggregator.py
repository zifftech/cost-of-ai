# Token aggregation logic

from collections import defaultdict
from datetime import datetime
from typing import Dict, List
from .data_models import TokenRecord, MonthlyAggregation, Provider


class TokenAggregator:
    """Aggregates token usage data by month and provider"""
    
    def __init__(self):
        self.aggregations: Dict[str, MonthlyAggregation] = {}
    
    def aggregate_records(self, records: List[TokenRecord]) -> List[MonthlyAggregation]:
        """
        Aggregate token records by month and provider
        
        Args:
            records: List of TokenRecord objects
            
        Returns:
            List of MonthlyAggregation objects
        """
        # Group by year-month-provider
        grouped = defaultdict(lambda: defaultdict(int))
        
        for record in records:
            key = f"{record.date.year}-{record.date.month:02d}-{record.provider.value}"
            grouped[key][record.model] += record.total_tokens
        
        # Create MonthlyAggregation objects
        aggregations = []
        for key, model_tokens in grouped.items():
            year, month, provider_str = key.split('-')
            provider = Provider(provider_str)
            
            total_tokens = sum(model_tokens.values())
            
            aggregation = MonthlyAggregation(
                year=int(year),
                month=int(month),
                provider=provider,
                model_tokens=dict(model_tokens),
                total_tokens=total_tokens
            )
            
            aggregations.append(aggregation)
            self.aggregations[key] = aggregation
        
        return aggregations
    
    def get_aggregation(self, year: int, month: int, provider: Provider) -> MonthlyAggregation:
        """Get aggregation for specific year-month-provider"""
        key = f"{year}-{month:02d}-{provider.value}"
        return self.aggregations.get(key)
    
    def get_all_aggregations(self) -> List[MonthlyAggregation]:
        """Get all aggregations"""
        return list(self.aggregations.values())
    
    def get_aggregations_by_provider(self, provider: Provider) -> List[MonthlyAggregation]:
        """Get all aggregations for a specific provider"""
        return [agg for agg in self.aggregations.values() if agg.provider == provider]
    
    def get_aggregations_by_month(self, year: int, month: int) -> List[MonthlyAggregation]:
        """Get all aggregations for a specific month"""
        return [agg for agg in self.aggregations.values() 
                if agg.year == year and agg.month == month]
    
    def get_total_tokens_by_provider(self) -> Dict[Provider, int]:
        """Get total tokens by provider across all months"""
        totals = defaultdict(int)
        for agg in self.aggregations.values():
            totals[agg.provider] += agg.total_tokens
        return dict(totals)
    
    def get_total_tokens_by_month(self) -> Dict[str, int]:
        """Get total tokens by month across all providers"""
        totals = defaultdict(int)
        for agg in self.aggregations.values():
            key = f"{agg.year}-{agg.month:02d}"
            totals[key] += agg.total_tokens
        return dict(totals)
    
    def clear(self):
        """Clear all aggregations"""
        self.aggregations.clear()
