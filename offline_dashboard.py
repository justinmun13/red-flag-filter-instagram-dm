#!/usr/bin/env python3
"""
Offline Debug Dashboard - No External Dependencies
This version works without internet connection
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from red_flag_detector import RedFlagDetector, RiskLevel
    print("✅ Red Flag Detector imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

detector = RedFlagDetector()
ALERTS_FILE = 'red_flag_alerts.json'

# Completely offline HTML - no external dependencies
OFFLINE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚩 Red Flag Filter - Offline Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .status {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }
        
        .controls {
            margin: 20px 0;
            text-align: center;
        }
        
        .btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 2px solid rgba(255,255,255,0.3);
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            margin: 0 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            background: rgba(255,255,255,0.3);
            border-color: rgba(255,255,255,0.5);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stat-label {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .critical { color: #ff4757; }
        .high { color: #ffa502; }
        .medium { color: #3742fa; }
        .total { color: #2ed573; }
        
        .alerts-section {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 20px;
            margin: 30px 0;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .section-title {
            font-size: 1.8rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .alert-card {
            background: rgba(255,255,255,0.1);
            margin: 15px 0;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #ff4757;
            transition: all 0.3s ease;
        }
        
        .alert-card:hover {
            transform: translateX(5px);
            background: rgba(255,255,255,0.15);
        }
        
        .alert-critical { border-left-color: #ff4757; }
        .alert-high { border-left-color: #ffa502; }
        .alert-medium { border-left-color: #3742fa; }
        
        .alert-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .alert-sender {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .risk-badge {
            background: #ff4757;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .badge-high { background: #ffa502; }
        .badge-medium { background: #3742fa; }
        
        .alert-message {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-style: italic;
        }
        
        .debug-log {
            background: #1a1a1a;
            color: #00ff00;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            height: 200px;
            overflow-y: auto;
            margin: 20px 0;
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            opacity: 0.7;
        }
        
        .success {
            color: #2ed573;
            font-weight: bold;
        }
        
        .error {
            color: #ff4757;
            font-weight: bold;
        }
        
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .controls {
                flex-direction: column;
                gap: 10px;
            }
            
            .btn {
                margin: 5px 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚩 Red Flag Filter</h1>
            <p>AI-Powered Instagram DM Safety Analysis</p>
        </div>
        
        <div class="status" id="status">
            <strong>📡 Connection Status:</strong> <span id="connection-status">Testing...</span>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="testConnection()" id="test-btn">
                🧪 Test Connection
            </button>
            <button class="btn" onclick="loadData()" id="load-btn">
                📊 Load Data
            </button>
            <button class="btn" onclick="clearLog()">
                🗑️ Clear Log
            </button>
            <button class="btn" onclick="testMessage()">
                ⚡ Test Message
            </button>
        </div>
        
        <div class="debug-log" id="debug-log">
            🔍 Debug Log - Waiting for commands...\n
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number critical" id="critical-count">0</div>
                <div class="stat-label">Critical Threats</div>
            </div>
            <div class="stat-card">
                <div class="stat-number high" id="high-count">0</div>
                <div class="stat-label">High Risk</div>
            </div>
            <div class="stat-card">
                <div class="stat-number medium" id="medium-count">0</div>
                <div class="stat-label">Medium Risk</div>
            </div>
            <div class="stat-card">
                <div class="stat-number total" id="total-count">0</div>
                <div class="stat-label">Messages Analyzed</div>
            </div>
        </div>
        
        <div class="alerts-section">
            <h2 class="section-title">🚨 Recent Security Alerts</h2>
            <div id="alerts-container">
                <div class="loading">Loading alerts...</div>
            </div>
        </div>
    </div>

    <script>
        // Debug logging function
        function log(message) {
            const debugLog = document.getElementById('debug-log');
            const timestamp = new Date().toLocaleTimeString();
            debugLog.textContent += `[${timestamp}] ${message}\n`;
            debugLog.scrollTop = debugLog.scrollHeight;
            console.log(`[Red Flag Filter] ${message}`);
        }

        function clearLog() {
            document.getElementById('debug-log').textContent = '🔍 Debug Log Cleared\n';
        }

        function updateConnectionStatus(status, isConnected) {
            const statusElement = document.getElementById('connection-status');
            statusElement.textContent = status;
            statusElement.className = isConnected ? 'success' : 'error';
        }

        async function testConnection() {
            log('🔧 Testing API connection...');
            updateConnectionStatus('Testing...', false);
            
            const testBtn = document.getElementById('test-btn');
            testBtn.textContent = '🔄 Testing...';
            testBtn.disabled = true;
            
            try {
                // Test stats endpoint
                log('📊 Testing /api/stats endpoint...');
                const statsResponse = await fetch('/api/stats');
                log(`📊 Stats response status: ${statsResponse.status}`);
                
                if (statsResponse.ok) {
                    const statsData = await statsResponse.json();
                    log(`📊 Stats data received: ${JSON.stringify(statsData)}`);
                    log(`📊 Critical: ${statsData.critical_count}, High: ${statsData.high_count}, Medium: ${statsData.medium_count}, Total: ${statsData.messages_scanned}`);
                } else {
                    log(`❌ Stats endpoint failed: ${statsResponse.statusText}`);
                }
                
                // Test alerts endpoint
                log('🚨 Testing /api/alerts endpoint...');
                const alertsResponse = await fetch('/api/alerts');
                log(`🚨 Alerts response status: ${alertsResponse.status}`);
                
                if (alertsResponse.ok) {
                    const alertsData = await alertsResponse.json();
                    log(`🚨 Alerts data received: ${alertsData.alerts ? alertsData.alerts.length : 0} alerts`);
                    
                    if (alertsData.alerts && alertsData.alerts.length > 0) {
                        const firstAlert = alertsData.alerts[0];
                        log(`🚨 First alert: ${firstAlert.sender} - ${firstAlert.risk_level} - "${firstAlert.message ? firstAlert.message.substring(0, 50) + '...' : 'No message'}"`);
                    }
                } else {
                    log(`❌ Alerts endpoint failed: ${alertsResponse.statusText}`);
                }
                
                if (statsResponse.ok && alertsResponse.ok) {
                    updateConnectionStatus('✅ Connected - APIs working', true);
                    log('✅ Connection test SUCCESSFUL - Both APIs responding');
                } else {
                    updateConnectionStatus('❌ API Connection Failed', false);
                    log('❌ Connection test FAILED - One or more APIs not responding');
                }
                
            } catch (error) {
                log(`❌ Connection test ERROR: ${error.message}`);
                updateConnectionStatus('❌ Connection Error', false);
            } finally {
                testBtn.textContent = '🧪 Test Connection';
                testBtn.disabled = false;
            }
        }

        async function loadData() {
            log('📡 Loading real Instagram analyzer data...');
            
            const loadBtn = document.getElementById('load-btn');
            loadBtn.textContent = '🔄 Loading...';
            loadBtn.disabled = true;
            
            try {
                // Load stats
                log('📊 Fetching stats...');
                const statsResponse = await fetch('/api/stats');
                const statsData = await statsResponse.json();
                
                log(`📊 Stats loaded: Critical(${statsData.critical_count}) High(${statsData.high_count}) Medium(${statsData.medium_count}) Total(${statsData.messages_scanned})`);
                
                // Update stats display
                log('🔄 Updating stats display...');
                document.getElementById('critical-count').textContent = statsData.critical_count || 0;
                document.getElementById('high-count').textContent = statsData.high_count || 0;
                document.getElementById('medium-count').textContent = statsData.medium_count || 0;
                document.getElementById('total-count').textContent = statsData.messages_scanned || 0;
                log('✅ Stats display updated successfully');
                
                // Load alerts
                log('🚨 Fetching alerts...');
                const alertsResponse = await fetch('/api/alerts');
                const alertsData = await alertsResponse.json();
                
                log(`🚨 Alerts loaded: ${alertsData.alerts ? alertsData.alerts.length : 0} total alerts`);
                
                // Update alerts display
                const alertsContainer = document.getElementById('alerts-container');
                
                if (!alertsData.alerts || alertsData.alerts.length === 0) {
                    alertsContainer.innerHTML = '<div class="loading">No alerts found in your Instagram analysis results.</div>';
                    log('📝 No alerts to display');
                } else {
                    log('🔄 Creating alert cards...');
                    let alertsHTML = '';
                    
                    // Show first 5 alerts
                    const alertsToShow = alertsData.alerts.slice(0, 5);
                    alertsToShow.forEach((alert, index) => {
                        log(`🚨 Creating card for alert ${index + 1}: ${alert.sender} - ${alert.risk_level}`);
                        
                        alertsHTML += `
                            <div class="alert-card alert-${alert.risk_level}">
                                <div class="alert-header">
                                    <span class="alert-sender">${alert.sender || 'Unknown User'}</span>
                                    <span class="risk-badge badge-${alert.risk_level}">${(alert.risk_level || 'unknown').toUpperCase()}</span>
                                </div>
                                <div class="alert-message">
                                    "${alert.message || 'No message content available'}"
                                </div>
                                <div style="margin-top: 15px; opacity: 0.8;">
                                    <strong>Red Flags:</strong> ${alert.red_flags ? alert.red_flags.length : 0} detected
                                    <br>
                                    <strong>Time:</strong> ${alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'Unknown'}
                                </div>
                            </div>
                        `;
                    });
                    
                    alertsContainer.innerHTML = alertsHTML;
                    log(`✅ Alert cards created successfully (showing ${alertsToShow.length} of ${alertsData.alerts.length} total)`);
                }
                
                log('🎉 Data loading COMPLETE! Your real Instagram analysis is now displayed.');
                updateConnectionStatus('✅ Data Loaded Successfully', true);
                
            } catch (error) {
                log(`❌ Data loading ERROR: ${error.message}`);
                updateConnectionStatus('❌ Data Loading Failed', false);
            } finally {
                loadBtn.textContent = '📊 Load Data';
                loadBtn.disabled = false;
            }
        }

        async function testMessage() {
            const message = prompt('Enter a message to test for red flags:', 'I need money for an emergency. Can you send me $500?');
            if (!message) return;
            
            log(`🧪 Testing message: "${message.substring(0, 50)}..."`);
            
            try {
                const response = await fetch('/api/test-message', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const result = await response.json();
                log(`🎯 Analysis result: ${result.risk_level.toUpperCase()} risk level`);
                log(`🚩 Red flags found: ${result.red_flags ? result.red_flags.length : 0}`);
                
                alert(`Analysis Result:\n\nRisk Level: ${result.risk_level.toUpperCase()}\nRed Flags: ${result.red_flags ? result.red_flags.length : 0}\nConfidence: ${Math.round((result.confidence || 0) * 100)}%`);
                
            } catch (error) {
                log(`❌ Message test ERROR: ${error.message}`);
            }
        }

        // Auto-load data when page loads
        document.addEventListener('DOMContentLoaded', function() {
            log('🚀 Red Flag Filter Dashboard loaded');
            log('🔧 Running automatic connection test...');
            
            // Auto-test connection and load data
            setTimeout(() => {
                testConnection().then(() => {
                    log('🔄 Auto-loading data...');
                    loadData();
                });
            }, 1000);
        });
    </script>
</body>
</html>
'''

def load_instagram_analysis_results():
    """Load results from Instagram analyzer"""
    results = {
        'alerts': [],
        'stats': {
            'messages_scanned': 0,
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0
        },
        'last_updated': None
    }
    
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, 'r') as f:
                data = json.load(f)
                
            alerts = data.get('alerts', [])
            print(f"📊 Loaded {len(alerts)} alerts from Instagram analyzer")
            
            for alert in alerts:
                results['alerts'].append(alert)
                risk_level = alert.get('risk_level', 'low').lower()
                if f'{risk_level}_count' in results['stats']:
                    results['stats'][f'{risk_level}_count'] += 1
                results['stats']['messages_scanned'] += 1
            
            file_stats = os.stat(ALERTS_FILE)
            results['last_updated'] = datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            
        except Exception as e:
            print(f"❌ Error loading alerts: {e}")
    
    return results

@app.route('/')
def offline_dashboard():
    """Serve offline dashboard"""
    return render_template_string(OFFLINE_HTML)

@app.route('/api/stats')
def get_stats():
    """Get statistics"""
    try:
        results = load_instagram_analysis_results()
        return jsonify(results['stats'])
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get alerts"""
    try:
        results = load_instagram_analysis_results()
        alerts = results['alerts'][-20:]  # Most recent 20
        
        return jsonify({
            'alerts': alerts,
            'total_count': len(results['alerts']),
            'last_updated': results['last_updated']
        })
    except Exception as e:
        print(f"❌ Alerts error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-message', methods=['POST'])
def test_message():
    """Test message analysis"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        result = detector.analyze_message(message)
        
        response = {
            'message': message,
            'risk_level': result['risk_level'].value if hasattr(result['risk_level'], 'value') else str(result['risk_level']),
            'confidence': result.get('confidence', 0.0),
            'red_flags': [
                {
                    'category': getattr(flag, 'category', ''),
                    'explanation': getattr(flag, 'explanation', ''),
                    'confidence': getattr(flag, 'confidence', 0.0)
                } if hasattr(flag, 'category') else flag
                for flag in result.get('red_flags', [])
            ],
            'recommendations': result.get('recommendations', [])
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Test message error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🔧 RED FLAG FILTER - OFFLINE VERSION")
    print("=" * 50)
    print("📡 No external dependencies - works offline")
    
    if os.path.exists(ALERTS_FILE):
        results = load_instagram_analysis_results()
        print(f"✅ Found your Instagram analysis: {len(results['alerts'])} alerts")
        print(f"📊 Critical: {results['stats']['critical_count']}, High: {results['stats']['high_count']}, Medium: {results['stats']['medium_count']}")
    else:
        print(f"⚠️  No analysis file found: {ALERTS_FILE}")
    
    print("🌐 Starting offline dashboard...")
    print("📱 Open: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)