# Report generator with Chart.js visualizations

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from ..core.data_models import MonthlyAggregation, ImpactMetrics, ReportConfiguration

# Real-world equivalency conversion factors (inspired by Real World Visuals Energy Converter)
# https://www.realworldvisuals.com/energy-converter
EQUIVALENCY_FACTORS = {
    # Transportation equivalencies
    "miles_driven": {
        "description": "Miles Driven (avg car, ~393g/mi)",
        "co2_per_unit": 0.393,  # kg CO2 per mile
        "unit": "miles"
    },
    "flights_nyc_la": {
        "description": "Flights NYC to LA (~900 kg CO2 per flight)",
        "co2_per_unit": 900.0,  # kg CO2 per flight
        "unit": "flights"
    },
    "flights_nyc_london": {
        "description": "Flights NYC to London (~1,200 kg CO2 per flight)",
        "co2_per_unit": 1200.0,  # kg CO2 per flight
        "unit": "flights"
    },
    
    # Household energy equivalencies
    "household_electricity": {
        "description": "Household Electricity (avg US home, ~10,500 kWh/yr)",
        "kwh_per_unit": 10500.0,  # kWh per year
        "unit": "years"
    },
    "household_electricity_days": {
        "description": "Household Electricity (avg US home, ~28.8 kWh/day)",
        "kwh_per_unit": 28.8,  # kWh per day
        "unit": "days"
    },
    "household_electricity_hours": {
        "description": "Household Electricity (avg US home, ~1.2 kWh/hour)",
        "kwh_per_unit": 1.2,  # kWh per hour
        "unit": "hours"
    },
    
    # Technology equivalencies
    "smartphone_charges": {
        "description": "Smartphone Charges (~8g/charge)",
        "co2_per_unit": 0.008,  # kg CO2 per charge
        "unit": "charges",
        "min_display": 0.0  # Always show - provides meaningful context even for small values
    },
    "laptop_charges": {
        "description": "Laptop Charges (~50g/charge)",
        "co2_per_unit": 0.050,  # kg CO2 per charge
        "unit": "charges",
        "min_display": 0.0  # Always show - provides meaningful context even for small values
    },
    "tv_watching_hours": {
        "description": "TV Watching (LED TV, ~0.1 kWh/hour)",
        "kwh_per_unit": 0.1,  # kWh per hour
        "unit": "hours"
    },
    "gaming_hours": {
        "description": "Gaming (Gaming PC, ~0.3 kWh/hour)",
        "kwh_per_unit": 0.3,  # kWh per hour
        "unit": "hours"
    },
    
    # Food and lifestyle equivalencies
    # Note: Hamburger value represents a restaurant cheeseburger with all ingredients (meat, bun, cheese, condiments, transport)
    # Sources vary: EPA and research show 1-3 kg CO2, with 2.5 kg representing a full restaurant meal burger
    "hamburgers": {
        "description": "Cheeseburgers (~2.5 kg CO2 per burger)",
        "co2_per_unit": 2.5,  # kg CO2 per burger (restaurant cheeseburger, lifecycle - on higher end of typical 1-3 kg range)
        "unit": "burgers",
        "min_display": 0.05  # Lower threshold for accountability - show even small impacts
    },
    "coffee_cups": {
        "description": "Coffee Cups (~0.2 kg CO2 per cup)",
        "co2_per_unit": 0.2,  # kg CO2 per cup
        "unit": "cups",
        "min_display": 0.0  # Always show - more intuitive than fractional burgers for small amounts
    },
    "beer_bottles": {
        "description": "Beer Bottles (~0.3 kg CO2 per bottle)",
        "co2_per_unit": 0.3,  # kg CO2 per bottle
        "unit": "bottles",
        "min_display": 0.0  # Always show - more intuitive than fractional burgers for small amounts
    },
    
    # Water equivalencies
    "water_bottles": {
        "description": "Plastic Water Bottles (500mL/16.9oz each)",
        "liters_per_unit": 0.5,  # liters per bottle (standard 16.9oz/500mL bottle)
        "unit": "bottles",
        "min_display": 0.1
    },
    "shower_minutes": {
        "description": "Shower Minutes (standard 2.5 gpm ≈ 9.5L/min)",
        "liters_per_unit": 9.5,  # liters per minute (standard 2.5 gpm showerhead - not efficient, for accountability)
        "unit": "minutes",
        "min_display": 0.0  # Always show for accountability
    },
    "showers": {
        "description": "Showers (avg 8 minutes, 76L total)",
        "liters_per_unit": 76.0,  # liters per shower (8 min × 9.5 L/min for standard showerhead)
        "unit": "showers",
        "min_display": 0.05  # Lower threshold for accountability
    },
    "bathtubs": {
        "description": "Bathtubs (avg 150L)",
        "liters_per_unit": 150.0,  # liters per bath
        "unit": "baths"
    },
    
    # Environmental equivalencies
    "urban_tree_sequestration": {
        "description": "Urban Tree Sequestration (~60kg/yr)",
        "co2_per_unit": 60.0,  # kg CO2 per year
        "unit": "years"
    },
    "tree_planting": {
        "description": "Tree Planting (mature tree absorbs ~22kg CO2/yr)",
        "co2_per_unit": 22.0,  # kg CO2 per year
        "unit": "trees"
    },
    "solar_panel_hours": {
        "description": "Solar Panel Output (1kW panel, ~1 kWh/hour)",
        "kwh_per_unit": 1.0,  # kWh per hour
        "unit": "hours"
    },
    
    # Industrial equivalencies
    "steel_production": {
        "description": "Steel Production (1 ton = ~1,800 kg CO2)",
        "co2_per_unit": 1800.0,  # kg CO2 per ton
        "unit": "tons"
    },
    "cement_production": {
        "description": "Cement Production (1 ton = ~900 kg CO2)",
        "co2_per_unit": 900.0,  # kg CO2 per ton
        "unit": "tons"
    }
}


