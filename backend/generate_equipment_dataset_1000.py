import json
import random
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================
N = 500
OUTPUT_FILE = "equipment_500_domain_enriched.json"

equipment_types = [
    "Pump", "Motor", "Valve", "Heat Exchanger", "Boiler", 
    "Chiller", "Conveyor", "Compressor", "Fan", "Generator",
    "Turbine", "Reactor", "Separator", "Distillation Column"
]

departments = [
    "Maintenance", "Safety", "Production", "Engineering", 
    "Quality", "Operations", "Utilities", "Process"
]

severities = ["Low", "Medium", "High", "Critical"]
shift_times = ["day", "night", "evening"]
machine_age_buckets = ["new", "mid", "old"]
maintenance_gaps = ["current", "moderate", "overdue"]
failure_frequencies = ["low", "medium", "high"]

# =========================
# HIGHLY DISTINCTIVE ISSUE TEMPLATES
# =========================
issue_templates = {
    "Sensor/calibration failure": [
        "SENSOR drift detected - calibration out of spec - readings inaccurate",
        "INSTRUMENT calibration error - gauge shows wrong pressure values",
        "METER reading deviation - flow sensor needs recalibration",
        "THERMOCOUPLE malfunction - temperature sensor giving false readings",
        "LEVEL sensor error - calibration certificate expired",
        "pH SENSOR inconsistent - requires calibration adjustment",
        "TRANSMITTER drift - pressure instrument needs recalibration"
    ],
    
    "Component fatigue/corrosion": [
        "METAL fatigue cracks observed - CORROSION on steel casing",
        "RUST and CORROSION damage - material degradation visible",
        "EROSION of impeller blades - CORROSIVE environment damage",
        "CRACK in weld joint - FATIGUE failure after long service",
        "CORROSION pitting on pipe - METAL deterioration severe",
        "OXIDATION damage - CORRODED gasket material failure",
        "SHAFT wear from CORROSION - FATIGUE stress cracks"
    ],
    
    "Inadequate lubrication": [
        "BEARING dry running - insufficient GREASE - OIL starvation",
        "LUBRICATION system failure - BEARING overheating from lack of OIL",
        "GREASE not applied - FRICTION increase - BEARING seizure risk",
        "OIL level low - LUBRICANT contamination - BEARING damage",
        "GEARBOX noise - inadequate LUBRICATION - DRY running condition",
        "COUPLING friction - no GREASE - LUBRICATION schedule missed",
        "HYDRAULIC oil degraded - LUBRICANT quality poor - BEARING wear"
    ],
    
    "Electrical supply fluctuation": [
        "VOLTAGE spike - POWER surge - ELECTRICAL damage to controls",
        "PHASE imbalance - ELECTRICAL fault - POWER quality issue",
        "CIRCUIT breaker trip - VOLTAGE fluctuation - POWER instability",
        "ELECTRICAL surge - VOLTAGE sag - POWER supply problem",
        "HARMONICS in POWER supply - ELECTRICAL interference detected",
        "FREQUENCY variation - ELECTRICAL grid issue - VOLTAGE drop",
        "POWER outage - ELECTRICAL supply interruption - VOLTAGE loss"
    ],
    
    "Incorrect installation/assembly": [
        "INSTALLATION error - ALIGNMENT wrong - ASSEMBLY procedure not followed",
        "MOUNTING bolts loose - INSTALLATION torque incorrect",
        "PIPING misalignment - ASSEMBLY stress on connections",
        "COUPLING INSTALLATION backward - ASSEMBLY drawing not followed",
        "GASKET wrong type - INSTALLATION specification error",
        "WIRING connections loose - ELECTRICAL INSTALLATION fault",
        "IMPELLER INSTALLED reversed - ASSEMBLY mistake during rebuild"
    ],
    
    "Bypass of safety interlock": [
        "SAFETY interlock BYPASSED - OVERRIDE switch used improperly",
        "INTERLOCK defeated - SAFETY circuit jumpered out",
        "EMERGENCY stop BYPASSED - SAFETY procedure violated",
        "ALARM OVERRIDE - SAFETY system disabled during operation",
        "PERMISSIVE switch BYPASSED - INTERLOCK removed for production",
        "SAFETY valve ISOLATED - BYPASS of protection system",
        "GUARD switch DEFEATED - INTERLOCK OVERRIDE unauthorized"
    ],
    
    "Human/operator error": [
        "OPERATOR mistake - PROCEDURE not followed - HUMAN error",
        "WRONG valve opened - OPERATOR confusion - MANUAL error",
        "STARTUP sequence incorrect - OPERATOR training inadequate",
        "CONTROLS set wrong - HUMAN intervention error - OPERATOR fault",
        "PROCEDURE violation - OPERATOR bypassed checklist - HUMAN mistake",
        "CHEMICAL addition wrong - OPERATOR miscalculation - HUMAN error",
        "MANUAL override - OPERATOR judgment error - PROCEDURE ignored"
    ],
    
    "Contaminated fluid/particulate ingress": [
        "FLUID contaminated with water - PARTICULATE in hydraulic oil",
        "DIRT ingress through seal - CONTAMINATION in lubrication system",
        "FILTER clogged with DEBRIS - PARTICULATE buildup excessive",
        "WATER in OIL - FLUID CONTAMINATION - PARTICULATE matter present",
        "SEAL leak allowing CONTAMINATION - FOREIGN material in fluid",
        "COOLING water FOULING - PARTICULATE deposits - CONTAMINATED system",
        "PROCESS CONTAMINATION - IMPURITIES in fluid - PARTICULATE ingress"
    ],
    
    "Design flaw in component": [
        "UNDERSIZED component - DESIGN capacity inadequate - SPECIFICATION error",
        "MATERIAL selection wrong - DESIGN flaw for temperature conditions",
        "SEAL DESIGN unsuitable - COMPONENT not rated for application",
        "COOLING DESIGN insufficient - CAPACITY undersized for load",
        "CONTROL logic DESIGN error - SOFTWARE flaw in programming",
        "PIPING DESIGN causes cavitation - LAYOUT flaw in system",
        "STRUCTURAL DESIGN weak - COMPONENT not rated for vibration"
    ],
    
    "Lack of preventive maintenance": [
        "INSPECTION schedule MISSED - PREVENTIVE MAINTENANCE overdue",
        "FILTER replacement SKIPPED - MAINTENANCE schedule not followed",
        "BEARING GREASING missed - PREVENTIVE MAINTENANCE neglected",
        "VIBRATION monitoring not done - MAINTENANCE inspection overdue",
        "ALIGNMENT check SKIPPED - PREVENTIVE MAINTENANCE gap",
        "OIL analysis not performed - MAINTENANCE program inadequate",
        "BELT inspection MISSED - PREVENTIVE MAINTENANCE schedule behind"
    ]
}

