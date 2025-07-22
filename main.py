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
        
        # Rate limiting and error tracking
        self.consecutive_errors = 0
        self.max_errors = 5
        self.last_request_time = 0
        self.min_request_interval = 60  # Minimum 1 minute between requests
        self.is_client_working = True
        
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
                    
                    # Decode the URL-encoded sessionid
                    import urllib.parse
                    decoded_sessionid = urllib.parse.unquote(self.ig_sessionid)
                    print(f"🔓 Decoded sessionid: {decoded_sessionid[:20]}...")
                    
                    # Set the sessionid in the client settings
                    settings = {
                        "sessionid": decoded_sessionid,
                        "mid": "",
                        "ig_u_ds": "",
                        "ig_www_claim": "",
                        "csrftoken": "",
                    }
                    
                    self.instagram_client.set_settings(settings)
                    
                    # Test the session by getting user info
                    try:
                        user_info = self.instagram_client.account_info()
                        print(f"✅ Session login successful! Logged in as: {user_info.username}")
                        return True
                    except Exception as test_error:
                        print(f"🔄 Session test failed, trying login_by_sessionid: {test_error}")
                        
                        # Try alternative method
                        self.instagram_client = Client()
                        self.instagram_client.login_by_sessionid(decoded_sessionid)
                        user_info = self.instagram_client.account_info()
                        print(f"✅ Alternative session login successful! Logged in as: {user_info.username}")
                        return True
                    
                except Exception as e:
                    print(f"❌ Sessionid login failed: {e}")
                    print("🔄 Trying to create new session...")
                    # Fall through to username/password method
            
            # Method 2: Try to load existing session file
            if os.path.exists(self.session_file):
                try:
                    print("📂 Loading existing Instagram session...")
                    self.instagram_client.load_settings(self.session_file)
                    
                    # Try to relogin to refresh session
                    if self.ig_username and self.ig_password:
                        self.instagram_client.login(self.ig_username, self.ig_password)
                        print("✅ Instagram session loaded and refreshed successfully!")
                        return True
                    else:
                        # Try to use existing session without relogin
                        user_info = self.instagram_client.account_info()
                        print("✅ Instagram session loaded successfully!")
                        return True
                        
                except Exception as e:
                    print(f"⚠️ Failed to load session: {e}")
                    try:
                        os.remove(self.session_file)
                    except:
                        pass
            
            # Method 3: Login with credentials if available
            if self.ig_username and self.ig_password:
                try:
                    print("🔐 Logging into Instagram with username/password...")
                    
                    # Create a fresh client
                    self.instagram_client = Client()
                    
                    # Set some device info to look more legitimate
                    self.instagram_client.set_device({
                        "app_version": "269.0.0.18.75",
                        "android_version": 26,
                        "android_release": "8.0.0",
                        "dpi": "480dpi",
                        "resolution": "1080x1920",
                        "manufacturer": "OnePlus",
                        "device": "OnePlus6T",
                        "model": "ONEPLUS A6013",
                        "cpu": "qcom"
                    })
                    
                    self.instagram_client.login(self.ig_username, self.ig_password)
                    
                    # Save session for future use
                    self.instagram_client.dump_settings(self.session_file)
                    print("✅ Instagram login successful and session saved!")
                    return True
                    
                except BadPassword:
                    print("❌ Instagram: Invalid username or password")
                    return False
                except ChallengeRequired as e:
                    print(f"❌ Instagram: Challenge required (2FA or verification): {e}")
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
    
    def wait_for_rate_limit(self):
        """Wait to avoid rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last_request
            print(f"⏳ Rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def handle_instagram_error(self, error):
        """Handle Instagram API errors and decide if should stop"""
        self.consecutive_errors += 1
        print(f"❌ Instagram error ({self.consecutive_errors}/{self.max_errors}): {error}")
        
        # Check for specific error types that mean we should stop
        error_str = str(error).lower()
        
        if any(keyword in error_str for keyword in [
            'challenge', 'login_required', 'checkpoint', 'banned', 'spam', 
            'rate limit', 'too many requests', 'forbidden'
        ]):
            print(f"🚨 Critical error detected: {error}")
            self.is_client_working = False
            self.send_telegram_message(
                f"🚨 Instagram Bot נעצר!\n"
                f"❌ שגיאה קריטית: {error}\n\n"
                f"💡 ייתכן שהחשבון נחסם או צריך verification.\n"
                f"בדוק את החשבון Instagram ועדכן sessionid חדש."
            )
            return False
        
        # If too many consecutive errors, stop the client
        if self.consecutive_errors >= self.max_errors:
            print(f"🛑 Too many consecutive errors ({self.max_errors}), stopping Instagram client")
            self.is_client_working = False
            self.send_telegram_message(
                f"🚨 Instagram Bot נעצר!\n"
                f"❌ יותר מדי שגיאות רצופות: {self.max_errors}\n\n"
                f"💡 ייתכן שיש בעיה עם החיבור או שהחשבון נחסם.\n"
                f"בדוק את החשבון ונסה להפעיל מחדש."
            )
            return False
        
        return True
    
    def reset_error_counter(self):
        """Reset error counter after successful operation"""
        if self.consecutive_errors > 0:
            print(f"✅ Instagram working again, reset error counter")
            self.consecutive_errors = 0
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
        """Get real Instagram stories using instagrapi with rate limiting"""
        try:
            if not self.instagram_client or not self.is_client_working:
                print("❌ Instagram client not available or disabled")
                return []
            
            # Rate limiting
            self.wait_for_rate_limit()
                
            print(f"📱 Getting stories for @{self.instagram_username}...")
            
            # Get user info
            try:
                user_info = self.instagram_client.user_info_by_username(self.instagram_username)
                user_id = user_info.pk
                print(f"✅ Found user: {user_info.full_name} (@{user_info.username})")
                
                # Reset error counter on success
                self.reset_error_counter()
                
            except Exception as e:
                print(f"❌ User not found: {e}")
                if not self.handle_instagram_error(e):
                    return []
                return []
            
            # Small delay before next request
            time.sleep(2)
            
            # Get user stories
            try:
                user_stories = self.instagram_client.user_stories(user_id)
                
                # Reset error counter on success
                self.reset_error_counter()
                
                if not user_stories:
                    print(f"ℹ️ No active stories found for @{self.instagram_username}")
                    return []
                
                stories = []
                print(f"📸 Found {len(user_stories)} stories")
                
                for story in user_stories:
                    try:
                        story_id = f"real_{story.pk}"
                        
                        # Skip if already sent
                        if story_id in self.sent_stories:
                            continue
                        
                        # Debug: Print story attributes
                        print(f"🔍 Processing story {story.pk}, attributes: {dir(story)}")
                        
                        # Get media URL - Safe approach
                        media_url = None
                        media_type = None
                        
                        # Try different ways to get the media URL
                        if hasattr(story, 'video_url') and getattr(story, 'video_url', None):
                            media_url = getattr(story, 'video_url')
                            media_type = 'video'
                            print(f"✅ Found video URL for story {story.pk}")
                        elif hasattr(story, 'thumbnail_url') and getattr(story, 'thumbnail_url', None):
                            media_url = getattr(story, 'thumbnail_url')
                            media_type = 'photo'
                            print(f"✅ Found thumbnail URL for story {story.pk}")
                        elif hasattr(story, 'url') and getattr(story, 'url', None):
                            media_url = getattr(story, 'url')
                            media_type = 'photo'
                            print(f"✅ Found regular URL for story {story.pk}")
                        
                        if not media_url:
                            print(f"⚠️ No media URL found for story {story.pk}, skipping")
                            continue
                        
                        story_data = {
                            'id': story_id,
                            'url': media_url,
                            'type': media_type,
                            'timestamp': getattr(story, 'taken_at', datetime.now()),
                            'story_pk': story.pk
                        }
                        
                        stories.append(story_data)
                        print(f"✅ Successfully processed story: {story.pk} ({media_type})")
                        
                    except Exception as story_error:
                        print(f"❌ Error processing individual story {story.pk}: {story_error}")
                        continue
                
                return stories
                
            except Exception as e:
                print(f"❌ Error getting stories: {e}")
                if not self.handle_instagram_error(e):
                    return []
                return []
                
        except Exception as e:
            print(f"❌ Error in get_user_stories: {e}")
            self.handle_instagram_error(e)
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
        """Check for new stories and send them - ONLY REAL STORIES"""
        
        # Check if Instagram client is working
        if not self.instagram_client:
            print("⚠️ Instagram client not initialized - stopping")
            self.is_client_working = False
            return
        
        if not self.is_client_working:
            print("⚠️ Instagram client disabled due to previous errors - stopping")
            return
        
        # Try to get real stories
        stories = self.get_user_stories()
        
        if stories:
            print(f"📱 Processing {len(stories)} new REAL stories")
            
            for story in stories:
                try:
                    # Prepare caption for real stories
                    caption = (
                        f"📸 🎯 REAL Story מ-@{self.instagram_username}\n"
                        f"🕐 {story['timestamp'].strftime('%d/%m/%Y %H:%M')}\n\n"
                        f"✅ הבוט עובד עם Instagram Private API!\n"
                        f"🔥 זהו סטורי אמיתי מהאינסטגרם!"
                    )
                    
                    # Send to Telegram based on type
                    success = False
                    if story['type'] == 'video':
                        success = self.send_telegram_video(story['url'], caption)
                    elif story['type'] == 'photo':
                        success = self.send_telegram_photo(story['url'], caption)
                    
                    if success:
                        print(f"✅ Sent REAL story: {story['id']}")
                        
                        # Mark as sent
                        self.sent_stories.append(story['id'])
                        self.save_sent_stories()
                        
                        # Clean up old entries
                        if len(self.sent_stories) > 100:
                            self.sent_stories = self.sent_stories[-100:]
                            self.save_sent_stories()
                    else:
                        print(f"❌ Failed to send story: {story['id']}")
                    
                    # Wait between sends to avoid spam
                    time.sleep(5)
                    
                except Exception as e:
                    print(f"❌ Error processing story: {e}")
        else:
            print("ℹ️ No new REAL stories found - continuing to monitor")
        
        # NEVER go to demo mode - only real stories or nothing
    
    def start_monitoring(self):
        """Start monitoring Instagram stories"""
        print(f"🚀 Starting Instagram Story Monitor...")
        print(f"👤 Monitoring: @{self.instagram_username}")
        print(f"📱 Sending to Telegram chat: {self.chat_id}")
        print(f"⏱️ Checking every 30 minutes...")
        
        # Send startup message based on authentication method
        if self.instagram_client:
            if self.ig_sessionid:
                startup_msg = (
                    f"🤖 Instagram Story Bot V6 הופעל!\n"
                    f"👤 עוקב אחר: @{self.instagram_username}\n\n"
                    f"🔑 מחובר עם Session ID!\n"
                    f"✅ Instagram API פעיל\n"
                    f"📱 יקבל סטוריז אמיתיים כל 30 דקות!"
                )
            elif self.ig_username:
                startup_msg = (
                    f"🤖 Instagram Story Bot V6 הופעל!\n"
                    f"👤 עוקב אחר: @{self.instagram_username}\n\n"
                    f"🔥 מחובר לInstagram Private API!\n"
                    f"✅ חשבון Instagram: @{self.ig_username}\n"
                    f"📱 יקבל סטוריז אמיתיים כל 30 דקות!"
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
                f"🛑 Bot will stop - לא ישלח Demo Stories\n"
                f"💡 הוסף IG_SESSIONID או IG_USERNAME/IG_PASSWORD"
            )
        
        self.send_telegram_message(startup_msg)
        
        # Check for stories immediately
        print("📸 Checking for stories...")
        self.process_new_stories()
        
        while True:
            try:
                # Check if Instagram client is still working
                if not self.is_client_working:
                    print("🛑 Instagram client disabled due to errors. Bot stopped.")
                    self.send_telegram_message(
                        f"🛑 Instagram Bot נעצר סופית!\n"
                        f"❌ יותר מדי שגיאות או בעיות אבטחה.\n\n"
                        f"💡 לאחר שתתקן את הבעיה, הפעל מחדש את הבוט."
                    )
                    break
                
                self.process_new_stories()
                next_check = datetime.now().strftime('%H:%M:%S')
                print(f"⏳ Next check in 30 minutes... ({next_check})")
                time.sleep(1800)  # 30 minutes
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                # Check if Instagram is still working before retrying
                if not self.is_client_working:
                    print("🛑 Instagram client disabled, stopping retries")
                    break
                print("⏳ Retrying in 5 minutes...")
                time.sleep(300)  # Shorter retry interval

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
