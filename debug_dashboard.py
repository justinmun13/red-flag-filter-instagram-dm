#!/usr/bin/env python3
"""
Debug Dashboard - Minimal Version to Test Data Flow
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

# Simple HTML for debugging
DEBUG_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚩 Debug Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #1a1a1a;
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 20px 0;
        }
        .stat-box {
            background: #333;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .critical { color: #ff4757; }
        .high { color: #ffa502; }
        .medium { color: #3742fa; }
        .total { color: #2ed573; }
        .alerts {
            margin-top: 30px;
        }
        .alert {
            background: #333;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ff4757;
        }
        .alert-high { border-left-color: #ffa502; }
        .alert-medium { border-left-color: #3742fa; }
        .debug {
            background: #444;
            padding: 15px;
            margin: 20px 0;
            border-radius: 8px;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px;
        }
        .btn:hover {
            background: #5a6fd8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚩 Red Flag Filter - Debug Dashboard</h1>
        
        <button class="btn" onclick="testAPI()">🧪 Test API Connection</button>
        <button class="btn" onclick="loadData()">📊 Load Real Data</button>
        <button class="btn" onclick="clearLog()">🗑️ Clear Log</button>
        
        <div id="debug" class="debug">🔍 Debug log will appear here...</div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number critical" id="critical">0</div>
                <div>Critical Threats</div>
            </div>
            <div class="stat-box">
                <div class="stat-number high" id="high">0</div>
                <div>High Risk</div>
            </div>
            <div class="stat-box">
                <div class="stat-number medium" id="medium">0</div>
                <div>Medium Risk</div>
            </div>
            <div class="stat-box">
                <div class="stat-number total" id="total">0</div>
                <div>Messages Scanned</div>
            </div>
        </div>
        
        <div class="alerts">
            <h2>🚨 Recent Alerts</h2>
            <div id="alerts-container">
                <p>No alerts loaded yet...</p>
            </div>
        </div>
    </div>

    <script>
        function log(message) {
            const debugDiv = document.getElementById('debug');
            const timestamp = new Date().toLocaleTimeString();
            debugDiv.textContent += `[${timestamp}] ${message}\n`;
            debugDiv.scrollTop = debugDiv.scrollHeight;
            console.log(message);
        }

        function clearLog() {
            document.getElementById('debug').textContent = '🔍 Debug log cleared...\n';
        }

        async function testAPI() {
            log('🔧 Testing API connection...');
            
            try {
                // Test stats endpoint
                log('📊 Testing /api/stats...');
                const statsResponse = await fetch('/api/stats');
                log(`📊 Stats status: ${statsResponse.status}`);
                
                if (statsResponse.ok) {
                    const statsData = await statsResponse.json();
                    log(`📊 Stats data: ${JSON.stringify(statsData)}`);
                } else {
                    log(`❌ Stats failed: ${statsResponse.statusText}`);
                }
                
                // Test alerts endpoint
                log('🚨 Testing /api/alerts...');
                const alertsResponse = await fetch('/api/alerts');
                log(`🚨 Alerts status: ${alertsResponse.status}`);
                
                if (alertsResponse.ok) {
                    const alertsData = await alertsResponse.json();
                    log(`🚨 Alerts count: ${alertsData.alerts ? alertsData.alerts.length : 0}`);
                    log(`🚨 First alert: ${alertsData.alerts && alertsData.alerts[0] ? JSON.stringify(alertsData.alerts[0]).substring(0, 200) + '...' : 'none'}`);
                } else {
                    log(`❌ Alerts failed: ${alertsResponse.statusText}`);
                }
                
                log('✅ API test complete');
                
            } catch (error) {
                log(`❌ API test error: ${error.message}`);
            }
        }

        async function loadData() {
            log('📡 Loading real data...');
            
            try {
                // Load stats
                const statsResponse = await fetch('/api/stats');
                const statsData = await statsResponse.json();
                log(`📊 Loaded stats: ${JSON.stringify(statsData)}`);
                
                // Update stats display
                document.getElementById('critical').textContent = statsData.critical_count || 0;
                document.getElementById('high').textContent = statsData.high_count || 0;
                document.getElementById('medium').textContent = statsData.medium_count || 0;
                document.getElementById('total').textContent = statsData.messages_scanned || 0;
                log('✅ Stats display updated');
                
                // Load alerts
                const alertsResponse = await fetch('/api/alerts');
                const alertsData = await alertsResponse.json();
                log(`🚨 Loaded ${alertsData.alerts ? alertsData.alerts.length : 0} alerts`);
                
                // Update alerts display
                const alertsContainer = document.getElementById('alerts-container');
                
                if (!alertsData.alerts || alertsData.alerts.length === 0) {
                    alertsContainer.innerHTML = '<p>No alerts found</p>';
                    log('📝 No alerts to display');
                } else {
                    let alertsHTML = '';
                    alertsData.alerts.slice(0, 5).forEach((alert, index) => {
                        log(`🚨 Processing alert ${index + 1}: ${alert.sender} - ${alert.risk_level}`);
                        
                        alertsHTML += `
                            <div class="alert alert-${alert.risk_level}">
                                <h4>${alert.sender || 'Unknown'} - ${(alert.risk_level || 'unknown').toUpperCase()}</h4>
                                <p><strong>Message:</strong> "${alert.message || 'No message'}"</p>
                                <p><strong>Red Flags:</strong> ${alert.red_flags ? alert.red_flags.length : 0}</p>
                                <p><strong>Time:</strong> ${alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'Unknown'}</p>
                            </div>
                        `;
                    });
                    
                    alertsContainer.innerHTML = alertsHTML;
                    log('✅ Alerts display updated');
                }
                
                log('🎉 Data loading complete!');
                
            } catch (error) {
                log(`❌ Data loading error: ${error.message}`);
            }
        }

        // Auto-load data when page loads
        document.addEventListener('DOMContentLoaded', function() {
            log('🚀 Debug dashboard loaded');
            log('🔄 Auto-loading data...');
            loadData();
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
            print(f"📊 Debug: Loaded {len(alerts)} alerts from file")
            
            for alert in alerts:
                results['alerts'].append(alert)
                risk_level = alert.get('risk_level', 'low').lower()
                if f'{risk_level}_count' in results['stats']:
                    results['stats'][f'{risk_level}_count'] += 1
                results['stats']['messages_scanned'] += 1
            
            file_stats = os.stat(ALERTS_FILE)
            results['last_updated'] = datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            
            print(f"📊 Debug: Stats calculated - Critical: {results['stats']['critical_count']}, High: {results['stats']['high_count']}, Medium: {results['stats']['medium_count']}")
            
        except Exception as e:
            print(f"❌ Debug: Error loading alerts: {e}")
    else:
        print(f"📁 Debug: No {ALERTS_FILE} found")
    
    return results

@app.route('/')
def debug_dashboard():
    """Serve debug dashboard"""
    return render_template_string(DEBUG_HTML)

@app.route('/api/stats')
def get_stats():
    """Get statistics"""
    try:
        results = load_instagram_analysis_results()
        stats = results['stats']
        print(f"📊 API: Returning stats - {stats}")
        return jsonify(stats)
    except Exception as e:
        print(f"❌ API: Stats error - {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get alerts"""
    try:
        results = load_instagram_analysis_results()
        alerts = results['alerts'][-20:]  # Most recent 20
        print(f"🚨 API: Returning {len(alerts)} alerts")
        
        # Debug: Print first alert details
        if alerts:
            first_alert = alerts[0]
            print(f"🚨 API: First alert details - Sender: {first_alert.get('sender')}, Risk: {first_alert.get('risk_level')}, Message length: {len(first_alert.get('message', ''))}")
        
        return jsonify({
            'alerts': alerts,
            'total_count': len(results['alerts']),
            'last_updated': results['last_updated']
        })
    except Exception as e:
        print(f"❌ API: Alerts error - {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-message', methods=['POST'])
def test_message():
    """Test message analysis"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        print(f"🔍 Testing message: '{message[:50]}...'")
        
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
        
        print(f"✅ Analysis result: {response['risk_level']} risk")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Test message error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🔧 RED FLAG FILTER - DEBUG VERSION")
    print("=" * 50)
    
    # Check for data file
    if os.path.exists(ALERTS_FILE):
        results = load_instagram_analysis_results()
        print(f"✅ Found data: {len(results['alerts'])} alerts")
        print(f"📊 Stats: Critical({results['stats']['critical_count']}) High({results['stats']['high_count']}) Medium({results['stats']['medium_count']})")
    else:
        print(f"⚠️  No data file found: {ALERTS_FILE}")
    
    print("🌐 Starting debug server...")
    print("📱 Debug dashboard: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)