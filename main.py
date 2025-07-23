import requests
import time
import json
import os
from datetime import datetime
from instagrapi import Client
import random
import urllib.parse

class InstagramStoryBot:
    def __init__(self, bot_token, chat_id, instagram_username, ig_sessionid=None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.instagram_username = instagram_username.replace('@', '')
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.ig_sessionid = ig_sessionid
        
        # Track sent stories
        self.sent_stories = []
        
        # Initialize Instagram client
        self.instagram_client = None
        self.is_working = False
        self.init_instagram_client()
        
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
                                'timestamp': getattr(story, 'taken_at', datetime.now()),
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
                if story['type'] == 'placeholder':
                    caption = (
                        f"📸 🎯 Story מ-@{self.instagram_username}\n"
                        f"🕐 {story['timestamp'].strftime('%d/%m/%Y %H:%M')}\n\n"
                        f"⚠️ לא הצלחתי לקבל תמונה אמיתית\n"
                        f"✅ אבל זיהיתי שיש סטורי חדש!"
                    )
                else:
                    caption = (
                        f"📸 🎯 REAL Story מ-@{self.instagram_username}\n"
                        f"🕐 {story['timestamp'].strftime('%d/%m/%Y %H:%M')}\n\n"
                        f"✅ Instagram Story Bot פועל!\n"
                        f"🔥 סטורי אמיתי מ-Instagram!"
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
        print(f"⏱️ Checking every 30 minutes...")
        
        if self.is_working:
            startup_msg = (
                f"🤖 Instagram Story Bot V7 (Simple) הופעל!\n"
                f"👤 עוקב אחר: @{self.instagram_username}\n\n"
                f"✅ מחובר לInstagram!\n"
                f"📱 יקבל סטוריז כל 30 דקות!"
            )
        else:
            startup_msg = (
                f"🤖 Instagram Story Bot V7 (Simple) הופעל!\n"
                f"👤 עוקב אחר: @{self.instagram_username}\n\n"
                f"❌ לא מחובר לInstagram\n"
                f"💡 בדוק את IG_SESSIONID"
            )
        
        self.send_telegram_message(startup_msg)
        
        # Check immediately
        if self.is_working:
            print("📸 Checking for stories...")
            self.process_stories()
        
        # Main loop
        while True:
            try:
                if not self.is_working:
                    print("🛑 Instagram client not working, stopping...")
                    break
                
                self.process_stories()
                next_check = datetime.now().strftime('%H:%M:%S')
                print(f"⏳ Next check in 30 minutes... ({next_check})")
                time.sleep(1800)  # 30 minutes
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                time.sleep(300)  # 5 minutes on error

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
