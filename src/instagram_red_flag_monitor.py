#!/usr/bin/env python3
"""
Red Flag Filter - Real Instagram MCP Integration
Monitors actual Instagram DMs using the Gala Labs MCP server
"""

import sys
import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the red flag detector
from red_flag_detector import RedFlagDetector, RiskLevel

# Try to import the MCP server functions
try:
    # Import their MCP server tools (adjust imports based on their actual structure)
    from mcp_server import list_chats, list_messages, send_message, get_thread_details
    MCP_AVAILABLE = True
    print("✅ Instagram MCP Server modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Could not import MCP server modules: {e}")
    print("Running in demo mode with simulated Instagram data")
    MCP_AVAILABLE = False

# Alternative: try different import patterns
if not MCP_AVAILABLE:
    try:
        # Try importing from their actual file structure
        import mcp_server as mcp
        list_chats = getattr(mcp, 'list_chats', None)
        list_messages = getattr(mcp, 'list_messages', None)
        send_message = getattr(mcp, 'send_message', None)
        
        if list_chats and list_messages:
            MCP_AVAILABLE = True
            print("✅ Instagram MCP Server modules loaded via alternative import")
    except ImportError:
        print("ℹ️ MCP server not available - using demo mode")
        MCP_AVAILABLE = False

