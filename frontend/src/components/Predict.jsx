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
        const saved = localStorage.getItem('predictionHistory');
        if (saved) {
            setHistory(JSON.parse(saved));
        }
    }, []);

    const predictNow = async () => {
        if (!text.trim()) {
            alert('Please enter a description');
            return;
        }

        setLoading(true);
        try {
            const res = await axios.post(
                'http://127.0.0.1:8000/predict-hybrid',
                {
                    description: text,
                    severity: "high",
                    shift_time: "night",
                    machine_age_bucket: "old",
                    maintenance_gap_days: "overdue",
                    failure_frequency: "high"
                }
            );

            setResult(res.data);

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
            setSuggestions([]);
        } catch (error) {
            console.error(error);
            alert(
                error.response?.data?.detail ||
                'Failed to get prediction from server'
            );
        } finally {
            setLoading(false);
        }
    };

    const fetchSuggestions = (query) => {
        if (query.length < 3) {
            setSuggestions([]);
            return;
        }

        const mockSuggestions = [
            'motor overheating and vibration',
            'bearing failure due to lubrication',
            'pump leakage during night shift',
            'conveyor belt tear',
            'sensor malfunction causing false alarms'
        ].filter(item =>
            item.toLowerCase().includes(query.toLowerCase())
        );

        setSuggestions(mockSuggestions);
    };

    const handleInputChange = (e) => {
        const value = e.target.value;
        setText(value);
        fetchSuggestions(value);
    };

    return (
        <div className="predict-container">
            <div className="predict-header">
                <h1>🔍 Smart Root Cause Predictor</h1>
               
            </div>

            <div className="predict-main">
                <div className="input-section">
                    <label>Issue Description</label>
                    <textarea
                        rows="6"
                        placeholder="Example: Motor overheating and vibration during night shift..."
                        value={text}
                        onChange={handleInputChange}
                        className="issue-textarea"
                    />

                    {suggestions.length > 0 && (
                        <div className="suggestions-box">
                            {suggestions.map((s, i) => (
                                <div
                                    key={i}
                                    className="suggestion-item"
                                    onClick={() => {
                                        setText(s);
                                        setSuggestions([]);
                                    }}
                                >
                                    {s}
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

                    {result && (
                        <div className="result-section gradient-result">
                            <h3>📊 Analysis Result</h3>

                            <p className="root-cause">
                                <strong>Prediction:</strong> {result.prediction}
                            </p>

                            <p>
                                <strong>Confidence:</strong>{' '}
                                {(result.confidence * 100).toFixed(1)}%
                            </p>

                            <p>
                                <strong>Method Used:</strong>{' '}
                                {result.method === 'ml'
                                    ? 'Machine Learning'
                                    : 'Groq LLM'}
                            </p>

                            {result.reasoning && (
                                <p>
                                    <strong>LLM Reasoning:</strong>{' '}
                                    {result.reasoning}
                                </p>
                            )}

                            {result.five_why && (
                                <div className="why-analysis">
                                    <h4>🎯 5-Why Analysis</h4>
                                    {['why1','why2','why3','why4','why5'].map((k, i) => (
                                        <p key={k}>
                                            <strong>Why {i + 1}:</strong>{' '}
                                            {result.five_why[k]}
                                        </p>
                                    ))}
                                </div>
                            )}

                            {result.five_why?.solution && (
                                <div className="solution-section">
                                    <h4>💡 Recommended Solution</h4>
                                    <p>{result.five_why.solution}</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <div className="history-section">
                    <h3>📜 Recent Predictions</h3>
                    {history.length === 0 ? (
                        <p>No predictions yet</p>
                    ) : (
                        history.map((item, i) => (
                            <div key={i} className="history-card">
                                <strong>{item.prediction}</strong>
                                <div>{item.timestamp}</div>
                                <p>{item.description.slice(0, 80)}...</p>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default Predict;
