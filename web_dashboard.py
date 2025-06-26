#!/usr/bin/env python3
"""
Simple Red Flag Filter Dashboard
No external dependencies - uses only Python built-in libraries
"""

import json
import os
import sys
import webbrowser
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from red_flag_detector import RedFlagDetector, RiskLevel
except ImportError:
    print("Could not import red_flag_detector. Make sure src/red_flag_detector.py exists")
    detector = None
else:
    detector = RedFlagDetector()

class DashboardHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for the dashboard"""
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == '/' or path == '/dashboard':
            self.serve_dashboard()
        elif path == '/api/stats':
            self.serve_stats()
        elif path == '/api/alerts':
            self.serve_alerts()
        elif path == '/api/conversations':
            self.serve_conversations()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        if path == '/api/analyze':
            self.handle_analyze()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html = self.get_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_stats(self):
        """Serve statistics API"""
        stats = self.get_stats()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode())
    
    def serve_alerts(self):
        """Serve alerts API"""
        alerts = self.load_alerts()
        
        # Sort by timestamp (most recent first)
        try:
            alerts.sort(key=lambda x: datetime.fromisoformat(x.get('timestamp', '').replace('Z', '+00:00')), reverse=True)
        except:
            pass
        
        # Return last 20 alerts
        recent_alerts = alerts[-20:]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(recent_alerts).encode())
    
    def serve_conversations(self):
        """Serve conversations API"""
        conversations = self.get_conversations()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(conversations).encode())
    
    def handle_analyze(self):
        """Handle message analysis"""
        if not detector:
            self.send_error(500, "Red flag detector not available")
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            message = data.get('message', '').strip()
            if not message:
                self.send_error(400, "Message is required")
                return
            
            # Analyze the message
            analysis = detector.analyze_message(message)
            
            if not analysis:
                self.send_error(500, "Analysis failed")
                return
            
            # Format the response
            response = {
                'message': message,
                'risk_level': analysis['risk_level'].value if hasattr(analysis['risk_level'], 'value') else str(analysis['risk_level']),
                'red_flags': [
                    {
                        'category': flag.category,
                        'explanation': flag.explanation,
                        'confidence': flag.confidence
                    }
                    for flag in analysis.get('red_flags', [])
                ],
                'recommendations': analysis.get('recommendations', []),
                'confidence_score': analysis.get('confidence_score', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Analysis error: {str(e)}")
    
    def load_alerts(self):
        """Load alerts from JSON file"""
        try:
            with open('red_flag_alerts.json', 'r') as f:
                data = json.load(f)
                return data.get('alerts', [])
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
    
    def get_stats(self):
        """Get statistics about alerts"""
        alerts = self.load_alerts()
        
        stats = {
            'total_alerts': len(alerts),
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'conversations_analyzed': 0,
            'unique_senders': set(),
            'recent_alerts': 0
        }
        
        # Count alerts by risk level
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        for alert in alerts:
            risk_level = alert.get('risk_level', '').lower()
            
            if risk_level == 'critical':
                stats['critical'] += 1
            elif risk_level == 'high':
                stats['high'] += 1
            elif risk_level == 'medium':
                stats['medium'] += 1
            elif risk_level == 'low':
                stats['low'] += 1
            
            # Track unique senders
            sender = alert.get('sender', '')
            if sender:
                stats['unique_senders'].add(sender)
            
            # Count recent alerts (last 24 hours)
            try:
                alert_time = datetime.fromisoformat(alert.get('timestamp', '').replace('Z', '+00:00'))
                if alert_time.replace(tzinfo=None) > last_24h:
                    stats['recent_alerts'] += 1
            except:
                pass
        
        stats['conversations_analyzed'] = len(stats['unique_senders'])
        stats['unique_senders'] = list(stats['unique_senders'])
        
        return stats
    
    def get_conversations(self):
        """Get conversation summaries"""
        alerts = self.load_alerts()
        
        # Group alerts by sender
        conversations = {}
        for alert in alerts:
            sender = alert.get('sender', 'Unknown')
            if sender not in conversations:
                conversations[sender] = {
                    'sender': sender,
                    'total_alerts': 0,
                    'highest_risk': 'low',
                    'latest_message': '',
                    'latest_timestamp': '',
                    'red_flag_count': 0
                }
            
            conv = conversations[sender]
            conv['total_alerts'] += 1
            conv['red_flag_count'] += len(alert.get('red_flags', []))
            
            # Track highest risk level
            risk_levels = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            current_risk = risk_levels.get(alert.get('risk_level', '').lower(), 1)
            highest_risk = risk_levels.get(conv['highest_risk'], 1)
            
            if current_risk > highest_risk:
                conv['highest_risk'] = alert.get('risk_level', '').lower()
            
            # Track latest message
            try:
                alert_time = datetime.fromisoformat(alert.get('timestamp', '').replace('Z', '+00:00'))
                if not conv['latest_timestamp'] or alert_time > datetime.fromisoformat(conv['latest_timestamp'].replace('Z', '+00:00')):
                    conv['latest_message'] = alert.get('message', '')[:100] + ('...' if len(alert.get('message', '')) > 100 else '')
                    conv['latest_timestamp'] = alert.get('timestamp', '')
            except:
                if not conv['latest_message']:
                    conv['latest_message'] = alert.get('message', '')[:100] + ('...' if len(alert.get('message', '')) > 100 else '')
        
        # Convert to list and sort by risk level
        conversation_list = list(conversations.values())
        risk_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        conversation_list.sort(key=lambda x: risk_order.get(x['highest_risk'], 1), reverse=True)
        
        return conversation_list
    
    def get_dashboard_html(self):
        """Generate the dashboard HTML"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Red Flag Filter Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            color: #333;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9rem;
        }
        
        .critical { color: #e74c3c; }
        .high { color: #f39c12; }
        .medium { color: #f1c40f; }
        .low { color: #27ae60; }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
        
        .message-tester {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .message-tester h2 {
            margin-bottom: 20px;
            color: #333;
        }
        
        .demo-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .demo-btn {
            padding: 8px 12px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: opacity 0.3s ease;
        }
        
        .demo-btn:hover {
            opacity: 0.8;
        }
        
        .demo-safe { background: #d4edda; color: #155724; }
        .demo-medium { background: #fff3cd; color: #856404; }
        .demo-critical { background: #f8d7da; color: #721c24; }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        #messageInput {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        #messageInput:focus {
            outline: none;
            border-color: #667eea;
        }
        
        #analyzeBtn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        
        #analyzeBtn:hover {
            transform: translateY(-2px);
        }
        
        #analyzeBtn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .result-card {
            margin-top: 20px;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid;
            display: none;
        }
        
        .real-data-section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .real-data-section h2 {
            margin-bottom: 20px;
            color: #333;
        }
        
        .conversations-grid {
            display: grid;
            gap: 15px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .conversation-card {
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid;
            background: #f8f9fa;
        }
        
        .conversation-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .sender-name {
            font-weight: bold;
            color: #333;
        }
        
        .risk-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
            color: white;
        }
        
        .conversation-stats {
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 8px;
        }
        
        .latest-message {
            font-style: italic;
            color: #555;
            font-size: 0.9rem;
        }
        
        .recent-alerts {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            margin-top: 30px;
        }
        
        .recent-alerts h2 {
            margin-bottom: 20px;
            color: #333;
        }
        
        .alerts-list {
            max-height: 500px;
            overflow-y: auto;
        }
        
        .alert-item {
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 5px solid;
            background: #f8f9fa;
        }
        
        .alert-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .alert-sender {
            font-weight: bold;
            color: #333;
        }
        
        .alert-time {
            color: #999;
            font-size: 0.8rem;
        }
        
        .alert-message {
            margin-bottom: 10px;
            padding: 10px;
            background: white;
            border-radius: 8px;
            font-style: italic;
        }
        
        .alert-flags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .flag-tag {
            padding: 4px 8px;
            background: #e9ecef;
            border-radius: 12px;
            font-size: 0.75rem;
            color: #495057;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-radius: 50%;
            border-top: 3px solid #667eea;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .no-data {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .refresh-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-left: 10px;
            transition: background 0.3s ease;
        }
        
        .refresh-btn:hover {
            background: #218838;
        }
        
        .status {
            text-align: center;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 8px;
            background: #d1ecf1;
            color: #0c5460;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Red Flag Filter Dashboard</h1>
            <p>AI-Powered Instagram DM Safety Analysis</p>
        </div>
        
        <div class="status">
            <strong>Simple Dashboard:</strong> No external dependencies required! Updates automatically every 30 seconds.
        </div>
        
        <!-- Statistics Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-number" id="totalAlerts">0</div>
                <div class="stat-label">Total Alerts</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon critical">🚨</div>
                <div class="stat-number critical" id="criticalAlerts">0</div>
                <div class="stat-label">Critical Threats</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">💬</div>
                <div class="stat-number" id="conversationsAnalyzed">0</div>
                <div class="stat-label">Conversations Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⏰</div>
                <div class="stat-number" id="recentAlerts">0</div>
                <div class="stat-label">Last 24 Hours</div>
            </div>
        </div>
        
        <!-- Main Content Grid -->
        <div class="main-content">
            <!-- Live Message Tester -->
            <div class="message-tester">
                <h2>Test Message Analysis</h2>
                
                <div class="demo-buttons">
                    <button class="demo-btn demo-safe" onclick="testMessage('Hi! How has your day been? Would you like to grab coffee sometime?')">
                        Safe Message
                    </button>
                    <button class="demo-btn demo-medium" onclick="testMessage('Hey beautiful! You are absolutely perfect and I think we are soulmates meant to be together forever!')">
                        Love Bombing
                    </button>
                    <button class="demo-btn demo-critical" onclick="testMessage('I need emergency money right now. Can you send me $500 on Venmo? Its urgent!')">
                        Financial Scam
                    </button>
                </div>
                
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Enter a message to analyze..." />
                    <button id="analyzeBtn" onclick="analyzeMessage()">Analyze</button>
                </div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Analyzing message...</p>
                </div>
                
                <div id="testResult" class="result-card"></div>
            </div>
            
            <!-- Real Instagram Data -->
            <div class="real-data-section">
                <h2>Your Instagram Analysis
                    <button class="refresh-btn" onclick="loadData()">Refresh</button>
                </h2>
                
                <div id="conversationsContainer">
                    <div class="no-data">
                        <p>No Instagram DM analysis data found</p>
                        <p style="margin-top: 10px; font-size: 0.9rem;">
                            Run <code>python Working_real_instagram_analyzer.py</code> to analyze your DMs
                        </p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Recent Alerts Section -->
        <div class="recent-alerts">
            <h2>Recent Red Flag Alerts</h2>
            <div id="alertsContainer">
                <div class="no-data">
                    <p>No red flag alerts found</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Load dashboard data on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadData();
            
            // Handle Enter key in message input
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    analyzeMessage();
                }
            });
        });
        
        // Load all dashboard data
        function loadData() {
            loadStats();
            loadConversations();
            loadAlerts();
        }
        
        // Load statistics
        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('totalAlerts').textContent = data.total_alerts || 0;
                    document.getElementById('criticalAlerts').textContent = data.critical || 0;
                    document.getElementById('conversationsAnalyzed').textContent = data.conversations_analyzed || 0;
                    document.getElementById('recentAlerts').textContent = data.recent_alerts || 0;
                })
                .catch(error => {
                    console.error('Error loading stats:', error);
                });
        }
        
        // Load conversation summaries
        function loadConversations() {
            fetch('/api/conversations')
                .then(response => response.json())
                .then(conversations => {
                    const container = document.getElementById('conversationsContainer');
                    
                    if (conversations.length === 0) {
                        container.innerHTML = `
                            <div class="no-data">
                                <p>No conversations with red flags found</p>
                                <p style="margin-top: 10px; font-size: 0.9rem;">
                                    Your Instagram DMs appear safe!
                                </p>
                            </div>
                        `;
                        return;
                    }
                    
                    const conversationsHtml = conversations.map(conv => `
                        <div class="conversation-card" style="border-left-color: ${getRiskColor(conv.highest_risk)}">
                            <div class="conversation-header">
                                <span class="sender-name">${conv.sender}</span>
                                <span class="risk-badge" style="background-color: ${getRiskColor(conv.highest_risk)}">
                                    ${conv.highest_risk.toUpperCase()}
                                </span>
                            </div>
                            <div class="conversation-stats">
                                ${conv.total_alerts} alerts • ${conv.red_flag_count} red flags
                            </div>
                            <div class="latest-message">
                                "${conv.latest_message}"
                            </div>
                        </div>
                    `).join('');
                    
                    container.innerHTML = `<div class="conversations-grid">${conversationsHtml}</div>`;
                })
                .catch(error => {
                    console.error('Error loading conversations:', error);
                });
        }
        
        // Load recent alerts
        function loadAlerts() {
            fetch('/api/alerts')
                .then(response => response.json())
                .then(alerts => {
                    const container = document.getElementById('alertsContainer');
                    
                    if (alerts.length === 0) {
                        container.innerHTML = `
                            <div class="no-data">
                                <p>No red flag alerts found</p>
                                <p style="margin-top: 10px; font-size: 0.9rem;">
                                    Run the Instagram analyzer to see alerts here
                                </p>
                            </div>
                        `;
                        return;
                    }
                    
                    const alertsHtml = alerts.slice(0, 10).map(alert => `
                        <div class="alert-item" style="border-left-color: ${getRiskColor(alert.risk_level)}">
                            <div class="alert-header">
                                <span class="alert-sender">${alert.sender}</span>
                                <span class="alert-time">${formatTime(alert.timestamp)}</span>
                            </div>
                            <div class="alert-message">
                                "${alert.message}"
                            </div>
                            <div class="alert-flags">
                                <span class="risk-badge" style="background-color: ${getRiskColor(alert.risk_level)}">
                                    ${alert.risk_level.toUpperCase()}
                                </span>
                                ${(alert.red_flags || []).slice(0, 3).map(flag => 
                                    `<span class="flag-tag">${flag.category}</span>`
                                ).join('')}
                            </div>
                        </div>
                    `).join('');
                    
                    container.innerHTML = `<div class="alerts-list">${alertsHtml}</div>`;
                })
                .catch(error => {
                    console.error('Error loading alerts:', error);
                });
        }
        
        // Analyze message function
        function analyzeMessage() {
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (!message) {
                alert('Please enter a message to analyze');
                return;
            }
            
            const loading = document.getElementById('loading');
            const resultDiv = document.getElementById('testResult');
            const analyzeBtn = document.getElementById('analyzeBtn');
            
            // Show loading
            loading.style.display = 'block';
            resultDiv.style.display = 'none';
            analyzeBtn.disabled = true;
            
            fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                displayResult(data);
            })
            .catch(error => {
                console.error('Error:', error);
                displayError(error.message);
            })
            .finally(() => {
                loading.style.display = 'none';
                analyzeBtn.disabled = false;
            });
        }
        
        // Test message function
        function testMessage(message) {
            document.getElementById('messageInput').value = message;
            analyzeMessage();
        }
        
        // Display analysis result
        function displayResult(data) {
            const resultDiv = document.getElementById('testResult');
            const riskColor = getRiskColor(data.risk_level);
            
            const flagsHtml = (data.red_flags || []).map(flag => 
                `<li><strong>${flag.category}:</strong> ${flag.explanation}</li>`
            ).join('');
            
            const recommendationsHtml = (data.recommendations || []).map(rec => 
                `<li>${rec}</li>`
            ).join('');
            
            resultDiv.innerHTML = `
                <div style="border-left-color: ${riskColor}; background: ${getRiskBackground(data.risk_level)}">
                    <h3 style="color: ${riskColor}">
                        ${getRiskIcon(data.risk_level)} Risk Level: ${data.risk_level.toUpperCase()}
                    </h3>
                    <p><strong>Message:</strong> "${data.message}"</p>
                    
                    ${flagsHtml ? `
                        <div style="margin: 15px 0;">
                            <strong>Red Flags Detected:</strong>
                            <ul style="margin-left: 20px; margin-top: 5px;">
                                ${flagsHtml}
                            </ul>
                        </div>
                    ` : '<p>No red flags detected</p>'}
                    
                    ${recommendationsHtml ? `
                        <div style="margin: 15px 0;">
                            <strong>Recommendations:</strong>
                            <ul style="margin-left: 20px; margin-top: 5px;">
                                ${recommendationsHtml}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
            
            resultDiv.style.display = 'block';
        }
        
        // Display error
        function displayError(message) {
            const resultDiv = document.getElementById('testResult');
            resultDiv.innerHTML = `
                <div style="border-left-color: #e74c3c; background: #fdf2f2;">
                    <h3 style="color: #e74c3c">Analysis Error</h3>
                    <p>${message}</p>
                </div>
            `;
            resultDiv.style.display = 'block';
        }
        
        // Helper functions
        function getRiskColor(riskLevel) {
            const colors = {
                'critical': '#e74c3c',
                'high': '#f39c12',
                'medium': '#f1c40f',
                'low': '#27ae60'
            };
            return colors[riskLevel?.toLowerCase()] || '#6c757d';
        }
        
        function getRiskBackground(riskLevel) {
            const backgrounds = {
                'critical': '#fdf2f2',
                'high': '#fef8e7',
                'medium': '#fffbdb',
                'low': '#f0f9f4'
            };
            return backgrounds[riskLevel?.toLowerCase()] || '#f8f9fa';
        }
        
        function getRiskIcon(riskLevel) {
            const icons = {
                'critical': '🚨',
                'high': '⚠️',
                'medium': '⚡',
                'low': '✅'
            };
            return icons[riskLevel?.toLowerCase()] || '❓';
        }
        
        function formatTime(timestamp) {
            try {
                const date = new Date(timestamp);
                const now = new Date();
                const diffMs = now - date;
                const diffMins = Math.floor(diffMs / 60000);
                const diffHours = Math.floor(diffMins / 60);
                const diffDays = Math.floor(diffHours / 24);
                
                if (diffMins < 1) return 'Just now';
                if (diffMins < 60) return `${diffMins}m ago`;
                if (diffHours < 24) return `${diffHours}h ago`;
                if (diffDays < 7) return `${diffDays}d ago`;
                
                return date.toLocaleDateString();
            } catch (e) {
                return 'Unknown';
            }
        }
        
        // Auto-refresh data every 30 seconds
        setInterval(loadData, 30000);
    </script>
