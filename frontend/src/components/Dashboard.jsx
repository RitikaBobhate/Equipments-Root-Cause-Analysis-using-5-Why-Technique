import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const response = await axios.get('http://localhost:8000/analytics/summary');
            setSummary(response.data);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="loading-spinner">Loading dashboard...</div>;
    }

    return (
        <div className="dashboard-container">
            <div className="dashboard-header">
                <h1>📊 Analytics Dashboard</h1>
                <p>Real-time insights from your 5-Why analysis data</p>
            </div>

            <div className="stats-grid">
                <div className="stat-card gradient-card-1">
                    <h3>Total Records</h3>
                    <h2>{summary?.total_records || 0}</h2>
                    <p>Total issues analyzed</p>
                </div>

                <div className="stat-card gradient-card-2">
                    <h3>Departments</h3>
                    <h2>{summary?.departments ? Object.keys(summary.departments).length : 0}</h2>
                    <p>Different departments</p>
                </div>

                <div className="stat-card gradient-card-3">
                    <h3>High Severity</h3>
                    <h2>{summary?.severity?.High || 0}</h2>
                    <p>Critical issues</p>
                </div>

                <div className="stat-card gradient-card-4">
                    <h3>Root Causes</h3>
                    <h2>{summary?.top_root_causes ? Object.keys(summary.top_root_causes).length : 0}</h2>
                    <p>Unique causes identified</p>
                </div>
            </div>

            <div className="quick-actions">
                <h2>🚀 Quick Actions</h2>
                <div className="action-buttons">
                    <Link to="/predict" className="action-btn gradient-btn-primary">
                        🔍 Predict Root Cause
                    </Link>
                    <Link to="/manage" className="action-btn gradient-btn-secondary">
                        📝 Add New Record
                    </Link>
                    <Link to="/analytics" className="action-btn gradient-btn-tertiary">
                        📈 View Detailed Analytics
                    </Link>
                </div>
            </div>

            <div className="recent-activity">
                <h2>📋 Recent Issues</h2>
                <div className="activity-list">
                    {summary?.top_root_causes && Object.entries(summary.top_root_causes).slice(0, 5).map(([cause, count], index) => (
                        <div key={index} className="activity-item">
                            <div className="activity-dot"></div>
                            <div className="activity-content">
                                <strong>{cause}</strong>
                                <span className="activity-count">{count} occurrences</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;