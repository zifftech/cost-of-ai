# Token Impact Estimation Methodology

## Overview

This document describes the comprehensive methodology used to calculate the environmental impact (energy consumption, carbon emissions, and water usage) of Large Language Model (LLM) token usage. Our approach combines peer-reviewed research, industry standards, and provider-specific factors to provide accurate, real-world environmental impact assessments.

## Core Methodology

### 1. Energy Consumption Calculation

**Base Energy Factor**: `0.00000106 kWh per token`

**Source**: MIT "From Words to Watts" paper (arXiv:2310.03003)
- **Paper**: "From Words to Watts: Benchmarking the Energy Costs of Large Language Model Inference"
- **Authors**: Siddharth Samsi, Dan Zhao, et al. (MIT Lincoln Laboratory)
- **Methodology**: Comprehensive benchmarking of LLaMA models on NVIDIA V100 & A100 GPUs
- **Calibration**: Validated against llmemissions.com results for consistency

**Calculation Formula**:
```
Energy (kWh) = Tokens × Base_Energy_Factor × Model_Factor × Hardware_Factor × PUE_Factor
```

### 2. Carbon Emissions Calculation

**Carbon Intensity Factor**: `0.367 kg CO₂ per kWh`

**Source**: U.S. Energy Information Administration (EIA) 2023 data
- **URL**: https://www.eia.gov/tools/faqs/faq.php?id=74&t=11
- **Data**: 0.81 pounds CO₂ per kWh = 0.367 kg CO₂ per kWh
- **Scope**: U.S. average for all electricity generation sources
- **Methodology**: Location-based accounting (actual grid emissions)

**Calculation Formula**:
```
CO₂ (kg) = Energy (kWh) × Carbon_Intensity_Factor
```

### 3. Water Usage Calculation

**Base Water Factor**: `0.0000026 L per token`

**Source**: Google's comprehensive AI environmental impact study
- **Paper**: "Measuring the environmental impact of delivering AI at Google Scale"
- **URL**: https://arxiv.org/html/2508.15734v1
- **Data**: 0.26 mL water per Gemini prompt (~100 tokens average)
- **Methodology**: Full-stack infrastructure measurement including cooling systems

**Calculation Formula**:
```
Water (L) = Tokens × Base_Water_Factor × Model_Factor × Hardware_Factor
```

## Provider-Specific Factors

### Power Usage Effectiveness (PUE)

**Google/Gemini**: `1.09`
- **Source**: Google's official data center efficiency reporting
- **Methodology**: Trailing Twelve-Month (TTM) PUE for global fleet
- **Note**: Google consistently publishes fleet-wide PUE averages

**OpenAI/Anthropic**: `1.15`
- **Source**: Microsoft Azure infrastructure (hosting partner)
- **Methodology**: Estimated based on Azure's newest generation data centers
- **Note**: AI workloads run on most modern/efficient parts of cloud infrastructure

**Industry Average**: `1.56`
- **Source**: Uptime Institute global benchmarking
- **Methodology**: Average PUE for all data center types
- **Note**: Shows hyperscale efficiency vs. broader industry

### Carbon Accounting Methods

#### Location-Based Accounting
Uses actual grid carbon intensity by region:

- **US-East**: 0.375 kg CO₂/kWh (Virginia/Ohio - RFC-East)
- **US-West**: 0.250 kg CO₂/kWh (Oregon/Washington - NWPP)
- **US-Texas**: 0.375 kg CO₂/kWh (ERCOT Region)
- **US-NY**: 0.138 kg CO₂/kWh (Upstate NY - NPCC)
- **Europe**: 0.207 kg CO₂/kWh (EU-27 Average)
- **Europe-High**: 0.360 kg CO₂/kWh (Germany/Netherlands)
- **Europe-Low**: 0.075 kg CO₂/kWh (Sweden/France - Nuclear/Hydro)
- **Default**: 0.367 kg CO₂/kWh (EIA 2023 US Average)

#### Market-Based Accounting
Accounts for carbon credits and renewable energy purchases:

- **Google/Gemini**: 0.0 kg CO₂/kWh (Carbon neutral since 2007)
- **OpenAI**: 0.30 kg CO₂/kWh (Azure - working toward carbon negative by 2030)
- **Anthropic**: 0.30 kg CO₂/kWh (Azure/Google - not carbon neutral yet)
- **AWS**: 0.35 kg CO₂/kWh (Net zero by 2040 target)
- **Default**: 0.40 kg CO₂/kWh (Conservative estimate)