</body>
</html>"""
    
    def log_message(self, format, *args):
        """Suppress HTTP server log messages"""
        pass

def start_dashboard_server():
    """Start the dashboard server"""
    server_address = ('localhost', 8000)
    httpd = HTTPServer(server_address, DashboardHandler)
    
    print("Red Flag Filter Dashboard")
    print("=" * 50)
    print("✅ Simple dashboard with NO external dependencies!")
    print("📊 Dashboard URL: http://localhost:8000")
    print("🔍 Features:")
    print("   - Live message analysis")
    print("   - Real Instagram DM alerts")
    print("   - Statistics and summaries")
    print("   - Auto-refresh every 30 seconds")
    print("=" * 50)
    
    # Try to open browser automatically
    try:
        def open_browser():
            time.sleep(1)  # Wait for server to start
            webbrowser.open('http://localhost:8000')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        print("🌐 Opening browser automatically...")
    except:
        print("💡 Please open your browser and go to: http://localhost:8000")
    
    print("\n🚀 Server starting... Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n⏹️  Dashboard stopped")
        httpd.server_close()

if __name__ == "__main__":
    # Check if red flag alerts file exists
    if not os.path.exists('red_flag_alerts.json'):
        print("📭 No red flag alerts found")
        print("💡 Run your Instagram analyzer first:")
        print("   python Working_real_instagram_analyzer.py")
        print("")
        
        # Create empty alerts file for demo
        demo_data = {'alerts': []}
        with open('red_flag_alerts.json', 'w') as f:
            json.dump(demo_data, f)
        print("📄 Created empty alerts file for dashboard demo")
    
    start_dashboard_server()