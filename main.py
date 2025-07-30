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

class StealthInstagramBot:
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
        
        # Initialize Instagram client with stealth settings
        self.instagram_client = None
        self.is_working = False
        self.last_instagram_action = 0  # Track last Instagram action
        self.init_instagram_client()
    
    def get_stealth_delay(self):
        """Get random delay to appear more human"""
        # Random delay between 5-15 seconds for Instagram actions
        return random.uniform(5, 15)
    
    def get_next_check_interval(self):
        """Calculate next check interval - EXTRA LONG intervals"""
        current_time = datetime.now(ISRAEL_TZ)
        current_hour = current_time.hour
        
        # Night hours (11 PM - 8 AM): Check every 4-8 hours
        if current_hour >= 23 or current_hour < 8:
            random_hours = random.uniform(4, 8)  # 4-8 hours
            minutes = int(random_hours * 60)
            print(f"🌙 Night mode: Next check in {random_hours:.1f} hours")
            return minutes * 60
        
        # Day hours: Check every 2-4 hours (much longer than before)
        else:
            random_hours = random.uniform(2, 4)  # 2-4 hours
            minutes = int(random_hours * 60)
            print(f"☀️ Day mode: Next check in {random_hours:.1f} hours")
            return minutes * 60
    
    def should_skip_this_check(self):
        """Randomly skip some checks to be less predictable"""
        # 40% chance to skip a check (increased from 20%)
        if random.random() < 0.4:
            print("🎲 Randomly skipping this check to avoid detection")
            return True
        return False
        
    def init_instagram_client(self):
        """Initialize Instagram client with stealth settings"""
        try:
            print("🔧 Initializing stealth Instagram client...")
            self.instagram_client = Client()
            
            # Stealth settings
            self.instagram_client.delay_range = [3, 7]  # Longer delays between requests
            
            if self.ig_sessionid:
                try:
                    print("🔑 Using sessionid for login...")
                    decoded_sessionid = urllib.parse.unquote(self.ig_sessionid)
                    self.instagram_client.login_by_sessionid(decoded_sessionid)
                    
                    # Add delay after login
                    time.sleep(self.get_stealth_delay())
                    
                    user_info = self.instagram_client.account_info()
                    print(f"✅ Stealth login successful! Logged in as: {user_info.username}")
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
    
    def instagram_action_delay(self):
        """Ensure minimum delay between Instagram actions"""
        current_time = time.time()
        time_since_last = current_time - self.last_instagram_action
        min_delay = 30  # Minimum 30 seconds between Instagram actions (increased from 15)
        
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last + random.uniform(0, 15)  # Added more random delay
            print(f"⏳ Waiting {sleep_time:.1f}s between Instagram actions...")
            time.sleep(sleep_time)
        
        self.last_instagram_action = time.time()
    
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
    
    def get_user_stories_stealth(self):
        """Get Instagram stories with stealth approach"""
        if not self.instagram_client or not self.is_working:
            print("❌ Instagram client not working")
            return []
        
        try:
            # Add delay before Instagram action
            self.instagram_action_delay()
            
            print(f"📱 Getting stories for @{self.instagram_username}...")
            
            # Get user info with delay
            user_info = self.instagram_client.user_info_by_username(self.instagram_username)
            user_id = user_info.pk
            print(f"✅ Found user: {user_info.full_name}")
            
            # Random delay between actions
            time.sleep(self.get_stealth_delay())
            
            try:
                user_stories = self.instagram_client.user_stories(user_id)
                
                if not user_stories:
                    print(f"ℹ️ No active stories found")
                    return []
                
                stories = []
                print(f"📸 Found {len(user_stories)} stories")
                
                for i, story in enumerate(user_stories):
                    try:
                        story_id = f"story_{story.pk}"
                        
                        # Skip if already sent
                        if story_id in self.sent_stories:
                            print(f"⏭️ Story already sent, skipping")
                            continue
                        
                        print(f"🔍 Processing story {i+1}/{len(user_stories)}")
                        
                        # Get media URL with stealth delays
                        media_url = None
                        media_type = 'photo'
                        
                        try:
                            if hasattr(story, 'video_url') and getattr(story, 'video_url', None):
                                media_url = getattr(story, 'video_url')
                                media_type = 'video'
                            elif hasattr(story, 'thumbnail_url') and getattr(story, 'thumbnail_url', None):
                                media_url = getattr(story, 'thumbnail_url')
                                media_type = 'photo'
                            elif hasattr(story, 'url') and getattr(story, 'url', None):
                                media_url = getattr(story, 'url')
                                media_type = 'photo'
                        except Exception as url_error:
                            print(f"⚠️ Could not get direct URL: {url_error}")
                        
                        # Random delay between story processing
                        time.sleep(random.uniform(5, 12))  # Increased from 2-5
                        
                        if media_url:
                            story_data = {
                                'id': story_id,
                                'url': media_url,
                                'type': media_type,
                                'timestamp': getattr(story, 'taken_at', datetime.now(ISRAEL_TZ)),
                                'story_pk': story.pk
                            }
                            
                            stories.append(story_data)
                            print(f"✅ Added story to queue")
                        
                    except Exception as story_error:
                        print(f"❌ Error processing story: {story_error}")
                        continue
                
                print(f"📦 Returning {len(stories)} stories")
                return stories
                
            except Exception as stories_error:
                print(f"❌ Error getting stories: {stories_error}")
                return []
                
        except Exception as e:
            print(f"❌ Error in get_user_stories_stealth: {e}")
            return []
    
    def process_stories(self):
        """Process and send stories with stealth delays"""
        if not self.is_working:
            print("⚠️ Instagram client not working, skipping stories")
            return
        
        # Random chance to skip
        if self.should_skip_this_check():
            return
        
        stories = self.get_user_stories_stealth()
        
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
                
                # Clean caption
                caption = f"@{self.instagram_username} • {story_time.strftime('%d/%m %H:%M')}"
                
                success = False
                if story['type'] == 'video':
                    success = self.send_telegram_video(story['url'], caption)
                else:
                    success = self.send_telegram_photo(story['url'], caption)
                
                if success:
                    print(f"✅ Sent story: {story['type']}")
                    self.sent_stories.append(story['id'])
                    
                    # Keep only last 50 sent stories
                    if len(self.sent_stories) > 50:
                        self.sent_stories = self.sent_stories[-50:]
                else:
                    print(f"❌ Failed to send story")
                
                # Random delay between sends
                time.sleep(random.uniform(15, 30))  # Increased from 8-15
                
            except Exception as e:
                print(f"❌ Error processing story: {e}")
    
    def check_followers_changes_stealth(self):
        """Check for followers changes with stealth approach - LESS FREQUENT"""
        if not self.instagram_client or not self.is_working:
            print("⚠️ Instagram client not working, skipping followers check")
            return
        
        # Only check followers every 4th time (reduce API calls even more)
        if random.random() < 0.75:  # 75% chance to skip followers check (increased from 66%)
            print("🎲 Skipping followers check this time")
            return
        
        try:
            # Add delay before Instagram action
            self.instagram_action_delay()
            
            print(f"👥 Checking followers changes...")
            
            # Get user info
            user_info = self.instagram_client.user_info_by_username(self.instagram_username)
            current_followers_count = user_info.follower_count
            current_following_count = user_info.following_count
            
            # Check if this is first time running
            is_first_run = not self.last_followers.get('initialized', False)
            
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
                return
            
            # Get previous counts
            last_followers_count = self.last_followers.get('count', 0)
            last_following_count = self.last_following.get('count', 0)
            
            # Check for changes
            followers_changed = current_followers_count != last_followers_count
            following_changed = current_following_count != last_following_count
            
            if not followers_changed and not following_changed:
                return
            
            messages = []
            
            if followers_changed:
                if current_followers_count > last_followers_count:
                    new_count = current_followers_count - last_followers_count
                    messages.append(f"➕ {new_count} new followers")
                else:
                    lost_count = last_followers_count - current_followers_count
                    messages.append(f"➖ {lost_count} unfollowed")
                
                self.last_followers['count'] = current_followers_count
                self.save_followers_data(self.last_followers)
            
            if following_changed:
                if current_following_count > last_following_count:
                    new_count = current_following_count - last_following_count
                    messages.append(f"👤 Following {new_count} new accounts")
                else:
                    unfollowed_count = last_following_count - current_following_count
                    messages.append(f"➖ Unfollowed {unfollowed_count} accounts")
                
                self.last_following['count'] = current_following_count
                self.save_following_data(self.last_following)
            
            # Send message
            if messages:
                summary_time = datetime.now(ISRAEL_TZ).strftime('%d/%m %H:%M')
                summary_msg = f"@{self.instagram_username} • {summary_time}\n" + "\n".join(messages)
                self.send_telegram_message(summary_msg)
                print(f"📱 Sent followers update")
            
        except Exception as e:
            print(f"❌ Error checking followers changes: {e}")
    
    def start_monitoring(self):
        """Start stealth monitoring"""
        print(f"🥷 Starting STEALTH Instagram Monitor...")
        print(f"👤 Monitoring: @{self.instagram_username}")
        print(f"📱 Sending to Telegram chat: {self.chat_id}")
        print(f"⏱️ Ultra stealth timing: 2-4h (day) | 4-8h (night)")
        print(f"🎲 40% random skips, 75% follower skips enabled")
        
        if self.is_working:
            startup_msg = f"🥷 Ultra Stealth Bot • @{self.instagram_username}"
        else:
            startup_msg = f"🥷 Ultra Stealth Bot • Not connected"
        
        self.send_telegram_message(startup_msg)
        
        # Don't check immediately - wait for first interval
        print("⏳ Starting with delay to avoid detection...")
        
        # Main loop with stealth timing
        while True:
            try:
                if not self.is_working:
                    print("🛑 Instagram client not working, stopping...")
                    break
                
                # Get next interval (much longer now)
                next_interval = self.get_next_check_interval()
                
                current_time = datetime.now(ISRAEL_TZ)
                next_check_time = datetime.fromtimestamp(
                    current_time.timestamp() + next_interval, 
                    tz=ISRAEL_TZ
                )
                
                print(f"⏳ Next check: {next_check_time.strftime('%d/%m %H:%M')}")
                time.sleep(next_interval)
                
                print(f"🔄 Running stealth checks at {datetime.now(ISRAEL_TZ).strftime('%H:%M:%S')}")
                
                # Process stories (with random skips)
                self.process_stories()
                
                # Random delay between story and follower checks
                time.sleep(random.uniform(60, 180))  # 1-3 minutes (increased from 30-90 seconds)
                
                # Check followers (less frequently)
                self.check_followers_changes_stealth()
                
            except KeyboardInterrupt:
                print("\n🛑 Stealth bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                # Longer retry delay
                print("⏳ Error occurred, retrying in 1 hour...")
                time.sleep(3600)  # 1 hour (increased from 30 minutes)

def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    CHAT_ID = os.getenv('CHAT_ID') 
    INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
    IG_SESSIONID = os.getenv('IG_SESSIONID')
    
    if not BOT_TOKEN or not CHAT_ID or not INSTAGRAM_USERNAME:
        print("❌ Missing required environment variables!")
        return
    
    print(f"🥷 Starting stealth bot...")
    print(f"👤 Target: @{INSTAGRAM_USERNAME}")
    
    if IG_SESSIONID:
        print(f"🔑 Using Session ID authentication")
    else:
        print("❌ No Session ID provided")
        return
    
    bot = StealthInstagramBot(BOT_TOKEN, CHAT_ID, INSTAGRAM_USERNAME, IG_SESSIONID)
    bot.start_monitoring()

if __name__ == "__main__":
    main()
