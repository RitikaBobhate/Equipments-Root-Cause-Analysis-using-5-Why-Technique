// frontend/src/context/AuthContext.js

import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            axios.get('http://localhost:8000/auth/me')
                .then(response => {
                    setUser(response.data);
                })
                .catch(() => {
                    localStorage.removeItem('token');
                    setToken(null);
                })
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, [token]);

    const login = async (username, password) => {
        try {
            // FIX: Trim the username and password to remove accidental spaces
            const trimmedUsername = username.trim();
            const trimmedPassword = password.trim();
            
            console.log('🔍 Login attempt:', { 
                original: { username, password },
                trimmed: { username: trimmedUsername, password: trimmedPassword }
            });
            
            const response = await axios.post('http://localhost:8000/auth/login', {
                username: trimmedUsername,
                password: trimmedPassword
            });
            
            console.log('✅ Login successful:', response.data);
            
            const { access_token, user } = response.data;
            
            localStorage.setItem('token', access_token);
            axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
            setToken(access_token);
            setUser(user);
            
            return { success: true };
        } catch (error) {
            console.error('❌ Login error:', error.response?.data || error.message);
            return { 
                success: false, 
                error: error.response?.data?.detail || 'Login failed' 
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
        setToken(null);
        setUser(null);
    };

    const value = {
        user,
        token,
        loading,
        login,
        logout,
        isAuthenticated: !!user
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};