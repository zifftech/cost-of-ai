# Token Impact Estimation System

Calculate environmental impact (kWh, CO₂, Water) of AI token usage using peer-reviewed research methodologies.

## Project Structure

```
src/
├── core/                 # Core data models and aggregation logic
├── parsers/              # CSV parsers for different providers
├── automation/           # Local calculation engine (MIT/Google research-based)
├── reporting/            # Report generation with Chart.js
├── cli/                  # Command-line interface
└── ui/                   # Web interface calculator

data/
├── input/               # CSV files from AI providers
│   ├── anthropic_data/
│   ├── gemini_data/
│   └── openai_data/
└── output/              # Generated reports
```

## Getting Started

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Validate System

```bash
python main.py validate
```

### Calculate Impact

```bash
python main.py calculate
```

### View Reports

Reports are generated in `data/output/`:
- HTML: Charts and visualizations
- JSON: Machine-readable data export
- CSV: Spreadsheet format

### Web Interface

A web-based calculator is available at `src/ui/index.html`. Open this file in a browser to:
- Calculate impact for text input
- Select provider, model, hardware, and region
- View results with real-world equivalencies
- Choose between location-based or market-based carbon accounting

The interface uses the same calculation methodology as the CLI and runs entirely client-side.

## Supported Data Formats

### Anthropic (Claude API)
- Files: `claude_api_tokens_*.csv`
- Columns: `usage_date_utc`, `model_version`, `usage_input_tokens_*`, `usage_output_tokens`

### Gemini (Google AI)
- Files: `ZD-INC_Cost table, *.csv`
- Columns: `Date`, `SKU Description`, `Credits`

### OpenAI (GPT API)
- Files: `completions_usage_*.csv`
- Columns: `date`, `model`, `prompt_tokens`, `completion_tokens`

## Model Mapping

The system maps CSV model names to known model factors:

1. **Substring Matching**: `claude-3-5-haiku-20241022` → `claude-3-haiku`
2. **Generic Fallback**: `very-large` models → `generic-very_large`
3. **Model Factors**: Recognized models have energy/water/CO₂ multipliers from research studies

## CLI Commands

```bash
# Validate system and data files
python main.py validate

# Calculate impact for all data
python main.py calculate

# Calculate for specific provider
python main.py calculate --provider anthropic

# Calculate for specific month
python main.py calculate --month 2025-07

# Generate reports only
python main.py report

# Show available models
python main.py models
```

## Calculation Methodology

Calculations are performed locally using research-based factors:

- **Energy**: MIT "From Words to Watts" paper (arXiv:2310.03003)
- **Water**: Google AI environmental impact study (arXiv:2508.15734v1)
- **Carbon Intensity**: U.S. Energy Information Administration (EIA) 2023 data
- **Model Factors**: Devera.ai study and API pricing ratios

See `docs/METHODOLOGY.md` for methodology details.

## Report Outputs

### HTML Reports
- Chart.js visualizations
- Provider and model breakdowns
- Summary statistics
- Data tables

### JSON Reports
- Machine-readable format
- Complete data export with summary statistics

### CSV Reports
- Spreadsheet format
- Monthly aggregations by provider

## Configuration

### CLI Options
- `--input-dir`: Input directory (default: `data/input`)
- `--output-dir`: Output directory (default: `data/output`)

## Troubleshooting

### Common Issues

1. **No CSV files found**
   - Ensure files are in `data/input/` subdirectories
   - Check file naming conventions

2. **Model mapping failures**
   - System uses generic fallbacks automatically
   - Check console output for mapping decisions

3. **Calculation errors**
   - Check that input CSV files are properly formatted
   - Verify model names are recognized or will use generic fallbacks

## Development

### Adding New Providers
1. Create parser in `src/parsers/`
2. Add to `ParserFactory`
3. Update model mapping as needed

### Customizing Reports
1. Modify `ReportGenerator` class
2. Add new chart types
3. Update CLI options

## Contributing

1. Follow development rules in `docs/DEVELOPMENT_RULES.md`
2. Use proper error handling
3. Include logging
4. Test with real data files

## License

This project is for internal use at Tactech.
