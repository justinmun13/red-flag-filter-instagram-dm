#!/usr/bin/env python3
"""
Red Flag Filter - Instagram DM Monitor Service (Updated with Environment Variables)
Monitors Instagram DMs and analyzes them for dating red flags
"""

import json
import time
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the red flag detector
from red_flag_detector import RedFlagDetector, RiskLevel

class DMMonitorService:
    def __init__(self, check_interval: int = 30):
        # Get credentials from environment variables
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        
        # Validate credentials
        if not self.username or not self.password:
            raise ValueError(
                "Instagram credentials not found. Please set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env file"
            )
        
        self.check_interval = check_interval
        self.detector = RedFlagDetector()
        self.processed_messages = set()
        self.alerts = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('red_flag_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load processed messages from file
        self.load_processed_messages()
        
        self.logger.info(f"✅ Monitor initialized for account: {self.username}")
    
    def load_processed_messages(self):
        """Load previously processed message IDs"""
        try:
            with open('processed_messages.json', 'r') as f:
                data = json.load(f)
                self.processed_messages = set(data.get('processed_messages', []))
        except FileNotFoundError:
            self.processed_messages = set()
    
    def save_processed_messages(self):
        """Save processed message IDs"""
        with open('processed_messages.json', 'w') as f:
            json.dump({
                'processed_messages': list(self.processed_messages),
                'last_updated': datetime.now().isoformat(),
                'account': self.username
            }, f, indent=2)
    
    def get_recent_messages(self) -> List[Dict]:
        """Get recent messages from Instagram DMs"""
        try:
            # This would integrate with the actual MCP server
            # For now, we'll simulate with a placeholder
            
            # In real implementation, you'd use the MCP tools:
            # - list_chats() to get conversations
            # - list_messages(thread_id) to get messages from each chat
            # - Filter for messages from last check_interval
            
            # Placeholder data structure for demonstration
            recent_messages = [
                {
                    'id': f'msg_{int(time.time())}_001',
                    'thread_id': 'thread_001',
                    'sender_username': 'potential_red_flag_user',
                    'sender_id': '12345',
                    'message': "Hey beautiful! You're absolutely perfect. I think we're soulmates!",
                    'timestamp': datetime.now().isoformat(),
                    'is_from_me': False
                },
                {
                    'id': f'msg_{int(time.time())}_002',
                    'thread_id': 'thread_002',
                    'sender_username': 'financial_scammer_demo',
                    'sender_id': '67890',
                    'message': "I need financial help for an emergency. Can you send $500?",
                    'timestamp': datetime.now().isoformat(),
                    'is_from_me': False
                }
            ]
            
            return recent_messages
            
        except Exception as e:
            self.logger.error(f"Error fetching messages: {e}")
            return []
    
    def analyze_message(self, message_data: Dict) -> Dict:
        """Analyze a message for red flags"""
        try:
            # Extract message content
            message_text = message_data.get('message', '')
            sender_info = {
                'username': message_data.get('sender_username'),
                'user_id': message_data.get('sender_id'),
                'message_frequency': self.get_message_frequency(message_data.get('sender_id')),
                'account_age_days': self.get_account_age(message_data.get('sender_username'))
            }
            
            # Analyze with red flag detector
            analysis = self.detector.analyze_message(message_text, sender_info)
            
            # Add metadata
            analysis['message_id'] = message_data.get('id')
            analysis['thread_id'] = message_data.get('thread_id')
            analysis['sender'] = message_data.get('sender_username')
            analysis['timestamp'] = message_data.get('timestamp')
            analysis['account'] = self.username
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing message: {e}")
            return None
    
    def get_message_frequency(self, sender_id: str) -> int:
        """Get message frequency for a sender (placeholder)"""
        # In real implementation, count messages from this sender in last hour
        return 1
    
    def get_account_age(self, username: str) -> int:
        """Get account age in days (placeholder)"""
        # In real implementation, get account creation date
        return 30
    
    def handle_high_risk_message(self, analysis: Dict):
        """Handle high-risk or critical messages"""
        risk_level = analysis.get('risk_level')
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'sender': analysis.get('sender'),
                'message': analysis.get('message'),
                'message_id': analysis.get('message_id'),
                'risk_level': risk_level.value if hasattr(risk_level, 'value') else risk_level,
                'red_flags': [
                    {
                        'category': flag.category if hasattr(flag, 'category') else str(flag),
                        'explanation': flag.explanation if hasattr(flag, 'explanation') else 'Red flag detected',
                        'confidence': flag.confidence if hasattr(flag, 'confidence') else 0.8
                    }
                    for flag in analysis.get('red_flags', [])
                ],
                'recommendations': analysis.get('recommendations', []),
                'account': self.username
            }
            
            self.alerts.append(alert)
            self.save_alert(alert)
            
            # Log critical alerts
            if risk_level == RiskLevel.CRITICAL:
                self.logger.critical(f"🚨 CRITICAL RED FLAG from {analysis.get('sender')}: {analysis.get('message')}")
            else:
                self.logger.warning(f"⚠️ HIGH RISK message from {analysis.get('sender')}")
    
    def save_alert(self, alert: Dict):
        """Save alert to file"""
        alerts_file = 'red_flag_alerts.json'
        
        try:
            with open(alerts_file, 'r') as f:
                alerts_data = json.load(f)
        except FileNotFoundError:
            alerts_data = {'alerts': []}
        
        alerts_data['alerts'].append(alert)
        
        with open(alerts_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)
    
    def generate_daily_report(self):
        """Generate daily safety report"""
        today = datetime.now().date()
        today_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']).date() == today
        ]
        
        report = {
            'date': today.isoformat(),
            'account': self.username,
            'total_alerts': len(today_alerts),
            'critical_alerts': len([a for a in today_alerts if a['risk_level'] == 'critical']),
            'high_risk_alerts': len([a for a in today_alerts if a['risk_level'] == 'high']),
            'alerts': today_alerts
        }
        
        report_filename = f'daily_report_{today.isoformat()}_{self.username.replace("@", "").replace(".", "_")}.json'
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        self.logger.info("🔍 Starting monitoring cycle...")
        
        # Get recent messages
        messages = self.get_recent_messages()
        new_messages = [
            msg for msg in messages 
            if msg['id'] not in self.processed_messages and not msg['is_from_me']
        ]
        
        self.logger.info(f"📬 Found {len(new_messages)} new messages to analyze")
        
        for message in new_messages:
            # Analyze message
            analysis = self.analyze_message(message)
            
            if analysis:
                risk_level = analysis['risk_level']
                if hasattr(risk_level, 'value'):
                    risk_level_str = risk_level.value
                else:
                    risk_level_str = str(risk_level)
                
                self.logger.info(f"📊 Analyzed message from {message['sender_username']}: Risk Level {risk_level_str.upper()}")
                
                # Handle high-risk messages
                self.handle_high_risk_message(analysis)
                
                # Mark as processed
                self.processed_messages.add(message['id'])
        
        # Save processed messages
        self.save_processed_messages()
        
        self.logger.info("✅ Monitoring cycle completed")
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        self.logger.info("🚩 Red Flag Filter - DM Monitor Started")
        self.logger.info(f"👤 Monitoring account: {self.username}")
        self.logger.info(f"⏱️ Check interval: {self.check_interval} seconds")
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"💥 Monitoring error: {e}")
    
    def get_dashboard_data(self) -> Dict:
        """Get data for dashboard display"""
        try:
            with open('red_flag_alerts.json', 'r') as f:
                alerts_data = json.load(f)
        except FileNotFoundError:
            alerts_data = {'alerts': []}
        
        # Filter alerts for this account
        account_alerts = [
            alert for alert in alerts_data['alerts']
            if alert.get('account') == self.username
        ]
        
        recent_alerts = sorted(
            account_alerts,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:10]
        
        stats = {
            'total_alerts': len(account_alerts),
            'critical_count': len([a for a in account_alerts if a['risk_level'] == 'critical']),
            'high_risk_count': len([a for a in account_alerts if a['risk_level'] == 'high']),
            'medium_risk_count': len([a for a in account_alerts if a['risk_level'] == 'medium']),
            'recent_alerts': recent_alerts,
            'account': self.username
        }
        
        return stats

def main():
    parser = argparse.ArgumentParser(description='Red Flag Filter - Instagram DM Monitor (Environment Variable Version)')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run once instead of continuous monitoring')
    parser.add_argument('--generate-report', action='store_true', help='Generate daily report and exit')
    
    args = parser.parse_args()
    
    try:
        monitor = DMMonitorService(args.interval)
        
        if args.generate_report:
            report = monitor.generate_daily_report()
            print(f"📋 Daily report generated: {json.dumps(report, indent=2)}")
        elif args.once:
            monitor.run_monitoring_cycle()
        else:
            monitor.start_monitoring()
            
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n💡 To fix this:")
        print("1. Create a .env file in your project directory")
        print("2. Add the following lines:")
        print("   INSTAGRAM_USERNAME=your_username")
        print("   INSTAGRAM_PASSWORD=your_password")
        print("3. Make sure the .env file is in the same directory as this script")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()