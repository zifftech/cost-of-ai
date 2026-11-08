# Local calculation engine based on reverse-engineered tokenomy.ai formulas

from typing import Dict, Optional
from ..core.data_models import MonthlyAggregation, ImpactMetrics


class LocalCalculator:
    """
    Local calculation engine based on Google's comprehensive AI environmental impact methodology
    
    Based on: "Measuring the environmental impact of delivering AI at Google Scale" 
    (https://arxiv.org/html/2508.15734v1)
    
    Google's methodology includes:
    - Active AI accelerator power
    - Host system energy (CPU, DRAM) 
    - Idle machine capacity (provisioned for reliability/latency)
    - Data center energy overhead (PUE)
    
    Key findings:
    - Median Gemini prompt: 0.24 Wh energy, 0.26 mL water
    - 33x energy reduction, 44x carbon reduction over 1 year
    - Uses less energy than 9 seconds of TV watching
    """
    
    def __init__(self):
        # Base calculation factors based on MIT "From Words to Watts" paper methodology
        # https://arxiv.org/abs/2310.03003 - Benchmarking LLM inference energy costs
        # Calibrated to match llmemissions.com results (0.00000106 kWh/token)
        self.BASE_ENERGY_FACTOR = 0.00000106  # kWh per token (MIT paper methodology)
        self.BASE_CO2_FACTOR = 0.00000039    # kg CO2 per token (EIA 2023: 0.367 kg CO2/kWh)
        self.BASE_WATER_FACTOR = 0.0000026   # L water per token (Google: 0.26 mL per prompt = 0.0026 mL per token)
        
        # PUE (Power Usage Effectiveness) factors by provider
        # Based on your research data
        self.PUE_FACTORS = {
            "google": 1.09,      # Google's fleet-wide average
            "gemini": 1.09,       # Gemini uses Google's infrastructure
            "openai": 1.15,       # Estimated (uses Azure)
            "anthropic": 1.15,    # Estimated (uses Azure/Google)
            "default": 1.56       # Industry average
        }
        
        # Regional carbon intensity (kg CO2 per kWh) - location-based
        # Based on EIA 2023 data: https://www.eia.gov/tools/faqs/faq.php?id=74&t=11
        self.CARBON_INTENSITY = {
            "us-east": 0.375,    # Virginia/Ohio (RFC-East) - 300-450 gCO2/kWh avg
            "us-west": 0.250,    # Oregon/Washington (NWPP) - 200-300 gCO2/kWh avg
            "us-texas": 0.375,   # ERCOT Region - 350-400 gCO2/kWh avg
            "us-ny": 0.138,      # Upstate NY (NPCC) - 125-150 gCO2/kWh avg
            "europe": 0.207,     # EU-27 Average
            "europe-high": 0.360, # Germany/Netherlands - 320-400 gCO2/kWh avg
            "europe-low": 0.075,  # Sweden/France (Nuclear/Hydro) - 50-100 gCO2/kWh avg
            "default": 0.367     # EIA 2023 US average (0.81 lbs/kWh = 0.367 kg/kWh)
        }
        
        # Market-based carbon intensity (with carbon credits/renewable energy)
        # Only Google is currently carbon neutral; others are working toward it
        # Updated based on comparison with LLM Emissions Calculator (0.327 kg CO2/kWh)
        self.MARKET_CARBON_INTENSITY = {
            "google": 0.0,       # Carbon neutral since 2007
            "gemini": 0.0,       # Gemini uses Google's carbon-neutral infrastructure
            "openai": 0.30,      # Uses Azure - Microsoft claims carbon negative by 2030, but not yet
            "anthropic": 0.30,   # Uses Azure/Google - not carbon neutral yet, closer to location-based
            "microsoft": 0.30,   # Claims carbon negative by 2030, but not yet achieved
            "aws": 0.35,         # Claims net zero by 2040, but not yet achieved
            "default": 0.40       # Conservative estimate for providers without carbon commitments
        }
        
        # Hardware-specific multipliers based on tokenomy.ai research
        # Different hardware types have varying energy efficiency
        self.HARDWARE_FACTORS = {
            # GPU Types (most common for AI inference)
            "h100": {"energy": 1.0, "co2": 1.0, "water": 1.0},  # Baseline - NVIDIA H100
            "a100": {"energy": 1.1, "co2": 1.1, "water": 1.1},   # NVIDIA A100 (slightly less efficient)
            "v100": {"energy": 1.3, "co2": 1.3, "water": 1.3},  # NVIDIA V100 (older, less efficient)
            "t4": {"energy": 0.8, "co2": 0.8, "water": 0.8},    # NVIDIA T4 (more efficient for smaller models)
            "rtx4090": {"energy": 0.9, "co2": 0.9, "water": 0.9}, # Consumer RTX 4090
            
            # CPU Types (less common for large models)
            "cpu_intel": {"energy": 0.6, "co2": 0.6, "water": 0.6},  # Intel CPUs
            "cpu_amd": {"energy": 0.5, "co2": 0.5, "water": 0.5},    # AMD CPUs (more efficient)
            
            # Specialized AI Hardware
            "tpu": {"energy": 0.7, "co2": 0.7, "water": 0.7},       # Google TPU
            "inferentia": {"energy": 0.8, "co2": 0.8, "water": 0.8}, # AWS Inferentia
            
            # Generic fallbacks
            "gpu_generic": {"energy": 1.0, "co2": 1.0, "water": 1.0},
            "cpu_generic": {"energy": 0.6, "co2": 0.6, "water": 0.6},
        }
        
        # Model-specific multipliers based on research + API pricing as an energy proxy.
        # Baseline: 1.0x ≈ mid/large frontier-class inference.
        # Updated Nov 2026 for ZD stack: Anthropic + Cursor (Claude-routed) primary, Gemini tertiary.
        # Longer / more specific keys first so substring matching prefers them.
        self.MODEL_FACTORS = {
            # --- Anthropic (current, Nov 2026) ---
            "claude-fable-5-1": {"energy": 3.5, "co2": 3.5, "water": 3.5},  # highest-tier reasoning
            "claude-opus-5-5": {"energy": 2.7, "co2": 2.7, "water": 2.7},    # flagship agentic
            "claude-sonnet-5-5": {"energy": 1.0, "co2": 1.0, "water": 1.0},  # default Cursor/Claude workhorse
            "claude-haiku-5-5": {"energy": 0.15, "co2": 0.15, "water": 0.15},

            # Anthropic 4.x / 4.5 / 4.6 (still appear in usage CSVs)
            "claude-opus-4-6": {"energy": 2.7, "co2": 2.7, "water": 2.7},
            "claude-sonnet-4-6": {"energy": 0.95, "co2": 0.95, "water": 0.95},
            "claude-opus-4-5": {"energy": 2.7, "co2": 2.7, "water": 2.7},
            "claude-sonnet-4-5": {"energy": 0.9, "co2": 0.9, "water": 0.9},
            "claude-haiku-4-5": {"energy": 0.2, "co2": 0.2, "water": 0.2},
            "claude-opus-4": {"energy": 2.7, "co2": 2.7, "water": 2.7},
            "claude-sonnet-4": {"energy": 0.9, "co2": 0.9, "water": 0.9},

            # Anthropic 3.x (Devera.ai measurements; legacy CSV mapping)
            "claude-3-opus": {"energy": 2.7, "co2": 2.7, "water": 2.7},   # 4.05 Wh/query
            "claude-3-sonnet": {"energy": 0.8, "co2": 0.8, "water": 0.8},
            "claude-3-haiku": {"energy": 0.2, "co2": 0.2, "water": 0.2},  # 0.22 Wh/query

            # --- Google Gemini (current 3.x + retained 2.5) ---
            "gemini-3.1-pro-preview": {"energy": 0.6, "co2": 0.6, "water": 0.6},
            "gemini-3.1-pro": {"energy": 0.6, "co2": 0.6, "water": 0.6},
            "gemini-3.8-flash": {"energy": 0.3, "co2": 0.3, "water": 0.3},
            "gemini-3.6-flash": {"energy": 0.3, "co2": 0.3, "water": 0.3},
            "gemini-3-flash-preview": {"energy": 0.3, "co2": 0.3, "water": 0.3},
            "gemini-3-flash": {"energy": 0.3, "co2": 0.3, "water": 0.3},
            "gemini-3.5-flash-lite": {"energy": 0.15, "co2": 0.15, "water": 0.15},
            "gemini-3.1-flash-lite": {"energy": 0.15, "co2": 0.15, "water": 0.15},
            "gemini-2.5-pro": {"energy": 0.5, "co2": 0.5, "water": 0.5},  # 0.24 Wh/query (Devera.ai)
            "gemini-2.5-flash-lite": {"energy": 0.15, "co2": 0.15, "water": 0.15},
            "gemini-2.5-flash": {"energy": 0.2, "co2": 0.2, "water": 0.2},
            "gemini-1.5-pro": {"energy": 0.5, "co2": 0.5, "water": 0.5},
            "gemini-1.5-flash": {"energy": 0.2, "co2": 0.2, "water": 0.2},
            "gemini-1.0-pro": {"energy": 0.4, "co2": 0.4, "water": 0.4},
            "gemini-flash": {"energy": 0.2, "co2": 0.2, "water": 0.2},

            # --- OpenAI (secondary; pricing-proxy estimates) ---
            "gpt-6.1": {"energy": 1.2, "co2": 1.2, "water": 1.2},
            "gpt-6": {"energy": 1.1, "co2": 1.1, "water": 1.1},
            "gpt-5": {"energy": 1.0, "co2": 1.0, "water": 1.0},
            "gpt-4o": {"energy": 0.5, "co2": 0.5, "water": 0.5},  # 0.30 Wh/query (Devera.ai)
            "gpt-4-turbo": {"energy": 0.8, "co2": 0.8, "water": 0.8},
            "gpt-4": {"energy": 1.1, "co2": 1.1, "water": 1.1},
            "gpt-3.5-turbo": {"energy": 0.2, "co2": 0.2, "water": 0.2},
            "gpt-4o-mini": {"energy": 0.1, "co2": 0.1, "water": 0.1},

            # Generic size-based fallbacks
            "generic-small": {"energy": 0.3, "co2": 0.3, "water": 0.3},
            "generic-medium": {"energy": 0.6, "co2": 0.6, "water": 0.6},
            "generic-large": {"energy": 0.9, "co2": 0.9, "water": 0.9},
            "generic-very_large": {"energy": 1.2, "co2": 1.2, "water": 1.2},
        }
    
    def get_model_factors(self, model_name: str) -> Dict[str, float]:
        """Get calculation factors for a specific model"""
        model_lower = model_name.lower().strip()
        # Strip dated Anthropic suffixes: claude-sonnet-4-5-20250929 → claude-sonnet-4-5
        if model_lower.startswith("claude-") and len(model_lower) > 8 and model_lower[-8:].isdigit():
            model_lower = model_lower.rsplit("-", 1)[0]
        
        # Direct match first
        if model_lower in self.MODEL_FACTORS:
            return self.MODEL_FACTORS[model_lower]
        
        # Substring matching for model variants (longest keys first)
        for known_model, factors in sorted(
            self.MODEL_FACTORS.items(), key=lambda item: len(item[0]), reverse=True
        ):
            if known_model.startswith("generic-"):
                continue
            if known_model in model_lower or model_lower in known_model:
                return factors
        
        # Size-based fallback logic (aligned with dictionary factors)
        if any(keyword in model_lower for keyword in ["fable", "opus", "gpt-6", "gpt-5"]):
            return self.MODEL_FACTORS["generic-very_large"]
        elif any(keyword in model_lower for keyword in ["sonnet", "gpt-4", "gemini-3.1-pro", "gemini-2.5-pro", "gemini-1.5-pro"]):
            return self.MODEL_FACTORS["generic-large"]
        elif any(keyword in model_lower for keyword in ["haiku", "flash-lite", "mini", "nano", "lite"]):
            return self.MODEL_FACTORS["generic-small"]
        elif any(keyword in model_lower for keyword in ["flash", "gpt-3.5", "gemini"]):
            return self.MODEL_FACTORS["generic-medium"]
        
        # Default to medium
        return self.MODEL_FACTORS["generic-medium"]
    
    def get_hardware_factors(self, hardware_type: str = "h100") -> Dict[str, float]:
        """Get calculation factors for specific hardware type"""
        hardware_lower = hardware_type.lower()
        
        # Direct match first
        if hardware_lower in self.HARDWARE_FACTORS:
            return self.HARDWARE_FACTORS[hardware_lower]
        
        # Substring matching for hardware variants
        for known_hardware, factors in self.HARDWARE_FACTORS.items():
            if known_hardware in hardware_lower or hardware_lower in known_hardware:
                return factors
        
        # Generic fallback based on hardware type
        if any(keyword in hardware_lower for keyword in ['gpu', 'nvidia', 'amd', 'rtx', 'gtx']):
            return self.HARDWARE_FACTORS["gpu_generic"]
        elif any(keyword in hardware_lower for keyword in ['cpu', 'intel', 'amd', 'x86']):
            return self.HARDWARE_FACTORS["cpu_generic"]
        
        # Default to H100 (most common for AI inference)
        return self.HARDWARE_FACTORS["h100"]
    
    def _get_provider_hardware(self, provider) -> str:
        """Auto-detect likely hardware based on provider"""
        from ..core.data_models import Provider
        
        if provider == Provider.OPENAI:
            return "h100"  # OpenAI likely uses H100s for GPT models
        elif provider == Provider.ANTHROPIC:
            return "h100"  # Anthropic likely uses H100s via AWS
        elif provider == Provider.GEMINI:
            return "tpu"   # Google likely uses TPUs for Gemini models
        else:
            return "h100"  # Default to H100 for unknown providers
    
    def calculate_impact(self, aggregation: MonthlyAggregation, hardware_type: str = None) -> Optional[ImpactMetrics]:
        """
        Calculate environmental impact using local formulas
        
        Args:
            aggregation: MonthlyAggregation containing token data
            hardware_type: Hardware type (auto-detected by provider if None)
            
        Returns:
            ImpactMetrics object with calculated values
        """
        try:
            total_kwh = 0.0
            total_co2 = 0.0
            total_water = 0.0
            
            print(f"🌐 Starting local impact calculation for {aggregation.year}-{aggregation.month:02d}")
            
            # Auto-detect hardware based on provider if not specified
            if hardware_type is None:
                hardware_type = self._get_provider_hardware(aggregation.provider)
            
            # Get hardware-specific factors
            hardware_factors = self.get_hardware_factors(hardware_type)
            print(f"🔧 Hardware: {hardware_type} (energy={hardware_factors['energy']:.1f}x, co2={hardware_factors['co2']:.1f}x, water={hardware_factors['water']:.1f}x)")
            
            # Process each model in the aggregation
            for model, tokens in aggregation.model_tokens.items():
                try:
                    print(f"  📊 Processing {model}: {tokens:,} tokens")
                    
                    # Get model-specific factors
                    model_factors = self.get_model_factors(model)
                    print(f"  🎯 Model factors: energy={model_factors['energy']:.1f}x, co2={model_factors['co2']:.1f}x, water={model_factors['water']:.1f}x")
                    
                    # Calculate impact for this model (model × hardware factors)
                    model_kwh = tokens * self.BASE_ENERGY_FACTOR * model_factors["energy"] * hardware_factors["energy"]
                    model_co2 = tokens * self.BASE_CO2_FACTOR * model_factors["co2"] * hardware_factors["co2"]
                    model_water = tokens * self.BASE_WATER_FACTOR * model_factors["water"] * hardware_factors["water"]
                    
                    # Add to totals
                    total_kwh += model_kwh
                    total_co2 += model_co2
                    total_water += model_water
                    
                    print(f"  ✅ {model}: {model_kwh:.3f} kWh, {model_co2:.3f} kg CO2, {model_water:.3f} L water")
                    
                except Exception as e:
                    print(f"  ❌ Error processing {model}: {e}")
                    continue
            
            # Create final impact metrics
            metrics = ImpactMetrics(
                kwh=total_kwh,
                co2_kg=total_co2,
                water_liters=total_water
            )
            
            print(f"🎯 Total impact: {total_kwh:.3f} kWh, {total_co2:.3f} kg CO2, {total_water:.3f} L water")
            return metrics
            
        except Exception as e:
            print(f"❌ Failed to calculate impact: {e}")
            return None
    
    def calculate_impact_with_carbon_accounting(self, aggregation: MonthlyAggregation, 
                                              hardware_type: str = None,
                                              accounting_method: str = "location",
                                              region: str = "default") -> Optional[ImpactMetrics]:
        """
        Calculate environmental impact with carbon accounting options
        
        Args:
            aggregation: MonthlyAggregation containing token data
            hardware_type: Hardware type (auto-detected by provider if None)
            accounting_method: "location" (actual grid) or "market" (with carbon credits)
            region: Geographic region for carbon intensity
            
        Returns:
            ImpactMetrics object with calculated values
        """
        try:
            total_kwh = 0.0
            total_co2 = 0.0
            total_water = 0.0
            
            print(f"🌐 Starting carbon-aware impact calculation for {aggregation.year}-{aggregation.month:02d}")
            print(f"📊 Accounting method: {accounting_method}")
            print(f"🌍 Region: {region}")
            
            # Auto-detect hardware based on provider if not specified
            if hardware_type is None:
                hardware_type = self._get_provider_hardware(aggregation.provider)
            
            # Get hardware-specific factors
            hardware_factors = self.get_hardware_factors(hardware_type)
            print(f"🔧 Hardware: {hardware_type} (energy={hardware_factors['energy']:.1f}x, co2={hardware_factors['co2']:.1f}x, water={hardware_factors['water']:.1f}x)")
            
            # Get PUE factor based on provider
            provider_key = aggregation.provider.value.lower()
            pue = self.PUE_FACTORS.get(provider_key, self.PUE_FACTORS["default"])
            print(f"🏢 PUE factor: {pue:.2f}")
            
            # Get carbon intensity based on accounting method
            if accounting_method == "market":
                carbon_intensity = self.MARKET_CARBON_INTENSITY.get(provider_key, 0.0)
                print(f"🌱 Market-based carbon intensity: {carbon_intensity:.3f} kg CO2/kWh (with carbon credits)")
            else:
                carbon_intensity = self.CARBON_INTENSITY.get(region, self.CARBON_INTENSITY["default"])
                print(f"⚡ Location-based carbon intensity: {carbon_intensity:.3f} kg CO2/kWh")
            
            # Process each model in the aggregation
            for model, tokens in aggregation.model_tokens.items():
                try:
                    print(f"  📊 Processing {model}: {tokens:,} tokens")
                    
                    # Get model-specific factors
                    model_factors = self.get_model_factors(model)
                    print(f"  🎯 Model factors: energy={model_factors['energy']:.1f}x, co2={model_factors['co2']:.1f}x, water={model_factors['water']:.1f}x")
                    
                    # Calculate energy consumption (with PUE)
                    model_kwh = tokens * self.BASE_ENERGY_FACTOR * model_factors["energy"] * hardware_factors["energy"] * pue
                    
                    # Calculate CO2 based on accounting method
                    model_co2 = model_kwh * carbon_intensity
                    
                    # Calculate water consumption
                    model_water = tokens * self.BASE_WATER_FACTOR * model_factors["water"] * hardware_factors["water"]
                    
                    # Add to totals
                    total_kwh += model_kwh
                    total_co2 += model_co2
                    total_water += model_water
                    
                    print(f"  ✅ {model}: {model_kwh:.3f} kWh, {model_co2:.3f} kg CO2, {model_water:.3f} L water")
                    
                except Exception as e:
                    print(f"  ❌ Error processing {model}: {e}")
                    continue
            
            print(f"🎯 Total impact: {total_kwh:.3f} kWh, {total_co2:.3f} kg CO2, {total_water:.3f} L water")
            
            return ImpactMetrics(kwh=total_kwh, co2_kg=total_co2, water_liters=total_water)
            
        except Exception as e:
            print(f"❌ Failed to calculate impact: {e}")
            return None
    
    def validate_against_google_measurements(self, tokens: int = 100) -> Dict[str, float]:
        """
        Validate our calculations against Google's actual Gemini measurements
        
        Args:
            tokens: Number of tokens to test (default 100, typical prompt size)
            
        Returns:
            Dictionary with comparison metrics
        """
        # Google's actual measurements for Gemini
        google_energy_wh = 0.24  # Wh per prompt
        google_water_ml = 0.26   # mL per prompt
        
        # Our calculations for same token count
        our_energy_kwh = tokens * self.BASE_ENERGY_FACTOR
        our_energy_wh = our_energy_kwh * 1000
        our_water_liters = tokens * self.BASE_WATER_FACTOR
        our_water_ml = our_water_liters * 1000
        
        return {
            "tokens_tested": tokens,
            "google_energy_wh": google_energy_wh,
            "our_energy_wh": our_energy_wh,
            "energy_ratio": our_energy_wh / google_energy_wh,
            "google_water_ml": google_water_ml,
            "our_water_ml": our_water_ml,
            "water_ratio": our_water_ml / google_water_ml,
            "energy_match": abs(our_energy_wh - google_energy_wh) / google_energy_wh < 0.1,  # Within 10%
            "water_match": abs(our_water_ml - google_water_ml) / google_water_ml < 0.1
        }
    
    def validate_factors_against_pricing(self) -> Dict[str, Dict[str, float]]:
        """
        Validate model factors against API pricing ratios (Phase 3 recommendation)
        API cost differences are strong proxy for energy efficiency
        """
        # Approximate API pricing ratios (as of Nov 2026) — energy-proxy sanity check
        pricing_ratios = {
            "gpt-4": 1.0,
            "gpt-4o": 0.5,
            "gpt-4-turbo": 0.7,
            "gpt-3.5-turbo": 0.1,
            "gpt-4o-mini": 0.05,
            "gpt-6": 1.1,
            "claude-fable-5-1": 2.0,
            "claude-opus-5-5": 1.5,
            "claude-sonnet-5-5": 0.7,
            "claude-haiku-5-5": 0.1,
            "claude-3-opus": 1.5,
            "claude-opus-4": 1.5,
            "claude-sonnet-4": 0.6,
            "claude-3-haiku": 0.2,
            "gemini-3.1-pro": 0.5,
            "gemini-3.8-flash": 0.25,
            "gemini-2.5-pro": 0.4,
            "gemini-1.5-pro": 0.4,
        }
        
        validation_results = {}
        for model, price_ratio in pricing_ratios.items():
            if model in self.MODEL_FACTORS:
                energy_factor = self.MODEL_FACTORS[model]["energy"]
                # Expected: higher pricing should correlate with higher energy factors
                # Price ratio vs energy factor should be roughly proportional
                validation_results[model] = {
                    "price_ratio": price_ratio,
                    "energy_factor": energy_factor,
                    "ratio_alignment": price_ratio / energy_factor if energy_factor > 0 else 0,
                    "is_reasonable": 0.5 <= (price_ratio / energy_factor) <= 2.0 if energy_factor > 0 else False
                }
        
        return validation_results
