// frontend/src/App.js

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';  // ✅ ADD THIS IMPORT
import PrivateRoute from './components/PrivateRoute';   // ✅ ADD THIS IMPORT
import Login from './components/Login';                 // ✅ ADD THIS IMPORT
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import Predict from './components/Predict';
import Analytics from './components/Analytics';
import DataManager from './components/DataManager';
import axios from 'axios';                              // ✅ ADD THIS IMPORT
import './styles/App.css';
import Register from './components/Register';

// Setup axios defaults
axios.defaults.baseURL = 'http://localhost:8000';

function App() {
    return (
        <AuthProvider>  {/* ✅ WRAP EVERYTHING WITH AuthProvider */}
            <Router>
                <div className="app-container">
                    <Navbar />
                    
                    <div className="main-content">
                        <Routes>
                            {/* Public route - no authentication needed */}
                            <Route path="/login" element={<Login />} />
                            <Route path="/register" element={<Register />} />
                            {/* Protected routes - require authentication */}
                            <Route path="/" element={
                                <PrivateRoute>
                                    <Dashboard />
                                </PrivateRoute>
                            } />
                            
                            <Route path="/predict" element={
                                <PrivateRoute>
                                    <Predict />
                                </PrivateRoute>
                            } />
                            
                            <Route path="/analytics" element={
                                <PrivateRoute>
                                    <Analytics />
                                </PrivateRoute>
                            } />
                            
                            <Route path="/manage" element={
                                <PrivateRoute>
                                    <DataManager />
                                </PrivateRoute>
                            } />
                        </Routes>
                    </div>
                    
                    <footer className="app-footer">
                        <p>
                            &copy; {new Date().getFullYear()} Smart 5-Why Root Cause Predictor System | Designed with accessibility in mind
                        </p>
                    </footer>
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App;