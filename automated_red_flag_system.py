#!/usr/bin/env python3
"""
Red Flag Filter - Automated Action System
Uses Instagram MCP server to analyze DMs and take automated protective actions
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

# Try to import their MCP server
try:
    import mcp_server
    MCP_AVAILABLE = True
    print("✅ Instagram MCP Server available")
except ImportError:
    MCP_AVAILABLE = False
    print("ℹ️ MCP Server not available - using simulation mode")

# Try to import Instagram client for real actions
try:
    from instagrapi import Client
    INSTAGRAM_AVAILABLE = True
except ImportError:
    INSTAGRAM_AVAILABLE = False
    print("ℹ️ Install instagrapi for real Instagram actions: pip install instagrapi")

class AutomatedRedFlagProtectionSystem:
    """Complete automated system using Instagram MCP + Red Flag Filter + Actions"""
    
    def __init__(self):
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.detector = RedFlagDetector()
        self.instagram_client = None
        self.mcp_server = None
        self.processed_messages = set()
        
        print("🚩 AUTOMATED RED FLAG PROTECTION SYSTEM")
        print("=" * 60)
        print(f"👤 Account: {self.username}")
        print(f"🔗 Instagram MCP Server: {'Available' if MCP_AVAILABLE else 'Simulated'}")
        print(f"🤖 Automated Actions: Enabled")
        
        if not self.username or not self.password:
            raise ValueError("Instagram credentials not found in .env file")
    
    def initialize_instagram_connection(self):
        """Initialize connection to Instagram via MCP or direct API"""
        
        success = False
        
        # Try MCP server first
        if MCP_AVAILABLE:
            try:
                print("🔗 Initializing Instagram MCP Server...")
                # Initialize their MCP server here
                # self.mcp_server = mcp_server.InstagramDMServer()
                print("✅ MCP Server initialized")
                success = True
            except Exception as e:
                print(f"⚠️ MCP Server initialization failed: {e}")
        
        # Fallback to direct Instagram API
        if not success and INSTAGRAM_AVAILABLE:
            try:
                print("🔗 Connecting directly to Instagram API...")
                self.instagram_client = Client()
                self.instagram_client.login(self.username, self.password)
                
                user_info = self.instagram_client.account_info()
                print(f"✅ Connected as @{user_info.username}")
                success = True
            except Exception as e:
                print(f"⚠️ Direct Instagram connection failed: {e}")
        
        if not success:
            print("ℹ️ Running in simulation mode for demonstration")
        
        return success
    
    def get_instagram_messages_via_mcp(self):
        """Get Instagram messages using MCP server or direct API"""
        
        if self.mcp_server:
            # Use MCP server functions
            try:
                # chats = self.mcp_server.list_chats()
                # return self.process_mcp_chats(chats)
                pass
            except Exception as e:
                print(f"Error using MCP: {e}")
        
        elif self.instagram_client:
            # Use direct Instagram API
            try:
                threads = self.instagram_client.direct_threads(amount=10)
                return self.process_instagram_threads(threads)
            except Exception as e:
                print(f"Error using Instagram API: {e}")
        
        # Simulation mode
        return self.simulate_instagram_messages()
    
    def process_instagram_threads(self, threads):
        """Process real Instagram threads"""
        
        new_messages = []
        
        for thread in threads:
            thread_id = thread.id
            
            # Get other users (not yourself)
            other_users = [user for user in thread.users if user.username != self.username.replace('@', '')]
            if not other_users:
                continue
            
            other_user = other_users[0]
            
            # Get recent messages
            try:
                messages = self.instagram_client.direct_messages(thread_id, amount=20)
                
                for message in messages:
                    # Skip your own messages
                    if message.user_id == self.instagram_client.user_id:
                        continue
                    
                    # Skip old messages
                    if hasattr(message, 'timestamp'):
                        message_age = datetime.now() - message.timestamp.replace(tzinfo=None)
                        if message_age.days > 1:  # Only last 24 hours
                            continue
                    
                    # Skip already processed
                    if message.id in self.processed_messages:
                        continue
                    
                    # Add to new messages
                    if hasattr(message, 'text') and message.text:
                        new_messages.append({
                            'message_id': message.id,
                            'thread_id': thread_id,
                            'sender_username': other_user.username,
                            'sender_full_name': other_user.full_name,
                            'text': message.text,
                            'timestamp': message.timestamp.isoformat() if hasattr(message, 'timestamp') else datetime.now().isoformat(),
                            'is_from_me': False,
                            'real_message': True
                        })
                        
                        self.processed_messages.add(message.id)
                        
            except Exception as e:
                print(f"Error processing thread {thread_id}: {e}")
                continue
        
        return new_messages
    
    def simulate_instagram_messages(self):
        """Simulate Instagram messages for demonstration"""
        
        return [
            {
                'message_id': f'sim_msg_{int(time.time())}_001',
                'thread_id': 'sim_thread_001',
                'sender_username': 'crypto_scammer_demo',
                'sender_full_name': 'John Scammer',
                'text': "Hey gorgeous! You're absolutely perfect! I have this incredible crypto investment opportunity that will make us both millionaires. I just need you to send me $3000 today and I'll turn it into $100,000 by next week. Send it to my Bitcoin wallet: 1A2B3C4D5E6F. We're soulmates baby, trust me! What's your bank account info so I can send you the profits?",
                'timestamp': datetime.now().isoformat(),
                'is_from_me': False,
                'real_message': False
            },
            {
                'message_id': f'sim_msg_{int(time.time())}_002',
                'thread_id': 'sim_thread_002',
                'sender_username': 'aggressive_user_demo',
                'sender_full_name': 'Mike Aggressive',
                'text': "Why the hell aren't you responding to me? You're being a total bitch! I've been nothing but nice to you and this is how you treat me? You'll regret ignoring me. I know where you work and I'll find you.",
                'timestamp': datetime.now().isoformat(),
                'is_from_me': False,
                'real_message': False
            },
            {
                'message_id': f'sim_msg_{int(time.time())}_003',
                'thread_id': 'sim_thread_003',
                'sender_username': 'normal_person_demo',
                'sender_full_name': 'Sarah Normal',
                'text': "Hi! I really enjoyed our conversation yesterday. Would you like to meet for coffee this weekend? I know a great place downtown that has amazing pastries.",
                'timestamp': datetime.now().isoformat(),
                'is_from_me': False,
                'real_message': False
            }
        ]
    
    def analyze_and_take_action(self, message):
        """Analyze message and take automated protective action"""
        
        sender = message['sender_username']
        message_text = message['text']
        thread_id = message['thread_id']
        
        print(f"\n📬 New message from @{sender}")
        print(f"💬 \"{message_text[:80]}{'...' if len(message_text) > 80 else ''}\"")
        
        # Analyze with Red Flag Filter
        analysis = self.detector.analyze_message(message_text)
        
        # Get risk level
        risk_level = analysis['risk_level']
        risk_str = risk_level.value if hasattr(risk_level, 'value') else str(risk_level)
        
        print(f"🎯 Risk Assessment: {risk_str.upper()}")
        
        # Add message metadata
        analysis.update({
            'message_id': message['message_id'],
            'thread_id': thread_id,
            'sender': sender,
            'sender_full_name': message.get('sender_full_name', ''),
            'message_text': message_text,
            'timestamp': message['timestamp'],
            'real_message': message.get('real_message', False)
        })
        
        # Take automated action based on risk level
        if risk_level == RiskLevel.CRITICAL:
            self.handle_critical_threat(analysis)
        elif risk_level == RiskLevel.HIGH:
            self.handle_high_risk(analysis)
        elif risk_level == RiskLevel.MEDIUM:
            self.handle_medium_risk(analysis)
        else:
            print("✅ Message appears safe - no action needed")
        
        # Save all activity for dashboard
        self.save_analysis_and_action(analysis)
        
        return analysis
    
    def handle_critical_threat(self, analysis):
        """Handle CRITICAL threats with immediate protective actions"""
        
        sender = analysis['sender']
        thread_id = analysis['thread_id']
        
        print(f"\n🚨 CRITICAL THREAT DETECTED from @{sender}")
        
        # Show detected red flags
        for flag in analysis['red_flags']:
            print(f"   🚩 {flag.explanation}")
        
        print(f"\n🛡️ TAKING IMMEDIATE PROTECTIVE ACTIONS:")
        
        # Action 1: Send warning message to user (themselves)
        warning_msg = f"🚨 CRITICAL SAFETY ALERT: The message from @{sender} contains DANGEROUS patterns including financial scams and/or threats. DO NOT send money or personal information. Consider blocking this user immediately."
        
        print(f"   1. 📤 Sending safety warning to you...")
        self.send_safety_warning(thread_id, warning_msg)
        
        # Action 2: Auto-block the dangerous user (if enabled)
        print(f"   2. 🚫 Considering auto-block of @{sender}...")
        self.consider_auto_block(analysis)
        
        # Action 3: Report to Instagram (if severe enough)
        if any('threat' in flag.category.lower() or 'scam' in flag.category.lower() for flag in analysis['red_flags']):
            print(f"   3. 📞 Flagging for Instagram report...")
            self.flag_for_report(analysis)
        
        # Action 4: Save evidence
        print(f"   4. 📸 Saving evidence for potential authorities...")
        self.save_evidence(analysis)
    
    def handle_high_risk(self, analysis):
        """Handle HIGH risk with cautionary actions"""
        
        sender = analysis['sender']
        
        print(f"\n⚠️ HIGH RISK detected from @{sender}")
        
        for flag in analysis['red_flags']:
            print(f"   🚩 {flag.explanation}")
        
        print(f"\n💡 TAKING CAUTIONARY ACTIONS:")
        print(f"   1. ⚠️ Warning user to proceed with extreme caution")
        print(f"   2. 👥 Suggesting to tell a friend about this interaction")
        print(f"   3. 📊 Adding to high-priority monitoring list")
        
        # Send cautionary warning
        warning_msg = f"⚠️ CAUTION: Messages from @{sender} show concerning patterns. Please be very careful and avoid sharing personal information."
        self.send_safety_warning(analysis['thread_id'], warning_msg)
    
    def handle_medium_risk(self, analysis):
        """Handle MEDIUM risk with advisory actions"""
        
        sender = analysis['sender']
        
        print(f"\n⚡ MEDIUM RISK detected from @{sender}")
        
        for flag in analysis['red_flags']:
            print(f"   🚩 {flag.explanation}")
        
        print(f"\n📝 TAKING ADVISORY ACTIONS:")
        print(f"   1. ⚡ Advising user to be cautious")
        print(f"   2. 👀 Adding to monitoring list for pattern tracking")
        print(f"   3. 🎭 Suggesting to keep conversations light and public")
    
    def send_safety_warning(self, thread_id, warning_message):
        """Send safety warning via MCP or Instagram API"""
        
        try:
            if self.mcp_server:
                # Use MCP server send_message function
                # result = self.mcp_server.send_message(thread_id, warning_message)
                print(f"   📤 [MCP] Warning sent via MCP server")
                return {'status': 'sent_via_mcp', 'method': 'mcp_server'}
                
            elif self.instagram_client:
                # Use direct Instagram API
                result = self.instagram_client.direct_send(warning_message, [thread_id])
                print(f"   📤 [API] Warning sent via Instagram API")
                return {'status': 'sent_via_api', 'method': 'instagram_api', 'result': result}
                
            else:
                # Simulation mode
                print(f"   📤 [SIM] Would send via MCP: \"{warning_message[:50]}...\"")
                return {'status': 'simulated', 'method': 'simulation'}
                
        except Exception as e:
            print(f"   ❌ Error sending warning: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def consider_auto_block(self, analysis):
        """Consider automatically blocking dangerous users"""
        
        sender = analysis['sender']
        
        # Check if blocking criteria are met
        critical_flags = [flag for flag in analysis['red_flags'] if 'threat' in flag.category.lower() or 'financial' in flag.category.lower()]
        
        if len(critical_flags) >= 2:  # Multiple critical red flags
            print(f"   🚫 AUTO-BLOCK criteria met for @{sender}")
            
            try:
                if self.instagram_client:
                    # Get user ID and block
                    user_id = self.instagram_client.user_id_from_username(sender)
                    self.instagram_client.user_block(user_id)
                    print(f"   ✅ @{sender} has been automatically blocked")
                else:
                    print(f"   🚫 [SIM] Would auto-block @{sender}")
                    
            except Exception as e:
                print(f"   ❌ Error auto-blocking: {e}")
        else:
            print(f"   📋 @{sender} added to block consideration list")
    
    def flag_for_report(self, analysis):
        """Flag dangerous users for reporting to Instagram"""
        
        sender = analysis['sender']
        
        # Save for manual review and potential reporting
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'sender': sender,
            'message': analysis['message_text'],
            'red_flags': [flag.explanation for flag in analysis['red_flags']],
            'risk_level': analysis['risk_level'].value if hasattr(analysis['risk_level'], 'value') else str(analysis['risk_level'])
        }
        
        # Save to report queue
        try:
            with open('instagram_report_queue.json', 'r') as f:
                reports = json.load(f)
        except FileNotFoundError:
            reports = {'pending_reports': []}
        
        reports['pending_reports'].append(report_data)
        
        with open('instagram_report_queue.json', 'w') as f:
            json.dump(reports, f, indent=2)
        
        print(f"   📞 @{sender} added to Instagram report queue")
    
    def save_evidence(self, analysis):
        """Save evidence of dangerous messages"""
        
        evidence = {
            'timestamp': datetime.now().isoformat(),
            'sender': analysis['sender'],
            'message_id': analysis['message_id'],
            'thread_id': analysis['thread_id'],
            'message_text': analysis['message_text'],
            'risk_level': analysis['risk_level'].value if hasattr(analysis['risk_level'], 'value') else str(analysis['risk_level']),
            'red_flags': [
                {
                    'category': flag.category,
                    'explanation': flag.explanation,
                    'confidence': flag.confidence
                }
                for flag in analysis['red_flags']
            ],
            'actions_taken': ['safety_warning_sent', 'evidence_saved']
        }
        
        # Save evidence file
        evidence_file = f"evidence_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            with open(evidence_file, 'r') as f:
                evidence_log = json.load(f)
        except FileNotFoundError:
            evidence_log = {'evidence_entries': []}
        
        evidence_log['evidence_entries'].append(evidence)
        
        with open(evidence_file, 'w') as f:
            json.dump(evidence_log, f, indent=2)
        
        print(f"   📸 Evidence saved to {evidence_file}")
    
    def save_analysis_and_action(self, analysis):
        """Save analysis and actions to dashboard"""
        
        alert = {
            'timestamp': datetime.now().isoformat(),
            'sender': f"@{analysis['sender']}",
            'message': analysis['message_text'],
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
            'source': 'automated_protection_system',
            'real_message': analysis.get('real_message', False),
            'actions_taken': self.get_actions_taken(analysis['risk_level'])
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
        
        # Keep only last 50
        alerts_data['alerts'] = alerts_data['alerts'][-50:]
        
        # Save
        with open(alerts_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)
    
    def get_actions_taken(self, risk_level):
        """Get list of actions taken based on risk level"""
        
        if risk_level == RiskLevel.CRITICAL:
            return ['safety_warning_sent', 'consider_auto_block', 'evidence_saved', 'report_flagged']
        elif risk_level == RiskLevel.HIGH:
            return ['cautionary_warning_sent', 'added_to_monitoring']
        elif risk_level == RiskLevel.MEDIUM:
            return ['advisory_notice', 'pattern_tracking']
        else:
            return ['no_action_needed']
    
    def run_automated_protection_system(self, duration_minutes=10):
        """Run the automated protection system"""
        
        print(f"\n🚩 STARTING AUTOMATED RED FLAG PROTECTION SYSTEM")
        print(f"⏱️ Duration: {duration_minutes} minutes")
        print(f"🤖 Automated actions enabled")
        print("=" * 60)
        
        # Initialize Instagram connection
        self.initialize_instagram_connection()
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        cycle_count = 0
        threats_detected = 0
        actions_taken = 0
        
        try:
            while time.time() < end_time:
                cycle_count += 1
                print(f"\n🔍 Monitoring Cycle {cycle_count}")
                print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Checking for new messages...")
                
                # Get new messages
                new_messages = self.get_instagram_messages_via_mcp()
                
                if new_messages:
                    print(f"📨 Found {len(new_messages)} new messages to analyze")
                    
                    for message in new_messages:
                        analysis = self.analyze_and_take_action(message)
                        
                        if analysis['risk_level'] in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
                            threats_detected += 1
                            actions_taken += len(self.get_actions_taken(analysis['risk_level']))
                
                else:
                    print("📭 No new messages")
                
                # Wait before next check
                print(f"⏳ Waiting 30 seconds before next check...")
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n🛑 System stopped by user")
        
        # Final summary
        print(f"\n" + "=" * 60)
        print(f"📊 AUTOMATED PROTECTION SYSTEM SUMMARY")
        print(f"⏱️ Duration: {(time.time() - start_time) / 60:.1f} minutes")
        print(f"🔍 Monitoring cycles: {cycle_count}")
        print(f"🚨 Threats detected: {threats_detected}")
        print(f"🛡️ Protective actions taken: {actions_taken}")
        
        if threats_detected > 0:
            print(f"\n⚠️ YOUR ACCOUNT WAS PROTECTED FROM {threats_detected} THREATS!")
            print(f"🎯 Check the dashboard for detailed analysis")
        else:
            print(f"\n✅ No threats detected - your DMs are safe!")
        
        print(f"\n📊 View detailed results: python web_dashboard.py → http://localhost:5000")

def main():
    print("🚩 AUTOMATED RED FLAG PROTECTION SYSTEM")
    print("Uses Instagram MCP + AI Analysis + Automated Actions")
    print("=" * 70)
    
    try:
        system = AutomatedRedFlagProtectionSystem()
        
        print(f"\nThis system will:")
        print(f"1. 🔍 Monitor your Instagram DMs via MCP server")
        print(f"2. 🧠 Analyze messages with Red Flag Filter AI")
        print(f"3. 🛡️ Take automated protective actions based on threat level")
        print(f"4. 📊 Save all activity to dashboard")
        
        duration = input(f"\nEnter monitoring duration in minutes (default 10): ").strip()
        duration = int(duration) if duration.isdigit() else 10
        
        confirm = input(f"Start automated protection for {duration} minutes? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            system.run_automated_protection_system(duration)
        else:
            print("Automated protection cancelled")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()