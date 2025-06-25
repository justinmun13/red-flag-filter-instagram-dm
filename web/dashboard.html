<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚩 Red Flag Filter - Dating DM Validator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            font-size: 2.5em;
            color: #2d3748;
            margin-bottom: 10px;
        }

        .header p {
            color: #4a5568;
            font-size: 1.1em;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .stat-label {
            color: #4a5568;
            font-size: 1.1em;
        }

        .critical { color: #e53e3e; }
        .high { color: #dd6b20; }
        .medium { color: #d69e2e; }
        .low { color: #38a169; }

        .alerts-section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }

        .section-title {
            font-size: 1.8em;
            color: #2d3748;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .alert-card {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }

        .alert-card:hover {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }

        .alert-card.critical {
            border-color: #e53e3e;
            background: #fed7d7;
        }

        .alert-card.high {
            border-color: #dd6b20;
            background: #feebc8;
        }

        .alert-card.medium {
            border-color: #d69e2e;
            background: #faf089;
        }

        .alert-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .alert-sender {
            font-weight: bold;
            font-size: 1.1em;
        }

        .alert-time {
            color: #666;
            font-size: 0.9em;
        }

        .risk-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }

        .risk-badge.critical {
            background: #e53e3e;
            color: white;
        }

        .risk-badge.high {
            background: #dd6b20;
            color: white;
        }

        .risk-badge.medium {
            background: #d69e2e;
            color: white;
        }

        .alert-message {
            background: rgba(255, 255, 255, 0.7);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-style: italic;
        }

        .red-flags {
            margin-bottom: 15px;
        }

        .red-flag-item {
            background: rgba(255, 255, 255, 0.5);
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 8px;
            border-left: 4px solid #e53e3e;
        }

        .red-flag-category {
            font-weight: bold;
            color: #e53e3e;
            text-transform: capitalize;
        }

        .recommendations {
            background: rgba(255, 255, 255, 0.7);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #38a169;
        }

        .recommendation-item {
            margin-bottom: 8px;
            padding-left: 20px;
            position: relative;
        }

        .recommendation-item::before {
            content: "•";
            position: absolute;
            left: 0;
            color: #38a169;
            font-weight: bold;
        }

        .live-indicator {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: #38a169;
            color: white;
            padding: 10px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 25px;
            margin-bottom: 20px;
        }

        .pulse {
            width: 6px;
            height: 6px;
            background: #68d391;
            border-radius: 50%;
            animation: pulse 2s infinite;
            flex-shrink: 0;
        }

        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
            100% { opacity: 1; transform: scale(1); }
        }

        .test-section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-top: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }

        .test-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1.1em;
            margin-bottom: 15px;
            resize: vertical;
            min-height: 100px;
        }

        .test-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .test-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .test-result {
            margin-top: 20px;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #e2e8f0;
        }

        .no-alerts {
            text-align: center;
            color: #4a5568;
            font-style: italic;
            padding: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚩 Red Flag Filter</h1>
            <p>AI-Powered Dating DM Validator - Protecting you from digital red flags</p>
            <div class="live-indicator">
                <div class="pulse"></div>
                Monitoring Active
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number critical" id="criticalCount">0</div>
                <div class="stat-label">Critical Alerts</div>
            </div>
            <div class="stat-card">
                <div class="stat-number high" id="highCount">0</div>
                <div class="stat-label">High Risk</div>
            </div>
            <div class="stat-card">
                <div class="stat-number medium" id="mediumCount">0</div>
                <div class="stat-label">Medium Risk</div>
            </div>
            <div class="stat-card">
                <div class="stat-number low" id="totalScanned">0</div>
                <div class="stat-label">Messages Scanned</div>
            </div>
        </div>

        <div class="test-section">
            <h2 class="section-title">🧪 Test Red Flag Detection</h2>
            <textarea 
                id="testMessage" 
                class="test-input" 
                placeholder="Enter a message to test for red flags...&#10;&#10;Try examples like:&#10;- 'Hey beautiful, you're perfect! We're soulmates!'&#10;- 'Why aren't you responding? You don't care about me.'&#10;- 'I need financial help. Can you send me $500?'"
            ></textarea>
            <button class="test-button" onclick="testMessage()">Analyze Message</button>
            <div id="testResult"></div>
        </div>

        <div class="alerts-section">
            <h2 class="section-title">🚨 Recent Alerts</h2>
            <div id="alertsContainer">
                <div class="no-alerts">
                    No alerts yet. The system is monitoring your DMs for red flags.
                </div>
            </div>
        </div>
    </div>

    <script>
        // Test message function
        async function testMessage() {
            const messageText = document.getElementById('testMessage').value.trim();
            if (!messageText) {
                alert('Please enter a message to test');
                return;
            }

            try {
                const response = await fetch('/api/test-message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: messageText })
                });

                const result = await response.json();
                displayTestResult(result);
            } catch (error) {
                console.error('Error testing message:', error);
                document.getElementById('testResult').innerHTML = 
                    '<div class="test-result" style="border-color: #e53e3e; background: #fed7d7;">Error testing message. Please try again.</div>';
            }
        }

        function displayTestResult(result) {
            const resultDiv = document.getElementById('testResult');
            
            const riskColors = {
                low: '#38a169',
                medium: '#d69e2e',
                high: '#dd6b20',
                critical: '#e53e3e'
            };

            let html = `
                <div class="test-result" style="border-color: ${riskColors[result.risk_level]};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3>Analysis Result</h3>
                        <span class="risk-badge ${result.risk_level}">${result.risk_level.toUpperCase()}</span>
                    </div>
                    
                    <div class="alert-message">
                        "${result.message}"
                    </div>
            `;

            if (result.red_flags && result.red_flags.length > 0) {
                html += '<div class="red-flags"><h4>🚩 Red Flags Detected:</h4>';
                result.red_flags.forEach(flag => {
                    html += `
                        <div class="red-flag-item">
                            <div class="red-flag-category">${flag.category.replace(/_/g, ' ')}</div>
                            <div>${flag.explanation}</div>
                        </div>
                    `;
                });
                html += '</div>';
            }

            if (result.recommendations && result.recommendations.length > 0) {
                html += '<div class="recommendations"><h4>💡 Recommendations:</h4>';
                result.recommendations.forEach(rec => {
                    html += `<div class="recommendation-item">${rec}</div>`;
                });
                html += '</div>';
            }

            html += '</div>';
            resultDiv.innerHTML = html;
        }

        function createAlertCard(alert) {
            const timeAgo = getTimeAgo(new Date(alert.timestamp));
            
            return `
                <div class="alert-card ${alert.risk_level}">
                    <div class="alert-header">
                        <div class="alert-sender">${alert.sender}</div>
                        <div class="alert-time">${timeAgo}</div>
                        <span class="risk-badge ${alert.risk_level}">${alert.risk_level.toUpperCase()}</span>
                    </div>
                    
                    <div class="alert-message">
                        "${alert.message}"
                    </div>
                    
                    <div class="red-flags">
                        <h4>🚩 Red Flags:</h4>
                        ${alert.red_flags.map(flag => `
                            <div class="red-flag-item">
                                <div class="red-flag-category">${flag.category.replace(/_/g, ' ')}</div>
                                <div>${flag.explanation}</div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="recommendations">
                        <h4>💡 Recommendations:</h4>
                        ${alert.recommendations.map(rec => `
                            <div class="recommendation-item">${rec}</div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        function getTimeAgo(date) {
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);

            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            return `${diffDays}d ago`;
        }

        async function loadDashboardData() {
            try {
                // Load stats
                const statsResponse = await fetch('/api/stats');
                const stats = await statsResponse.json();
                
                document.getElementById('criticalCount').textContent = stats.critical_count || 0;
                document.getElementById('highCount').textContent = stats.high_count || 0;
                document.getElementById('mediumCount').textContent = stats.medium_count || 0;
                document.getElementById('totalScanned').textContent = stats.messages_scanned || 0;

                // Load alerts
                const alertsResponse = await fetch('/api/alerts');
                const alertsData = await alertsResponse.json();
                
                const alertsContainer = document.getElementById('alertsContainer');
                if (alertsData.alerts && alertsData.alerts.length > 0) {
                    alertsContainer.innerHTML = alertsData.alerts.map(createAlertCard).join('');
                } else {
                    alertsContainer.innerHTML = '<div class="no-alerts">No alerts yet. The system is monitoring your DMs for red flags.</div>';
                }
            } catch (error) {
                console.error('Error loading dashboard data:', error);
            }
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboardData();
            
            // Refresh data every 30 seconds
            setInterval(loadDashboardData, 30000);
        });
    </script>
</body>
</html>