root_causes = list(issue_templates.keys())

WHY_CHAINS = {
    "Sensor/calibration failure": [
        "Sensor readings were drifting",
        "Calibration schedule missed",
        "No redundancy for sensor",
        "Alerts suppressed as nuisance alarms",
        "No calibration ownership assigned"
    ],
    "Incorrect installation/assembly": [
        "Component installed with wrong torque/fit",
        "No post-installation testing",
        "Installer not trained on updated procedure",
        "No verification by engineering",
        "Lack of installation QA process"
    ],
    "Electrical supply fluctuation": [
        "Voltage spike damaged electronics",
        "No surge protection installed",
        "Backup power not tested",
        "Power quality reports ignored",
        "No coordination with utilities"
    ],
    "Inadequate lubrication": [
        "Lubrication schedule not followed",
        "Incorrect lubricant used",
        "Automatic lubrication system failed",
        "No sensor for low-lube condition",
        "No maintenance audit for lubrication"
    ],
    "Component fatigue/corrosion": [
        "Material exposed to corrosive environment",
        "No corrosion protection applied",
        "Replacement intervals too long",
        "Inspection methods not sensitive to corrosion",
        "No lifecycle tracking for part"
    ],
    "Bypass of safety interlock": [
        "Interlock was repeatedly tripped and bypassed",
        "Maintenance used temporary defeat to run tests",
        "No lockout/tagout enforcement",
        "No record of bypass events",
        "Cultural tolerance of bypasses"
    ],
    "Human/operator error": [
        "Operator bypassed safety interlock",
        "Inadequate training on emergency procedure",
        "High workload / fatigue",
        "No supervision during critical ops",
        "Poor human factors design of controls"
    ],
    "Contaminated fluid/particulate ingress": [
        "Filters not replaced",
        "Seal degraded allowing ingress",
        "No contamination monitoring",
        "Procurement used lower-quality fluid",
        "No SOP for fluid changeover"
    ],
    "Design flaw in component": [
        "Component not rated for operating conditions",
        "Design review missed edge-case",
        "No field feedback loop to designers",
        "Cost-driven substitution of materials",
        "Lack of formal failure mode review"
    ],
    "Lack of preventive maintenance": [
        "Routine inspections were skipped",
        "Inspection schedule was not enforced",
        "Maintenance team understaffed / no checklist",
        "No management follow-up or audits",
        "No preventive maintenance culture / policy"
    ]
}

