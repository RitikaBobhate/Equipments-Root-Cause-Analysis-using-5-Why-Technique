// frontend/src/components/Login.js

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        // FIX: Trim the username to remove any accidental spaces
        const trimmedUsername = username.trim();
        
        console.log('Original username:', JSON.stringify(username));
        console.log('Trimmed username:', JSON.stringify(trimmedUsername));
        
        const result = await login(trimmedUsername, password);
        
        if (result.success) {
            navigate('/');
        } else {
            setError(result.error);
        }
        
        setLoading(false);
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <h1>🔐 Smart 5-Why RCA System</h1>
                <h2>Login to Dashboard</h2>
                
                {error && (
                    <div className="error-message">
                        ❌ {error}
                    </div>
                )}
                
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            placeholder="Enter username"
                        />
                        <small style={{color: '#999', display: 'block', marginTop: '5px'}}>
                            Enter: testuser (no spaces)
                        </small>
                    </div>
                    
                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="Enter password"
                        />
                    </div>
                    
                    <button 
                        type="submit" 
                        disabled={loading}
                        className="login-btn"
                    >
                        {loading ? 'Logging in...' : '🔓 Login'}
                    </button>
                    {/* Add this after the login button */}
                    <p className="register-link">
                        Don't have an account? <Link to="/register">Register here</Link>
                    </p>
                 </form>
                
                <div className="demo-info">
                    <p><strong>Demo Credentials:</strong></p>
                    <p>Username: <code>testuser</code></p>
                    <p>Password: <code>password123</code></p>
                </div>
            </div>
        </div>
    );
};

export default Login;