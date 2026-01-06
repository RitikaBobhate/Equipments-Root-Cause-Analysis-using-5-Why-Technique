from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from pymongo import MongoClient
import joblib
import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
from groq import Groq
import os
import json

app = FastAPI(title="Root Cause Analysis API", version="2.0")

# Fix CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# GROQ LLM INITIALIZATION
# =====================================================
groq_client = None
try:
    # Use your Groq API key directly
    groq_client = Groq(api_key="")
    print("✅ Groq LLM initialized (FREE)")
except Exception as e:
    print(f"⚠️  Groq not available: {e}")

# Load model (updated for new pipeline)
try:
    model_data = joblib.load("model_prod_v2.pkl")
    pipeline = model_data["pipeline"]
    label_encoder = model_data["label_encoder"]
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    pipeline = None
    label_encoder = None

# Connect DB
MONGO_URL = "mongodb+srv://RIL_sys:M(>$s8!p@rootcause-db.wayefpy.mongodb.net/?appName=rootcause-db"
client = MongoClient(MONGO_URL)
db = client["fivewhy_db"]
collection = db["equipment_data"]

# =====================================================
# PYDANTIC MODELS
# =====================================================

class InputText(BaseModel):
    description: str

class InputData(BaseModel):
    description: str
    environment: str = "clean"
    operating_load: str = "normal"
    recent_maintenance: str = "yes"
    severity: str = "medium"
    shift_time: str = "day"
    machine_age_bucket: str = "mid"
    maintenance_gap_days: str = "moderate"
    failure_frequency: str = "medium"

class EquipmentData(BaseModel):
    equipment_id: str
    equipment_type: str
    issue: str
    root_cause: str
    why1: str
    why2: str
    why3: str
    why4: str
    why5: str
    solution: str
    department: str
    severity: str
    date_reported: str

class UpdateEquipmentData(BaseModel):
    equipment_type: Optional[str] = None
    issue: Optional[str] = None
    root_cause: Optional[str] = None
    why1: Optional[str] = None
    why2: Optional[str] = None
    why3: Optional[str] = None
    why4: Optional[str] = None
    why5: Optional[str] = None
    solution: Optional[str] = None
    department: Optional[str] = None
    severity: Optional[str] = None
    date_reported: Optional[str] = None

# =====================================================
# GROQ LLM PREDICTION FUNCTION
# =====================================================
def predict_with_llm(description: str) -> dict:
    """Use FREE Groq to predict root cause"""
    
    if not groq_client:
        raise HTTPException(status_code=503, detail="Groq LLM not configured")
    
    root_causes = [
        "Sensor/calibration failure",
        "Component fatigue/corrosion",
        "Inadequate lubrication",
        "Electrical supply fluctuation",
        "Incorrect installation/assembly",
        "Bypass of safety interlock",
        "Human/operator error",
        "Contaminated fluid/particulate ingress",
        "Design flaw in component",
        "Lack of preventive maintenance"
    ]
    
    prompt = f"""You are an expert in industrial equipment failure analysis.

**Equipment Failure Description:**
{description}

**Available Root Causes:**
{chr(10).join(f'{i+1}. {rc}' for i, rc in enumerate(root_causes))}

**Instructions:**
Analyze the failure description and select the MOST LIKELY root cause from the list above.

**Response Format (JSON only):**
{{
  "root_cause": "exact name from list above",
  "confidence": 85,
  "reasoning": "Brief explanation (2-3 sentences)",
  "key_indicators": ["keyword1", "keyword2"]
}}

Return ONLY valid JSON."""

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert industrial failure analyst. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=1000,
        )
        
             
   
        # Clean markdown if present
        message = chat_completion.choices[0].message

        if not message or not message.content:
            raise HTTPException(status_code=500, detail="LLM returned empty response")

        response_text = message.content.strip()

        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
                
        result = json.loads(response_text)
                
        return {
            "prediction": result["root_cause"],
            "confidence": result["confidence"] / 100,
            "reasoning": result["reasoning"],
            "key_indicators": result.get("key_indicators", []),
            "method": "llm_free"
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        print(f"Raw response: {response_text}")
        raise HTTPException(status_code=500, detail="LLM returned invalid JSON")
    except Exception as e:
        print(f"LLM error: {e}")
        raise HTTPException(status_code=500, detail=f"LLM failed: {str(e)}")

# =====================================================
# BASIC ENDPOINTS
# =====================================================

@app.get("/")
def test_backend():
    return {
        "message": "Root Cause Analysis API",
        "status": "running",
        "version": "2.0",
        "groq_llm": "available" if groq_client else "not configured",
        "endpoints": {
            "predictions": ["/predict", "/predict-enhanced", "/predict-hybrid", "/predict-llm"],
            "analytics": ["/analytics/summary", "/analytics/plots", "/analytics/trends"],
            "crud": ["/all-data", "/add-record", "/update-record/{id}", "/delete-record/{id}"]
        }
    }

@app.get("/health")
def health_check():
    model_status = "loaded" if pipeline else "not loaded"
    try:
        client.server_info()
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "model": model_status,
        "database": db_status,
        "groq_llm": "available" if groq_client else "not configured",
        "records": collection.count_documents({})
    }