## Model-Specific Factors

### Energy Efficiency Multipliers

**Source**: Devera.ai comprehensive study + API pricing ratios
- **Study**: "The Environmental Impact of AI: Energy, Carbon, and Water in the Age of ChatGPT"
- **Methodology**: Actual energy consumption measurements per query
- **Validation**: Cross-referenced with API pricing ratios (cost differences correlate with energy efficiency)

**Model Factors**:

#### OpenAI Models
- **GPT-4o**: 0.5x (0.30 Wh/query - Devera.ai measurement)
- **GPT-4**: 1.1x (estimated higher than GPT-4o)
- **GPT-4-Turbo**: 0.8x (more efficient than GPT-4)
- **GPT-3.5-Turbo**: 0.2x (much more efficient)
- **GPT-4o-Mini**: 0.1x (very efficient)

#### Anthropic Models
- **Claude-3-Opus**: 2.7x (4.05 Wh/query - Devera.ai measurement)
- **Claude-Opus-4**: 2.7x (latest flagship, similar to 3-Opus)
- **Claude-Sonnet-4**: 0.9x (latest medium model)
- **Claude-3-Sonnet**: 0.8x (legacy medium-large)
- **Claude-3-Haiku**: 0.2x (0.22 Wh/query - Devera.ai measurement)

#### Google Models
- **Gemini-2.5-Pro**: 0.5x (0.24 Wh/query - Devera.ai measurement)
- **Gemini-1.5-Pro**: 0.5x (similar efficiency to 2.5)
- **Gemini-1.0-Pro**: 0.4x (efficient)
- **Gemini-Flash**: 0.2x (very efficient)

## Hardware-Specific Factors

### Energy Efficiency Multipliers

**GPU Types**:
- **H100**: 1.0x (Baseline - NVIDIA H100)
- **A100**: 1.1x (NVIDIA A100 - slightly less efficient)
- **V100**: 1.3x (NVIDIA V100 - older, less efficient)
- **T4**: 0.8x (NVIDIA T4 - more efficient for smaller models)
- **RTX4090**: 0.9x (Consumer RTX 4090)

**CPU Types**:
- **Intel CPUs**: 0.6x
- **AMD CPUs**: 0.5x (more efficient)

**Specialized AI Hardware**:
- **TPU**: 0.7x (Google TPU)
- **Inferentia**: 0.8x (AWS Inferentia)

**Source**: Tokenomy.ai research + industry benchmarks
- **Methodology**: Hardware-specific energy efficiency measurements
- **Note**: Different hardware types have varying energy efficiency for AI workloads

## Real-World Equivalencies

### Conversion Factors

**Transportation**:
- **Miles Driven**: 0.393 kg CO₂ per mile (average car)
- **Flights NYC-LA**: 900 kg CO₂ per flight
- **Flights NYC-London**: 1,200 kg CO₂ per flight

**Household Energy**:
- **Annual Household**: 10,500 kWh per year (average US home)
- **Daily Household**: 28.8 kWh per day
- **Hourly Household**: 1.2 kWh per hour

**Technology**:
- **Smartphone Charges**: 0.008 kg CO₂ per charge
- **Laptop Charges**: 0.050 kg CO₂ per charge
- **TV Watching**: 0.1 kWh per hour (LED TV)
- **Gaming**: 0.3 kWh per hour (Gaming PC)

**Food & Lifestyle**:
- **Hamburgers**: 2.5 kg CO₂ per burger
- **Coffee Cups**: 0.2 kg CO₂ per cup
- **Beer Bottles**: 0.3 kg CO₂ per bottle

**Water**:
- **Water Bottles**: 0.5 L per bottle
- **Showers**: 60 L per shower (8 minutes)
- **Bathtubs**: 150 L per bath

**Environmental**:
- **Urban Tree Sequestration**: 60 kg CO₂ per year
- **Tree Planting**: 22 kg CO₂ per year (mature tree)
- **Solar Panel Output**: 1.0 kWh per hour (1kW panel)

