# CLI interface for token impact estimation system

import click
import os
from typing import List, Optional
from ..core.data_models import SystemConfiguration, ReportConfiguration, Provider
from ..parsers import ParserFactory
from ..core import TokenAggregator
from ..automation import LocalCalculator
from ..reporting import ReportGenerator


@click.group()
@click.option('--input-dir', default='data/input', help='Input directory containing CSV files')
@click.option('--output-dir', default='data/output', help='Output directory for reports')
@click.pass_context
def cli(ctx, input_dir, output_dir):
    """Token Impact Estimation System - Calculate environmental impact of AI token usage"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = SystemConfiguration(
        input_directory=input_dir,
        output_directory=output_dir
    )
    ctx.obj['report_config'] = ReportConfiguration()


@cli.command()
@click.pass_context
def validate(ctx):
    """Validate system configuration and data files"""
    config = ctx.obj['config']
    
    print("🔍 Validating system...")
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return
    
    print("✅ Configuration valid")
    
    # Check input directory
    if not os.path.exists(config.input_directory):
        print(f"❌ Input directory does not exist: {config.input_directory}")
        return
    
    print(f"✅ Input directory exists: {config.input_directory}")
    
    # Check for CSV files
    csv_files = []
    for root, dirs, files in os.walk(config.input_directory):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    if not csv_files:
        print("❌ No CSV files found in input directory")
        return
    
    print(f"✅ Found {len(csv_files)} CSV files")
    
    # Validate file formats
    parser_factory = ParserFactory()
    valid_files = 0
    
    for csv_file in csv_files:
        parser = parser_factory.create_parser_for_file(csv_file)
        if parser:
            valid_files += 1
            print(f"  ✅ {os.path.basename(csv_file)} - {parser.get_provider().value}")
        else:
            print(f"  ⚠️ {os.path.basename(csv_file)} - Unknown format")
    
    print(f"✅ {valid_files}/{len(csv_files)} files have valid formats")
    
    print("🎯 System validation complete!")




@cli.command()
@click.option('--provider', type=click.Choice(['anthropic', 'gemini', 'openai', 'all']), 
              default='all', help='Process specific provider or all')
@click.option('--month', help='Process specific month (YYYY-MM format)')
@click.option('--accounting', type=click.Choice(['location', 'market']), 
              default='location', help='Carbon accounting method: location (actual grid) or market (with carbon credits)')
@click.option('--region', type=click.Choice(['us-east', 'us-west', 'us-texas', 'us-ny', 'europe', 'europe-high', 'europe-low', 'default']), 
              default='default', help='Geographic region for carbon intensity')
@click.pass_context
def calculate_carbon_aware(ctx, provider, month, accounting, region):
    """Calculate environmental impact with carbon accounting options"""
    config = ctx.obj['config']
    report_config = ctx.obj['report_config']
    
    print("🌱 Starting carbon-aware environmental impact calculation...")
    print(f"📊 Accounting method: {accounting}")
    print(f"🌍 Region: {region}")
    
    # Parse CSV files
    parser_factory = ParserFactory()
    aggregator = TokenAggregator()
    
    all_records = []
    csv_files = []
    
    # Find CSV files
    for root, dirs, files in os.walk(config.input_directory):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    # Filter by provider if specified
    if provider != 'all':
        provider_enum = Provider(provider)
        csv_files = [f for f in csv_files 
                    if parser_factory.detect_provider_from_filename(os.path.basename(f)) == provider_enum]
    
    print(f"📁 Processing {len(csv_files)} CSV files...")
    
    # Parse files
    for csv_file in csv_files:
        parser = parser_factory.create_parser_for_file(csv_file)
        if parser:
            print(f"  📊 Parsing {os.path.basename(csv_file)}...")
            result = parser.parse_file(csv_file)
            
            if result.success:
                all_records.extend(result.records)
                print(f"    ✅ {result.records_processed} records processed")
            else:
                print(f"    ❌ {result.error_message}")
    
    if not all_records:
        print("❌ No valid records found")
        return
    
    print(f"📈 Total records: {len(all_records)}")
    
    # Aggregate records
    aggregations = aggregator.aggregate_records(all_records)
    
    # Filter by month if specified
    if month:
        year, month_num = month.split('-')
        aggregations = [agg for agg in aggregations 
                       if agg.year == int(year) and agg.month == int(month_num)]
    
    print(f"📅 Processing {len(aggregations)} monthly aggregations...")
    
    # Calculate impact with carbon accounting
    calculator = LocalCalculator()
    impact_results = []
    
    for aggregation in aggregations:
        print(f"\n🔄 Processing {aggregation.year}-{aggregation.month:02d} ({aggregation.provider.value})")
        print(f"  📊 {aggregation.total_tokens:,} tokens across {len(aggregation.model_tokens)} models")
        
        impact = calculator.calculate_impact_with_carbon_accounting(
            aggregation, 
            accounting_method=accounting,
            region=region
        )
        
        if impact:
            impact_results.append(impact)
            print(f"  ✅ Impact: {impact.kwh:.3f} kWh, {impact.co2_kg:.3f} kg CO₂, {impact.water_liters:.3f} L water")
        else:
            impact_results.append(None)
            print(f"  ❌ Failed to calculate impact")
    
    # Generate reports
    print(f"\n📋 Generating reports...")
    report_generator = ReportGenerator(report_config)
    
    # Generate all report formats
    html_file = report_generator._generate_html_report(aggregations, impact_results)
    json_file = report_generator._generate_json_report(aggregations, impact_results)
    csv_file = report_generator._generate_csv_report(aggregations, impact_results)
    
    print(f"✅ Calculation complete!")
    print(f"📄 Reports generated:")
    print(f"  - HTML: {html_file}")
    print(f"  - JSON: {json_file}")
    print(f"  - CSV: {csv_file}")


@cli.command()
@click.option('--provider', type=click.Choice(['anthropic', 'gemini', 'openai', 'all']), 
              default='all', help='Process specific provider or all')
@click.option('--month', help='Process specific month (YYYY-MM format)')
@click.pass_context
def calculate(ctx, provider, month):
    """Calculate environmental impact for token usage data"""
    config = ctx.obj['config']
    
    print("🌱 Starting environmental impact calculation...")
    
    # Parse CSV files
    parser_factory = ParserFactory()
    aggregator = TokenAggregator()
    
    all_records = []
    csv_files = []
    
    # Find CSV files
    for root, dirs, files in os.walk(config.input_directory):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    # Filter by provider if specified
    if provider != 'all':
        provider_enum = Provider(provider)
        csv_files = [f for f in csv_files 
                    if parser_factory.detect_provider_from_filename(os.path.basename(f)) == provider_enum]
    
    print(f"📁 Processing {len(csv_files)} CSV files...")
    
    # Parse files
    for csv_file in csv_files:
        parser = parser_factory.create_parser_for_file(csv_file)
        if parser:
            print(f"  📊 Parsing {os.path.basename(csv_file)}...")
            result = parser.parse_file(csv_file)
            
            if result.success:
                all_records.extend(result.records)
                print(f"    ✅ {result.records_processed} records processed")
            else:
                print(f"    ❌ {result.error_message}")
    
    if not all_records:
        print("❌ No valid records found")
        return
    
    print(f"📈 Total records: {len(all_records)}")
    
    # Aggregate records
    aggregations = aggregator.aggregate_records(all_records)
    
    # Filter by month if specified
    if month:
        year, month_num = month.split('-')
        aggregations = [agg for agg in aggregations 
                      if agg.year == int(year) and agg.month == int(month_num)]
    
    if not aggregations:
        print("❌ No aggregations found for specified criteria")
        return
    
    print(f"📅 Processing {len(aggregations)} monthly aggregations...")
    
    # Calculate impact using local calculator (faster and more reliable)
    calculator = LocalCalculator()
    impact_results = []
    
    for i, aggregation in enumerate(aggregations):
        print(f"\n🔄 Processing {aggregation.year}-{aggregation.month:02d} ({aggregation.provider.value})")
        print(f"  📊 {aggregation.total_tokens:,} tokens across {len(aggregation.model_tokens)} models")
        
        impact = calculator.calculate_impact(aggregation)
        impact_results.append(impact)
        
        if impact:
            print(f"  ✅ Impact: {impact.kwh:.3f} kWh, {impact.co2_kg:.3f} kg CO₂, {impact.water_liters:.3f} L water")
        else:
            print(f"  ❌ Failed to calculate impact")
    
    # Generate reports
    print(f"\n📋 Generating reports...")
    report_config = ReportConfiguration()
    report_generator = ReportGenerator(report_config)
    
    reports = report_generator.generate_reports(aggregations, impact_results)
    
    print("✅ Calculation complete!")
    print(f"📄 Reports generated:")
    for format_type, file_path in reports.items():
        print(f"  - {format_type.upper()}: {file_path}")


@cli.command()
@click.pass_context
def report(ctx):
    """Generate reports from existing data (requires previous calculation)"""
    config = ctx.obj['config']
    
    print("📋 Generating reports...")
    
    # This would typically read from a data file or database
    # For now, we'll just show the available output files
    if os.path.exists(config.output_directory):
        output_files = os.listdir(config.output_directory)
        if output_files:
            print(f"📁 Available reports in {config.output_directory}:")
            for file in output_files:
                print(f"  - {file}")
        else:
            print(f"📁 No reports found in {config.output_directory}")
    else:
        print(f"❌ Output directory does not exist: {config.output_directory}")


@cli.command()
@click.option('--provider', type=click.Choice(['anthropic', 'gemini', 'openai']), 
              help='Show models for specific provider')
def models(provider):
    """Show available models and their mappings"""
    print("🤖 Available models and mappings:")
    
    if provider:
        provider_enum = Provider(provider)
        print(f"\n{provider_enum.value.title()} models:")
        # This would show models from the actual data files
        print("  (Run 'calculate' to see actual models from your data)")
    else:
        print("\nAll supported providers:")
        for p in Provider:
            print(f"  - {p.value}")


if __name__ == '__main__':
    cli()
