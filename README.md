# Token Impact Estimation System

Calculate environmental impact (kWh, CO₂, Water) of AI token usage using peer-reviewed research methodologies.

## 🌱 Features

- **Multi-Provider Support**: Parse token usage data from Anthropic, Gemini, and OpenAI
- **Local Calculations**: Direct calculations based on MIT and Google research (no external API dependencies)
- **Intelligent Model Mapping**: Smart fallback strategy for model selection
- **Comprehensive Reporting**: Generate HTML, JSON, and CSV reports with Chart.js visualizations
- **CLI Interface**: Easy-to-use command-line interface

## 📁 Project Structure

```
src/
├── core/                 # Core data models and aggregation logic
├── parsers/              # CSV parsers for different providers
├── automation/           # Local calculation engine (MIT/Google research-based)
├── reporting/            # Report generation with Chart.js
└── cli/                  # Command-line interface

data/
├── input/               # CSV files from AI providers
│   ├── anthropic_data/
│   ├── gemini_data/
│   └── openai_data/
└── output/              # Generated reports
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Validate System

```bash
python main.py validate
```

### 3. Calculate Impact

```bash
python main.py calculate
```

### 4. View Reports

Check the `data/output/` directory for generated reports:
- **HTML Report**: Interactive charts with Chart.js
- **JSON Report**: Machine-readable data
- **CSV Report**: Spreadsheet-compatible format

## 📊 Supported Data Formats

### Anthropic (Claude API)
- Files: `claude_api_tokens_*.csv`
- Columns: `usage_date_utc`, `model_version`, `usage_input_tokens_*`, `usage_output_tokens`

### Gemini (Google AI)
- Files: `ZD-INC_Cost table, *.csv`
- Columns: `Date`, `SKU Description`, `Credits`

### OpenAI (GPT API)
- Files: `completions_usage_*.csv`
- Columns: `date`, `model`, `prompt_tokens`, `completion_tokens`

## 🎯 Model Mapping Strategy

The system uses intelligent model mapping to match your data with known model factors:

1. **Substring Matching**: `claude-3-5-haiku-20241022` → `claude-3-haiku`
2. **Generic Fallback**: `very-large` models → `generic-very_large`
3. **Research-Based Factors**: Each recognized model has energy/water/CO₂ multipliers based on actual measurements

## 🔧 CLI Commands

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

## 🧮 Calculation Methodology

The system uses local calculations based on peer-reviewed research:

- **Energy**: MIT "From Words to Watts" paper (arXiv:2310.03003)
- **Water**: Google's comprehensive AI environmental impact study (arXiv:2508.15734v1)
- **Carbon Intensity**: U.S. Energy Information Administration (EIA) 2023 data
- **Model Factors**: Devera.ai study + API pricing ratios
- **No External Dependencies**: All calculations performed locally using research-backed factors

See `docs/METHODOLOGY.md` for complete details.

## 📈 Report Features

### HTML Reports
- Interactive Chart.js visualizations
- Provider breakdown charts
- Model-specific impact analysis
- Summary statistics
- Detailed data tables

### JSON Reports
- Machine-readable format
- Complete data export
- Summary statistics
- Structured impact metrics

### CSV Reports
- Spreadsheet-compatible
- Monthly aggregations
- Provider breakdown
- Impact metrics

## 🛠️ Configuration

### CLI Options
- `--input-dir`: Input directory (default: `data/input`)
- `--output-dir`: Output directory (default: `data/output`)

## 🔍 Troubleshooting

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

## 📝 Development

### Adding New Providers
1. Create parser in `src/parsers/`
2. Add to `ParserFactory`
3. Update model mapping if needed

### Customizing Reports
1. Modify `ReportGenerator` class
2. Add new chart types
3. Update CLI options

## 🤝 Contributing

1. Follow the development rules in `docs/DEVELOPMENT_RULES.md`
2. Use proper error handling
3. Add comprehensive logging
4. Test with real data files

## 📄 License

This project is for internal use at Tactech.
