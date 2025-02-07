from typing import Dict, Final

SEVERITY_COLORS: Final[Dict[str, str]] = {
    "CRITICAL": "#FF0000",    # Red
    "HIGH": "#FF4B4B",        # Light Red
    "MEDIUM": "#FFA500",      # Orange
    "LOW": "#FFFF00",         # Yellow
    "INFO": "#0066CC",        # Blue
    "DEFAULT": "#666666"      # Gray
}

EVENT_TYPES: Final[Dict[str, str]] = {
    "LOGIN": "Login",
    "USB": "USB Device",
    "NETWORK": "Network",
    "FILE": "File",
    "PROCESS": "Process",
    "SYSTEM": "System"
}

# Auto-refresh settings
REFRESH_INTERVALS: Final[Dict[str, int]] = {
    "FAST": 15,     # Seconds
    "NORMAL": 30,
    "SLOW": 60
}

# Analysis constants
ANALYSIS_CONSTANTS: Final[Dict[str, float]] = {
    "ANOMALY_THRESHOLD": 0.85,  # Anomaly Threshold
    "MAX_DATA_POINTS": 1000     # Maximum Data Points
}

# General-purpose colors
COLOR_PALETTE: Final[Dict[str, str]] = {
    "PRIMARY": "#306998",    # Python Blue
    "SECONDARY": "#FFD43B",  # Python Yellow
    "SUCCESS": "#4CAF50",    # Green
    "WARNING": "#FFC107",    # Warning Yellow
    "DANGER": "#DC3545"      # Danger Red
}

# Chart settings
CHART_CONFIG: Final[Dict[str, str]] = {
    "BG_COLOR": "#FFFFFF",
    "FONT": "Arial",
    "AXIS_COLOR": "#666666"
}
