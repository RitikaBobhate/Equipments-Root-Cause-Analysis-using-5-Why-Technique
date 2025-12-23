import pandas as pd
import numpy as np
import joblib
from pymongo import MongoClient
import xgboost as xgb

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.utils.class_weight import compute_class_weight



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
print(f"Unique root causes: {df['root_cause'].nunique()}")
print(f"\nClass distribution:")
print(df['root_cause'].value_counts())

# =====================================================
# ENHANCE TEXT FEATURES
# =====================================================
# Combine multiple text fields for better context
def enhance_text_features(row):
    text_parts = []
    
    # Add issue description
    if pd.notna(row.get('issue')):
        text_parts.append(str(row['issue']))
    
    # Add equipment type
    if pd.notna(row.get('equipment_type')):
        text_parts.append(f"Equipment: {row['equipment_type']}")
    
    # Add department
    if pd.notna(row.get('department')):
        text_parts.append(f"Department: {row['department']}")
    
    # Add severity
    if pd.notna(row.get('severity')):
        text_parts.append(f"Severity: {row['severity']}")
    
    return " ".join(text_parts)

# Apply text enhancement
df['enhanced_text'] = df.apply(enhance_text_features, axis=1)

# =====================================================
# SAFETY DEFAULTS
# =====================================================
defaults = {
    "environment": "clean",
    "operating_load": "normal", 
    "recent_maintenance": "yes",
    "severity": "medium",
    "shift_time": "day",
    "machine_age_bucket": "mid",
    "maintenance_gap_days": "moderate",
    "failure_frequency": "medium"
}

for col, default in defaults.items():
    if col not in df.columns:
        df[col] = default
    else:
        df[col] = df[col].astype(str).fillna(default)

# =====================================================
# FEATURE SEPARATION
# =====================================================
TEXT_COL = "enhanced_text"  # Use enhanced text

CAT_COLS = [
    "environment",
    "operating_load", 
    "recent_maintenance",
    "severity",
    "shift_time",
    "machine_age_bucket",
    "maintenance_gap_days",
    "failure_frequency"
]

# Add equipment_type as categorical feature
if 'equipment_type' in df.columns:
    CAT_COLS.append("equipment_type")

# Add department as categorical feature
if 'department' in df.columns:
    CAT_COLS.append("department")

X = df[[TEXT_COL] + CAT_COLS]
y = df["root_cause"]

print(f"\n=== FEATURE MATRIX SHAPE ===")
print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")
print(f"Text feature: {TEXT_COL}")
print(f"Categorical features: {CAT_COLS}")

# =====================================================
# ENCODE TARGET VARIABLE
# =====================================================
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

print(f"\n=== TARGET ENCODING ===")
print(f"Classes: {label_encoder.classes_}")
print(f"Encoded: {np.unique(y_encoded)}")


class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_encoded),
    y=y_encoded
)
print(f"\n=== CLASS WEIGHTS ===")
for i, cls in enumerate(label_encoder.classes_):
    print(f"{cls}: {class_weights[i]:.3f}")
# =====================================================
# TRAIN / TEST SPLIT
# =====================================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    stratify=y_encoded,
    random_state=42
)

print(f"\n=== TRAIN/TEST SPLIT ===")
print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")
print(f"Training class distribution:")
train_classes, train_counts = np.unique(y_train, return_counts=True)
for cls_idx, count in zip(train_classes, train_counts):
    print(f"  {label_encoder.classes_[cls_idx]}: {count}")

# =====================================================
# PREPROCESSOR PIPELINE
# =====================================================
preprocessor = ColumnTransformer(
    transformers=[
        (
            "text",
            TfidfVectorizer(
                max_features=2000,  
                min_df=0.1  ,           
                max_df=0.9,         
                ngram_range=(1, 3), 
                stop_words="english",
                sublinear_tf=True,  
                use_idf=True,
                smooth_idf=True
            ),
            TEXT_COL
        ),
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            CAT_COLS
        )
    ]
)

# =====================================================
# MODEL - Improved with better handling of imbalanced data
# =====================================================
from sklearn.model_selection import GridSearchCV

models_to_try = {
    "RandomForest": RandomForestClassifier(
        n_estimators=300,
        max_depth=20,
        min_samples_split=3,
        min_samples_leaf=1,
        class_weight='balanced_subsample',  # Better for RF
        random_state=42,
        n_jobs=-1
    ),
    "LogisticRegression": LogisticRegression(
        max_iter=5000,
        C=0.1,
        class_weight='balanced',
        solver='saga',
        penalty='l2',
        random_state=42
    ),
    "SVM": SVC(
        kernel='rbf',  # Changed from linear to rbf for better separation
        C=1.0,
        class_weight='balanced',
        probability=True,
        random_state=42,
        gamma='scale'
    ),
    "GradientBoosting": GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.05,  # Reduced learning rate
        max_depth=7,
        subsample=0.8,
        random_state=42,
        min_samples_split=5,
        min_samples_leaf=2
    ),
    "XGBoost": xgb.XGBClassifier(  # Add XGBoost - often performs better
        n_estimators=200,
        learning_rate=0.05,
        max_depth=7,
        objective='multi:softmax',
        random_state=42,
        scale_pos_weight=1
    )
}

best_model = None
best_score = 0
best_model_name = ""

print("\n=== MODEL EVALUATION ===")

