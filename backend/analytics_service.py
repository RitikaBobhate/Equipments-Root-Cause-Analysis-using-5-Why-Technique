import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pymongo import MongoClient
import plotly.io as pio
import json
from datetime import datetime

pio.templates.default = "plotly_white"

client = MongoClient("mongodb+srv://RIL_sys:M(>$s8!p@rootcause-db.wayefpy.mongodb.net/?appName=rootcause-db")
db = client["fivewhy_db"]
collection = db["equipment_data"]

def generate_dashboard_plots():
    """Generate analytics plots and return them in a frontend-friendly format"""
    
    try:
        data = list(collection.find({}, {"_id": 0}))
        if not data:
            return {"error": "No data available", "message": "Database is empty"}
        
        df = pd.DataFrame(data)
        
        if df.empty:
            return {"error": "No data available", "message": "DataFrame is empty"}
        
        plots_data = {
            "charts": {},
            "stats": {},
            "data": {}
        }
        
        # ========== 1. SEVERITY DISTRIBUTION ==========
        if 'severity' in df.columns and not df['severity'].empty:
            severity_counts = df['severity'].value_counts()
            
            # Create data for frontend
            plots_data["data"]["severity"] = {
                "labels": severity_counts.index.tolist(),
                "values": severity_counts.values.tolist(),
                "colors": ['#FF6B6B', '#FFD166', '#06D6A0', '#118AB2']
            }
            
            # Create simplified chart data
            fig_severity = go.Figure(data=[go.Pie(
                labels=severity_counts.index,
                values=severity_counts.values,
                hole=.3,
                marker_colors=['#FF6B6B', '#FFD166', '#06D6A0']
            )])
            fig_severity.update_layout(
                title="Issue Severity Distribution",
                height=400,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            # Convert to JSON for Plotly
            plots_data["charts"]["severity"] = fig_severity.to_dict()
            plots_data["stats"]["severity"] = severity_counts.to_dict()
        
        # ========== 2. TOP ROOT CAUSES ==========
        if 'root_cause' in df.columns and not df['root_cause'].empty:
            top_causes = df['root_cause'].value_counts().head(100)
            
            plots_data["data"]["root_causes"] = {
                "labels": top_causes.index.tolist(),
                "values": top_causes.values.tolist()
            }
            
            fig_causes = go.Figure(data=[go.Bar(
                x=top_causes.values,
                y=top_causes.index,
                orientation='h',
                marker_color='#118AB2',
                text=top_causes.values,
                textposition='outside'
            )])
            fig_causes.update_layout(
                title="Top 10 Root Causes",
                xaxis_title="Count",
                yaxis_title="Root Cause",
                height=500,
                margin=dict(l=150, r=50, t=50, b=50)
            )
            
            plots_data["charts"]["root_causes"] = fig_causes.to_dict()
            plots_data["stats"]["top_causes"] = top_causes.to_dict()
        
        # ========== 3. DEPARTMENT DISTRIBUTION ==========
        if 'department' in df.columns and not df['department'].empty:
            dept_counts = df['department'].value_counts()
            
            plots_data["data"]["departments"] = {
                "labels": dept_counts.index.tolist(),
                "values": dept_counts.values.tolist()
            }
            
            fig_dept = go.Figure(data=[go.Bar(
                x=dept_counts.index,
                y=dept_counts.values,
                marker_color='#06D6A0',
                text=dept_counts.values,
                textposition='auto'
            )])
            fig_dept.update_layout(
                title="Issues by Department",
                xaxis_title="Department",
                yaxis_title="Count",
                height=400,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            plots_data["charts"]["departments"] = fig_dept.to_dict()
            plots_data["stats"]["departments"] = dept_counts.to_dict()
        
        # ========== 4. EQUIPMENT TYPE DISTRIBUTION ==========
        if 'equipment_type' in df.columns and not df['equipment_type'].empty:
            eq_counts = df['equipment_type'].value_counts()
            
            plots_data["data"]["equipment"] = {
                "labels": eq_counts.index.tolist(),
                "values": eq_counts.values.tolist()
            }
            
            fig_eq = go.Figure(data=[go.Bar(
                x=eq_counts.index,
                y=eq_counts.values,
                marker_color='#EF476F',
                text=eq_counts.values,
                textposition='auto'
            )])
            fig_eq.update_layout(
                title="Equipment Type Distribution",
                xaxis_title="Equipment Type",
                yaxis_title="Count",
                height=400,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            plots_data["charts"]["equipment"] = fig_eq.to_dict()
            plots_data["stats"]["equipment"] = eq_counts.to_dict()
        
        # ========== 5. MONTHLY TRENDS ==========
        if 'date_reported' in df.columns and not df['date_reported'].empty:
            try:
                df['month'] = pd.to_datetime(df['date_reported']).dt.strftime('%Y-%m')
                monthly_counts = df['month'].value_counts().sort_index()
                
                plots_data["data"]["trends"] = {
                    "labels": monthly_counts.index.tolist(),
                    "values": monthly_counts.values.tolist()
                }
                
                fig_trend = go.Figure(data=[go.Scatter(
                    x=monthly_counts.index,
                    y=monthly_counts.values,
                    mode='lines+markers',
                    line=dict(color='#7B2CBF', width=3),
                    marker=dict(size=8, color='#7B2CBF'),
                    fill='tozeroy',
                    fillcolor='rgba(123, 44, 191, 0.2)'
                )])
                fig_trend.update_layout(
                    title="Monthly Trend of Issues",
                    xaxis_title="Month",
                    yaxis_title="Count",
                    height=400,
                    margin=dict(t=50, b=50, l=50, r=50)
                )
                
                plots_data["charts"]["trends"] = fig_trend.to_dict()
                plots_data["stats"]["trends"] = monthly_counts.to_dict()
                
            except Exception as e:
                plots_data["error"] = f"Could not generate trend chart: {str(e)}"
        
        # ========== 6. DOMAIN FEATURES ==========
        domain_features = ['shift_time', 'machine_age_bucket', 'maintenance_gap_days', 'failure_frequency']
        
        for feature in domain_features:
            if feature in df.columns and not df[feature].empty:
                counts = df[feature].value_counts()
                plots_data["stats"][feature] = counts.to_dict()
                
                # Create simple chart data
                plots_data["data"][feature] = {
                    "labels": counts.index.tolist(),
                    "values": counts.values.tolist()
                }
        
        # ========== 7. OVERALL STATISTICS ==========
        plots_data["overall_stats"] = {
            "total_records": len(df),
            "unique_equipment": df['equipment_type'].nunique() if 'equipment_type' in df.columns else 0,
            "unique_root_causes": df['root_cause'].nunique() if 'root_cause' in df.columns else 0,
            "unique_departments": df['department'].nunique() if 'department' in df.columns else 0,
            "generated_at": datetime.now().isoformat()
        }
        
        return plots_data
        
    except Exception as e:
        return {
            "error": "Failed to generate plots",
            "details": str(e),
            "timestamp": datetime.now().isoformat()
        }

def generate_simple_plots():
    """Generate very simple data for frontend charts"""
    
    try:
        data = list(collection.find({}, {"_id": 0}))
        if not data:
            return {"error": "No data available"}
        
        df = pd.DataFrame(data)
        
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "charts": {}
        }
        
        # Severity Chart
        if 'severity' in df.columns:
            severity = df['severity'].value_counts()
            response["charts"]["severity"] = {
                "type": "pie",
                "data": {
                    "labels": severity.index.tolist(),
                    "datasets": [{
                        "data": severity.values.tolist(),
                        "backgroundColor": ['#FF6B6B', '#FFD166', '#06D6A0']
                    }]
                },
                "options": {
                    "title": "Issue Severity Distribution"
                }
            }
        
        # Root Causes Chart
        if 'root_cause' in df.columns:
            causes = df['root_cause'].value_counts().head(10)
            response["charts"]["root_causes"] = {
                "type": "bar",
                "data": {
                    "labels": causes.index.tolist(),
                    "datasets": [{
                        "label": "Count",
                        "data": causes.values.tolist(),
                        "backgroundColor": '#118AB2'
                    }]
                },
                "options": {
                    "indexAxis": 'y',
                    "title": "Top 10 Root Causes"
                }
            }
        
        # Department Chart
        if 'department' in df.columns:
            dept = df['department'].value_counts()
            response["charts"]["departments"] = {
                "type": "bar",
                "data": {
                    "labels": dept.index.tolist(),
                    "datasets": [{
                        "label": "Count",
                        "data": dept.values.tolist(),
                        "backgroundColor": '#06D6A0'
                    }]
                },
                "options": {
                    "title": "Issues by Department"
                }
            }
        
        # Equipment Chart
        if 'equipment_type' in df.columns:
            equipment = df['equipment_type'].value_counts()
            response["charts"]["equipment"] = {
                "type": "bar",
                "data": {
                    "labels": equipment.index.tolist(),
                    "datasets": [{
                        "label": "Count",
                        "data": equipment.values.tolist(),
                        "backgroundColor": '#EF476F'
                    }]
                },
                "options": {
                    "title": "Equipment Type Distribution"
                }
            }
        
        # Stats
        response["stats"] = {
            "total": len(df),
            "unique_root_causes": df['root_cause'].nunique() if 'root_cause' in df.columns else 0,
            "unique_equipment": df['equipment_type'].nunique() if 'equipment_type' in df.columns else 0,
            "unique_departments": df['department'].nunique() if 'department' in df.columns else 0
        }
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Test function
if __name__ == "__main__":
    print("Testing analytics service...")
    
    print("\n1. Testing generate_dashboard_plots():")
    result1 = generate_dashboard_plots()
    if "error" in result1:
        print(f"Error: {result1['error']}")
    else:
        print(f"Success! Generated charts: {list(result1.get('charts', {}).keys())}")
        print(f"Total records: {result1.get('overall_stats', {}).get('total_records', 0)}")
    
    print("\n2. Testing generate_simple_plots():")
    result2 = generate_simple_plots()
    if result2.get("success"):
        print(f"Success! Generated {len(result2.get('charts', {}))} charts")
    else:
        print(f"Error: {result2.get('error')}")
        
        
        