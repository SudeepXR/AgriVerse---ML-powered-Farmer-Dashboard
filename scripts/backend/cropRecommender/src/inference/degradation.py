from enum import Enum

class DegradationLevel(str, Enum):
    """
    Formal Degradation Ladder for the Inference Service.
    
    This Enum defines the FINITE, EXPLICIT fallback states the system can enter
    when user inputs are incomplete or reference data is missing.
    
    Design Canon:
    - No implicit fallbacks. Every state must map to one of these levels.
    - Lower levels imply wider uncertainty and reduced confidence.
    """
    
    EXACT_REGION = "exact_region"
    """
    Ideal State.
    - Reference Data: District-specific profiles (Soil & Crops).
    - Missing: None.
    - Assumptions: User input matches historical district patterns.
    - Safety: Highest precision.
    """
    
    STATE_FALLBACK = "state_fallback"
    """
    Degraded State (Level 1).
    - Trigger: District unknown or unmapped.
    - Reference Data: State-level aggregated averages.
    - Missing: Local micro-climate and district soil nuances.
    - Assumptions: State averages are a 'good enough' proxy for unknown districts.
    - Safety: Reduces precision but prevents denial of service. confidence is capped at Medium.
    """
    
    NATIONAL_FALLBACK = "national_fallback"
    """
    Degraded State (Level 2).
    - Trigger: Region completely unknown or State lookup failed.
    - Reference Data: National/Global averages.
    - Missing: All regional context.
    - Assumptions: Crops feasible nationally are technically possible, though suitability is unknown.
    - Safety: Failsafe. Use only with explicit warnings and Low confidence.
    """

    @classmethod
    def from_string(cls, value: str):
        """Safe converter for legacy string values."""
        try:
            return cls(value)
        except ValueError:
            return cls.NATIONAL_FALLBACK # Fail-safe default

def get_confidence_cap(level: DegradationLevel) -> str:
    """
    Enforces Confidence Caps based on Degradation Level.
    
    Rules:
    - EXACT_REGION: No Cap (Can be High).
    - STATE_FALLBACK: Capped at Medium.
    - NATIONAL_FALLBACK: Forced Low.
    """
    if level == DegradationLevel.EXACT_REGION:
        return "High"
    elif level == DegradationLevel.STATE_FALLBACK:
        return "Medium"
    else:
        return "Low"

def get_coverage_meta(level: DegradationLevel) -> str:
    """Maps internal degradation level to external metadata schema."""
    if level == DegradationLevel.EXACT_REGION:
        return "high"
    elif level == DegradationLevel.STATE_FALLBACK:
        return "medium"
    else:
        return "low"
