import json
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Create demo data
demo_alerts = [
    {
        'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
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
        'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
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
            }
        ],
        'recommendations': [
            '⚠️ PROCEED WITH EXTREME CAUTION',
            '🚫 Do not share personal information',
            '🔒 Consider blocking if behavior continues'
        ]
    }
]

# Save to the main directory
output_file = os.path.join(os.path.dirname(__file__), '..', 'red_flag_alerts.json')
with open(output_file, 'w') as f:
    json.dump({'alerts': demo_alerts}, f, indent=2)

print("✅ Demo data created successfully!")
print(f"📊 Created {len(demo_alerts)} sample alerts")
print(f"💾 Saved to: {output_file}")

# Show summary
risk_counts = {}
for alert in demo_alerts:
    risk_level = alert['risk_level']
    risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1

print("\n📈 Risk Level Summary:")
for level, count in risk_counts.items():
    emoji = {'critical': '🚨', 'high': '⚠️', 'medium': '⚡', 'low': '✅'}.get(level, '📊')
    print(f"  {emoji} {level.upper()}: {count}")