class ReportGenerator:
    """Generate reports with Chart.js visualizations"""
    
    def __init__(self, config: ReportConfiguration):
        self.config = config
        self.output_dir = "data/output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _calculate_equivalencies(self, total_impact: ImpactMetrics) -> Dict[str, float]:
        """Calculate real-world equivalencies for the total impact"""
        equivalencies = {}
        
        for key, factor in EQUIVALENCY_FACTORS.items():
            min_display = factor.get("min_display", 0.0)  # Default: show all
            
            if "co2_per_unit" in factor:
                # CO2-based equivalencies (skip zero division)
                if factor["co2_per_unit"] > 0:
                    value = total_impact.co2_kg / factor["co2_per_unit"]
                    # Only include if above minimum display threshold
                    # Exception: Always show coffee cups, beer bottles, and smartphone/laptop charges 
                    # as they provide meaningful context even for small values
                    if value >= min_display or key in ["coffee_cups", "beer_bottles", "smartphone_charges", "laptop_charges"]:
                        equivalencies[key] = value
                else:
                    equivalencies[key] = float('inf')  # Infinite bike rides for zero emissions
            elif "kwh_per_unit" in factor:
                # Energy-based equivalencies
                value = total_impact.kwh / factor["kwh_per_unit"]
                if value >= min_display:
                    equivalencies[key] = value
            elif "liters_per_unit" in factor:
                # Water-based equivalencies
                value = total_impact.water_liters / factor["liters_per_unit"]
                # For water, show shower_minutes even if below threshold (more intuitive than 0.0645 showers)
                if value >= min_display or key == "shower_minutes":
                    equivalencies[key] = value
        
        return equivalencies

    def generate_reports(self, aggregations: List[MonthlyAggregation], 
                        impact_results: List[Optional[ImpactMetrics]]) -> Dict[str, str]:
        """
        Generate comprehensive reports
        
        Args:
            aggregations: List of monthly aggregations
            impact_results: List of corresponding impact metrics
            
        Returns:
            Dictionary of generated report file paths
        """
        reports = {}
        
        # Generate HTML report with charts
        if self.config.include_charts:
            html_report = self._generate_html_report(aggregations, impact_results)
            reports['html'] = html_report
        
        # Generate JSON report
        if 'json' in self.config.output_formats:
            json_report = self._generate_json_report(aggregations, impact_results)
            reports['json'] = json_report
        
        # Generate CSV report
        if 'csv' in self.config.output_formats:
            csv_report = self._generate_csv_report(aggregations, impact_results)
            reports['csv'] = csv_report
        
        return reports
    
    def _generate_html_report(self, aggregations: List[MonthlyAggregation], 
                            impact_results: List[Optional[ImpactMetrics]]) -> str:
        """Generate HTML report with Chart.js visualizations"""
        
        # Prepare data for charts
        provider_data = self._prepare_provider_data(aggregations, impact_results)
        model_data = self._prepare_model_data(aggregations, impact_results)
        monthly_data = self._prepare_monthly_data(aggregations, impact_results)
        monthly_provider_data = self._prepare_monthly_provider_data(aggregations, impact_results)
        
        # Calculate total impact for equivalencies
        total_impact = ImpactMetrics(
            kwh=sum(impact.kwh for impact in impact_results if impact),
            co2_kg=sum(impact.co2_kg for impact in impact_results if impact),
            water_liters=sum(impact.water_liters for impact in impact_results if impact)
        )
        equivalencies = self._calculate_equivalencies(total_impact)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Token Impact Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1, h2 {{
            color: #333;
        }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 8px;
        }}
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #1976d2;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .equivalencies {{
            margin: 30px 0;
            padding: 20px;
            background: #f0f8ff;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
        }}
        .equivalencies h2 {{
            color: #1976d2;
            margin-top: 0;
        }}
        .equivalency-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .equivalency-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .equivalency-value {{
            font-size: 1.2em;
            font-weight: bold;
            color: #1976d2;
        }}
        .equivalency-description {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 Token Impact Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        {self._generate_summary_stats(aggregations, impact_results)}
        
        {self._generate_equivalencies_section(equivalencies)}
        
        <div class="chart-container">
            <h2>📊 Carbon Impact by Provider</h2>
            <canvas id="providerChart" width="400" height="200"></canvas>
        </div>
        
        <div class="chart-container">
            <h2>📅 Monthly Impact Breakdown</h2>
            <canvas id="monthlyChart" width="400" height="200"></canvas>
        </div>
        
        <div class="chart-container">
            <h2>📅 Monthly Impact by Provider</h2>
            <canvas id="monthlyProviderChart" width="400" height="200"></canvas>
        </div>
        
        {self._generate_model_charts(model_data)}
        
        {self._generate_data_table(aggregations, impact_results)}
    </div>
    
    <script>
        {self._generate_chart_js(provider_data, model_data, monthly_data, monthly_provider_data)}
    </script>
</body>
</html>
"""
        
        # Save HTML report
        html_file = os.path.join(self.output_dir, f"token_impact_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML report generated: {html_file}")
        return html_file
    
    def _prepare_provider_data(self, aggregations: List[MonthlyAggregation], 
                              impact_results: List[Optional[ImpactMetrics]]) -> Dict:
        """Prepare data for provider chart"""
        provider_stats = {}
        
        for agg, impact in zip(aggregations, impact_results):
            provider = agg.provider.value.title()
            
            if provider not in provider_stats:
                provider_stats[provider] = {
                    'tokens': 0,
                    'kwh': 0.0,
                    'co2': 0.0,
                    'water': 0.0
                }
            
            provider_stats[provider]['tokens'] += agg.total_tokens
            
            if impact:
                provider_stats[provider]['kwh'] += impact.kwh
                provider_stats[provider]['co2'] += impact.co2_kg
                provider_stats[provider]['water'] += impact.water_liters
        
        return provider_stats
    
    def _prepare_model_data(self, aggregations: List[MonthlyAggregation], 
                           impact_results: List[Optional[ImpactMetrics]]) -> Dict:
        """Prepare data for model charts"""
        model_stats = {}
        
        for agg, impact in zip(aggregations, impact_results):
            provider = agg.provider.value.title()
            
            if provider not in model_stats:
                model_stats[provider] = {}
            
            for model, tokens in agg.model_tokens.items():
                if model not in model_stats[provider]:
                    model_stats[provider][model] = {
                        'tokens': 0,
                        'kwh': 0.0,
                        'co2': 0.0,
                        'water': 0.0
                    }
                
                model_stats[provider][model]['tokens'] += tokens
                
                if impact:
                    # Distribute impact proportionally by token count
                    total_tokens = agg.total_tokens
                    if total_tokens > 0:
                        proportion = tokens / total_tokens
                        model_stats[provider][model]['kwh'] += impact.kwh * proportion
                        model_stats[provider][model]['co2'] += impact.co2_kg * proportion
                        model_stats[provider][model]['water'] += impact.water_liters * proportion
        
        return model_stats
    
    def _prepare_monthly_data(self, aggregations: List[MonthlyAggregation], 
                             impact_results: List[Optional[ImpactMetrics]]) -> Dict:
        """Prepare data for monthly chart"""
        monthly_stats = {}
        
        for agg, impact in zip(aggregations, impact_results):
            month_key = f"{agg.year}-{agg.month:02d}"
            
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {
                    'tokens': 0,
                    'kwh': 0.0,
                    'co2': 0.0,
                    'water': 0.0
                }
            
            monthly_stats[month_key]['tokens'] += agg.total_tokens
            
            if impact:
                monthly_stats[month_key]['kwh'] += impact.kwh
                monthly_stats[month_key]['co2'] += impact.co2_kg
                monthly_stats[month_key]['water'] += impact.water_liters
        
        return monthly_stats
    
    def _prepare_monthly_provider_data(self, aggregations: List[MonthlyAggregation], 
                                     impact_results: List[Optional[ImpactMetrics]]) -> Dict:
        """Prepare data for monthly provider chart"""
        monthly_provider_stats = {}
        
        for agg, impact in zip(aggregations, impact_results):
            month_key = f"{agg.year}-{agg.month:02d}"
            provider = agg.provider.value.title()
            
            if month_key not in monthly_provider_stats:
                monthly_provider_stats[month_key] = {}
            
            if provider not in monthly_provider_stats[month_key]:
                monthly_provider_stats[month_key][provider] = {
                    'tokens': 0,
                    'kwh': 0.0,
                    'co2': 0.0,
                    'water': 0.0
                }
            
            monthly_provider_stats[month_key][provider]['tokens'] += agg.total_tokens
            
            if impact:
                monthly_provider_stats[month_key][provider]['kwh'] += impact.kwh
                monthly_provider_stats[month_key][provider]['co2'] += impact.co2_kg
                monthly_provider_stats[month_key][provider]['water'] += impact.water_liters
        
        return monthly_provider_stats
    
    def _generate_summary_stats(self, aggregations: List[MonthlyAggregation], 
                               impact_results: List[Optional[ImpactMetrics]]) -> str:
        """Generate summary statistics"""
        total_tokens = sum(agg.total_tokens for agg in aggregations)
        total_kwh = sum(impact.kwh for impact in impact_results if impact)
        total_co2 = sum(impact.co2_kg for impact in impact_results if impact)
        total_water = sum(impact.water_liters for impact in impact_results if impact)
        
        return f"""
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-value">{total_tokens:,}</div>
                <div class="stat-label">Total Tokens</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_kwh:,.2f}</div>
                <div class="stat-label">kWh Energy</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_co2:,.2f}</div>
                <div class="stat-label">kg CO₂</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_water:,.2f}</div>
                <div class="stat-label">L Water</div>
            </div>
        </div>
        """
    
    def _generate_equivalencies_section(self, equivalencies: Dict[str, float]) -> str:
        """Generate equivalencies section"""
        equivalency_items = []
        
        for key, value in equivalencies.items():
            factor = EQUIVALENCY_FACTORS[key]
            unit = factor["unit"]
            description = factor["description"]
            
            # Format the value appropriately
            if value == float('inf'):
                formatted_value = "∞"
            elif value < 0.001:
                # For very small values, use scientific notation
                formatted_value = f"{value:.2e}"
            elif value < 0.1:
                # For small values, show more decimal places
                formatted_value = f"{value:.4f}"
            elif value < 1:
                # For fractional values, show 3 decimal places
                formatted_value = f"{value:.3f}"
            else:
                # For large values, use comma formatting
                formatted_value = f"{value:,.1f}"
            
            equivalency_items.append(f"""
                <div class="equivalency-item">
                    <div class="equivalency-value">{formatted_value} {unit}</div>
                    <div class="equivalency-description">{description}</div>
                </div>
            """)
        
        return f"""
        <div class="equivalencies">
            <h2>🌍 Real-World Equivalencies</h2>
            <p>Your AI token usage is equivalent to:</p>
            <div class="equivalency-grid">
                {''.join(equivalency_items)}
            </div>
        </div>
        """
    
    def _generate_model_charts(self, model_data: Dict) -> str:
        """Generate individual model charts for each provider"""
        charts_html = ""
        
        for provider, models in model_data.items():
            if not models:
                continue
                
            chart_id = f"modelChart_{provider.lower().replace(' ', '_')}"
            charts_html += f"""
        <div class="chart-container">
            <h2>🤖 {provider} Models Impact</h2>
            <canvas id="{chart_id}" width="400" height="200"></canvas>
        </div>
            """
        
        return charts_html
    
    def _generate_chart_js(self, provider_data: Dict, model_data: Dict, monthly_data: Dict, monthly_provider_data: Dict) -> str:
        """Generate Chart.js JavaScript code"""
        
        # Provider chart data
        providers = list(provider_data.keys())
        co2_data = [provider_data[p]['co2'] for p in providers]
        token_data = [provider_data[p]['tokens'] for p in providers]
        
        # Create labels with tokens
        labels = [f"{p}\n({t:,} tokens)" for p, t in zip(providers, token_data)]
        
        provider_chart_js = f"""
        // Provider Chart
        const providerCtx = document.getElementById('providerChart').getContext('2d');
        new Chart(providerCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'CO₂ Emissions (kg)',
                    data: {json.dumps(co2_data)},
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 205, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 205, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'CO₂ Emissions (kg)'
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Carbon Impact by Provider'
                    }},
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        """
        
        # Monthly chart data
        months = sorted(monthly_data.keys())
        monthly_co2 = [monthly_data[m]['co2'] for m in months]
        monthly_tokens = [monthly_data[m]['tokens'] for m in months]
        
        # Create labels with tokens
        monthly_labels = [f"{m}\n({t:,} tokens)" for m, t in zip(months, monthly_tokens)]
        
        monthly_chart_js = f"""
        // Monthly Chart
        const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
        new Chart(monthlyCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(monthly_labels)},
                datasets: [{{
                    label: 'CO₂ Emissions (kg)',
                    data: {json.dumps(monthly_co2)},
                    backgroundColor: 'rgba(255, 159, 64, 0.8)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'CO₂ Emissions (kg)'
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Monthly Carbon Impact Breakdown'
                    }},
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        """
        
        # Monthly provider chart data
        months = sorted(monthly_provider_data.keys())
        providers = list(set(provider for month_data in monthly_provider_data.values() for provider in month_data.keys()))
        
        # Create datasets for each provider
        monthly_provider_datasets = []
        colors = [
            'rgba(255, 99, 132, 0.8)',   # Red
            'rgba(54, 162, 235, 0.8)',   # Blue  
            'rgba(255, 205, 86, 0.8)',   # Yellow
            'rgba(75, 192, 192, 0.8)',   # Teal
            'rgba(153, 102, 255, 0.8)',  # Purple
        ]
        
        for i, provider in enumerate(providers):
            provider_co2_data = []
            provider_tokens_data = []
            
            for month in months:
                if provider in monthly_provider_data[month]:
                    provider_co2_data.append(monthly_provider_data[month][provider]['co2'])
                    provider_tokens_data.append(monthly_provider_data[month][provider]['tokens'])
                else:
                    provider_co2_data.append(0)
                    provider_tokens_data.append(0)
            
            monthly_provider_datasets.append({
                'label': provider,
                'data': provider_co2_data,
                'backgroundColor': colors[i % len(colors)],
                'borderColor': colors[i % len(colors)].replace('0.8', '1'),
                'borderWidth': 1
            })
        
        monthly_provider_chart_js = f"""
        // Monthly Provider Chart
        const monthlyProviderCtx = document.getElementById('monthlyProviderChart').getContext('2d');
        new Chart(monthlyProviderCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(months)},
                datasets: {json.dumps(monthly_provider_datasets)}
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'CO₂ Emissions (kg)'
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Monthly Carbon Impact by Provider'
                    }},
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }}
            }}
        }});
        """
        
        # Model charts
        model_charts_js = ""
        for provider, models in model_data.items():
            if not models:
                continue
                
            chart_id = f"modelChart_{provider.lower().replace(' ', '_')}"
            model_names = list(models.keys())
            model_co2 = [models[m]['co2'] for m in model_names]
            model_tokens = [models[m]['tokens'] for m in model_names]
            
            # Create labels with tokens
            model_labels = [f"{m}\n({t:,} tokens)" for m, t in zip(model_names, model_tokens)]
            
            model_charts_js += f"""
        // {provider} Model Chart
        const {chart_id.replace('-', '_')}Ctx = document.getElementById('{chart_id}').getContext('2d');
        new Chart({chart_id.replace('-', '_')}Ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(model_labels)},
                datasets: [{{
                    label: 'CO₂ Emissions (kg)',
                    data: {json.dumps(model_co2)},
                    backgroundColor: 'rgba(75, 192, 192, 0.8)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'CO₂ Emissions (kg)'
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: '{provider} Models Carbon Impact'
                    }},
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
            """
        
        return provider_chart_js + monthly_chart_js + monthly_provider_chart_js + model_charts_js
    
    def _generate_data_table(self, aggregations: List[MonthlyAggregation], 
                           impact_results: List[Optional[ImpactMetrics]]) -> str:
        """Generate data table"""
        if not self.config.include_raw_data:
            return ""
        
        table_rows = ""
        for agg, impact in zip(aggregations, impact_results):
            impact_str = f"{impact.kwh:.3f} kWh, {impact.co2_kg:.3f} kg CO₂, {impact.water_liters:.3f} L" if impact else "Failed"
            
            table_rows += f"""
            <tr>
                <td>{agg.year}-{agg.month:02d}</td>
                <td>{agg.provider.value.title()}</td>
                <td>{agg.total_tokens:,}</td>
                <td>{impact_str}</td>
            </tr>
            """
        
        return f"""
        <div class="chart-container">
            <h2>📋 Detailed Data</h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <thead>
                    <tr style="background-color: #f0f0f0;">
                        <th style="padding: 10px; border: 1px solid #ddd;">Month</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Provider</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Tokens</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Impact</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_json_report(self, aggregations: List[MonthlyAggregation], 
                            impact_results: List[Optional[ImpactMetrics]]) -> str:
        """Generate JSON report"""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_aggregations": len(aggregations),
                "successful_calculations": sum(1 for r in impact_results if r is not None),
                "total_tokens": sum(agg.total_tokens for agg in aggregations),
                "total_kwh": sum(impact.kwh for impact in impact_results if impact),
                "total_co2_kg": sum(impact.co2_kg for impact in impact_results if impact),
                "total_water_liters": sum(impact.water_liters for impact in impact_results if impact)
            },
            "data": []
        }
        
        for agg, impact in zip(aggregations, impact_results):
            record = {
                "year": agg.year,
                "month": agg.month,
                "provider": agg.provider.value,
                "total_tokens": agg.total_tokens,
                "model_tokens": agg.model_tokens,
                "impact": {
                    "kwh": impact.kwh if impact else None,
                    "co2_kg": impact.co2_kg if impact else None,
                    "water_liters": impact.water_liters if impact else None
                } if impact else None
            }
            report_data["data"].append(record)
        
        json_file = os.path.join(self.output_dir, f"token_impact_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"✅ JSON report generated: {json_file}")
        return json_file
    
    def _generate_csv_report(self, aggregations: List[MonthlyAggregation], 
                           impact_results: List[Optional[ImpactMetrics]]) -> str:
        """Generate CSV report"""
        import csv
        
        csv_file = os.path.join(self.output_dir, f"token_impact_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Year', 'Month', 'Provider', 'Total_Tokens', 'kWh', 'CO2_kg', 'Water_L'])
            
            for agg, impact in zip(aggregations, impact_results):
                writer.writerow([
                    agg.year,
                    agg.month,
                    agg.provider.value,
                    agg.total_tokens,
                    impact.kwh if impact else '',
                    impact.co2_kg if impact else '',
                    impact.water_liters if impact else ''
                ])
        
        print(f"✅ CSV report generated: {csv_file}")
        return csv_file