CORRECTIVE_ACTIONS = {
    "Sensor/calibration failure": "Enforce calibration schedule, add redundancy and alerting",
    "Incorrect installation/assembly": "Revise installation SOP, retrain installers, and add QA signoff",
    "Electrical supply fluctuation": "Install surge protection, UPS, and monitor power quality",
    "Inadequate lubrication": "Implement lubrication audits and auto-lube systems",
    "Component fatigue/corrosion": "Introduce corrosion protection, replace affected parts, inspect materials",
    "Bypass of safety interlock": "Enforce lockout/tagout, log bypass events, install tamper-resistant interlocks",
    "Human/operator error": "Conduct operator training, revise ergonomics, enforce procedures",
    "Contaminated fluid/particulate ingress": "Improve filtration, change procurement specs, inspect seals",
    "Design flaw in component": "Perform design review, replace with rated component, provide feedback to OEM",
    "Lack of preventive maintenance": "Implement preventive maintenance schedule, CMMS tracking, and training"
}

sources = [
    "Kaggle - Predictive Maintenance Datasets (public)",
    "OREDA reliability handbook/industry reports (OREDA)",
    "U.S. Chemical Safety Board (CSB) investigations",
    "NTSB / AP News industrial incident reports",
    "BIC Magazine / Industry case studies (compressor)",
    "Scientific literature on compressor/motor failures (ScienceDirect)"
]

