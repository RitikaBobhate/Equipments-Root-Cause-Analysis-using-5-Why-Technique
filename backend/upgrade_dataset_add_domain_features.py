import json
import random

INPUT_FILE = "Equipment_Failures_Realistic_100_with_5Whys.json"
OUTPUT_FILE = "equipment_100_domain_enriched.json"

shift_times = ["day", "night"]
machine_age_buckets = ["new", "mid", "old"]
maintenance_gaps = ["recent", "moderate", "overdue"]
failure_frequencies = ["low", "medium", "high"]

def infer_domain_features(record):
    root = record.get("root_cause", "Unknown")

    shift = (
        random.choices(["night", "day"], weights=[0.7, 0.3])[0]
        if root == "Insufficient operator training"
        else random.choice(shift_times)
    )

    age = (
        random.choices(["old", "mid", "new"], weights=[0.6, 0.3, 0.1])[0]
        if root in ["Lack of preventive maintenance", "Dusty workshop environment"]
        else random.choice(machine_age_buckets)
    )

    gap = (
        random.choices(["overdue", "moderate", "recent"], weights=[0.7, 0.2, 0.1])[0]
        if root == "Lack of preventive maintenance"
        else random.choice(maintenance_gaps)
    )

    freq = (
        random.choices(["high", "medium", "low"], weights=[0.6, 0.3, 0.1])[0]
        if root in ["Lack of preventive maintenance", "Outdated CAM files"]
        else random.choice(failure_frequencies)
    )

    return shift, age, gap, freq

# LOAD
with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

# ENRICH
for record in data:
    shift, age, gap, freq = infer_domain_features(record)
    record.update({
        "shift_time": shift,
        "machine_age_bucket": age,
        "maintenance_gap_days": gap,
        "failure_frequency": freq
    })

# SAVE
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"✅ Domain-enriched dataset saved → {OUTPUT_FILE}")
print(f"Total records: {len(data)}")
