import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import Predict from './components/Predict';
import Analytics from './components/Analytics';
import DataManager from './components/DataManager';
import './styles/App.css';

function App() {
    return (
        <Router>
            <div className="app-container">
                <Navbar />
                <div className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/predict" element={<Predict />} />
                        <Route path="/analytics" element={<Analytics />} />
                        <Route path="/manage" element={<DataManager />} />
                    </Routes>
                </div>
                <footer className="app-footer">
                    <p> &copy; {new Date().getFullYear()} Smart 5-Why Root Cause Predictor System | Designed with accessibility in mind</p>
                </footer>
            </div>
        </Router>
    );
}

export default App;
