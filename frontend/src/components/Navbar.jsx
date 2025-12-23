import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
    return (
        <nav className="navbar gradient-navbar">
            <div className="nav-container">
                <div className="nav-logo">
                    <h1>🔍 Smart 5-Why Analyzer</h1>
                </div>
                <div className="nav-links">
                    <Link to="/">Dashboard</Link>
                    <Link to="/predict">Predict</Link>
                    <Link to="/analytics">Analytics</Link>
                    <Link to="/manage">Manage Data</Link>
                </div>
                <div className="nav-user">
                    <span>👤 Admin</span>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;