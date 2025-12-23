import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import './Analytics.css';


const Analytics = () => {
    const [plots, setPlots] = useState({});
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        fetchAnalyticsData();
    }, []);

    const fetchAnalyticsData = async () => {
        try {
            const response = await axios.get('http://localhost:8000/analytics/plots');
            setPlots(response.data);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    const renderPlot = (plotData) => {
        if (!plotData || !plotData.data) return null;
        
        return (
            <Plot
                data={plotData.data}
                layout={plotData.layout}
                config={{ responsive: true }}
                style={{ width: '100%', height: '400px' }}
            />
        );
    };

    if (loading) {
        return (
            <div className="analytics-loading">
                <div className="loading-spinner"></div>
                <p>Loading analytics data...</p>
            </div>
        );
    }

    return (
        <div className="analytics-container">
            <div className="analytics-header">
                <h1>📈 Advanced Analytics Dashboard</h1>
                <p>Interactive visualizations and insights from your data</p>
            </div>
           
            <div className="analytics-tabs">
                
                <button 
                    className={activeTab === 'overview' ? 'active' : ''}
                    onClick={() => setActiveTab('overview')}
                >
                    📊 Overview
                </button>
                <button 
                    className={activeTab === 'causes' ? 'active' : ''}
                    onClick={() => setActiveTab('causes')}
                >
                    🎯 Root Causes
                </button>
                <button 
                    className={activeTab === 'trends' ? 'active' : ''}
                    onClick={() => setActiveTab('trends')}
                >
                    📈 Trends
                </button>
                <button 
                    className={activeTab === 'distribution' ? 'active' : ''}
                    onClick={() => setActiveTab('distribution')}
                >
                    📊 Distribution
                </button>
            </div>

            <div className="analytics-content">
                {activeTab === 'overview' && (
                    <div className="charts-grid">
                        <div className="chart-card">
                            <h3>Issue Severity Distribution</h3>
                            {renderPlot(plots.severity_chart)}
                        </div>
                        <div className="chart-card">
                            <h3>Department-wise Issues</h3>
                            {renderPlot(plots.department_chart)}
                        </div>
                        <div className="chart-card">
                            <h3>Equipment Type Distribution</h3>
                            {renderPlot(plots.equipment_chart)}
                        </div>
                        <div className="chart-card">
                            <h3>Monthly Trends</h3>
                            {renderPlot(plots.trend_chart)}
                        </div>
                    </div>
                )}

                {activeTab === 'causes' && (
                    <div className="full-width-chart">
                        <div className="chart-card">
                            <h3>Top 10 Root Causes</h3>
                            {renderPlot(plots.causes_chart)}
                        </div>
                    </div>
                )}

                {activeTab === 'trends' && (
                    <div className="charts-grid">
                        <div className="chart-card">
                            <h3>Issue Trends Over Time</h3>
                            {renderPlot(plots.trend_chart)}
                        </div>
                        <div className="chart-card">
                            <h3>Severity Trends</h3>
                            {/* Add severity trend chart */}
                            <div className="placeholder-chart">
                                <p>Severity trend visualization would appear here</p>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'distribution' && (
                    <div className="charts-grid">
                        <div className="chart-card">
                            <h3>Equipment Distribution</h3>
                            {renderPlot(plots.equipment_chart)}
                        </div>
                        <div className="chart-card">
                            <h3>Department Distribution</h3>
                            {renderPlot(plots.department_chart)}
                        </div>
                    </div>
                )}
            </div>

            <div className="analytics-actions">
                <button 
                    onClick={fetchAnalyticsData}
                    className="refresh-btn gradient-btn-primary"
                >
                    🔄 Refresh Analytics
                </button>
                <button 
                    onClick={() => window.print()}
                    className="export-btn gradient-btn-secondary"
                >
                    📥 Export Report
                </button>
            </div>
        </div>
    );
};

export default Analytics;