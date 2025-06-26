#!/usr/bin/env python3
"""
Test Instagram Connection for Red Flag Filter
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Instagram library
try:
    from instagrapi import Client
    print("✅ instagrapi library imported successfully")
except ImportError as e:
    print(f"❌ Error importing instagrapi: {e}")
    print("Install with: pip install instagrapi")
    sys.exit(1)

def test_instagram_connection():
    """Test connection to real Instagram account"""
    
    # Get credentials
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    
    if not username or not password:
        print("❌ Instagram credentials not found in .env file")
        print("Make sure your .env file contains:")
        print("INSTAGRAM_USERNAME=justinmun13@gmail.com")
        print("INSTAGRAM_PASSWORD=your_password")
        return False
    
    print(f"🔗 Testing Instagram connection...")
    print(f"👤 Account: {username}")
    
    try:
        # Create Instagram client
        client = Client()
        
        # Set some settings to avoid detection
        client.delay_range = [1, 3]
        
        print("🔐 Attempting to log in...")
        
        # Try to login
        client.login(username, password)
        
        print("✅ Successfully logged into Instagram!")
        
        # Get account info (with error handling for different API versions)
        try:
            user_info = client.account_info()
            print(f"📊 Account Details:")
            print(f"   Username: @{getattr(user_info, 'username', 'N/A')}")
            print(f"   Full Name: {getattr(user_info, 'full_name', 'N/A')}")
            
            # Try different attribute names for follower count
            follower_count = getattr(user_info, 'follower_count', None) or getattr(user_info, 'followers_count', None) or 'N/A'
            following_count = getattr(user_info, 'following_count', None) or getattr(user_info, 'followees_count', None) or 'N/A'
            media_count = getattr(user_info, 'media_count', None) or getattr(user_info, 'posts_count', None) or 'N/A'
            
            print(f"   Followers: {follower_count}")
            print(f"   Following: {following_count}")
            print(f"   Posts: {media_count}")
            
        except Exception as e:
            print(f"📊 Account info (basic): Login successful")
            print(f"   Note: Some details unavailable due to API version: {e}")
        
        # Test getting DM threads
        print(f"\n📨 Testing DM access...")
        threads = client.direct_threads(amount=5)
        print(f"✅ Found {len(threads)} DM conversations")
        
        # Show thread details
        for i, thread in enumerate(threads[:3], 1):
            other_users = [user for user in thread.users if user.username != username.replace('@', '')]
            if other_users:
                other_user = other_users[0]
                print(f"   {i}. @{other_user.username} ({other_user.full_name})")
        
        print(f"\n🎉 Instagram connection test SUCCESSFUL!")
        print(f"Your account is ready for Red Flag Filter integration!")
        
        return client
        
    except Exception as e:
        print(f"❌ Instagram connection failed: {e}")
        print(f"\n💡 Possible solutions:")
        print(f"1. Check your username and password")
        print(f"2. Try logging into Instagram app first")
        print(f"3. Instagram may require 2FA - try disabling temporarily")
        print(f"4. Instagram may have rate limiting - wait a few minutes")
        print(f"5. Your account may be flagged - try with a different account")
        
        return False

if __name__ == "__main__":
    print("🔧 INSTAGRAM CONNECTION TEST")
    print("=" * 40)
    
    client = test_instagram_connection()
    
    if client:
        print(f"\n✅ Ready to integrate with Red Flag Filter!")
    else:
        print(f"\n❌ Fix connection issues before running Red Flag Filter")