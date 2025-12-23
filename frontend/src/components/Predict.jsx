import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Predict.css';

const Predict = () => {
    const [text, setText] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const [history, setHistory] = useState([]);

    useEffect(() => {
        loadRecentPredictions();
    }, []);

    const loadRecentPredictions = () => {
        const saved = localStorage.getItem('predictionHistory');
        if (saved) {
            setHistory(JSON.parse(saved));
        }
    };

    const predictNow = async () => {
        if (!text.trim()) {
            alert('Please enter a description');
            return;
        }

        setLoading(true);
        try {
            const res = await axios.post('http://127.0.0.1:8000/predict', {
                description: text,
            });
            setResult(res.data);

            // Save to history
            const newHistory = [
                {
                    description: text,
                    prediction: res.data.prediction,
                    timestamp: new Date().toLocaleString(),
                    five_why: res.data.five_why
                },
                ...history.slice(0, 4)
            ];
            setHistory(newHistory);
            localStorage.setItem('predictionHistory', JSON.stringify(newHistory));

            // Clear suggestions
            setSuggestions([]);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to get prediction. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const fetchSuggestions = async (query) => {
        if (query.length < 3) {
            setSuggestions([]);
            return;
        }
        // You can implement API for suggestions here
        const mockSuggestions = [
            'motor overheating',
            'bearing failure',
            'pump leakage',
            'conveyor belt tear',
            'sensor malfunction'
        ].filter(item => item.toLowerCase().includes(query.toLowerCase()));
        setSuggestions(mockSuggestions);
    };

    const handleInputChange = (e) => {
        const value = e.target.value;
        setText(value);
        fetchSuggestions(value);
    };

    const handleSuggestionClick = (suggestion) => {
        setText(suggestion);
        setSuggestions([]);
    };

    return (
        <div className="predict-container">
            <div className="predict-header">
                <h1>🔍 Smart Root Cause Predictor</h1>
                <p>Enter issue description to predict root cause using 5-Why analysis</p>
            </div>

            <div className="predict-main">
                <div className="input-section">
                    <div className="input-container">
                        <label htmlFor="issueInput">Issue Description</label>
                        <textarea
                            id="issueInput"
                            rows="6"
                            placeholder="Example: Motor is making loud grinding noise and overheating during operation..."
                            value={text}
                            onChange={handleInputChange}
                            className="issue-textarea"
                        />
                        
                        {suggestions.length > 0 && (
                            <div className="suggestions-box">
                                {suggestions.map((suggestion, index) => (
                                    <div
                                        key={index}
                                        className="suggestion-item"
                                        onClick={() => handleSuggestionClick(suggestion)}
                                    >
                                        {suggestion}
                                    </div>
                                ))}
                            </div>
                        )}

                        <button 
                            onClick={predictNow} 
                            disabled={loading}
                            className="predict-btn gradient-btn-primary"
                        >
                            {loading ? 'Analyzing...' : '🔍 Predict Root Cause'}
                        </button>
                    </div>

                    {result && (
                        <div className="result-section gradient-result">
                            <h3>📊 Analysis Results</h3>
                            
                            <div className="result-card">
                                <h4>Predicted Root Cause</h4>
                                <p className="root-cause">{result.prediction}</p>
                            </div>

                            {result.five_why && (
                                <div className="why-analysis">
                                    <h4>🎯 5-Why Analysis</h4>
                                    <div className="why-steps">
                                        <div className="why-step">
                                            <span className="step-number">1</span>
                                            <p><strong>Why 1:</strong> {result.five_why.why1}</p>
                                        </div>
                                        <div className="why-step">
                                            <span className="step-number">2</span>
                                            <p><strong>Why 2:</strong> {result.five_why.why2}</p>
                                        </div>
                                        <div className="why-step">
                                            <span className="step-number">3</span>
                                            <p><strong>Why 3:</strong> {result.five_why.why3}</p>
                                        </div>
                                        <div className="why-step">
                                            <span className="step-number">4</span>
                                            <p><strong>Why 4:</strong> {result.five_why.why4}</p>
                                        </div>
                                        <div className="why-step">
                                            <span className="step-number">5</span>
                                            <p><strong>Why 5:</strong> {result.five_why.why5}</p>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {result.five_why?.solution && (
                                <div className="solution-section">
                                    <h4>💡 Recommended Solution</h4>
                                    <p className="solution-text">{result.five_why.solution}</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <div className="history-section">
                    <h3>📜 Recent Predictions</h3>
                    {history.length === 0 ? (
                        <p className="no-history">No predictions yet. Start analyzing!</p>
                    ) : (
                        <div className="history-list">
                            {history.map((item, index) => (
                                <div key={index} className="history-card">
                                    <div className="history-header">
                                        <strong>{item.prediction}</strong>
                                        <span className="history-time">{item.timestamp}</span>
                                    </div>
                                    <p className="history-description">{item.description.substring(0, 100)}...</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Predict;