# =====================================================
# PREDICTION ENDPOINTS
# =====================================================

# OLD prediction endpoint (simple text only)

# NEW: HYBRID ENDPOINT (ML + FREE Groq LLM) - RECOMMENDED
@app.post("/predict-hybrid")
def predict_hybrid(input_data: InputText):
    """
    HYBRID: Uses ML first (fast), falls back to FREE Groq LLM if confidence < 60%
    """
    if not input_data.description or len(input_data.description.strip()) < 5:
        raise HTTPException(status_code=400, detail="Description too short")
    
    ml_confidence = 0.0
    
    try:
        # Step 1: Try ML first
        if pipeline is not None:
            model_data = joblib.load("model_prod_v2.pkl")
            pipeline_obj = model_data["pipeline"]
            
            text = f"issue: {input_data.description}"
            record = {
                "enhanced_text": text,
                "severity": "medium",
                "shift_time": "day",
                "machine_age_bucket": "mid",
                "maintenance_gap_days": "moderate",
                "failure_frequency": "medium"
            }
            
            if "equipment_type" in model_data["cat_cols"]:
                record["equipment_type"] = "Unknown"
            if "department" in model_data["cat_cols"]:
                record["department"] = "Unknown"
            
            df_input = pd.DataFrame([record])
            prediction = pipeline_obj.predict(df_input)[0]
            probabilities = pipeline_obj.predict_proba(df_input)[0]
            ml_confidence = float(np.max(probabilities))
            
            # If ML is confident, use it
            if ml_confidence >= 0.60:
                results = list(collection.find(
                    {"root_cause": prediction},
                    {"_id": 0, "why1": 1, "why2": 1, "why3": 1, "why4": 1, "why5": 1, "solution": 1}
                ).limit(3))
                
                five_why = results[0] if results else {
                    "why1": "No details available",
                    "why2": "No details available",
                    "why3": "No details available",
                    "why4": "No details available",
                    "why5": "No details available",
                    "solution": "No solution documented"
                }
                
                return {
                    "prediction": prediction,
                    "confidence": ml_confidence,
                    "five_why": five_why,
                    "method": "ml",
                    "note": "High confidence ML prediction"
                }
        
        # Step 2: Use FREE Groq LLM
        print(f"ML confidence low ({ml_confidence:.2f}), using FREE Groq...")
        
        llm_result = predict_with_llm(input_data.description)
        
        results = list(collection.find(
            {"root_cause": llm_result["prediction"]},
            {"_id": 0, "why1": 1, "why2": 1, "why3": 1, "why4": 1, "why5": 1, "solution": 1}
        ).limit(3))
        
        five_why = results[0] if results else {
            "why1": "No details available",
            "why2": "No details available",
            "why3": "No details available",
            "why4": "No details available",
            "why5": "No details available",
            "solution": "No solution documented"
        }
        
        return {
            "prediction": llm_result["prediction"],
            "confidence": llm_result["confidence"],
            "five_why": five_why,
            "method": "llm_free",
            "reasoning": llm_result.get("reasoning", ""),
            "key_indicators": llm_result.get("key_indicators", []),
            "note": f"FREE Groq LLM (ML was {ml_confidence:.2f})"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# NEW: PURE LLM ENDPOINT (ALWAYS USES GROQ)
@app.post("/predict-llm")
def predict_llm_only(input_data: InputText):
    """Always uses FREE Groq LLM (most accurate)"""
    if not input_data.description or len(input_data.description.strip()) < 5:
        raise HTTPException(status_code=400, detail="Description too short")
    
    try:
        llm_result = predict_with_llm(input_data.description)
        
        results = list(collection.find(
            {"root_cause": llm_result["prediction"]},
            {"_id": 0, "why1": 1, "why2": 1, "why3": 1, "why4": 1, "why5": 1, "solution": 1}
        ).limit(3))
        
        five_why = results[0] if results else {
            "why1": "No details available",
            "why2": "No details available",
            "why3": "No details available",
            "why4": "No details available",
            "why5": "No details available",
            "solution": "No solution documented"
        }
        
        return {
            "prediction": llm_result["prediction"],
            "confidence": llm_result["confidence"],
            "five_why": five_why,
            "method": "llm_free",
            "reasoning": llm_result.get("reasoning", ""),
            "key_indicators": llm_result.get("key_indicators", []),
            "note": "FREE Groq LLM prediction"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

# NEW prediction endpoint with all features
@app.post("/predict-enhanced")
def predict_root_cause_enhanced(input_data: InputData):
    """New endpoint with all domain features"""
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    if not input_data.description or len(input_data.description.strip()) < 5:
        raise HTTPException(status_code=400, detail="Description too short")
    
    try:
        # Load model data
        model_data = joblib.load("model_prod_v2.pkl")
        pipeline_obj = model_data["pipeline"]
        
        # Create enhanced text
        text = f"issue: {input_data.description} severity: {input_data.severity}"
        
        # Prepare input record
        record = {
            "enhanced_text": text,
            "severity": input_data.severity,
            "shift_time": input_data.shift_time,
            "machine_age_bucket": input_data.machine_age_bucket,
            "maintenance_gap_days": input_data.maintenance_gap_days,
            "failure_frequency": input_data.failure_frequency
        }
        
        # Add equipment_type and department if they exist in model
        if "equipment_type" in model_data["cat_cols"]:
            record["equipment_type"] = "Unknown"
        if "department" in model_data["cat_cols"]:
            record["department"] = "Unknown"
        
        # Make prediction
        df_input = pd.DataFrame([record])
        prediction = pipeline_obj.predict(df_input)[0]
        probabilities = pipeline_obj.predict_proba(df_input)[0]
        confidence = np.max(probabilities)
        
        # Fetch matching records from database
        results = list(collection.find(
            {"root_cause": prediction},
            {"_id": 0, "why1": 1, "why2": 1, "why3": 1, "why4": 1, "why5": 1, 
             "solution": 1, "equipment_type": 1, "severity": 1, "department": 1}
        ).limit(3))
        
        if not results:
            five_why = {
                "why1": "No details available",
                "why2": "No details available",
                "why3": "No details available",
                "why4": "No details available",
                "why5": "No details available",
                "solution": "No solution documented"
            }
        else:
            result = results[0]
            five_why = {
                "why1": result.get("why1", ""),
                "why2": result.get("why2", ""),
                "why3": result.get("why3", ""),
                "why4": result.get("why4", ""),
                "why5": result.get("why5", ""),
                "solution": result.get("solution", ""),
                "equipment_type": result.get("equipment_type", ""),
                "department": result.get("department", "")
            }
        
        # Get top 3 predictions
        top_indices = np.argsort(probabilities)[-3:][::-1]
        top_predictions = [
            {
                "root_cause": model_data["label_encoder"].classes_[idx],
                "confidence": float(probabilities[idx])
            }
            for idx in top_indices
        ]
        
        return {
            "prediction": prediction,
            "confidence": float(confidence),
            "five_why": five_why,
            "top_predictions": top_predictions,
            "sample_matches": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# =====================================================
# CRUD OPERATIONS
# =====================================================

@app.get("/all-data")
def get_all_data():
    data = list(collection.find({}, {"_id": 0}))
    return {"data": data, "count": len(data)}

@app.get("/record/{equipment_id}")
def get_record(equipment_id: str):
    record = collection.find_one({"equipment_id": equipment_id}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.post("/add-record")
def add_record(record: EquipmentData):
    # Check if equipment_id already exists
    existing = collection.find_one({"equipment_id": record.equipment_id})
    if existing:
        raise HTTPException(status_code=400, detail=f"Equipment ID {record.equipment_id} already exists")
    
    record_dict = record.dict()
    result = collection.insert_one(record_dict)
    return {"message": "Record added successfully", "id": str(result.inserted_id)}

@app.put("/update-record/{equipment_id}")
def update_record(equipment_id: str, update_data: UpdateEquipmentData):
    existing = collection.find_one({"equipment_id": equipment_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Remove None values from update
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    collection.update_one({"equipment_id": equipment_id}, {"$set": update_dict})
    return {"message": "Record updated successfully"}

@app.delete("/delete-record/{equipment_id}")
def delete_record(equipment_id: str):
    result = collection.delete_one({"equipment_id": equipment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Record deleted successfully"}

# =====================================================
# ANALYTICS ENDPOINTS
# =====================================================

@app.get("/analytics/summary")
def get_analytics_summary():
    data = list(collection.find({}, {"_id": 0}))
    if not data:
        return {"error": "No data available"}
    
    df = pd.DataFrame(data)
    
    # Calculate statistics
    total_records = len(df)
    departments = df['department'].value_counts().to_dict() if 'department' in df.columns else {}
    severity_counts = df['severity'].value_counts().to_dict() if 'severity' in df.columns else {}
    top_root_causes = df['root_cause'].value_counts().head(10).to_dict() if 'root_cause' in df.columns else {}
    
    # Equipment type distribution
    equipment_types = df['equipment_type'].value_counts().to_dict() if 'equipment_type' in df.columns else {}
    
    # Domain features distribution
    shift_times = df['shift_time'].value_counts().to_dict() if 'shift_time' in df.columns else {}
    age_buckets = df['machine_age_bucket'].value_counts().to_dict() if 'machine_age_bucket' in df.columns else {}
    
    return {
        "total_records": total_records,
        "departments": departments,
        "severity": severity_counts,
        "top_root_causes": top_root_causes,
        "equipment_types": equipment_types,
        "shift_times": shift_times,
        "age_buckets": age_buckets
    }

@app.get("/analytics/trends")
def get_trends():
    data = list(collection.find({}, {"_id": 0}))
    if not data:
        return {"monthly_trends": {}}
    
    df = pd.DataFrame(data)
    
    # Monthly trends
    if 'date_reported' in df.columns and not df.empty:
        try:
            df['month'] = pd.to_datetime(df['date_reported']).dt.to_period('M')
            monthly_counts = df['month'].value_counts().sort_index().to_dict()
            monthly_counts = {str(k): v for k, v in monthly_counts.items()}
        except:
            monthly_counts = {}
    else:
        monthly_counts = {}
    
    return {"monthly_trends": monthly_counts}

@app.get("/analytics/department-stats")
def get_department_stats():
    data = list(collection.find({}, {"_id": 0}))
    if not data:
        return {"department_stats": {}}
    
    df = pd.DataFrame(data)
    
    if 'department' in df.columns and 'severity' in df.columns:
        dept_stats = df.groupby(['department', 'severity']).size().unstack(fill_value=0).to_dict()
    else:
        dept_stats = {}
    
    return {"department_stats": dept_stats}

@app.get("/analytics/root-cause-stats")
def get_root_cause_stats():
    data = list(collection.find({}, {"_id": 0}))
    if not data:
        return {"root_cause_stats": {}}
    
    df = pd.DataFrame(data)
    
    if 'root_cause' in df.columns and 'equipment_type' in df.columns:
        rc_stats = df.groupby(['root_cause', 'equipment_type']).size().unstack(fill_value=0).to_dict()
    else:
        rc_stats = {}
    
    return {"root_cause_stats": rc_stats}

@app.get("/analytics/plots")
def get_analytics_plots():
    """Generate analytics plots"""
    try:
        # Simple data extraction for charts
        data = list(collection.find({}, {"_id": 0}))
        if not data:
            return {"error": "No data available"}
        
        df = pd.DataFrame(data)
        
        # 1. Severity Distribution
        if 'severity' in df.columns:
            severity_counts = df['severity'].value_counts().head(5)
            severity_chart = {
                "data": [{
                    "type": "pie",
                    "labels": severity_counts.index.tolist(),
                    "values": severity_counts.values.tolist(),
                    "hole": .3,
                    "marker": {"colors": ['#FF6B6B', '#FFD166', '#06D6A0', '#118AB2']}
                }],
                "layout": {
                    "title": "Issue Severity Distribution",
                    "height": 400
                }
            }
        else:
            severity_chart = None
        
        # 2. Root Causes Chart
        if 'root_cause' in df.columns:
            top_causes = df['root_cause'].value_counts().head(10)
            causes_chart = {
                "data": [{
                    "type": "bar",
                    "x": top_causes.values.tolist(),
                    "y": top_causes.index.tolist(),
                    "orientation": "h",
                    "marker": {"color": "#118AB2"}
                }],
                "layout": {
                    "title": "Top 10 Root Causes",
                    "height": 500,
                    "margin": {"l": 150}
                }
            }
        else:
            causes_chart = None
        
        # 3. Department Chart
        if 'department' in df.columns:
            dept_counts = df['department'].value_counts()
            department_chart = {
                "data": [{
                    "type": "bar",
                    "x": dept_counts.index.tolist(),
                    "y": dept_counts.values.tolist(),
                    "marker": {"color": "#06D6A0"}
                }],
                "layout": {
                    "title": "Issues by Department",
                    "height": 400
                }
            }
        else:
            department_chart = None
        
        # 4. Equipment Chart
        if 'equipment_type' in df.columns:
            eq_counts = df['equipment_type'].value_counts()
            equipment_chart = {
                "data": [{
                    "type": "bar",
                    "x": eq_counts.index.tolist(),
                    "y": eq_counts.values.tolist(),
                    "marker": {"color": "#EF476F"}
                }],
                "layout": {
                    "title": "Equipment Type Distribution",
                    "height": 400
                }
            }
        else:
            equipment_chart = None
        
        # 5. Trend Chart (Monthly)
        if 'date_reported' in df.columns:
            try:
                df['month'] = pd.to_datetime(df['date_reported']).dt.strftime('%Y-%m')
                monthly_counts = df['month'].value_counts().sort_index()
                trend_chart = {
                    "data": [{
                        "type": "scatter",
                        "x": monthly_counts.index.tolist(),
                        "y": monthly_counts.values.tolist(),
                        "mode": "lines+markers",
                        "line": {"color": "#7B2CBF", "width": 3},
                        "marker": {"size": 8, "color": "#7B2CBF"}
                    }],
                    "layout": {
                        "title": "Monthly Trend of Issues",
                        "height": 400
                    }
                }
            except:
                trend_chart = None
        else:
            trend_chart = None
        
        return {
            "severity_chart": severity_chart,
            "causes_chart": causes_chart,
            "department_chart": department_chart,
            "equipment_chart": equipment_chart,
            "trend_chart": trend_chart,
            "stats": {
                "total_records": len(df),
                "unique_causes": df['root_cause'].nunique() if 'root_cause' in df.columns else 0,
                "unique_equipment": df['equipment_type'].nunique() if 'equipment_type' in df.columns else 0
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to generate plots: {str(e)}"}

# =====================================================
# SEARCH & FILTER ENDPOINTS
# =====================================================

@app.get("/search")
def search_records(
    equipment_type: Optional[str] = None,
    department: Optional[str] = None,
    severity: Optional[str] = None,
    root_cause: Optional[str] = None,
    limit: int = 50
):
    query = {}
    
    if equipment_type:
        query["equipment_type"] = {"$regex": equipment_type, "$options": "i"}
    if department:
        query["department"] = {"$regex": department, "$options": "i"}
    if severity:
        query["severity"] = severity.lower()
    if root_cause:
        query["root_cause"] = {"$regex": root_cause, "$options": "i"}
    
    data = list(collection.find(query, {"_id": 0}).limit(limit))
    return {"data": data, "count": len(data)}

@app.get("/root-causes")
def get_all_root_causes():
    root_causes = collection.distinct("root_cause")
    return {"root_causes": sorted(root_causes)}

@app.get("/equipment-types")
def get_all_equipment_types():
    equipment_types = collection.distinct("equipment_type")
    return {"equipment_types": sorted(equipment_types)}

@app.get("/departments")
def get_all_departments():
    departments = collection.distinct("department")
    return {"departments": sorted(departments)}

# =====================================================
# DATA EXPORT
# =====================================================

@app.get("/export/csv")
def export_to_csv():
    data = list(collection.find({}, {"_id": 0}))
    if not data:
        raise HTTPException(status_code=404, detail="No data to export")
    
    df = pd.DataFrame(data)
    
    # Create CSV file
    csv_file = "equipment_data_export.csv"
    df.to_csv(csv_file, index=False)
    
    return FileResponse(
        csv_file,
        media_type="text/csv",
        filename=f"equipment_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

# Favicon endpoint
@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon"}