for model_name, model in models_to_try.items():
    print(f"\nTraining {model_name}...")
    
    # Create pipeline with SMOTE for handling imbalanced data
    pipeline = ImbPipeline([
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=42, k_neighbors=3)),
        ("model", model)
    ])
    
    try:
        # Cross-validation
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)  # Reduced folds for small dataset
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring='accuracy')
        
        avg_score = cv_scores.mean()
        print(f"{model_name} CV scores: {cv_scores}")
        print(f"{model_name} mean accuracy: {avg_score:.3f}")
        
        if avg_score > best_score:
            best_score = avg_score
            best_model = pipeline
            best_model_name = model_name
    except Exception as e:
        print(f"Error training {model_name}: {e}")
        continue

print(f"\n✅ Best model: {best_model_name} with accuracy: {best_score:.3f}")

# =====================================================
# TRAIN BEST MODEL
# =====================================================
print(f"\n=== TRAINING BEST MODEL ({best_model_name}) ===")
best_model.fit(X_train, y_train)

# =====================================================
# EVALUATION
# =====================================================
y_pred = best_model.predict(X_test)
y_pred_labels = label_encoder.inverse_transform(y_pred)
y_test_labels = label_encoder.inverse_transform(y_test)

print("\n=== TEST PERFORMANCE ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")

print("\n=== CLASSIFICATION REPORT ===")
print(classification_report(y_test_labels, y_pred_labels))

print("\n=== CONFUSION MATRIX ===")
cm = confusion_matrix(y_test_labels, y_pred_labels, labels=label_encoder.classes_)
print(pd.DataFrame(cm, 
                   index=label_encoder.classes_, 
                   columns=label_encoder.classes_))

# =====================================================
# SAVE MODEL & ENCODERS
# =====================================================
# Create a dictionary with all necessary components
model_package = {
    "pipeline": best_model,
    "label_encoder": label_encoder,
    "text_column": TEXT_COL,
    "cat_columns": CAT_COLS,
    "defaults": defaults
}

joblib.dump(model_package, "model_prod_v2.pkl")
print("\n✅ Production pipeline saved as model_prod_v2.pkl")

# =====================================================
# INFERENCE FUNCTION (PRODUCTION SAFE)
# =====================================================
def predict_root_cause(record: dict, threshold: float = 0.3):
    """
    record = {
        "issue": "...",
        "equipment_type": "...",
        "department": "...",
        "environment": "...",
        "operating_load": "...",
        "recent_maintenance": "...",
        "severity": "...",
        "shift_time": "...",
        "machine_age_bucket": "...",
        "maintenance_gap_days": "...",
        "failure_frequency": "..."
    }
    """
    try:
        # Create enhanced text
        text_parts = []
        
        if record.get('issue'):
            text_parts.append(str(record['issue']))
        if record.get('equipment_type'):
            text_parts.append(f"Equipment: {record['equipment_type']}")
        if record.get('department'):
            text_parts.append(f"Department: {record['department']}")
        if record.get('severity'):
            text_parts.append(f"Severity: {record['severity']}")
        
        enhanced_text = " ".join(text_parts)
        
        # Prepare input dataframe
        input_dict = {"enhanced_text": enhanced_text}
        for col in CAT_COLS:
            input_dict[col] = record.get(col, defaults.get(col, "unknown"))
        
        df_input = pd.DataFrame([input_dict])
        
        # Make prediction
        probs = best_model.predict_proba(df_input)[0]
        idx = np.argmax(probs)
        confidence = probs[idx]
        predicted_class_encoded = best_model.predict(df_input)[0]
        predicted_class = label_encoder.inverse_transform([predicted_class_encoded])[0]
        
        if confidence < threshold:
            return "Needs human review", confidence, predicted_class, probs
        
        return predicted_class, confidence, predicted_class, probs
        
    except Exception as e:
        return f"Error: {str(e)}", 0.0, None, []

# =====================================================
# SAMPLE TEST
# =====================================================
print("\n=== SAMPLE PREDICTIONS ===")

samples = [
    {
        "issue": "Compressor overheating during night shift",
        "equipment_type": "Compressor",
        "department": "Operations",
        "environment": "clean",
        "operating_load": "high",
        "recent_maintenance": "no",
        "severity": "critical",
        "shift_time": "night",
        "machine_age_bucket": "mid",
        "maintenance_gap_days": "overdue",
        "failure_frequency": "high"
    },
    {
        "issue": "Generator unexpected shutdown with gas leak detected",
        "equipment_type": "Generator",
        "department": "Safety",
        "environment": "clean",
        "operating_load": "normal",
        "recent_maintenance": "yes",
        "severity": "medium",
        "shift_time": "day",
        "machine_age_bucket": "old",
        "maintenance_gap_days": "moderate",
        "failure_frequency": "medium"
    },
    {
        "issue": "Pump abnormal vibration and noise detected",
        "equipment_type": "Pump",
        "department": "Maintenance",
        "environment": "dusty",
        "operating_load": "high",
        "recent_maintenance": "no",
        "severity": "medium",
        "shift_time": "night",
        "machine_age_bucket": "new",
        "maintenance_gap_days": "overdue",
        "failure_frequency": "high"
    }
]

for i, s in enumerate(samples, 1):
    pred, conf, pred_class, probs = predict_root_cause(s, threshold=0.2)
    print(f"\nSample {i}: {s['issue'][:50]}...")
    print(f"  → Prediction: {pred}")
    print(f"  → Confidence: {conf:.3f}")
    print(f"  → Predicted class: {pred_class}")
    
    # Show top 3 predictions
    if len(probs) > 0:
        top_indices = np.argsort(probs)[-3:][::-1]
        print(f"  → Top predictions:")
        for idx in top_indices:
            cls_name = label_encoder.classes_[idx]
            print(f"     {cls_name}: {probs[idx]:.3f}")

print("\n✅ Model training complete!")