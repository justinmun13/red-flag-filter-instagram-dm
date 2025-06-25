#!/usr/bin/env python3
"""
Red Flag Filter - Web Dashboard Backend
Flask server for the Red Flag Filter dashboard with environment variable support
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Get Instagram credentials from environment
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

# Check if credentials are available
if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
    print("⚠️ WARNING: Instagram credentials not found in .env file")
    print("Please create a .env file with INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD")
    print("Example .env file:")
    print("INSTAGRAM_USERNAME=your_username")
    print("INSTAGRAM_PASSWORD=your_password")

try:
    from red_flag_detector import RedFlagDetector
except ImportError:
    print("Warning: Could not import RedFlagDetector. Make sure red_flag_detector.py is in the src/ directory.")
    RedFlagDetector = None

app = Flask(__name__, 
            template_folder='web',  # Look for templates in web/ directory
            static_folder='web')    # Look for static files in web/ directory
CORS(app)

# Initialize detector if available
detector = RedFlagDetector() if RedFlagDetector else None

@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_from_directory('web', 'dashboard.html')

@app.route('/api/test-message', methods=['POST'])
def test_message():
    """Test a message for red flags"""
    if not detector:
        return jsonify({'error': 'Red Flag Detector not available'}), 500
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Analyze the message
        result = detector.analyze_message(message)
        
        # Convert result to JSON serializable format
        json_result = {
            'message': result['message'],
            'risk_level': result['risk_level'].value if hasattr(result['risk_level'], 'value') else result['risk_level'],
            'red_flags': [
                {
                    'category': flag.category if hasattr(flag, 'category') else str(flag),
                    'explanation': flag.explanation if hasattr(flag, 'explanation') else 'Red flag detected',
                    'confidence': flag.confidence if hasattr(flag, 'confidence') else 0.8
                }
                for flag in result.get('red_flags', [])
            ],
            'recommendations': result.get('recommendations', []),
            'confidence': result.get('confidence', 0.0)
        }
        
        return jsonify(json_result)
        
    except Exception as e:
        print(f"Error in test_message: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get all alerts from the alerts file"""
    try:
        alerts_file = os.path.join(os.path.dirname(__file__), 'red_flag_alerts.json')
        with open(alerts_file, 'r') as f:
            alerts_data = json.load(f)
        return jsonify(alerts_data)
    except FileNotFoundError:
        return jsonify({'alerts': []})
    except Exception as e:
        print(f"Error loading alerts: {e}")
        return jsonify({'alerts': []})

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    try:
        alerts_file = os.path.join(os.path.dirname(__file__), 'red_flag_alerts.json')
        with open(alerts_file, 'r') as f:
            alerts_data = json.load(f)
        
        alerts = alerts_data.get('alerts', [])
        stats = {
            'total_alerts': len(alerts),
            'critical_count': len([a for a in alerts if a.get('risk_level') == 'critical']),
            'high_count': len([a for a in alerts if a.get('risk_level') == 'high']),
            'medium_count': len([a for a in alerts if a.get('risk_level') == 'medium']),
            'low_count': len([a for a in alerts if a.get('risk_level') == 'low']),
            'messages_scanned': 247,  # This would be dynamic in real implementation
            'last_updated': datetime.now().isoformat(),
            'credentials_configured': bool(INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD)
        }
        
        return jsonify(stats)
    except FileNotFoundError:
        return jsonify({
            'total_alerts': 0,
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'messages_scanned': 0,
            'last_updated': datetime.now().isoformat(),
            'credentials_configured': bool(INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD)
        })
    except Exception as e:
        print(f"Error loading stats: {e}")
        return jsonify({
            'total_alerts': 0,
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'messages_scanned': 0,
            'last_updated': datetime.now().isoformat(),
            'credentials_configured': bool(INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD)
        })

@app.route('/api/generate-demo-data', methods=['POST'])
def generate_demo_data():
    """Generate demo data for testing"""
    try:
        # Sample demo alerts
        demo_alerts = [
            {
                'timestamp': datetime.now().isoformat(),
                'sender': '@love_bomber_user',
                'message': "Hey gorgeous! You're absolutely perfect and I think we're soulmates. I've never felt this way about anyone before!",
                'risk_level': 'medium',
                'red_flags': [
                    {
                        'category': 'manipulation_love_bombing',
                        'explanation': 'Excessive romantic declarations too early in conversation',
                        'confidence': 0.8
                    }
                ],
                'recommendations': [
                    '⚡ BE CAUTIOUS - Some concerning patterns detected',
                    '🎭 Keep conversations light and public',
                    '🧠 Trust your instincts - manipulation tactics are red flags'
                ]
            },
            {
                'timestamp': datetime.now().isoformat(),
                'sender': '@financial_scammer',
                'message': "I need financial help for an emergency. Can you send me $500 on Venmo?",
                'risk_level': 'critical',
                'red_flags': [
                    {
                        'category': 'financial_scams_money_requests',
                        'explanation': 'Potential financial scam or money request',
                        'confidence': 0.9
                    }
                ],
                'recommendations': [
                    '🚨 BLOCK IMMEDIATELY - This person shows dangerous behavior patterns',
                    '💰 NEVER send money to someone you haven\'t met in person',
                    '📸 Screenshot the conversation for evidence'
                ]
            },
            {
                'timestamp': datetime.now().isoformat(),
                'sender': '@boundary_violator',
                'message': "Why aren't you responding? You don't care about me. Answer me right now!",
                'risk_level': 'high',
                'red_flags': [
                    {
                        'category': 'manipulation_guilt_tripping',
                        'explanation': 'Attempting to manipulate through guilt and emotional pressure',
                        'confidence': 0.85
                    },
                    {
                        'category': 'boundary_violations_persistent_messaging',
                        'explanation': 'Not respecting communication boundaries',
                        'confidence': 0.7
                    }
                ],
                'recommendations': [
                    '⚠️ PROCEED WITH EXTREME CAUTION',
                    '🚫 Do not share personal information',
                    '🔒 Consider blocking if behavior continues'
                ]
            }
        ]
        
        # Save demo data
        alerts_file = os.path.join(os.path.dirname(__file__), 'red_flag_alerts.json')
        with open(alerts_file, 'w') as f:
            json.dump({'alerts': demo_alerts}, f, indent=2)
        
        return jsonify({'message': 'Demo data generated successfully', 'count': len(demo_alerts)})
        
    except Exception as e:
        print(f"Error generating demo data: {e}")
        return jsonify({'error': f'Failed to generate demo data: {str(e)}'}), 500

@app.route('/api/config')
def get_config():
    """Get configuration status"""
    return jsonify({
        'instagram_username_configured': bool(INSTAGRAM_USERNAME),
        'instagram_password_configured': bool(INSTAGRAM_PASSWORD),
        'username': INSTAGRAM_USERNAME if INSTAGRAM_USERNAME else 'Not configured',
        'detector_available': detector is not None
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'detector_available': detector is not None,
        'credentials_configured': bool(INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚩 Red Flag Filter - Web Dashboard Starting...")
    print("🌐 Dashboard will be available at: http://localhost:5000")
    print("🧪 Test the API at: http://localhost:5000/health")
    
    # Print configuration status
    if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
        print(f"✅ Instagram credentials loaded for: {INSTAGRAM_USERNAME}")
    else:
        print("❌ Instagram credentials not found - please check your .env file")
    
    # Create necessary directories
    os.makedirs('web', exist_ok=True)
    os.makedirs('src', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)