"""
Domain constants for synthetic vehicle repair record generation.

Why this exists:
- Separates configuration from logic (single responsibility principle)
- Easy to tune distributions without touching the generator
- Mirrors how real fleet data teams maintain reference data
"""
from typing import Dict, List, Tuple

VEHICLE_MODELS: List[str] = [
    "Model S", "Model 3", "Model X", "Model Y", "Cybertruck", "Semi"
]

MODEL_WEIGHTS: List[int] = [15, 35, 10, 30, 5, 5]

REGIONS: List[str] = [
    "NA-West", "NA-East", "NA-Central", "EMEA-West", "EMEA-East"
]

COMPONENTS: List[str] = [
    "Battery Pack", "Drive Unit", "Suspension", "Brakes",
    "HVAC System", "Autopilot Sensors", "Charging Port",
    "Thermal Management", "Power Electronics", "Body & Trim"
]

FAILURE_DESCRIPTIONS: Dict[str, List[str]] = {
    "Battery Pack": [
        "Reduced range after full charge",
        "Battery management system fault code B1234",
        "Cell degradation detected in module 3",
        "Thermal runaway warning triggered during fast charge",
        "Unexpected voltage drop under load",
    ],
    "Drive Unit": [
        "Grinding noise from front drive unit at low speed",
        "Vibration felt during acceleration above 60mph",
        "Drive unit overheating fault during highway driving",
        "Loss of regenerative braking intermittently",
        "Clicking sound from rear motor on cold starts",
    ],
    "Suspension": [
        "Clunking noise from front left control arm",
        "Air suspension compressor failure",
        "Uneven tire wear indicating alignment drift",
        "Rattling from rear suspension over bumps",
        "Height sensor fault causing ride height error",
    ],
    "Brakes": [
        "Brake pedal pulsation at highway speeds",
        "Squealing from rear calipers in wet conditions",
        "Brake fluid leak at left rear caliper",
        "ABS fault code triggered on gravel surface",
        "Premature rotor wear on front axle",
    ],
    "HVAC System": [
        "AC compressor failure in hot weather",
        "Cabin heating insufficient below 20F",
        "Blower motor noise at high fan speed",
        "Refrigerant leak detected by pressure sensor",
        "Temperature inconsistency between driver and passenger zones",
    ],
    "Autopilot Sensors": [
        "Radar sensor misalignment after minor collision",
        "Camera feed dropout on driver assist display",
        "Ultrasonic sensor false positive in parking mode",
        "Lane departure warnings triggering incorrectly",
        "Forward collision warning delay reported by driver",
    ],
    "Charging Port": [
        "Charging port door not opening via app command",
        "Supercharger connection drops mid-session",
        "Charge rate limited to 50kW instead of expected 250kW",
        "Charging port latch stuck in locked position",
        "CCS adapter compatibility error on third-party charger",
    ],
    "Thermal Management": [
        "Coolant leak detected near front motor inlet",
        "Thermal management pump failure code TM-009",
        "Overheating warning during back-to-back DC fast charges",
        "Coolant temperature sensor fault affecting range estimate",
        "Heat pump efficiency degradation in sub-zero conditions",
    ],
    "Power Electronics": [
        "DC-DC converter fault causing 12V battery drain",
        "Onboard charger failure after firmware OTA update",
        "Inverter fault code PE-112 during high load acceleration",
        "HV interlock fault preventing vehicle startup",
        "Power distribution unit fault detected in BMS log",
    ],
    "Body & Trim": [
        "Door seal water ingress reported after heavy rain",
        "Trunk lid misalignment causing wind noise at speed",
        "Paint delamination on hood near front camera",
        "Window regulator failure on driver side",
        "Frunk latch not engaging on first press",
    ],
}

REPAIR_COST_RANGES_USD: Dict[str, Tuple[int, int]] = {
    "Battery Pack": (800, 8000),
    "Drive Unit": (400, 5000),
    "Suspension": (200, 2000),
    "Brakes": (150, 1200),
    "HVAC System": (300, 2500),
    "Autopilot Sensors": (500, 3500),
    "Charging Port": (100, 1500),
    "Thermal Management": (250, 3000),
    "Power Electronics": (600, 6000),
    "Body & Trim": (100, 1800),
}

COMPONENT_FAILURE_WEIGHTS: List[int] = [15, 8, 12, 18, 10, 7, 11, 6, 5, 8]
VEHICLE_YEARS: List[int] = [2020, 2021, 2022, 2023, 2024]
YEAR_WEIGHTS: List[int] = [5, 15, 25, 30, 25]
VIN_CHARSET: str = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
WARRANTY_CLAIM_PROBABILITY: float = 0.45
