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

### Real-Time Calculator

A web-based real-time calculator is available for calculating environmental impact of text input without processing CSV files.

**Location:** `src/ui/index.html`

**What it does:**
- Estimates token count from text input (approximately 4 characters per token)
- Calculates energy consumption (kWh), carbon emissions (kg CO₂), and water usage (liters) in real-time
- Uses the same calculation methodology as the CLI (MIT and Google research-based factors)
- Displays results with real-world equivalencies grouped by metric type (CO₂, energy, water)
- Runs entirely client-side - no server or API calls required

**How to launch:**
1. Open `src/ui/index.html` in any modern web browser
2. No installation or server setup required - works as a standalone HTML file

**Features:**
- Text input with live token count estimation
- Provider selection (OpenAI, Anthropic, Google Gemini)
- Model selection (automatically filtered by provider)
- Hardware selection (H100, A100, TPU, etc.)
- Region selection for location-based carbon accounting
- Carbon accounting method (location-based vs market-based)
- Sample text buttons for quick testing
- Real-world equivalencies (smartphone charges, coffee cups, shower minutes, etc.)

**Usage:**
1. Paste or type text into the input field
2. Select your provider, model, hardware, and region
3. Choose carbon accounting method
4. Click "Calculate Environmental Impact"
5. View results with energy, CO₂, and water metrics plus equivalencies

## LLM Provider Reports

### Anthropic (Claude API)

**File Format:**
- Files: `claude_api_tokens_*.csv`
- Columns: `usage_date_utc`, `model_version`, `usage_input_tokens_*`, `usage_output_tokens`

**How to Download:**
- Log in to your Anthropic account at console.anthropic.com
- Navigate to the Usage or Billing section
- Select the desired date range
- Export usage data as CSV
- Files should be named with pattern `claude_api_tokens_YYYY_MM.csv`

### Gemini (Google AI)

**File Format:**
- Files: `ZD-INC_Cost table, *.csv`
- Columns: `Date`, `SKU Description`, `Credits`

**How to Download:**
- Log in to Google Cloud Console
- Navigate to Billing > Cost table reports
- Select your billing account and the date range
- Export the cost table as CSV
- Files are typically named `ZD-INC_Cost table, YYYY-MM-DD — YYYY-MM-DD.csv`

### OpenAI (GPT API)

**File Format:**
- Files: `completions_usage_*.csv`
- Columns: `date`, `model`, `prompt_tokens`, `completion_tokens`

**How to Download:**
- Log in to your OpenAI account at platform.openai.com
- Navigate to Usage or Billing section
- Select the billing period (monthly)
- Export usage data as CSV
- Files should be named with pattern `completions_usage_YYYY-MM-DD_YYYY-MM-DD.csv`

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


## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.
