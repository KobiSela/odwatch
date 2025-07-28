import requests
import time
import json
import os
from datetime import datetime
import pytz
from instagrapi import Client
import random
import urllib.parse

# Israel timezone
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

class InstagramStoryBot:
    def __init__(self, bot_token, chat_id, instagram_username, ig_sessionid=None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.instagram_username = instagram_username.replace('@', '')
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.ig_sessionid = ig_sessionid
        
        # Track sent stories
        self.sent_stories = []
        
        # Track followers changes
        self.followers_file = "followers_data.json"
        self.following_file = "following_data.json"
        self.last_followers = self.load_followers_data()
        self.last_following = self.load_following_data()
        
        # Initialize Instagram client
        self.instagram_client = None
        self.is_working = False
        self.init_instagram_client()
    
    def get_next_check_interval(self):
        """Calculate next check interval based on current time"""
        current_time = datetime.now(ISRAEL_TZ)
        current_hour = current_time.hour
        
        # Night hours (3 AM - 9 AM): Check every hour
        if 3 <= current_hour < 9:
            random_minutes = random.randint(0, 59)
            minutes_to_next_hour = 60 - current_time.minute
            total_minutes = minutes_to_next_hour + random_minutes
            
            print(f"🌙 Night mode: Next check in {total_minutes} minutes")
            return total_minutes * 60
        
        # Regular hours: Random interval between 30-45 minutes
        else:
            random_minutes = random.randint(30, 45)
            print(f"☀️ Day mode: Next check in {random_minutes} minutes")
            return random_minutes * 60
    
    def is_night_hours(self):
        """Check if current time is in night hours (3-9 AM)"""
        current_hour = datetime.now(ISRAEL_TZ).hour
        return 3 <= current_hour < 9
        
    def init_instagram_client(self):
        """Initialize Instagram client"""
        try:
            print("🔧 Initializing Instagram client...")
            self.instagram_client = Client()
            
            if self.ig_sessionid:
                try:
                    print("🔑 Using sessionid for login...")
                    decoded_sessionid = urllib.parse.unquote(self.ig_sessionid)
                    self.instagram_client.login_by_sessionid(decoded_sessionid)
                    
                    user_info = self.instagram_client.account_info()
                    print(f"✅ Session login successful! Logged in as: {user_info.username}")
                    self.is_working = True
                    return True
                    
                except Exception as e:
                    print(f"❌ Sessionid login failed: {e}")
                    self.is_working = False
                    return False
            else:
                print("❌ No sessionid provided")
                self.is_working = False
                return False
                
        except Exception as e:
            print(f"❌ Failed to initialize Instagram client: {e}")
            self.is_working = False
            return False
    
    def load_followers_data(self):
        """Load previous followers data"""
        try:
            if os.path.exists(self.followers_file):
                with open(self.followers_file, 'r') as f:
                    return json.load(f)
            return {"count": None, "ids": [], "initialized": False}
        except:
            return {"count": None, "ids": [], "initialized": False}
    
    def save_followers_data(self, followers_data):
        """Save current followers data"""
        try:
            with open(self.followers_file, 'w') as f:
                json.dump(followers_data, f)
        except Exception as e:
            print(f"❌ Error saving followers data: {e}")
    
    def load_following_data(self):
        """Load previous following data"""
        try:
            if os.path.exists(self.following_file):
                with open(self.following_file, 'r') as f:
                    return json.load(f)
            return {"count": None, "ids": [], "initialized": False}
        except:
            return {"count": None, "ids": [], "initialized": False}
    
    def save_following_data(self, following_data):
        """Save current following data"""
        try:
            with open(self.following_file, 'w') as f:
                json.dump(following_data, f)
        except Exception as e:
            print(f"❌ Error saving following data: {e}")
    
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
            return response.status_code == 200
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
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error sending video: {e}")
            return False
    
    def get_user_stories(self):
        """Get Instagram stories"""
        if not self.instagram_client or not self.is_working:
            print("❌ Instagram client not working")
            return []
        
        try:
            print(f"📱 Getting stories for @{self.instagram_username}...")
            
            # Get user info
            user_info = self.instagram_client.user_info_by_username(self.instagram_username)
            user_id = user_info.pk
            print(f"✅ Found user: {user_info.full_name} (@{user_info.username})")
            
            time.sleep(2)
            
            try:
                user_stories = self.instagram_client.user_stories(user_id)
                
                if not user_stories:
                    print(f"ℹ️ No active stories found for @{self.instagram_username}")
                    return []
                
                stories = []
                print(f"📸 Found {len(user_stories)} stories")
                
                for i, story in enumerate(user_stories):
                    try:
                        story_id = f"story_{story.pk}"
                        
                        # Skip if already sent
                        if story_id in self.sent_stories:
                            print(f"⏭️ Story {story.pk} already sent, skipping")
                            continue
                        
                        print(f"🔍 Processing story {i+1}/{len(user_stories)}: {story.pk}")
                        
                        # Get media URL
                        media_url = None
                        media_type = 'photo'
                        
                        try:
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
                                print(f"✅ Found image URL for story {story.pk}")
                        except Exception as url_error:
                            print(f"⚠️ Could not get direct URL for story {story.pk}: {url_error}")
                        
                        # Try alternative method
                        if not media_url:
                            try:
                                story_info = self.instagram_client.story_info(story.pk)
                                if story_info and hasattr(story_info, 'video_url') and getattr(story_info, 'video_url', None):
                                    media_url = getattr(story_info, 'video_url')
                                    media_type = 'video'
                                    print(f"✅ Found video URL via story_info for {story.pk}")
                                elif story_info and hasattr(story_info, 'thumbnail_url') and getattr(story_info, 'thumbnail_url', None):
                                    media_url = getattr(story_info, 'thumbnail_url')
                                    media_type = 'photo'
                                    print(f"✅ Found thumbnail URL via story_info for {story.pk}")
                            except Exception as info_error:
                                print(f"⚠️ Could not get story_info for {story.pk}: {info_error}")
                        
                        if media_url:
                            story_data = {
                                'id': story_id,
                                'url': media_url,
                                'type': media_type,
                                'timestamp': getattr(story, 'taken_at', datetime.now(ISRAEL_TZ)),
                                'story_pk': story.pk
                            }
                            
                            stories.append(story_data)
                            print(f"✅ Added story {story.pk} to queue")
                        else:
                            print(f"❌ Could not get URL for story {story.pk}")
                            
                    except Exception as story_error:
                        print(f"❌ Error processing story {story.pk}: {story_error}")
                        continue
                
                print(f"📦 Returning {len(stories)} stories")
                return stories
                
            except Exception as stories_error:
                print(f"❌ Error getting stories: {stories_error}")
                return []
                
        except Exception as e:
            print(f"❌ Error in get_user_stories: {e}")
            return []
    
    def process_stories(self):
        """Process and send stories"""
        if not self.is_working:
            print("⚠️ Instagram client not working, skipping stories")
            return
        
        stories = self.get_user_stories()
        
        if not stories:
            print("ℹ️ No new stories to process")
            return
        
        print(f"📱 Processing {len(stories)} stories")
        
        for story in stories:
            try:
                # Convert timestamp to Israel time
                if story['timestamp'].tzinfo is None:
                    story_time = pytz.UTC.localize(story['timestamp']).astimezone(ISRAEL_TZ)
                else:
                    story_time = story['timestamp'].astimezone(ISRAEL_TZ)
                
                # Clean caption - just username and time
                caption = f"@{self.instagram_username} • {story_time.strftime('%d/%m %H:%M')}"
                
                success = False
                if story['type'] == 'video':
                    success = self.send_telegram_video(story['url'], caption)
                else:
                    success = self.send_telegram_photo(story['url'], caption)
                
                if success:
                    print(f"✅ Sent story: {story['id']} ({story['type']})")
                    self.sent_stories.append(story['id'])
                    
                    # Keep only last 50 sent stories
                    if len(self.sent_stories) > 50:
                        self.sent_stories = self.sent_stories[-50:]
                else:
                    print(f"❌ Failed to send story: {story['id']}")
                
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Error processing story: {e}")
    
    def check_followers_changes(self):
        """Check for followers changes"""
        if not self.instagram_client or not self.is_working:
            print("⚠️ Instagram client not working, skipping followers check")
            return
        
        try:
            print(f"👥 Checking followers changes for @{self.instagram_username}...")
            
            # Get user info
            user_info = self.instagram_client.user_info_by_username(self.instagram_username)
            user_id = user_info.pk
            
            current_followers_count = user_info.follower_count
            current_following_count = user_info.following_count
            
            # Check if this is first time running
            is_first_run = not self.last_followers.get('initialized', False) or not self.last_following.get('initialized', False)
            
            if is_first_run:
                print("🆕 First run - initializing followers data")
                
                self.last_followers = {
                    'count': current_followers_count,
                    'ids': [],
                    'initialized': True,
                    'last_updated': datetime.now(ISRAEL_TZ).isoformat()
                }
                self.last_following = {
                    'count': current_following_count,
                    'ids': [],
                    'initialized': True,
                    'last_updated': datetime.now(ISRAEL_TZ).isoformat()
                }
                
                self.save_followers_data(self.last_followers)
                self.save_following_data(self.last_following)
                
                print(f"✅ Initialized: {current_followers_count} followers, {current_following_count} following")
                return
            
            # Get previous counts
            last_followers_count = self.last_followers.get('count', 0)
            last_following_count = self.last_following.get('count', 0)
            
            print(f"📊 Followers: {last_followers_count} -> {current_followers_count}")
            print(f"📊 Following: {last_following_count} -> {current_following_count}")
            
            # Check for changes
            followers_changed = current_followers_count != last_followers_count
            following_changed = current_following_count != last_following_count
            
            if not followers_changed and not following_changed:
                print(f"ℹ️ No changes detected")
                return
            
            messages = []
            
            if followers_changed:
                print(f"📈 Followers count changed: {last_followers_count} -> {current_followers_count}")
                
                if current_followers_count > last_followers_count:
                    new_count = current_followers_count - last_followers_count
                    messages.append(f"➕ {new_count} new followers")
                else:
                    lost_count = last_followers_count - current_followers_count
                    messages.append(f"➖ {lost_count} unfollowed")
                
                self.last_followers['count'] = current_followers_count
                self.save_followers_data(self.last_followers)
            
            if following_changed:
                print(f"📈 Following count changed: {last_following_count} -> {current_following_count}")
                
                if current_following_count > last_following_count:
                    new_count = current_following_count - last_following_count
                    messages.append(f"👤 Following {new_count} new accounts")
                else:
                    unfollowed_count = last_following_count - current_following_count
                    messages.append(f"➖ Unfollowed {unfollowed_count} accounts")
                
                self.last_following['count'] = current_following_count
                self.save_following_data(self.last_following)
            
            # Send clean message
            if messages:
                summary_time = datetime.now(ISRAEL_TZ).strftime('%d/%m %H:%M')
                summary_msg = f"@{self.instagram_username} • {summary_time}\n" + "\n".join(messages)
                self.send_telegram_message(summary_msg)
                print(f"📱 Sent followers update: {len(messages)} changes")
            
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Error checking followers changes: {e}")
    
    def start_monitoring(self):
        """Start monitoring"""
        print(f"🚀 Starting Instagram Story Monitor...")
        print(f"👤 Monitoring: @{self.instagram_username}")
        print(f"📱 Sending to Telegram chat: {self.chat_id}")
        print(f"⏱️ Smart timing: 30-45min (day) | 60min (3-9 AM)")
        
        if self.is_working:
            startup_msg = f"Instagram Bot • @{self.instagram_username}"
        else:
            startup_msg = f"Instagram Bot • Not connected"
        
        self.send_telegram_message(startup_msg)
        
        # Check immediately
        if self.is_working:
            print("📸 Checking for stories...")
            self.process_stories()
            
            print("👥 Checking for followers changes...")
            self.check_followers_changes()
        
        # Main loop
        while True:
            try:
                if not self.is_working:
                    print("🛑 Instagram client not working, stopping...")
                    break
                
                next_interval = self.get_next_check_interval()
                
                current_time = datetime.now(ISRAEL_TZ)
                next_check_time = datetime.fromtimestamp(
                    current_time.timestamp() + next_interval, 
                    tz=ISRAEL_TZ
                )
                
                print(f"⏳ Waiting until {next_check_time.strftime('%H:%M:%S')}...")
                time.sleep(next_interval)
                
                print(f"🔄 Running checks at {datetime.now(ISRAEL_TZ).strftime('%H:%M:%S')}")
                self.process_stories()
                self.check_followers_changes()
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("⏳ Error occurred, retrying in 5 minutes...")
                time.sleep(300)

def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    CHAT_ID = os.getenv('CHAT_ID') 
    INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
    IG_SESSIONID = os.getenv('IG_SESSIONID')
    
    if not BOT_TOKEN or not CHAT_ID or not INSTAGRAM_USERNAME:
        print("❌ Missing required environment variables!")
        return
    
    print(f"🚀 Starting bot...")
    print(f"👤 Target: @{INSTAGRAM_USERNAME}")
    
    if IG_SESSIONID:
        print(f"🔑 Using Session ID authentication")
    else:
        print("❌ No Session ID provided")
        return
    
    bot = InstagramStoryBot(BOT_TOKEN, CHAT_ID, INSTAGRAM_USERNAME, IG_SESSIONID)
    bot.start_monitoring()

if __name__ == "__main__":
    main()
