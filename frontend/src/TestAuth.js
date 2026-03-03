// frontend/src/TestAuth.js

import React, { useState } from 'react';
import axios from 'axios';

function TestAuth() {
    const [token, setToken] = useState(localStorage.getItem('token') || '');
    const [user, setUser] = useState(null);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);

    const login = async () => {
        setLoading(true);
        try {
            const res = await axios.post('http://localhost:8000/auth/login', {
                username: "testuser",
                password: "password123"
            });
            
            const newToken = res.data.access_token;
            setToken(newToken);
            localStorage.setItem('token', newToken);
            axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
            setUser(res.data.user);
            alert('✅ Login successful!');
        } catch (error) {
            alert('❌ Login failed: ' + error.message);
        }
        setLoading(false);
    };

    const getData = async () => {
        try {
            setLoading(true);
            const res = await axios.get('http://localhost:8000/all-data');
            setData(res.data);
        } catch (error) {
            alert('❌ Failed: ' + error.message);
        }
        setLoading(false);
    };

    const logout = () => {
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
        setToken('');
        setUser(null);
        setData(null);
    };

    return (
        <div style={{ padding: '30px', maxWidth: '800px', margin: 'auto' }}>
            <h1>🔐 RCA System</h1>
            
            {!token ? (
                <button 
                    onClick={login}
                    disabled={loading}
                    style={{
                        padding: '10px 20px',
                        background: '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        fontSize: '16px'
                    }}
                >
                    {loading ? 'Logging in...' : '🔑 Login as Test User'}
                </button>
            ) : (
                <div>
                    <div style={{ 
                        background: '#e3f2fd', 
                        padding: '15px', 
                        borderRadius: '5px',
                        marginBottom: '20px'
                    }}>
                        <p><strong>✅ Logged in!</strong> as {user?.full_name} ({user?.role})</p>
                        <button onClick={logout}>Logout</button>
                    </div>

                    <button 
                        onClick={getData}
                        style={{
                            padding: '10px 20px',
                            background: '#2196F3',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px'
                        }}
                    >
                        📊 Get Protected Data
                    </button>

                    {data && (
                        <div style={{ 
                            background: '#d4edda', 
                            padding: '15px', 
                            borderRadius: '5px',
                            marginTop: '20px'
                        }}>
                            <h3>Data received! ({data.count} records)</h3>
                            <pre>{JSON.stringify(data.data.slice(0, 2), null, 2)}</pre>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default TestAuth;