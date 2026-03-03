// frontend/src/components/Navbar.jsx

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Logo from './LOGO.png';
import './Navbar.css';

const Navbar = () => {
    const { user, logout, isAuthenticated } = useAuth();
    const navigate = useNavigate();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth <= 768);
            if (window.innerWidth > 768) {
                setIsMobileMenuOpen(false);
            }
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const toggleMobileMenu = () => {
        setIsMobileMenuOpen(!isMobileMenuOpen);
    };

    const closeMobileMenu = () => {
        setIsMobileMenuOpen(false);
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
        closeMobileMenu();
    };

    if (!isAuthenticated) return null;

    return (
        <>
            <nav className="navbar gradient-navbar">
                <div className="nav-container">
                    <div className="nav-logo">
                        <img src={Logo} alt="Logo" className="logo-image" />
                        <h1>Equipments Root Cause Analyzer</h1>
                    </div>
                    
                    <div className="nav-links">
                        <Link to="/" onClick={closeMobileMenu}>Dashboard</Link>
                        <Link to="/predict" onClick={closeMobileMenu}>Predict</Link>
                        <Link to="/analytics" onClick={closeMobileMenu}>Analytics</Link>
                        <Link to="/manage" onClick={closeMobileMenu}>Manage Data</Link>
                    </div>
                    
                    <div className="nav-user">
                        <span>👤 {user?.full_name} ({user?.role})</span>
                        <button onClick={handleLogout} className="logout-btn">
                            🚪 Logout
                        </button>
                    </div>
                    
                    {isMobile && (
                        <div 
                            id="hamburger" 
                            className={isMobileMenuOpen ? 'open' : ''}
                            onClick={toggleMobileMenu}
                        >
                            <div className="hamburger-line"></div>
                            <div className="hamburger-line"></div>
                            <div className="hamburger-line"></div>
                        </div>
                    )}
                </div>
            </nav>
            
            {isMobile && (
                <div className={`mobile-overlay ${isMobileMenuOpen ? 'open' : ''}`}>
                    <div className="mobile-links">
                        <Link to="/" onClick={closeMobileMenu}>Dashboard</Link>
                        <Link to="/predict" onClick={closeMobileMenu}>Predict</Link>
                        <Link to="/analytics" onClick={closeMobileMenu}>Analytics</Link>
                        <Link to="/manage" onClick={closeMobileMenu}>Manage Data</Link>
                        
                        <Link to="/change-password" className="change-password-link">
                            🔑 Change Password
                        </Link>
                    </div>
                    <div style={{ marginTop: '30px', color: 'white', fontSize: '18px', textAlign: 'center' }}>
                        👤 {user?.full_name} ({user?.role})
                        <button 
                            onClick={handleLogout}
                            style={{
                                marginLeft: '10px',
                                padding: '5px 15px',
                                background: '#ff4444',
                                color: 'white',
                                border: 'none',
                                borderRadius: '5px',
                                cursor: 'pointer'
                            }}
                        >
                            Logout
                        </button>
                    </div>
                </div>
            )}
        </>
    );
};

export default Navbar;