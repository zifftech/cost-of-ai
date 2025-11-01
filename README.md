# Token Impact Estimation System

Calculate environmental impact (kWh, CO₂, Water) of AI token usage using Playwright automation with tokenomy.ai.

## 🌱 Features

- **Multi-Provider Support**: Parse token usage data from Anthropic, Gemini, and OpenAI
- **Playwright Automation**: Automatically interact with tokenomy.ai energy usage estimator
- **Intelligent Model Mapping**: Smart fallback strategy for model selection
- **Comprehensive Reporting**: Generate HTML, JSON, and CSV reports with Chart.js visualizations
- **CLI Interface**: Easy-to-use command-line interface

## 📁 Project Structure

```
src/
├── core/                 # Core data models and aggregation logic
├── parsers/              # CSV parsers for different providers
├── automation/           # Playwright automation engine
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
playwright install chromium
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

The system uses intelligent model mapping to match your data with available models on tokenomy.ai:

1. **Substring Matching**: `claude-3-5-haiku-20241022` → `claude-3-haiku`
2. **Generic Fallback**: `very-large` models → `generic-very_large`

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

## 🌐 Browser Automation

The system uses Playwright to automate tokenomy.ai:

- **Headless Mode**: Runs browser in background (default)
- **Dynamic UI**: Handles real-time result updates
- **Error Handling**: Robust fallback strategies
- **Model Selection**: Intelligent mapping to available options

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

### Environment Variables
- `NOVA_ACT_API_KEY`: Not used (Playwright replaces Nova Act)

### CLI Options
- `--input-dir`: Input directory (default: `data/input`)
- `--output-dir`: Output directory (default: `data/output`)
- `--headless/--no-headless`: Browser mode (default: headless)

## 🔍 Troubleshooting

### Common Issues

1. **No CSV files found**
   - Ensure files are in `data/input/` subdirectories
   - Check file naming conventions

2. **Playwright errors**
   - Run `playwright install chromium`
   - Check internet connection for tokenomy.ai access

3. **Model mapping failures**
   - System uses generic fallbacks automatically
   - Check console output for mapping decisions

4. **Empty results**
   - Verify tokenomy.ai is accessible
   - Check browser automation logs

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
