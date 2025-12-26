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

# ✅ CREATE APP
app = FastAPI(title="Root Cause Analysis API", version="2.0")

# Fix CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model (updated for new pipeline)
try:
    pipeline = joblib.load("model_prod.pkl")
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    pipeline = None

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
# BASIC ENDPOINTS
# =====================================================

@app.get("/")
def test_backend():
    return {"message": "Root Cause Analysis API", "status": "running", "version": "2.0"}

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
        "records": collection.count_documents({})
    }

# =====================================================
# PREDICTION ENDPOINTS (OLD & NEW)
# =====================================================

# OLD prediction endpoint (simple text only)
@app.post("/predict")
def predict_root_cause_simple(input_data: InputText):
    """Old endpoint for backward compatibility"""
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    if not input_data.description or len(input_data.description.strip()) < 5:
        raise HTTPException(status_code=400, detail="Description too short")
    
    try:
        # Create a default record for old endpoint
        record = {
            "issue": input_data.description,
            "environment": "clean",
            "operating_load": "normal",
            "recent_maintenance": "yes",
            "severity": "medium",
            "shift_time": "day",
            "machine_age_bucket": "mid",
            "maintenance_gap_days": "moderate",
            "failure_frequency": "medium"
        }
        
        # Make prediction
        df_input = pd.DataFrame([record])
        prediction = pipeline.predict(df_input)[0]
        
        # Fetch matching records
        results = list(collection.find(
            {"root_cause": prediction},
            {"_id": 0, "why1": 1, "why2": 1, "why3": 1, "why4": 1, "why5": 1, "solution": 1}
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
                "solution": result.get("solution", "")
            }
        
        return {
            "prediction": prediction,
            "five_why": five_why
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# NEW prediction endpoint with all features
@app.post("/predict-enhanced")
def predict_root_cause_enhanced(input_data: InputData):
    """New endpoint with all domain features"""
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    if not input_data.description or len(input_data.description.strip()) < 5:
        raise HTTPException(status_code=400, detail="Description too short")
    
    try:
        # Prepare input record
        record = {
            "issue": input_data.description,
            "environment": input_data.environment,
            "operating_load": input_data.operating_load,
            "recent_maintenance": input_data.recent_maintenance,
            "severity": input_data.severity,
            "shift_time": input_data.shift_time,
            "machine_age_bucket": input_data.machine_age_bucket,
            "maintenance_gap_days": input_data.maintenance_gap_days,
            "failure_frequency": input_data.failure_frequency
        }
        
        # Make prediction
        df_input = pd.DataFrame([record])
        prediction = pipeline.predict(df_input)[0]
        probabilities = pipeline.predict_proba(df_input)[0]
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
            # Take the first matching result
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
                "root_cause": pipeline.classes_[idx],
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
#
# ANALYTICS PLOTS ENDPOINT
# 

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
