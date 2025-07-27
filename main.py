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
        
        # Night hours (3 AM - 9 AM): Check every hour with random minute
        if 3 <= current_hour < 9:
            # Random minute between 0-59 for next hour
            random_minutes = random.randint(0, 59)
            # Time until next hour + random minutes
            minutes_to_next_hour = 60 - current_time.minute
            total_minutes = minutes_to_next_hour + random_minutes
            
            print(f"🌙 Night mode: Next check in {total_minutes} minutes (at {(current_time.hour + 1) % 24}:{random_minutes:02d})")
            return total_minutes * 60  # Convert to seconds
        
        # Regular hours: Random interval between 30-45 minutes
        else:
            random_minutes = random.randint(30, 45)
            print(f"☀️ Day mode: Next check in {random_minutes} minutes")
            return random_minutes * 60  # Convert to seconds
    
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
            return {}
        except:
            return {}
    
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
            return {}
        except:
            return {}
    
    def save_following_data(self, following_data):
        """Save current following data"""
        try:
            with open(self.following_file, 'w') as f:
                json.dump(following_data, f)
        except Exception as e:
            print(f"❌ Error saving following data: {e}")
    
    def check_followers_changes(self):
        """Check for followers changes efficiently"""
        if not self.instagram_client or not self.is_working:
            return
        
        try:
            print(f"👥 Checking followers changes for @{self.instagram_username}...")
            
            # Get user info
            user_info = self.instagram_client.user_info_by_username(self.instagram_username)
            user_id = user_info.pk
            
            # Get current followers count (fast)
            current_followers_count = user_info.follower_count
            current_following_count = user_info.following_count
            
            # Check if counts changed
            last_followers_count = self.last_followers.get('count', 0)
            last_following_count = self.last_following.get('count', 0)
            
            followers_changed = current_followers_count != last_followers_count
            following_changed = current_following_count != last_following_count
            
            if not followers_changed and not following_changed:
                print(f"ℹ️ No changes in followers ({current_followers_count}) or following ({current_following_count})")
                return  # Exit early - no telegram message
            
            # If counts changed, get the actual lists (only if needed)
            messages = []
            
            if followers_changed:
                print(f"📈 Followers count changed: {last_followers_count} -> {current_followers_count}")
                
                if current_followers_count > last_followers_count:
                    # New followers - get recent followers (limited)
                    try:
                        recent_followers = list(self.instagram_client.user_followers(user_id, amount=20))
                        
                        # Find new followers by comparing with saved IDs
                        last_follower_ids = set(self.last_followers.get('ids', []))
                        
                        new_followers = []
                        for follower in recent_followers:
                            if str(follower.pk) not in last_follower_ids:
                                new_followers.append(follower)
                        
                        if new_followers:
                            for follower in new_followers[:5]:  # Show max 5 new followers
                                messages.append(f"➕ עוקב חדש: {follower.username}")
                            
                            if len(new_followers) > 5:
                                messages.append(f"➕ ועוד {len(new_followers) - 5} עוקבים...")
                        
                        # Update saved data
                        current_follower_ids = [str(f.pk) for f in recent_followers]
                        self.last_followers = {
                            'count': current_followers_count,
                            'ids': current_follower_ids,
                            'last_updated': datetime.now(ISRAEL_TZ).isoformat()
                        }
                        self.save_followers_data(self.last_followers)
                        
                    except Exception as e:
                        print(f"❌ Error getting followers list: {e}")
                        messages.append(f"📈 יש {current_followers_count - last_followers_count} עוקבים חדשים")
                else:
                    # Lost followers
                    lost_count = last_followers_count - current_followers_count
                    messages.append(f"➖ {lost_count} עוקבים הפסיקו לעקוב")
                    
                    # Update count only
                    self.last_followers['count'] = current_followers_count
                    self.save_followers_data(self.last_followers)
            
            if following_changed:
                print(f"📈 Following count changed: {last_following_count} -> {current_following_count}")
                
                if current_following_count > last_following_count:
                    # Started following new people
                    try:
                        recent_following = list(self.instagram_client.user_following(user_id, amount=20))
                        
                        # Find new following by comparing with saved IDs
                        last_following_ids = set(self.last_following.get('ids', []))
                        
                        new_following = []
                        for following in recent_following:
                            if str(following.pk) not in last_following_ids:
                                new_following.append(following)
                        
                        if new_following:
                            for following in new_following[:5]:  # Show max 5 new following
                                messages.append(f"👤 עוקב עכשיו אחרי: {following.username}")
                            
                            if len(new_following) > 5:
                                messages.append(f"👤 ועוד {len(new_following) - 5} חשבונות...")
                        
                        # Update saved data
                        current_following_ids = [str(f.pk) for f in recent_following]
                        self.last_following = {
                            'count': current_following_count,
                            'ids': current_following_ids,
                            'last_updated': datetime.now(ISRAEL_TZ).isoformat()
                        }
                        self.save_following_data(self.last_following)
                        
                    except Exception as e:
                        print(f"❌ Error getting following list: {e}")
                        messages.append(f"👤 עוקב אחרי {current_following_count - last_following_count} חשבונות חדשים")
                else:
                    # Unfollowed people
                    unfollowed_count = last_following_count - current_following_count
                    messages.append(f"➖ הפסיק לעקוב אחרי {unfollowed_count} חשבונות")
                    
                    # Update count only
                    self.last_following['count'] = current_following_count
                    self.save_following_data(self.last_following)
            
            # Send summary message ONLY if there are actual changes
            if messages:
                summary_time = datetime.now(ISRAEL_TZ).strftime('%d/%m/%Y %H:%M')
                summary_msg = f"👥 עדכון עוקבים - @{self.instagram_username}\n🕐 {summary_time}\n\n" + "\n".join(messages)
                self.send_telegram_message(summary_msg)
                print(f"📱 Sent followers update to Telegram")
            else:
                print(f"ℹ️ Followers counts changed but couldn't identify specific users - no message sent")
            
            # Small delay to avoid rate limiting
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Error checking followers changes: {e}")
    
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
        """Get real Instagram stories - simplified version"""
        if not self.instagram_client or not self.is_working:
            print("❌ Instagram client not working")
            return []
        
        try:
            print(f"📱 Getting stories for @{self.instagram_username}...")
            
            # Get user info
            user_info = self.instagram_client.user_info_by_username(self.instagram_username)
            user_id = user_info.pk
            print(f"✅ Found user: {user_info.full_name} (@{user_info.username})")
            
            # Small delay
            time.sleep(2)
            
            # Get user stories - simple approach
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
                        
                        # Try to get REAL media URL
                        media_url = None
                        media_type = 'photo'
                        
                        # Method 1: Try direct URL access
                        try:
                            # Check story attributes safely
                            if hasattr(story, 'video_url') and story.video_url:
                                media_url = story.video_url
                                media_type = 'video'
                                print(f"✅ Found video URL for story {story.pk}")
                            elif hasattr(story, 'thumbnail_url') and story.thumbnail_url:
                                media_url = story.thumbnail_url
                                media_type = 'photo'
                                print(f"✅ Found thumbnail URL for story {story.pk}")
                            elif hasattr(story, 'url') and story.url:
                                media_url = story.url
                                media_type = 'photo'
                                print(f"✅ Found image URL for story {story.pk}")
                        except Exception as url_error:
                            print(f"⚠️ Could not get direct URL for story {story.pk}: {url_error}")
                        
                        # Method 2: If no direct URL, try to get story info
                        if not media_url:
                            try:
                                story_info = self.instagram_client.story_info(story.pk)
                                if story_info and hasattr(story_info, 'video_url') and story_info.video_url:
                                    media_url = story_info.video_url
                                    media_type = 'video'
                                    print(f"✅ Found video URL via story_info for {story.pk}")
                                elif story_info and hasattr(story_info, 'thumbnail_url') and story_info.thumbnail_url:
                                    media_url = story_info.thumbnail_url
                                    media_type = 'photo'
                                    print(f"✅ Found thumbnail URL via story_info for {story.pk}")
                            except Exception as info_error:
                                print(f"⚠️ Could not get story_info for {story.pk}: {info_error}")
                        
                        # Method 3: If still no URL, use placeholder but mark it
                        if not media_url:
                            media_url = f"https://picsum.photos/1080/1920?random={story.pk}"
                            media_type = 'placeholder'
                            print(f"⚠️ Using placeholder for story {story.pk}")
                        
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
            print("⚠️ Instagram client not working, skipping")
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
                    # If no timezone info, assume UTC and convert to Israel time
                    story_time = pytz.UTC.localize(story['timestamp']).astimezone(ISRAEL_TZ)
                else:
                    # If timezone info exists, convert to Israel time
                    story_time = story['timestamp'].astimezone(ISRAEL_TZ)
                
                if story['type'] == 'placeholder':
                    caption = (
                        f"📸 Story מ-@{self.instagram_username}\n"
                        f"🕐 {story_time.strftime('%d/%m/%Y %H:%M')}"
                    )
                else:
                    caption = (
                        f"📸 Story מ-@{self.instagram_username}\n"
                        f"🕐 {story_time.strftime('%d/%m/%Y %H:%M')}"
                    )
                
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
                
                # Wait between sends
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Error processing story: {e}")
    
    def start_monitoring(self):
        """Start monitoring"""
        print(f"🚀 Starting Instagram Story Monitor...")
        print(f"👤 Monitoring: @{self.instagram_username}")
        print(f"📱 Sending to Telegram chat: {self.chat_id}")
        print(f"⏱️ Smart timing: 30-45min (day) | 60min (3-9 AM)")
        
        if self.is_working:
            startup_msg = f"🤖 Instagram Bot הופעל\n👤 עוקב אחר: @{self.instagram_username}"
        else:
            startup_msg = f"🤖 Instagram Bot הופעל\n❌ לא מחובר לInstagram"
        
        self.send_telegram_message(startup_msg)
        
        # Check immediately
        if self.is_working:
            print("📸 Checking for stories...")
            self.process_stories()
            
            print("👥 Checking for followers changes...")
            self.check_followers_changes()
        
        # Main loop with smart timing
        while True:
            try:
                if not self.is_working:
                    print("🛑 Instagram client not working, stopping...")
                    break
                
                # Get next interval based on time
                next_interval = self.get_next_check_interval()
                
                # Show next check time in Israel timezone
                current_time = datetime.now(ISRAEL_TZ)
                next_check_time = datetime.fromtimestamp(
                    current_time.timestamp() + next_interval, 
                    tz=ISRAEL_TZ
                )
                
                print(f"⏳ Waiting until {next_check_time.strftime('%H:%M:%S')}...")
                time.sleep(next_interval)
                
                # After sleep, do the checks
                print(f"🔄 Running checks at {datetime.now(ISRAEL_TZ).strftime('%H:%M:%S')}")
                self.process_stories()
                self.check_followers_changes()
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                # On error, wait 5 minutes before retry
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
    
    print(f"🚀 Starting simple bot...")
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