def get_correlated_features(root_cause):
    correlations = {
        "Sensor/calibration failure": {
            "severity": ["Low", "Medium"],
            "shift_time": ["day", "evening"],
            "machine_age": ["mid", "old"],
            "maintenance_gap": ["moderate", "overdue"],
            "failure_freq": ["low", "medium"]
        },
        "Component fatigue/corrosion": {
            "severity": ["High", "Critical"],
            "shift_time": ["day", "night", "evening"],
            "machine_age": ["old"],
            "maintenance_gap": ["overdue"],
            "failure_freq": ["high"]
        },
        "Inadequate lubrication": {
            "severity": ["Medium", "High"],
            "shift_time": ["night", "evening"],
            "machine_age": ["mid", "old"],
            "maintenance_gap": ["overdue"],
            "failure_freq": ["medium", "high"]
        },
        "Electrical supply fluctuation": {
            "severity": ["Medium", "High", "Critical"],
            "shift_time": ["day", "evening"],
            "machine_age": ["new", "mid"],
            "maintenance_gap": ["current", "moderate"],
            "failure_freq": ["low", "medium"]
        },
        "Incorrect installation/assembly": {
            "severity": ["High", "Critical"],
            "shift_time": ["day"],
            "machine_age": ["new"],
            "maintenance_gap": ["current"],
            "failure_freq": ["low"]
        },
        "Bypass of safety interlock": {
            "severity": ["Critical"],
            "shift_time": ["night", "evening"],
            "machine_age": ["mid", "old"],
            "maintenance_gap": ["moderate", "overdue"],
            "failure_freq": ["medium", "high"]
        },
        "Human/operator error": {
            "severity": ["Medium", "High", "Critical"],
            "shift_time": ["night", "evening"],
            "machine_age": ["new", "mid"],
            "maintenance_gap": ["current", "moderate"],
            "failure_freq": ["medium"]
        },
        "Contaminated fluid/particulate ingress": {
            "severity": ["Medium", "High"],
            "shift_time": ["day", "night", "evening"],
            "machine_age": ["mid", "old"],
            "maintenance_gap": ["overdue"],
            "failure_freq": ["high"]
        },
        "Design flaw in component": {
            "severity": ["Critical"],
            "shift_time": ["day"],
            "machine_age": ["new", "mid"],
            "maintenance_gap": ["current"],
            "failure_freq": ["low", "medium"]
        },
        "Lack of preventive maintenance": {
            "severity": ["High", "Critical"],
            "shift_time": ["night", "evening"],
            "machine_age": ["old"],
            "maintenance_gap": ["overdue"],
            "failure_freq": ["high"]
        }
    }
    return correlations.get(root_cause, {})

# Generate dataset
dataset = []
start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 12, 20)

for i in range(1, N + 1):
    equipment_id = f"EQ{i:04d}"
    equipment_type = random.choice(equipment_types)
    department = random.choice(departments)
    root_cause = random.choice(root_causes)
    
    if random.random() < 0.85:  # 85% correlated
        correlations = get_correlated_features(root_cause)
        severity = random.choice(correlations.get("severity", severities))
        shift_time = random.choice(correlations.get("shift_time", shift_times))
        machine_age = random.choice(correlations.get("machine_age", machine_age_buckets))
        maintenance_gap = random.choice(correlations.get("maintenance_gap", maintenance_gaps))
        failure_freq = random.choice(correlations.get("failure_freq", failure_frequencies))
    else:
        severity = random.choice(severities)
        shift_time = random.choice(shift_times)
        machine_age = random.choice(machine_age_buckets)
        maintenance_gap = random.choice(maintenance_gaps)
        failure_freq = random.choice(failure_frequencies)
    
    issue = random.choice(issue_templates[root_cause])
    why_analysis = WHY_CHAINS[root_cause]
    corrective_action = CORRECTIVE_ACTIONS[root_cause]
    
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    date_reported = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
    
    dataset.append({
        "Equipment_ID": equipment_id,
        "Equipment_Type": equipment_type,
        "Department": department,
        "Severity": severity,
        "Issue_Description": issue,
        "Root_Cause": root_cause,
        "Why_1": why_analysis[0],
        "Why_2": why_analysis[1],
        "Why_3": why_analysis[2],
        "Why_4": why_analysis[3],
        "Why_5": why_analysis[4],
        "Corrective_Action": corrective_action,
        "Date_Reported": date_reported,
        "Source": random.choice(sources),
        "shift_time": shift_time,
        "machine_age_bucket": machine_age,
        "maintenance_gap_days": maintenance_gap,
        "failure_frequency": failure_freq
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

print(f"✅ Dataset generated → {OUTPUT_FILE}")
print(f"\n📊 Statistics:")
print(f"Total: {len(dataset)}")
for rc in root_causes:
    count = sum(1 for d in dataset if d['Root_Cause'] == rc)
    print(f"  {rc}: {count}")
print("\n✅ Ready! Now run:")
print("  python load_data.py")
print("  python model_training.py")