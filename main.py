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
    
    def get_instagram_stories_web(self):
        """Get stories using web scraping approach"""
        try:
            print(f"🔍 Checking stories for @{self.instagram_username} using web method...")
            
            # Try multiple Instagram story viewing services
            services = [
                f"https://storiesig.net/{self.instagram_username}",
                f"https://www.instastories.watch/{self.instagram_username}",
                f"https://instasaved.net/stories/{self.instagram_username}"
            ]
            
            for service_url in services:
                try:
                    print(f"🌐 Trying service: {service_url}")
                    
                    # Add random delay to avoid rate limiting
                    time.sleep(random.uniform(1, 3))
                    
                    response = self.session.get(service_url, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for story media URLs
                        stories = []
                        
                        # Find images
                        img_tags = soup.find_all('img', src=True)
                        for img in img_tags:
                            src = img['src']
                            if 'instagram' in src or 'story' in src.lower():
                                story_id = f"{self.instagram_username}_{hash(src)}"
                                if story_id not in self.sent_stories:
                                    stories.append({
                                        'id': story_id,
                                        'url': src,
                                        'type': 'photo',
                                        'timestamp': datetime.now()
                                    })
                        
                        # Find videos
                        video_tags = soup.find_all('video')
                        for video in video_tags:
                            if video.get('src'):
                                src = video['src']
                                story_id = f"{self.instagram_username}_{hash(src)}"
                                if story_id not in self.sent_stories:
                                    stories.append({
                                        'id': story_id,
                                        'url': src,
                                        'type': 'video',
                                        'timestamp': datetime.now()
                                    })
                        
                        if stories:
                            print(f"✅ Found {len(stories)} stories using web method")
                            return stories
                
                except Exception as e:
                    print(f"❌ Service {service_url} failed: {e}")
                    continue
            
            # If web scraping fails, try alternative API approach
            return self.get_stories_api_alternative()
            
        except Exception as e:
            print(f"❌ Error in web scraping: {e}")
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
        self.send_telegram_message(f"🤖 Instagram Story Bot V2 הופעל!\n👤 עוקב אחר: @{self.instagram_username}\n🔧 משתמש בשיטת Web Scraping")
        
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
