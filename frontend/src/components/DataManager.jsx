import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DataManager.css';

const DataManager = () => {
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);
    const [formData, setFormData] = useState({
        equipment_id: '',
        equipment_type: '',
        issue: '',
        root_cause: '',
        why1: '',
        why2: '',
        why3: '',
        why4: '',
        why5: '',
        solution: '',
        department: '',
        severity: 'Medium',
        date_reported: new Date().toISOString().split('T')[0]
    });

    useEffect(() => {
        fetchRecords();
    }, []);

    const fetchRecords = async () => {
        try {
            const response = await axios.get('http://localhost:8000/all-data');
            setRecords(response.data.data);
        } catch (error) {
            console.error('Error fetching records:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingRecord) {
                await axios.put(`http://127.0.0.1:8000/update-record/${formData.equipment_id}`, formData);
            } else {
                await axios.post('http://127.0.0.1:8000/add-record', formData);
            }
            fetchRecords();
            resetForm();
            setShowForm(false);
        } catch (error) {
            console.error('Error saving record:', error);
            alert('Failed to save record');
        }
    };

    const handleEdit = (record) => {
        setEditingRecord(record);
        setFormData(record);
        setShowForm(true);
    };

    const handleDelete = async (equipmentId) => {
        if (window.confirm('Are you sure you want to delete this record?')) {
            try {
                await axios.delete(`http://127.0.0.1:8000/delete-record/${equipmentId}`);
                fetchRecords();
            } catch (error) {
                console.error('Error deleting record:', error);
                alert('Failed to delete record');
            }
        }
    };

    const resetForm = () => {
        setFormData({
            equipment_id: '',
            equipment_type: '',
            issue: '',
            root_cause: '',
            why1: '',
            why2: '',
            why3: '',
            why4: '',
            why5: '',
            solution: '',
            department: '',
            severity: 'High',
            date_reported: new Date().StoISOString().split('T')[0]
        });
        setEditingRecord(null);
    };

    if (loading) {
        return <div className="loading">Loading records...</div>;
    }

    return (
        <div className="data-manager-container">
            <div className="data-manager-header">
                <h1>📋 Data Management</h1>
                <p>Manage your equipment issue records with full CRUD operations</p>
            </div>

            <div className="data-manager-actions">
                <button 
                    onClick={() => setShowForm(!showForm)}
                    className="add-record-btn gradient-btn-primary"
                >
                    {showForm ? '✕ Cancel' : '➕ Add New Record'}
                </button>
                <button 
                    onClick={fetchRecords}
                    className="refresh-btn gradient-btn-secondary"
                >
                    🔄 Refresh
                </button>
            </div>

            {showForm && (
                <div className="record-form gradient-form">
                    <h3>{editingRecord ? '✏️ Edit Record' : '➕ Add New Record'}</h3>
                    <form onSubmit={handleSubmit}>
                        <div className="form-grid">
                            <div className="form-group">
                                <label>Equipment ID *</label>
                                <input
                                    type="text"
                                    name="equipment_id"
                                    value={formData.equipment_id}
                                    onChange={handleInputChange}
                                    required
                                    disabled={editingRecord}
                                />
                            </div>

                            <div className="form-group">
                                <label>Equipment Type *</label>
                                <select
                                    name="equipment_type"
                                    value={formData.equipment_type}
                                    onChange={handleInputChange}
                                    required
                                >
                                    <option value="">Select Type</option>
                                    <option value="Motor">Motor</option>
                                    <option value="Pump">Pump</option>
                                    <option value="Conveyor">Conveyor</option>
                                    <option value="Compressor">Compressor</option>
                                    <option value="Generator">Generator</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label>Department *</label>
                                <select
                                    name="department"
                                    value={formData.department}
                                    onChange={handleInputChange}
                                    required
                                >
                                    <option value="">Select Department</option>
                                    <option value="Production">Production</option>
                                    <option value="Maintenance">Maintenance</option>
                                    <option value="Quality">Quality</option>
                                    <option value="Engineering">Engineering</option>
                                    <option value="Operations">Operations</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label>Severity *</label>
                                <select
                                    name="severity"
                                    value={formData.severity}
                                    onChange={handleInputChange}
                                    required
                                >
                                    <option value="Low">Low</option>
                                    <option value="Medium">Medium</option>
                                    <option value="High">High</option>
                                    <option value="Critical">Critical</option>
                                </select>
                            </div>

                            <div className="form-group full-width">
                                <label>Issue Description *</label>
                                <textarea
                                    name="issue"
                                    value={formData.issue}
                                    onChange={handleInputChange}
                                    rows="3"
                                    required
                                />
                            </div>

                            <div className="form-group full-width">
                                <label>Root Cause *</label>
                                <input
                                    type="text"
                                    name="root_cause"
                                    value={formData.root_cause}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>

                            {[1, 2, 3, 4, 5].map(num => (
                                <div className="form-group" key={num}>
                                    <label>Why {num}</label>
                                    <input
                                        type="text"
                                        name={`why${num}`}
                                        value={formData[`why${num}`]}
                                        onChange={handleInputChange}
                                    />
                                </div>
                            ))}

                            <div className="form-group full-width">
                                <label>Solution</label>
                                <textarea
                                    name="solution"
                                    value={formData.solution}
                                    onChange={handleInputChange}
                                    rows="2"
                                />
                            </div>

                            <div className="form-group">
                                <label>Date Reported</label>
                                <input
                                    type="date"
                                    name="date_reported"
                                    value={formData.date_reported}
                                    onChange={handleInputChange}
                                />
                            </div>
                        </div>

                        <div className="form-actions">
                            <button type="submit" className="submit-btn gradient-btn-primary">
                                {editingRecord ? 'Update Record' : 'Add Record'}
                            </button>
                            <button type="button" onClick={resetForm} className="reset-btn">
                                Reset
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="records-table-container">
                <h3>📁 Existing Records ({records.length})</h3>
                
                <div className="table-responsive">
                    <table className="records-table">
                        <thead>
                            <tr>
                                <th>Equipment ID</th>
                                <th>Type</th>
                                <th>Issue</th>
                                <th>Root Cause</th>
                                <th>Severity</th>
                                <th>Department</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {records.map((record, index) => (
                                <tr key={index}>
                                    <td>{record.equipment_id}</td>
                                    <td>{record.equipment_type}</td>
                                    <td className="truncate-text" title={record.issue}>
                                        {record.issue.substring(0, 50)}...
                                    </td>
                                    <td>{record.root_cause}</td>
                                    <td>
                                        <span className={`severity-badge severity-${record.severity?.toLowerCase()}`}>
                                            {record.severity}
                                        </span>
                                    </td>
                                    <td>{record.department}</td>
                                    <td>{record.date_reported}</td>
                                    <td className="action-buttons">
                                        <button 
                                            onClick={() => handleEdit(record)}
                                            className="edit-btn"
                                            title="Edit"
                                        >
                                            ✏️
                                        </button>
                                        <button 
                                            onClick={() => handleDelete(record.equipment_id)}
                                            className="delete-btn"
                                            title="Delete"
                                        >
                                            🗑️
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default DataManager;