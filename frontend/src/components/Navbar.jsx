import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

    // Check screen size on resize
    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth <= 768);
            // Close mobile menu when resizing to desktop
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

    return (
        <>
            <nav className="navbar gradient-navbar">
                <div className="nav-container">
                    <div className="nav-logo">
                        <img src="/LOGO.png" alt="Logo" height="70" />
                        <h1>Equipments Root Cause Analyzer</h1>
                    </div>
                    
                    {/* Desktop Navigation Links */}
                    <div className="nav-links">
                        <Link to="/">Dashboard</Link>
                        <Link to="/predict">Predict</Link>
                        <Link to="/analytics">Analytics</Link>
                        <Link to="/manage">Manage Data</Link>
                    </div>
                    
                    {/* Desktop User Info */}
                    
                    
                    {/* Hamburger Menu Icon (Mobile Only) */}
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
            
            {/* Mobile Menu Overlay */}
            {isMobile && (
                <div className={`mobile-overlay ${isMobileMenuOpen ? 'open' : ''}`}>
                    <div className="mobile-links">
                        <Link to="/" onClick={closeMobileMenu}>Dashboard</Link>
                        <Link to="/predict" onClick={closeMobileMenu}>Predict</Link>
                        <Link to="/analytics" onClick={closeMobileMenu}>Analytics</Link>
                        <Link to="/manage" onClick={closeMobileMenu}>Manage Data</Link>
                    </div>
                    <div style={{ marginTop: '30px', color: 'white', fontSize: '18px' }}>
                        👤 Admin
                    </div>
                </div>
            )}
        </>
    );
};

export default Navbar;
