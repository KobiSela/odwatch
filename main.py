import requests
import time
import json
import os
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, BadPassword
import random

class InstagramStoryBot:
    def __init__(self, bot_token, chat_id, instagram_username, ig_sessionid=None, ig_username=None, ig_password=None):
        """
        Initialize the Instagram Story Bot with sessionid or credentials
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.instagram_username = instagram_username.replace('@', '')
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # Instagram credentials and session
        self.ig_sessionid = ig_sessionid
        self.ig_username = ig_username
        self.ig_password = ig_password
        
        # File to track sent stories
        self.sent_stories_file = "sent_stories.json"
        self.sent_stories = self.load_sent_stories()
        
        # Instagram client
        self.instagram_client = None
        self.session_file = "ig_session.json"
        
        # Initialize Instagram client
        self.init_instagram_client()
        
    def init_instagram_client(self):
        """Initialize Instagram client with sessionid or authentication"""
        try:
            print("🔧 Initializing Instagram client...")
            self.instagram_client = Client()
            
            # Method 1: Use sessionid if available
            if self.ig_sessionid:
                try:
                    print("🔑 Using sessionid for login...")
                    self.instagram_client.set_settings({
                        "sessionid": self.ig_sessionid
                    })
                    
                    # Test the session by getting user info
                    user_info = self.instagram_client.account_info()
                    print(f"✅ Session login successful! Logged in as: {user_info.username}")
                    return True
                    
                except Exception as e:
                    print(f"❌ Sessionid login failed: {e}")
                    # Fall through to username/password method
            
            # Method 2: Try to load existing session file
            if os.path.exists(self.session_file):
                try:
                    print("📂 Loading existing Instagram session...")
                    self.instagram_client.load_settings(self.session_file)
                    self.instagram_client.login(self.ig_username, self.ig_password)
                    print("✅ Instagram session loaded successfully!")
                    return True
                except Exception as e:
                    print(f"⚠️ Failed to load session: {e}")
                    os.remove(self.session_file)
            
            # Method 3: Login with credentials if available
            if self.ig_username and self.ig_password:
                try:
                    print("🔐 Logging into Instagram with username/password...")
                    self.instagram_client.login(self.ig_username, self.ig_password)
                    
                    # Save session for future use
                    self.instagram_client.dump_settings(self.session_file)
                    print("✅ Instagram login successful and session saved!")
                    return True
                    
                except BadPassword:
                    print("❌ Instagram: Invalid username or password")
                    return False
                except ChallengeRequired:
                    print("❌ Instagram: Challenge required (2FA or verification)")
                    return False
                except Exception as e:
                    print(f"❌ Instagram login error: {e}")
                    return False
            else:
                print("⚠️ No Instagram credentials or sessionid provided - using demo mode")
                return False
                
        except Exception as e:
            print(f"❌ Failed to initialize Instagram client: {e}")
            return False
    
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
            response = requests.post(url, data=payload, timeout=30)
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
            'caption': caption[:1024],
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, data=payload, timeout=60)
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
            'caption': caption[:1024],
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, data=payload, timeout=60)
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Telegram video error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending video: {e}")
            return False
    
    def get_user_stories(self):
        """Get real Instagram stories using instagrapi"""
        try:
            if not self.instagram_client:
                print("❌ Instagram client not initialized")
                return []
                
            print(f"📱 Getting stories for @{self.instagram_username}...")
            
            # Get user info
            try:
                user_info = self.instagram_client.user_info_by_username(self.instagram_username)
                user_id = user_info.pk
                print(f"✅ Found user: {user_info.full_name} (@{user_info.username})")
            except Exception as e:
                print(f"❌ User not found: {e}")
                return []
            
            # Get user stories
            try:
                user_stories = self.instagram_client.user_stories(user_id)
                
                if not user_stories:
                    print(f"ℹ️ No active stories found for @{self.instagram_username}")
                    return []
                
                stories = []
                print(f"📸 Found {len(user_stories)} stories")
                
                for story in user_stories:
                    story_id = f"real_{story.pk}"
                    
                    # Skip if already sent
                    if story_id in self.sent_stories:
                        continue
                    
                    # Get media URL
                    if story.video_url:
                        media_url = story.video_url
                        media_type = 'video'
                    elif story.thumbnail_url:
                        media_url = story.thumbnail_url
                        media_type = 'photo'
                    else:
                        continue
                    
                    story_data = {
                        'id': story_id,
                        'url': media_url,
                        'type': media_type,
                        'timestamp': story.taken_at,
                        'story_pk': story.pk
                    }
                    
                    stories.append(story_data)
                    print(f"✅ Processed story: {story.pk} ({media_type})")
                
                return stories
                
            except Exception as e:
                print(f"❌ Error getting stories: {e}")
                return []
                
        except Exception as e:
            print(f"❌ Error in get_user_stories: {e}")
            return []
    
    def get_demo_stories(self):
        """Fallback demo stories if Instagram API fails"""
        try:
            print(f"🎭 Demo Mode: Creating demo story for @{self.instagram_username}...")
            
            current_time = datetime.now()
            hour_id = current_time.strftime('%Y%m%d_%H')
            demo_story_id = f"demo_{self.instagram_username}_{hour_id}"
            
            if demo_story_id not in self.sent_stories:
                random_seed = random.randint(100, 999)
                demo_story = {
                    'id': demo_story_id,
                    'url': f'https://picsum.photos/1080/1920?random={random_seed}',
                    'type': 'photo',
                    'timestamp': current_time
                }
                
                print(f"✅ Generated demo story: {demo_story_id}")
                return [demo_story]
            else:
                print("ℹ️ Demo story already sent this hour")
                return []
                
        except Exception as e:
            print(f"❌ Error in demo mode: {e}")
            return []
    
    def process_new_stories(self):
        """Check for new stories and send them"""
        
        # Try to get real stories first
        stories = self.get_user_stories()
        
        # If no real stories, try demo mode
        if not stories:
            stories = self.get_demo_stories()
        
        if not stories:
            print("ℹ️ No new stories found")
            return
        
        print(f"📱 Processing {len(stories)} new stories")
        
        for story in stories:
            try:
                # Prepare caption
                if 'real_' in story['id']:
                    caption = (
                        f"📸 🎯 REAL Story מ-@{self.instagram_username}\n"
                        f"🕐 {story['timestamp'].strftime('%d/%m/%Y %H:%M')}\n\n"
                        f"✅ הבוט עובד עם Instagram Private API!\n"
                        f"🔥 זהו סטורי אמיתי מהאינסטגרם!"
                    )
                else:
                    caption = (
                        f"📸 Demo Story מ-@{self.instagram_username}\n"
                        f"🕐 {story['timestamp'].strftime('%d/%m/%Y %H:%M')}\n\n"
                        f"🤖 Demo Mode - Instagram API לא זמין כרגע\n"
                        f"💡 יש צורך ב-sessionid או credentials נכונים"
                    )
                
                # Send to Telegram based on type
                success = False
                if story['type'] == 'video':
                    success = self.send_telegram_video(story['url'], caption)
                elif story['type'] == 'photo':
                    success = self.send_telegram_photo(story['url'], caption)
                
                if success:
                    print(f"✅ Sent story: {story['id']}")
                    
                    # Mark as sent
                    self.sent_stories.append(story['id'])
                    self.save_sent_stories()
                    
                    # Clean up old entries
                    if len(self.sent_stories) > 100:
                        self.sent_stories = self.sent_stories[-100:]
                        self.save_sent_stories()
                else:
                    print(f"❌ Failed to send story: {story['id']}")
                
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
        
        # Send startup message based on authentication method
        if self.instagram_client:
            if self.ig_sessionid:
                startup_msg = (
                    f"🤖 Instagram Story Bot V6 הופעל!\n"
                    f"👤 עוקב אחר: @{self.instagram_username}\n\n"
                    f"🔑 מחובר עם Session ID!\n"
                    f"✅ Instagram API פעיל\n"
                    f"📱 יקבל סטוריז אמיתיים כל 5 דקות!"
                )
            elif self.ig_username:
                startup_msg = (
                    f"🤖 Instagram Story Bot V6 הופעל!\n"
                    f"👤 עוקב אחר: @{self.instagram_username}\n\n"
                    f"🔥 מחובר לInstagram Private API!\n"
                    f"✅ חשבון Instagram: @{self.ig_username}\n"
                    f"📱 יקבל סטוריז אמיתיים כל 5 דקות!"
                )
            else:
                startup_msg = (
                    f"🤖 Instagram Story Bot V6 הופעל!\n"
                    f"👤 עוקב אחר: @{self.instagram_username}\n\n"
                    f"⚠️ Instagram API לא זמין\n"
                    f"🎭 Demo Mode פעיל\n"
                    f"💡 הוסף IG_SESSIONID או IG_USERNAME/IG_PASSWORD"
                )
        else:
            startup_msg = (
                f"🤖 Instagram Story Bot V6 הופעל!\n"
                f"👤 עוקב אחר: @{self.instagram_username}\n\n"
                f"⚠️ Instagram API לא זמין\n"
                f"🎭 Demo Mode פעיל\n"
                f"💡 הוסף IG_SESSIONID או IG_USERNAME/IG_PASSWORD"
            )
        
        self.send_telegram_message(startup_msg)
        
        # Check for stories immediately
        print("📸 Checking for stories...")
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
                print("⏳ Retrying in 2 minutes...")
                time.sleep(120)

def main():
    # Configuration - Environment Variables
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    CHAT_ID = os.getenv('CHAT_ID') 
    INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
    IG_SESSIONID = os.getenv('IG_SESSIONID')        # New: sessionid method
    IG_USERNAME = os.getenv('IG_USERNAME')          # Optional: username method
    IG_PASSWORD = os.getenv('IG_PASSWORD')          # Optional: password method
    
    # Validate required configuration
    if not BOT_TOKEN or not CHAT_ID or not INSTAGRAM_USERNAME:
        print("❌ Missing required environment variables!")
        print("Required: BOT_TOKEN, CHAT_ID, INSTAGRAM_USERNAME")
        print("Authentication options:")
        print("  1. IG_SESSIONID (recommended)")
        print("  2. IG_USERNAME + IG_PASSWORD")
        return
    
    print(f"🚀 Starting bot...")
    print(f"👤 Target: @{INSTAGRAM_USERNAME}")
    
    if IG_SESSIONID:
        print(f"🔑 Using Session ID authentication")
    elif IG_USERNAME:
        print(f"🔐 Instagram Account: @{IG_USERNAME}")
    else:
        print("⚠️ No Instagram credentials - Demo Mode only")
    
    # Create and start the bot
    bot = InstagramStoryBot(
        BOT_TOKEN, 
        CHAT_ID, 
        INSTAGRAM_USERNAME,
        IG_SESSIONID,
        IG_USERNAME,
        IG_PASSWORD
    )
    bot.start_monitoring()

if __name__ == "__main__":
    main()
