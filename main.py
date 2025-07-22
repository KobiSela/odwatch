import requests
import time
import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
import random

class InstagramStoryBot:
    def __init__(self, bot_token, chat_id, instagram_username):
        """
        Initialize the Instagram Story Bot
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.instagram_username = instagram_username
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # File to track sent stories
        self.sent_stories_file = "sent_stories.json"
        self.sent_stories = self.load_sent_stories()
        
        # Headers to mimic real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Session for maintaining cookies
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def load_sent_stories(self):
        """Load the list of already sent stories"""
        try:
            if os.path.exists(self.sent_stories_file):
                with open(self.sent_stories_file, 'r') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def save_sent_stories(self):
        """Save the list of sent stories"""
        try:
            with open(self.sent_stories_file, 'w') as f:
                json.dump(self.sent_stories, f)
        except Exception as e:
            print(f"❌ Error saving sent stories: {e}")
    
    def send_telegram_message(self, message):
        """Send text message to Telegram"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, data=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def send_telegram_photo(self, photo_url, caption=""):
        """Send photo URL to Telegram"""
        url = f"{self.base_url}/sendPhoto"
        payload = {
            'chat_id': self.chat_id,
            'photo': photo_url,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Telegram error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending photo: {e}")
            return False
    
    def send_telegram_video(self, video_url, caption=""):
        """Send video URL to Telegram"""
        url = f"{self.base_url}/sendVideo"
        payload = {
            'chat_id': self.chat_id,
            'video': video_url,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Telegram error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending video: {e}")
            return False
    
    def get_instagram_stories_direct(self):
        """Get stories using direct Instagram API with advanced evasion"""
        try:
            print(f"🔍 Checking stories for @{self.instagram_username} using direct method...")
            
            # Multiple approaches to access Instagram data
            approaches = [
                self.try_instagram_public_api,
                self.try_instagram_web_interface,
                self.simulate_stories_for_demo
            ]
            
            for approach in approaches:
                try:
                    stories = approach()
                    if stories:
                        return stories
                except Exception as e:
                    print(f"❌ Approach failed: {e}")
                    continue
            
            return []
            
        except Exception as e:
            print(f"❌ Error in direct method: {e}")
            return []
    
    def try_instagram_public_api(self):
        """Try Instagram's public API endpoints"""
        try:
            print("🔄 Trying Instagram public API...")
            
            # This would require proper Instagram API setup
            # For demo purposes, we'll simulate the response
            print("ℹ️ Instagram API requires authentication - would need Instagram Developer Account")
            return []
            
        except Exception as e:
            print(f"❌ Instagram API error: {e}")
            return []
    
    def try_instagram_web_interface(self):
        """Try accessing Instagram web interface directly"""
        try:
            print("🌐 Trying Instagram web interface...")
            
            # Instagram web interface requires complex authentication
            # This would need session management, CSRF tokens, etc.
            print("ℹ️ Instagram web interface requires complex authentication")
            return []
            
        except Exception as e:
            print(f"❌ Web interface error: {e}")
            return []
    
    def simulate_stories_for_demo(self):
        """Simulate story detection for demonstration"""
        try:
            print("🎭 Demo mode: Simulating story detection...")
            
            # For demonstration, we'll create a fake story every 30 minutes
            current_time = datetime.now()
            demo_story_id = f"demo_{self.instagram_username}_{current_time.strftime('%Y%m%d_%H')}"
            
            # Check if we already sent this demo story
            if demo_story_id not in self.sent_stories:
                # Create a demo story with a sample image URL
                demo_story = {
                    'id': demo_story_id,
                    'url': 'https://picsum.photos/400/600',  # Random demo image
                    'type': 'photo',
                    'timestamp': current_time
                }
                
                print(f"🎯 Created demo story: {demo_story_id}")
                return [demo_story]
            else:
                print("ℹ️ Demo story already sent this hour")
                return []
            
        except Exception as e:
            print(f"❌ Demo simulation error: {e}")
            return []
    
    def get_stories_api_alternative(self):
        """Alternative API approach using public Instagram endpoints"""
        try:
            print(f"🔄 Trying alternative API approach for @{self.instagram_username}...")
            
            # This is a simplified approach - in reality, Instagram's API is complex
            # For a production bot, you'd want to use official Instagram Basic Display API
            # or a paid service like RapidAPI
            
            # For now, we'll simulate finding stories
            print("ℹ️ Alternative API approach - would require Instagram API keys")
            print("💡 Consider using Instagram Basic Display API for production")
            
            return []
            
        except Exception as e:
            print(f"❌ Error in alternative API: {e}")
            return []
    
    def process_new_stories(self):
        """Check for new stories and send them"""
        stories = self.get_instagram_stories_web()
        
        if not stories:
            print("ℹ️ No new stories found")
            return
        
        print(f"📱 Found {len(stories)} new stories")
        
        for story in stories:
            try:
                # Prepare caption
                caption = f"📸 Story מ-@{self.instagram_username}\n🕐 {story['timestamp'].strftime('%d/%m/%Y %H:%M')}"
                
                # Send to Telegram
                success = False
                if story['type'] == 'video':
                    success = self.send_telegram_video(story['url'], caption)
                elif story['type'] == 'photo':
                    success = self.send_telegram_photo(story['url'], caption)
                
                if success:
                    print(f"✅ Sent story from @{self.instagram_username}")
                    
                    # Mark as sent
                    self.sent_stories.append(story['id'])
                    self.save_sent_stories()
                    
                    # Clean up old entries (keep only last 100)
                    if len(self.sent_stories) > 100:
                        self.sent_stories = self.sent_stories[-100:]
                        self.save_sent_stories()
                else:
                    print(f"❌ Failed to send story from @{self.instagram_username}")
                
                # Wait between sends to avoid rate limiting
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ Error processing story: {e}")
    
    def start_monitoring(self):
        """Start monitoring Instagram stories"""
        print(f"🚀 Starting Instagram Story Monitor...")
        print(f"👤 Monitoring: @{self.instagram_username}")
        print(f"📱 Sending to Telegram chat: {self.chat_id}")
        print(f"⏱️ Checking every 5 minutes...")
        
        # Send startup message
        self.send_telegram_message(f"🤖 Instagram Story Bot V3 הופעל!\n👤 עוקב אחר: @{self.instagram_username}\n\n⚠️ Demo Mode:\nהבוט ישלח תמונת דוגמה כל שעה להדגמה\n\n💡 לחיבור אמיתי לאינסטגרם נדרש Instagram API Key")
        
        # Send existing stories on first run
        print("📸 Checking for existing stories to send...")
        self.process_new_stories()
        
        while True:
            try:
                self.process_new_stories()
                print(f"⏳ Next check in 5 minutes... ({datetime.now().strftime('%H:%M:%S')})")
                time.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("⏳ Retrying in 1 minute...")
                time.sleep(60)

def main():
    # Configuration - קורא מ-Environment Variables
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    CHAT_ID = os.getenv('CHAT_ID') 
    INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
    
    # Validate configuration
    if not BOT_TOKEN or not CHAT_ID or not INSTAGRAM_USERNAME:
        print("❌ Missing environment variables!")
        print("Required: BOT_TOKEN, CHAT_ID, INSTAGRAM_USERNAME")
        return
    
    print(f"🚀 Starting bot with username: @{INSTAGRAM_USERNAME}")
    
    # Create and start the bot
    bot = InstagramStoryBot(BOT_TOKEN, CHAT_ID, INSTAGRAM_USERNAME)
    bot.start_monitoring()

if __name__ == "__main__":
    main()
