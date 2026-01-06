# =====================================================
# IMPORTS
# =====================================================
# =====================================================
# IMPORTS
# =====================================================
import pandas as pd
import numpy as np
import joblib
from pymongo import MongoClient

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

# =====================================================
# DATABASE CONNECTION
# =====================================================
client = MongoClient(
    "mongodb+srv://RIL_sys:M(>$s8!p@rootcause-db.wayefpy.mongodb.net/?appName=rootcause-db"
)
db = client["fivewhy_db"]
collection = db["equipment_data"]

# =====================================================
# LOAD DATA
# =====================================================
data = list(collection.find({}, {"_id": 0}))
df = pd.DataFrame(data)

print("\n=== DATA STATS ===")
print(f"Total records: {len(df)}")
print("\nRoot Cause Distribution:")
print(df["root_cause"].value_counts())

# =====================================================
# ENHANCED TEXT FEATURE
# =====================================================
def enhance_text(row):
    parts = []
    for col in ["issue", "equipment_type", "department", "severity"]:
        if col in row and pd.notna(row[col]):
            parts.append(f"{col}: {row[col]}")
    return " ".join(parts)

df["enhanced_text"] = df.apply(enhance_text, axis=1)

# =====================================================
# DEFAULTS
# =====================================================
defaults = {
    "severity": "medium",
    "shift_time": "day",
    "machine_age_bucket": "mid",
    "maintenance_gap_days": "moderate",
    "failure_frequency": "medium"
}

for col, val in defaults.items():
    if col not in df.columns:
        df[col] = val
    df[col] = df[col].astype(str).fillna(val)

# =====================================================
# FEATURES
# =====================================================
TEXT_COL = "enhanced_text"

CAT_COLS = [
    "severity",
    "shift_time",
    "machine_age_bucket",
    "maintenance_gap_days",
    "failure_frequency"
]

if "equipment_type" in df.columns:
    CAT_COLS.append("equipment_type")
if "department" in df.columns:
    CAT_COLS.append("department")

X = df[[TEXT_COL] + CAT_COLS]
y = df["root_cause"]

# =====================================================
# LABEL ENCODING
# =====================================================
label_encoder = LabelEncoder()
y_enc = label_encoder.fit_transform(y)

print(f"\n=== FEATURES ===")
print(f"Text feature: {TEXT_COL}")
print(f"Categorical features: {CAT_COLS}")
print(f"Number of classes: {len(label_encoder.classes_)}")

# =====================================================
# PREPROCESSOR  🔥 (KEY FIX HERE)
# =====================================================
preprocessor = ColumnTransformer(
    transformers=[
        (
            "text",
            TfidfVectorizer(
                max_features=60,        # 🔥 reduced from 150
                min_df=2,
                max_df=0.9,
                ngram_range=(1, 2),
                stop_words="english"
            ),
            TEXT_COL
        ),
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore", sparse_output=True),
            CAT_COLS
        )
    ]
)

# =====================================================
# MODEL  🔥 (KEY FIX HERE)
# =====================================================
model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    n_jobs=-1
)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model)
])

# =====================================================
# CROSS-VALIDATION
# =====================================================
print("\n=== CROSS-VALIDATION ===")
cv_scores = cross_val_score(pipeline, X, y_enc, cv=5, scoring="accuracy")
print(f"CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

# =====================================================
# TRAIN ON ALL DATA
# =====================================================
print("\n=== TRAINING ON ALL DATA ===")
pipeline.fit(X, y)

# =====================================================
# TEST ON SPLIT (for evaluation only)
# =====================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, stratify=y_enc, random_state=42
)

pipeline_test = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        n_jobs=-1
    ))
])

pipeline_test.fit(X_train, y_train)
y_pred = pipeline_test.predict(X_test)

print("\n=== TEST RESULTS (80/20 split) ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
print("\nClassification Report:")
print(classification_report(
    label_encoder.inverse_transform(y_test),
    label_encoder.inverse_transform(y_pred),
    zero_division=0
))

# =====================================================
# SAVE MODEL
# =====================================================
model_data = {
    "pipeline": pipeline,
    "label_encoder": label_encoder,
    "text_col": TEXT_COL,
    "cat_cols": CAT_COLS,
    "defaults": defaults
}

joblib.dump(model_data, "model_prod_v2.pkl")
print("\n✅ Model saved as model_prod_v2.pkl")

# =====================================================
# SAMPLE TEST
# =====================================================
def predict_root_cause(record: dict):
    text = " ".join(
        f"{k}: {record[k]}"
        for k in ["issue", "equipment_type", "department", "severity"]
        if record.get(k)
    )

    row = {"enhanced_text": text}
    for col in CAT_COLS:
        row[col] = record.get(col, defaults.get(col, "unknown"))

    df_input = pd.DataFrame([row])
    probs = pipeline.predict_proba(df_input)[0]
    idx = int(np.argmax(probs))

    return (
        label_encoder.classes_[idx],
        float(probs[idx]),
        dict(zip(label_encoder.classes_, probs))
    )

sample = {
    "issue": "Motor overheating and vibration",
    "equipment_type": "Motor",
    "department": "Maintenance",
    "severity": "Critical",
    "shift_time": "night",
    "machine_age_bucket": "old",
    "maintenance_gap_days": "current",
    "failure_frequency": "low"
}

pred, conf, probs = predict_root_cause(sample)

print("\n=== SAMPLE PREDICTION ===")
print(f"Input: {sample['issue']}")
print(f"Prediction: {pred}")
print(f"Confidence: {conf:.3f}")

print("\nTop 3 predictions:")
for rc, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]:
    print(f"  {rc}: {prob:.3f}")