class InstagramRedFlagMonitor:
    """Real Instagram DM monitor using MCP server + Red Flag detection"""
    
    def __init__(self):
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("Instagram credentials not found in .env file")
        
        self.detector = RedFlagDetector()
        self.processed_messages = set()
        self.monitoring = False
        
        # Setup logging (Windows-compatible)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('instagram_red_flag_monitor.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Configure logger to handle Unicode properly
        if sys.platform.startswith('win'):
            # Windows console compatibility
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        
        print(f"🚩 Instagram Red Flag Monitor initialized")
        print(f"👤 Account: {self.username}")
        print(f"🔗 MCP Available: {MCP_AVAILABLE}")
    
    def get_instagram_chats(self) -> List[Dict]:
        """Get Instagram chat threads using MCP server"""
        if not MCP_AVAILABLE:
            self.logger.warning("MCP server not available, using demo data")
            return self._get_demo_chats()
        
        try:
            # Use the real MCP function to get chats
            chats = list_chats()
            self.logger.info(f"Retrieved {len(chats)} Instagram chats")
            return chats
        except Exception as e:
            self.logger.error(f"Error getting Instagram chats: {e}")
            return []
    
    def get_chat_messages(self, thread_id: str) -> List[Dict]:
        """Get messages from a specific Instagram chat"""
        if not MCP_AVAILABLE:
            return self._get_demo_messages(thread_id)
        
        try:
            # Use the real MCP function to get messages
            messages = list_messages(thread_id)
            self.logger.debug(f"Retrieved {len(messages)} messages from thread {thread_id}")
            return messages
        except Exception as e:
            self.logger.error(f"Error getting messages for thread {thread_id}: {e}")
            return []
    
    def _get_demo_chats(self) -> List[Dict]:
        """Demo data when MCP is not available"""
        return [
            {'thread_id': 'demo_thread_1', 'participants': ['suspicious_user']},
            {'thread_id': 'demo_thread_2', 'participants': ['normal_user']}
        ]
    
    def _get_demo_messages(self, thread_id: str) -> List[Dict]:
        """Demo messages when MCP is not available"""
        demo_messages = {
            'demo_thread_1': [
                {
                    'id': 'demo_msg_1',
                    'thread_id': thread_id,
                    'user_id': '12345',
                    'username': 'suspicious_user',
                    'text': "Hey gorgeous! You're absolutely perfect and I think we're soulmates! I need $500 for an emergency, can you help me on Venmo?",
                    'timestamp': datetime.now().isoformat(),
                    'is_from_me': False
                }
            ],
            'demo_thread_2': [
                {
                    'id': 'demo_msg_2', 
                    'thread_id': thread_id,
                    'user_id': '67890',
                    'username': 'normal_user',
                    'text': "Hi! I saw we both like hiking. Would you like to grab coffee sometime?",
                    'timestamp': datetime.now().isoformat(),
                    'is_from_me': False
                }
            ]
        }
        return demo_messages.get(thread_id, [])
    
    def analyze_instagram_message(self, message: Dict) -> Dict:
        """Analyze an Instagram message for red flags"""
        
        # Extract message details
        message_text = message.get('text', '')
        sender = message.get('username', 'unknown')
        message_id = message.get('id', '')
        
        if not message_text or message.get('is_from_me', False):
            return None
        
        # Skip if already processed
        if message_id in self.processed_messages:
            return None
        
        self.logger.info(f"Analyzing message from @{sender}")  # Removed emoji for Windows compatibility
        self.logger.debug(f"Message: {message_text[:100]}...")
        
        # Analyze with Red Flag Detector
        analysis = self.detector.analyze_message(message_text)
        
        # Add metadata
        analysis.update({
            'message_id': message_id,
            'thread_id': message.get('thread_id'),
            'sender': sender,
            'sender_id': message.get('user_id'),
            'timestamp': message.get('timestamp'),
            'instagram_message': message_text
        })
        
        # Mark as processed
        self.processed_messages.add(message_id)
        
        return analysis
    
    def handle_red_flag_detection(self, analysis: Dict):
        """Handle detected red flags with appropriate actions"""
        
        risk_level = analysis['risk_level']
        sender = analysis['sender']
        message_text = analysis['instagram_message']
        
        # Get risk level value
        if hasattr(risk_level, 'value'):
            risk_value = risk_level.value
        else:
            risk_value = str(risk_level)
        
        print(f"\n🚨 RED FLAG DETECTED!")
        print(f"👤 Sender: @{sender}")
        print(f"⚡ Risk Level: {risk_value.upper()}")
        print(f"💬 Message: \"{message_text[:100]}{'...' if len(message_text) > 100 else ''}\"")
        
        # Show detected red flags
        if analysis['red_flags']:
            print(f"🚩 Red Flags:")
            for flag in analysis['red_flags']:
                print(f"   - {flag.explanation}")
        
        # Show recommendations
        print(f"💡 Recommendations:")
        for rec in analysis['recommendations'][:3]:
            print(f"   {rec}")
        
        # Take action based on risk level
        if risk_level == RiskLevel.CRITICAL:
            self.handle_critical_risk(analysis)
        elif risk_level == RiskLevel.HIGH:
            self.handle_high_risk(analysis)
        
        # Save alert
        self.save_alert(analysis)
        
        print("-" * 60)
    
    def handle_critical_risk(self, analysis: Dict):
        """Handle critical risk messages"""
        thread_id = analysis.get('thread_id')
        sender = analysis.get('sender')
        
        print(f"🛡️ CRITICAL RISK ACTION:")
        print(f"   - Flagged conversation with @{sender}")
        print(f"   - User will be warned about this interaction")
        
        # In a real implementation, you could:
        # - Send a warning message to the user
        # - Auto-block the sender
        # - Report to Instagram
        
        if MCP_AVAILABLE and thread_id:
            try:
                # Example: Send a warning message (be careful with this in real use)
                warning_message = "⚠️ This conversation has been flagged by Red Flag Filter for containing potential scam or threat patterns. Please exercise extreme caution."
                # send_message(thread_id, warning_message)  # Uncomment to actually send
                print(f"   - Warning message prepared (not sent in demo)")
            except Exception as e:
                self.logger.error(f"Error sending warning message: {e}")
    
    def handle_high_risk(self, analysis: Dict):
        """Handle high risk messages"""
        print(f"⚠️ HIGH RISK ACTION:")
        print(f"   - Conversation flagged for user review")
        print(f"   - Safety recommendations provided")
    
    def save_alert(self, analysis: Dict):
        """Save alert to the alerts file for dashboard"""
        
        # Convert to dashboard format
        alert = {
            'timestamp': datetime.now().isoformat(),
            'sender': f"@{analysis['sender']}",
            'message': analysis['instagram_message'],
            'risk_level': analysis['risk_level'].value if hasattr(analysis['risk_level'], 'value') else str(analysis['risk_level']),
            'red_flags': [
                {
                    'category': flag.category,
                    'explanation': flag.explanation,
                    'confidence': flag.confidence
                }
                for flag in analysis['red_flags']
            ],
            'recommendations': analysis['recommendations'],
            'source': 'instagram_mcp'
        }
        
        # Load existing alerts
        alerts_file = 'red_flag_alerts.json'
        try:
            with open(alerts_file, 'r') as f:
                alerts_data = json.load(f)
        except FileNotFoundError:
            alerts_data = {'alerts': []}
        
        # Add new alert
        alerts_data['alerts'].append(alert)
        
        # Save back to file
        with open(alerts_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)
    
    def monitor_instagram_dms(self, duration_minutes: int = 5):
        """Monitor Instagram DMs for red flags"""
        
        print(f"🚩 STARTING INSTAGRAM DM MONITORING")
        print(f"⏱️ Duration: {duration_minutes} minutes")
        print(f"👤 Account: {self.username}")
        print("=" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        self.monitoring = True
        
        try:
            while self.monitoring and time.time() < end_time:
                # Get Instagram chats
                chats = self.get_instagram_chats()
                
                if not chats:
                    print("📭 No chats found, waiting...")
                    time.sleep(10)
                    continue
                
                print(f"📨 Checking {len(chats)} chat threads...")
                
                # Check each chat for new messages
                for chat in chats:
                    thread_id = chat.get('thread_id')
                    messages = self.get_chat_messages(thread_id)
                    
                    # Analyze each message
                    for message in messages:
                        analysis = self.analyze_instagram_message(message)
                        
                        if analysis:
                            # Check if it's a red flag
                            if analysis['risk_level'] in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
                                self.handle_red_flag_detection(analysis)
                            else:
                                sender = analysis.get('sender', 'unknown')
                                print(f"✅ Safe message from @{sender}")
                
                # Wait before next check
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        
        self.monitoring = False
        print(f"\n🎉 Monitoring session completed!")
    
    def test_integration(self):
        """Test the MCP integration with sample data"""
        
        print(f"🧪 TESTING INSTAGRAM MCP INTEGRATION")
        print("=" * 50)
        
        # Test getting chats
        chats = self.get_instagram_chats()
        print(f"📨 Found {len(chats)} chat threads")
        
        # Test analyzing messages from each chat
        for chat in chats[:2]:  # Test first 2 chats
            thread_id = chat.get('thread_id')
            messages = self.get_chat_messages(thread_id)
            
            print(f"\n💬 Analyzing {len(messages)} messages from thread {thread_id}")
            
            for message in messages:
                analysis = self.analyze_instagram_message(message)
                
                if analysis:
                    risk_level = analysis['risk_level'].value if hasattr(analysis['risk_level'], 'value') else str(analysis['risk_level'])
                    sender = analysis.get('sender')
                    
                    print(f"   @{sender}: {risk_level.upper()} risk")
                    
                    if analysis['risk_level'] in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
                        self.handle_red_flag_detection(analysis)

def main():
    try:
        monitor = InstagramRedFlagMonitor()
        
        # Test the integration first
        monitor.test_integration()
        
        # Ask if user wants to start real monitoring
        print(f"\n" + "=" * 60)
        choice = input("Start live Instagram DM monitoring? (y/n): ").strip().lower()
        
        if choice in ['y', 'yes']:
            duration = input("Enter monitoring duration in minutes (default 5): ").strip()
            duration = int(duration) if duration.isdigit() else 5
            
            monitor.monitor_instagram_dms(duration)
        else:
            print("✅ Integration test completed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your .env file is configured with Instagram credentials")

if __name__ == "__main__":
    main()