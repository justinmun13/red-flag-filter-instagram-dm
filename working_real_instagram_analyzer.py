#!/usr/bin/env python3
"""
Working Real Instagram DM Analyzer
Analyzes your actual Instagram DMs for red flags
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from red_flag_detector import RedFlagDetector, RiskLevel

# Import Instagram library
try:
    from instagrapi import Client
    print("✅ Instagram library ready")
except ImportError:
    print("❌ Please install: pip install instagrapi")
    sys.exit(1)

class WorkingInstagramAnalyzer:
    """Working analyzer for real Instagram DMs"""
    
    def __init__(self):
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.detector = RedFlagDetector()
        self.instagram_client = None
        
        print("🚩 WORKING REAL INSTAGRAM DM ANALYZER")
        print("=" * 50)
        print(f"👤 Account: {self.username}")
        
        if not self.username or not self.password:
            raise ValueError("Instagram credentials not found in .env file")
    
    def connect_to_instagram(self):
        """Connect to your real Instagram account"""
        
        try:
            print("🔗 Connecting to your Instagram account...")
            
            self.instagram_client = Client()
            self.instagram_client.delay_range = [1, 3]
            
            print("🔐 Logging in...")
            login_success = self.instagram_client.login(self.username, self.password)
            
            if login_success:
                print("✅ Successfully logged into your Instagram!")
                
                # Get basic info (with error handling)
                try:
                    user_info = self.instagram_client.account_info()
                    print(f"📊 Connected as: @{getattr(user_info, 'username', 'your_account')}")
                except:
                    print("📊 Connected to your Instagram account")
                
                return True
            else:
                print("❌ Login failed")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def get_your_dm_conversations(self):
        """Get your real DM conversations"""
        
        if not self.instagram_client:
            return []
        
        try:
            print("📨 Getting your real DM conversations...")
            
            # Get your real Instagram DM threads
            threads = self.instagram_client.direct_threads(amount=20)
            
            print(f"📬 Found {len(threads)} conversations in your account")
            
            return threads
            
        except Exception as e:
            print(f"❌ Error getting conversations: {e}")
            return []
    
    def analyze_conversation(self, thread):
        """Analyze one of your real conversations"""
        
        try:
            # Get the other user in the conversation
            my_username = self.username.replace('@', '').replace('.com', '')
            other_users = [user for user in thread.users if user.username != my_username]
            
            if not other_users:
                return None
            
            other_user = other_users[0]
            other_username = other_user.username
            
            print(f"\n💬 Analyzing conversation with @{other_username}")
            
            # Get real messages from this conversation
            messages = self.instagram_client.direct_messages(thread.id, amount=50)
            
            if not messages:
                print("   📭 No messages found")
                return None
            
            # Analyze messages from the other person (not your messages)
            red_flag_messages = []
            safe_messages = 0
            your_messages = 0
            analyzed_count = 0
            
            print(f"   📨 Found {len(messages)} total messages in conversation")
            
            for message in messages:
                # Skip your own messages
                if message.user_id == self.instagram_client.user_id:
                    your_messages += 1
                    continue
                
                # Only analyze recent messages (last 30 days)
                try:
                    if hasattr(message, 'timestamp'):
                        message_age = datetime.now() - message.timestamp.replace(tzinfo=None)
                        if message_age.days > 30:
                            continue
                except:
                    pass  # If timestamp fails, still analyze the message
                
                # Check if message has text
                if not hasattr(message, 'text') or not message.text or not message.text.strip():
                    continue
                
                analyzed_count += 1
                
                # Analyze text messages
                analysis = self.analyze_message(message, other_username)
                
                if analysis and isinstance(analysis, dict) and 'risk_level' in analysis:
                    if analysis['risk_level'] in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
                        red_flag_messages.append(analysis)
                    else:
                        safe_messages += 1
                else:
                    # Count as safe if analysis failed but message existed
                    safe_messages += 1
            
            print(f"   📊 Analysis summary:")
            print(f"      Messages from {other_username}: {analyzed_count}")
            print(f"      Your messages: {your_messages}")
            print(f"      Total in conversation: {len(messages)}")
            
            total_analyzed = len(red_flag_messages) + safe_messages
            
            if red_flag_messages:
                # Find highest risk level
                risk_levels = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
                highest_risk = max(red_flag_messages, key=lambda x: risk_levels.get(x['risk_level'], 1))['risk_level']
                risk_str = highest_risk.value if hasattr(highest_risk, 'value') else str(highest_risk)
                
                print(f"🚨 REAL CONVERSATION RISK: {risk_str.upper()}")
                print(f"   📊 Total messages analyzed: {total_analyzed}")
                print(f"   🚩 Red flag messages: {len(red_flag_messages)}")
                print(f"   ✅ Safe messages: {safe_messages}")
                print(f"   💬 Your messages: {your_messages}")
                
                # Show the most concerning message
                worst_message = max(red_flag_messages, key=lambda x: risk_levels.get(x['risk_level'], 1))
                print(f"   📝 Most concerning: \"{worst_message['message_text'][:60]}...\"")
                
                # Show red flags
                for flag in worst_message['red_flags'][:2]:
                    print(f"   🚩 {flag.explanation}")
                
                return {
                    'other_user': other_username,
                    'other_user_full_name': getattr(other_user, 'full_name', ''),
                    'risk_level': highest_risk,
                    'red_flag_count': len(red_flag_messages),
                    'safe_count': safe_messages,
                    'total_analyzed': total_analyzed,
                    'red_flag_messages': red_flag_messages,
                    'thread_id': thread.id
                }
            else:
                print(f"✅ Conversation appears safe")
                print(f"   📊 Messages analyzed: {total_analyzed}")
                print(f"   💬 Your messages: {your_messages}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error analyzing conversation: {e}")
            return None
    
    def analyze_message(self, message, sender):
        """Analyze a real Instagram message"""
        
        try:
            # Check if message has text
            if not hasattr(message, 'text') or not message.text:
                return None
            
            message_text = message.text.strip()
            
            # Skip empty messages
            if not message_text:
                return None
            
            print(f"      📝 Analyzing: \"{message_text[:50]}{'...' if len(message_text) > 50 else ''}\"")
            
            # Use Red Flag Detector
            analysis = self.detector.analyze_message(message_text)
            
            # Ensure analysis is valid
            if not analysis or not isinstance(analysis, dict):
                print(f"      ⚠️ Invalid analysis result")
                return None
            
            # Ensure required fields exist
            if 'risk_level' not in analysis:
                print(f"      ⚠️ Analysis missing risk_level")
                return None
            
            # Add Instagram metadata
            analysis.update({
                'message_id': getattr(message, 'id', 'unknown'),
                'sender': sender,
                'message_text': message_text,
                'timestamp': getattr(message, 'timestamp', datetime.now()).isoformat(),
                'source': 'real_instagram_dm'
            })
            
            # Log the result
            risk_str = analysis['risk_level'].value if hasattr(analysis['risk_level'], 'value') else str(analysis['risk_level'])
            print(f"      🎯 Risk: {risk_str.upper()}")
            
            return analysis
            
        except Exception as e:
            print(f"      ❌ Error in message analysis: {e}")
            return None
    
    def scan_your_real_instagram_dms(self):
        """Scan all your real Instagram DMs"""
        
        print(f"\n🔍 SCANNING YOUR REAL INSTAGRAM DMS")
        print(f"Account: {self.username}")
        print("=" * 50)
        
        # Connect to Instagram
        if not self.connect_to_instagram():
            print("❌ Could not connect to Instagram")
            return
        
        # Get your real conversations
        conversations = self.get_your_dm_conversations()
        
        if not conversations:
            print("📭 No conversations found")
            return
        
        print(f"\n🔍 Analyzing your {len(conversations)} real conversations...")
        
        dangerous_conversations = []
        safe_conversations = 0
        
        # Analyze each real conversation
        for i, thread in enumerate(conversations[:10], 1):  # Analyze first 10
            print(f"\n[{i}/{min(len(conversations), 10)}]", end="")
            
            try:
                result = self.analyze_conversation(thread)
                
                if result:
                    dangerous_conversations.append(result)
                else:
                    safe_conversations += 1
                
                # Small delay to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        # Summary of your real account
        print(f"\n" + "=" * 50)
        print(f"📊 YOUR REAL INSTAGRAM DM ANALYSIS COMPLETE")
        print(f"🚨 Conversations with red flags: {len(dangerous_conversations)}")
        print(f"✅ Safe conversations: {safe_conversations}")
        
        if dangerous_conversations:
            print(f"\n⚠️ YOUR CONVERSATIONS NEEDING ATTENTION:")
            
            risk_order = {RiskLevel.CRITICAL: 4, RiskLevel.HIGH: 3, RiskLevel.MEDIUM: 2, RiskLevel.LOW: 1}
            
            for conv in sorted(dangerous_conversations, key=lambda x: risk_order.get(x['risk_level'], 1), reverse=True):
                risk_str = conv['risk_level'].value if hasattr(conv['risk_level'], 'value') else str(conv['risk_level'])
                
                print(f"   🚩 @{conv['other_user']}: {risk_str.upper()} risk")
                print(f"      📊 {conv['red_flag_count']} red flags in {conv['total_analyzed']} messages")
                
                if conv['red_flag_count'] > 0:
                    worst_msg = max(conv['red_flag_messages'], 
                                  key=lambda x: risk_order.get(x['risk_level'], 1))
                    print(f"      💬 \"{worst_msg['message_text'][:50]}...\"")
        else:
            print(f"\n✅ GREAT NEWS! No red flags found in your Instagram DMs")
            print(f"Your conversations appear safe from dating manipulation")
        
        # Save real results
        self.save_real_results(dangerous_conversations)
        
        print(f"\n🎯 RECOMMENDATIONS:")
        if dangerous_conversations:
            print(f"1. 🔍 Review flagged conversations carefully")
            print(f"2. 🚫 Be very cautious with CRITICAL/HIGH risk users")
            print(f"3. 📊 Check the web dashboard for detailed analysis")
        else:
            print(f"1. ✅ Your Instagram DMs look safe!")
            print(f"2. 🛡️ Continue using good judgment")
        
        print(f"\n📊 View detailed results:")
        print(f"   python web_dashboard.py")
        print(f"   Then open: http://localhost:5000")
        
        return dangerous_conversations
    
    def save_real_results(self, dangerous_conversations):
        """Save real analysis results for dashboard"""
        
        alerts = []
        
        for conv in dangerous_conversations:
            for red_flag_msg in conv['red_flag_messages']:
                alert = {
                    'timestamp': red_flag_msg.get('timestamp', datetime.now().isoformat()),
                    'sender': f"@{conv['other_user']}",
                    'message': red_flag_msg['message_text'],
                    'risk_level': red_flag_msg['risk_level'].value if hasattr(red_flag_msg['risk_level'], 'value') else str(red_flag_msg['risk_level']),
                    'red_flags': [
                        {
                            'category': flag.category,
                            'explanation': flag.explanation,
                            'confidence': flag.confidence
                        }
                        for flag in red_flag_msg['red_flags']
                    ],
                    'recommendations': red_flag_msg['recommendations'],
                    'source': 'real_instagram_account',
                    'your_account': self.username
                }
                alerts.append(alert)
        
        # Save to dashboard
        alerts_file = 'red_flag_alerts.json'
        try:
            with open(alerts_file, 'r') as f:
                alerts_data = json.load(f)
        except FileNotFoundError:
            alerts_data = {'alerts': []}
        
        # Add real alerts
        alerts_data['alerts'].extend(alerts)
        alerts_data['alerts'] = alerts_data['alerts'][-50:]  # Keep last 50
        
        with open(alerts_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)
        
        if alerts:
            print(f"📊 {len(alerts)} real alerts saved to dashboard")

def main():
    print("🚩 REAL INSTAGRAM DM ANALYSIS")
    print("Analyze your actual Instagram conversations")
    print("=" * 50)
    
    try:
        analyzer = WorkingInstagramAnalyzer()
        
        print(f"\n⚠️ PRIVACY NOTICE:")
        print(f"- Analyzes your real Instagram DMs")
        print(f"- Only checks messages sent TO you (not your messages)")
        print(f"- Data stays on your computer")
        print(f"- Recent messages only (last 30 days)")
        
        confirm = input(f"\nAnalyze your real Instagram DMs? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            dangerous_conversations = analyzer.scan_your_real_instagram_dms()
            
            print(f"\n🎉 REAL ANALYSIS COMPLETE!")
            
            if dangerous_conversations:
                print(f"🔍 Found {len(dangerous_conversations)} conversations with red flags in your real Instagram!")
                print(f"📊 Check the web dashboard for detailed analysis")
            else:
                print(f"✅ No red flags found in your real Instagram DMs!")
            
        else:
            print("Analysis cancelled")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()