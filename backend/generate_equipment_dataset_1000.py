import json
import random
from datetime import datetime, timedelta

# =========================
# CONFIG - Updated based on Excel sheet
# =========================
N = 100
BASE_OUTPUT_FILE = "Equipment_Failures_Realistic_100_with_5Whys.xlsx"

# Equipment types from Excel
equipment_types = [
    "Pump", "Motor", "Valve", "Heat Exchanger", "Boiler", 
    "Chiller", "Conveyor", "Compressor", "Fan", "Generator"
]

# Departments from Excel
departments = [
    "Maintenance", "Safety", "Production", "Engineering", 
    "Quality", "Operations"
]

# Severities from Excel (with additional Critical)
severities = ["Low", "Medium", "High", "Critical"]

# Issues from Excel
issues = [
    "Overheating of component leading to trip",
    "Control panel fault and PLC trip",
    "Abnormal vibration and noise detected",
    "Unexpected shutdown during operation",
    "Cooling system failure causing temp rise",
    "Seal/leakage detected causing fluid loss",
    "Gas/leak detected causing evacuation",
    "Bearing failure with smoke observed",
    "Belt slip and tear during operation",
    "Pressure surge and valve rupture"
]

# Root causes from Excel
root_causes = [
    "Sensor/calibration failure",
    "Incorrect installation/assembly",
    "Electrical supply fluctuation",
    "Inadequate lubrication",
    "Component fatigue/corrosion",
    "Bypass of safety interlock",
    "Human/operator error",
    "Contaminated fluid/particulate ingress",
    "Design flaw in component",
    "Lack of preventive maintenance"
]

# Sources from Excel
sources = [
    "Kaggle - Predictive Maintenance Datasets (public)",
    "OREDA reliability handbook/industry reports (OREDA)",
    "U.S. Chemical Safety Board (CSB) investigations",
    "NTSB / AP News industrial incident reports",
    "BIC Magazine / Industry case studies (compressor)",
    "Scientific literature on compressor/motor failures (ScienceDirect)"
]

# =========================
# WHY CHAINS - Updated based on Excel structure
# =========================
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

# Corrective actions mapping
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

# =========================
# DATASET GENERATION
# =========================
dataset = []

# Generate dates from 2023-01-01 to 2025-12-20
start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 12, 20)

for i in range(1, N + 1):
    equipment_id = f"EQ{i:04d}"
    equipment_type = random.choice(equipment_types)
    department = random.choice(departments)
    severity = random.choice(severities)
    issue = random.choice(issues)
    root_cause = random.choice(root_causes)
    
    # Get why analysis based on root cause
    why_analysis = WHY_CHAINS[root_cause]
    
    # Generate random date within range
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    date_reported = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
    
    # Get corrective action based on root cause
    corrective_action = CORRECTIVE_ACTIONS[root_cause]
    
    # Get source
    source = random.choice(sources)
    
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
        "Source": source
    })

# Save the dataset
with open(BASE_OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

print(f"✅ Dataset generated → {BASE_OUTPUT_FILE}")
print(f"Total records: {len(dataset)}")
print(f"Equipment types: {', '.join(sorted(set([d['Equipment_Type'] for d in dataset])))}")
print(f"Departments: {', '.join(sorted(set([d['Department'] for d in dataset])))}")
print(f"Severities: {', '.join(sorted(set([d['Severity'] for d in dataset])))}")

