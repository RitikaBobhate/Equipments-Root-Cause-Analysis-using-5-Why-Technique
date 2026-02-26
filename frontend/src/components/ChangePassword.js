// frontend/src/components/ChangePassword.js

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import './Login.css';

const ChangePassword = () => {
    const [passwords, setPasswords] = useState({
        current: '',
        new: '',
        confirm: ''
    });
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    
    const { user, logout } = useAuth();

    const handleChange = (e) => {
        setPasswords({
            ...passwords,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');

        if (passwords.new !== passwords.confirm) {
            setError('New passwords do not match');
            return;
        }

        if (passwords.new.length < 6) {
            setError('New password must be at least 6 characters');
            return;
        }

        setLoading(true);

        try {
            // You'll need to create this endpoint in your backend
            const response = await axios.post('http://localhost:8000/auth/change-password', {
                current_password: passwords.current,
                new_password: passwords.new
            });

            setMessage('Password changed successfully!');
            setTimeout(() => {
                logout(); // Force re-login with new password
            }, 2000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to change password');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <h1>🔐 Change Password</h1>
                <h2>{user?.full_name}</h2>
                
                {error && <div className="error-message">❌ {error}</div>}
                {message && <div style={{background: '#d4edda', color: '#155724', padding: '12px', borderRadius: '8px', marginBottom: '20px'}}>✅ {message}</div>}
                
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Current Password</label>
                        <input
                            type="password"
                            name="current"
                            value={passwords.current}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    
                    <div className="form-group">
                        <label>New Password</label>
                        <input
                            type="password"
                            name="new"
                            value={passwords.new}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    
                    <div className="form-group">
                        <label>Confirm New Password</label>
                        <input
                            type="password"
                            name="confirm"
                            value={passwords.confirm}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    
                    <button type="submit" disabled={loading} className="login-btn">
                        {loading ? 'Changing...' : 'Change Password'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChangePassword;