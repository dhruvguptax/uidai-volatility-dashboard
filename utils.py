"""
utils.py

Shared utility functions and constants for the
UIDAI Demographic Volatility Monitoring Platform.

Purpose:
- Keep policy labels clean and non-alarmist
- Centralise geographic coordinates
- Improve readability and maintainability
"""


def classify_volatility(score):
    """
    Convert a numeric volatility score into
    an interpretable administrative category.
    """
    if score < 0.2:
        return "Low Volatility"
    elif score < 0.5:
        return "Moderate Volatility"
    else:
        return "High Volatility"



STATE_COORDS = {
    "Andhra Pradesh": (15.91, 79.74),
    "Assam": (26.20, 92.94),
    "Bihar": (25.09, 85.31),
    "Chhattisgarh": (21.27, 81.86),
    "Delhi": (28.70, 77.10),
    "Gujarat": (22.25, 71.19),
    "Haryana": (29.06, 76.08),
    "Karnataka": (15.32, 75.71),
    "Kerala": (10.85, 76.27),
    "Madhya Pradesh": (22.97, 78.65),
    "Maharashtra": (19.75, 75.71),
    "Odisha": (20.95, 85.10),
    "Punjab": (31.14, 75.34),
    "Rajasthan": (27.02, 74.22),
    "Tamil Nadu": (11.12, 78.66),
    "Telangana": (18.11, 79.01),
    "Uttar Pradesh": (26.85, 80.91),
    "West Bengal": (22.99, 87.85)
}

-
def get_state_coords(state_name):
    """
    Safely return (lat, lon) for a state.
    Prevents app crashes if a state is missing.
    """
    return STATE_COORDS.get(state_name, (None, None))



INTRO_TEXT = """
UIDAI manages Aadhaar enrolment and demographic update infrastructure
across India. Demand for updates varies due to migration, seasonality,
and lifecycle transitions, often creating unexpected operational stress.
"""

VOLATILITY_EXPLANATION = """
Demographic Volatility measures how unstable update activity is over time.

• Low Volatility → predictable demand  
• Moderate Volatility → seasonal or transitional patterns  
• High Volatility → sudden spikes indicating demographic churn
"""

USAGE_GUIDE = """
High Volatility regions may require temporary staffing or enrolment kits.
Moderate Volatility regions should be monitored for escalation.
Trend increases indicate the need for proactive resource planning.
"""
