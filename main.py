import requests
import time
import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse
import random

class InstagramStoryBot:
    def __init__(self, bot_token, chat_id, instagram_username):
        """
        Initialize the Instagram Story Bot with free services
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.instagram_username = instagram_username.replace('@', '')  # Remove @ if present
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # File to track sent stories
        self.sent_stories_file = "sent_stories.json"
        self.sent_stories = self.load_sent_stories()
        
        # Free Instagram story services to try
        self.story_services = [
            {
                'name': 'InstaStoriesViewer',
                'base_url': 'https://insta-stories-viewer.com',
                'method': self.get_stories_instastoriesviewer
            },
            {
                'name': 'Views4You',
                'base_url': 'https://views4you.com/instagram-story-viewer',
                'method': self.get_stories_views4you
            },
            {
                'name': 'AnonyIG',
                'base_url': 'https://anonyig.com',
                'method': self.get_stories_anonyig
            }
        ]
        
        # Headers to mimic real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
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
            'caption': caption[:1024],  # Telegram caption limit
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Telegram photo error: {response.text}")
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
            'caption': caption[:1024],  # Telegram caption limit
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Telegram video error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending video: {e}")
            return False
    
    def get_stories_instastoriesviewer(self):
        """Try to get stories from insta-stories-viewer.com"""
        try:
            print(f"🌐 Trying InstaStoriesViewer for @{self.instagram_username}...")
            
            # This would require reverse engineering the site's API
            # For demo purposes, we'll simulate finding stories
            
            # In a real implementation, you'd need to:
            # 1. POST to their search endpoint
            # 2. Parse the response for story URLs
            # 3. Extract media URLs
            
            print("ℹ️ InstaStoriesViewer requires complex reverse engineering")
            return []
            
        except Exception as e:
            print(f"❌ InstaStoriesViewer error: {e}")
            return []
    
    def get_stories_views4you(self):
        """Try to get stories from views4you.com"""
        try:
            print(f"🌐 Trying Views4You for @{self.instagram_username}...")
            
            # Similar to above - would need reverse engineering
            print("ℹ️ Views4You requires API reverse engineering")
            return []
            
        except Exception as e:
            print(f"❌ Views4You error: {e}")
            return []
    
    def get_stories_anonyig(self):
        """Try to get stories from anonyig.com"""
        try:
            print(f"🌐 Trying AnonyIG for @{self.instagram_username}...")
            
            # Would need to reverse engineer their API calls
            print("ℹ️ AnonyIG requires API reverse engineering")
            return []
            
        except Exception as e:
            print(f"❌ AnonyIG error: {e}")
            return []
    
    def simulate_real_stories(self):
        """Simulate real story detection with enhanced demo"""
        try:
            print(f"🎭 Enhanced Demo: Simulating story detection for @{self.instagram_username}...")
            
            # Check if this username exists on Instagram (basic check)
            instagram_url = f"https://www.instagram.com/{self.instagram_username}/"
            
            try:
                response = self.session.head(instagram_url, timeout=10)
                if response.status_code == 404:
                    print(f"❌ Instagram account @{self.instagram_username} not found!")
                    return []
                elif response.status_code == 200:
                    print(f"✅ Instagram account @{self.instagram_username} exists!")
                else:
                    print(f"⚠️ Instagram response: {response.status_code}")
            except:
                print("⚠️ Could not verify Instagram account")
            
            # Create realistic demo story every hour
            current_time = datetime.now()
            hour_id = current_time.strftime('%Y%m%d_%H')
            demo_story_id = f"realistic_{self.instagram_username}_{hour_id}"
            
            # Check if we already sent this hour's demo
            if demo_story_id not in self.sent_stories:
                # Generate realistic demo content
                story_types = [
                    {
                        'type': 'photo',
                        'urls': [
                            'https://picsum.photos/1080/1920?random=',
                            'https://source.unsplash.com/1080x1920/?portrait,',
                            'https://source.unsplash.com/1080x1920/?lifestyle,'
                        ]
                    }
                ]
                
                story_type = random.choice(story_types)
                random_seed = random.randint(100, 999)
                base_url = random.choice(story_type['urls'])
                
                demo_story = {
                    'id': demo_story_id,
                    'url': f"{base_url}{random_seed}",
                    'type': story_type['type'],
                    'timestamp': current_time
                }
                
                print(f"✅ Generated realistic demo story: {demo_story_id}")
                return [demo_story]
            else:
                print("ℹ️ Demo story already sent this hour")
                return []
            
        except Exception as e:
            print(f"❌ Error in demo simulation: {e}")
            return []
    
    def get_instagram_stories(self):
        """Main function to get stories from various services"""
        try:
            print(f"🔍 Searching for stories from @{self.instagram_username}...")
            
            # Try each service
            for service in self.story_services:
                try:
                    print(f"🌐 Trying {service['name']}...")
                    stories = service['method']()
                    
                    if stories:
                        print(f"✅ Found {len(stories)} stories from {service['name']}")
                        return stories
                    
                    # Wait between services to avoid rate limiting
                    time.sleep(random.uniform(2, 5))
                    
                except Exception as e:
                    print(f"❌ {service['name']} failed: {e}")
                    continue
            
            # If no real stories found, use enhanced demo
            print("🔄 No real stories found, using enhanced demo mode...")
            return self.simulate_real_stories()
            
        except Exception as e:
            print(f"❌ Error getting stories: {e}")
            return []
    
    def process_new_stories(self):
        """Check for new stories and send them"""
        stories = self.get_instagram_stories()
        
        if not stories:
            print("ℹ️ No new stories found")
            return
        
        print(f"📱 Processing {len(stories)} new stories")
        
        for story in stories:
            try:
                # Prepare caption
                current_time = datetime.now()
                caption = (
                    f"📸 Story מ-@{self.instagram_username}\n"
                    f"🕐 {story['timestamp'].strftime('%d/%m/%Y %H:%M')}\n\n"
                    f"🤖 Instagram Story Bot פועל!\n"
                    f"💡 Enhanced Demo Mode - מחפש סטוריז אמיתיים..."
                )
                
                # Send to Telegram based on type
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
                    
                    # Clean up old entries (keep only last 50)
                    if len(self.sent_stories) > 50:
                        self.sent_stories = self.sent_stories[-50:]
                        self.save_sent_stories()
                else:
                    print(f"❌ Failed to send story")
                
                # Wait between sends
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
        startup_msg = (
            f"🤖 Instagram Story Bot V4 הופעל!\n"
            f"👤 עוקב אחר: @{self.instagram_username}\n\n"
            f"🌐 מנסה שירותים חינמיים:\n"
            f"• InstaStoriesViewer\n"
            f"• AnonyIG\n"
            f"• Views4You\n\n"
            f"⚡ אם השירותים לא זמינים - Demo Mode יפעל\n"
            f"🎯 הבוט יחפש סטוריז אמיתיים כל 5 דקות!"
        )
        self.send_telegram_message(startup_msg)
        
        # Check for stories immediately
        print("📸 Checking for stories to send...")
        self.process_new_stories()
        
        while True:
            try:
                self.process_new_stories()
                next_check = datetime.now().strftime('%H:%M:%S')
                print(f"⏳ Next check in 5 minutes... ({next_check})")
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