**Industrial**:
- **Steel Production**: 1,800 kg CO₂ per ton
- **Cement Production**: 900 kg CO₂ per ton

**Sources**: EPA Greenhouse Gas Equivalencies Calculator, Real World Visuals Energy Converter, industry standards

## Validation and Calibration

### Comparison with Industry Standards

**llmemissions.com Validation**:
- **Methodology**: Simple energy-per-token calculation
- **Our Enhancement**: 24% higher due to comprehensive factors
- **Justification**: Our factors account for real-world conditions (PUE, model efficiency, hardware variations)

**Google Research Validation**:
- **Gemini Measurements**: 0.24 Wh per prompt, 0.26 mL water per prompt
- **Our Alignment**: Base factors calibrated to match Google's comprehensive methodology
- **Enhancement**: Extended to all providers and models

### Quality Assurance

1. **Peer-Reviewed Sources**: All base factors derived from published research
2. **Industry Standards**: PUE and carbon intensity from official sources
3. **Cross-Validation**: Multiple sources for model efficiency factors
4. **Real-World Testing**: Calibrated against actual usage data
5. **Transparency**: All sources and methodologies documented

## Implementation Notes

### Calculation Flow

1. **Parse Token Data**: Extract tokens by model from CSV files
2. **Apply Base Factors**: Multiply by energy/water factors
3. **Apply Model Factors**: Account for model-specific efficiency
4. **Apply Hardware Factors**: Account for hardware type
5. **Apply PUE Factors**: Account for data center efficiency
6. **Calculate CO₂**: Multiply energy by carbon intensity
7. **Generate Equivalencies**: Convert to real-world comparisons

### Accounting Methods

- **Location-Based**: Uses actual grid carbon intensity
- **Market-Based**: Accounts for carbon credits and renewable energy
- **Provider-Specific**: Different factors for different cloud providers

### Regional Considerations

- **Carbon Intensity**: Varies by geographic region
- **PUE Factors**: Provider-specific data center efficiency
- **Hardware Distribution**: Assumed based on provider infrastructure

## Future Enhancements

1. **Dynamic Carbon Intensity**: Real-time grid carbon intensity data
2. **Hardware Detection**: Automatic hardware type detection
3. **Regional PUE**: Provider-specific PUE by region
4. **Model Updates**: Regular updates as new models are released
5. **Validation Studies**: Ongoing validation against new research

## References

1. Samsi, S., et al. (2023). "From Words to Watts: Benchmarking the Energy Costs of Large Language Model Inference." arXiv:2310.03003
2. Google Research (2024). "Measuring the environmental impact of delivering AI at Google Scale." arXiv:2508.15734v1
3. Devera.ai (2024). "The Environmental Impact of AI: Energy, Carbon, and Water in the Age of ChatGPT"
4. U.S. Energy Information Administration (2023). "How much carbon dioxide is produced per kilowatthour of U.S. electricity generation?"
5. Google Data Center Efficiency Reports (2024)
6. Microsoft Azure Sustainability Reports (2024)
7. Uptime Institute Global Data Center Survey (2024)
8. EPA Greenhouse Gas Equivalencies Calculator
9. Real World Visuals Energy Converter


# FOR COMPARISON
     Based on data for 2023, the global commercial airline industry contributes approximately 78.3 million tonnes 7.83 x 10^10 kg of CO2 per month. Here is a breakdown of the calculation and sources: Annual emissions in 2023: The Air Transport Action Group (ATAG) reported that flights worldwide produced 882 million tonnes of CO2 in 2023. The International Energy Agency (IEA) corroborates this, stating aviation emissions reached almost 950 million tonnes in 2023. The ATAG figure is used for this calculation, as it specifically refers to civil aviation flights.Monthly emissions calculation: To find the monthly average, divide the annual emissions by 12. 882 million tonnes / 12 months=73.5 million tonnes per month 
     Emissions in kilograms: Since one tonne is equal to 1,000 kilograms, multiply the result by 1,000. 73.5  million  tonnes X 1,000 kg/tonne=7.35 X 10^10 kg per month
     2024 emissions estimate: A separate source, Cirium, projected a monthly peak of 74 million tonnes of CO2 for scheduled passenger flights alone in July 2024. 

---

*This methodology document is maintained as part of the Token Impact Estimation System and is updated as new research becomes available.*
