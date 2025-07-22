import requests
import time
import json
import os
from datetime import datetime
import instaloader
from pathlib import Path

class InstagramStoryBot:
    def __init__(self, bot_token, chat_id, instagram_username):
        """
        Initialize the Instagram Story Bot
        
        Args:
            bot_token (str): Telegram bot token
            chat_id (str): Telegram chat ID
            instagram_username (str): Instagram username to monitor
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.instagram_username = instagram_username
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # Initialize Instaloader
        self.loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        
        # File to track sent stories
        self.sent_stories_file = "sent_stories.json"
        self.sent_stories = self.load_sent_stories()
        
        # Directory for downloaded files
        self.download_dir = "downloads"
        os.makedirs(self.download_dir, exist_ok=True)
    
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
    
    def send_telegram_photo(self, photo_path, caption=""):
        """Send photo to Telegram"""
        url = f"{self.base_url}/sendPhoto"
        
        try:
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }
                response = requests.post(url, files=files, data=data)
                return response.status_code == 200
        except Exception as e:
            print(f"❌ Error sending photo: {e}")
            return False
    
    def send_telegram_video(self, video_path, caption=""):
        """Send video to Telegram"""
        url = f"{self.base_url}/sendVideo"
        
        try:
            with open(video_path, 'rb') as video:
                files = {'video': video}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }
                response = requests.post(url, files=files, data=data)
                return response.status_code == 200
        except Exception as e:
            print(f"❌ Error sending video: {e}")
            return False
    
    def get_instagram_stories(self):
        """Get stories from Instagram profile"""
        try:
            print(f"🔍 Checking stories for @{self.instagram_username}...")
            
            # Get profile
            profile = instaloader.Profile.from_username(self.loader.context, self.instagram_username)
            
            # Check if profile has stories
            if not profile.has_viewable_story:
                print(f"ℹ️ No viewable stories for @{self.instagram_username}")
                return []
            
            stories = []
            story_items = self.loader.get_stories(userids=[profile.userid])
            
            for story in story_items:
                for item in story.get_items():
                    story_id = f"{item.owner_username}_{item.mediaid}"
                    
                    # Skip if already sent
                    if story_id in self.sent_stories:
                        continue
                    
                    stories.append({
                        'id': story_id,
                        'item': item,
                        'username': item.owner_username,
                        'timestamp': item.date_utc
                    })
            
            return stories
            
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"❌ Profile @{self.instagram_username} does not exist")
            return []
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            print(f"❌ Profile @{self.instagram_username} is private")
            return []
        except Exception as e:
            print(f"❌ Error getting stories: {e}")
            return []
    
    def download_story_item(self, story_item):
        """Download a single story item"""
        try:
            # Create filename
            timestamp = story_item['timestamp'].strftime("%Y%m%d_%H%M%S")
            
            if story_item['item'].is_video:
                filename = f"{story_item['username']}_{timestamp}_story.mp4"
                filepath = os.path.join(self.download_dir, filename)
                
                # Download video
                video_url = story_item['item'].video_url
                response = requests.get(video_url)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return filepath, 'video'
            else:
                filename = f"{story_item['username']}_{timestamp}_story.jpg"
                filepath = os.path.join(self.download_dir, filename)
                
                # Download image
                image_url = story_item['item'].url
                response = requests.get(image_url)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return filepath, 'photo'
                
        except Exception as e:
            print(f"❌ Error downloading story: {e}")
            return None, None
    
    def process_new_stories(self):
        """Check for new stories and send them"""
        stories = self.get_instagram_stories()
        
        if not stories:
            print("ℹ️ No new stories found")
            return
        
        print(f"📱 Found {len(stories)} new stories")
        
        for story in stories:
            try:
                # Download the story
                filepath, media_type = self.download_story_item(story)
                
                if not filepath:
                    continue
                
                # Prepare caption
                caption = f"📸 Story מ-@{story['username']}\n🕐 {story['timestamp'].strftime('%d/%m/%Y %H:%M')}"
                
                # Send to Telegram
                success = False
                if media_type == 'video':
                    success = self.send_telegram_video(filepath, caption)
                elif media_type == 'photo':
                    success = self.send_telegram_photo(filepath, caption)
                
                if success:
                    print(f"✅ Sent story from @{story['username']}")
                    
                    # Mark as sent
                    self.sent_stories.append(story['id'])
                    self.save_sent_stories()
                    
                    # Clean up old entries (keep only last 100)
                    if len(self.sent_stories) > 100:
                        self.sent_stories = self.sent_stories[-100:]
                        self.save_sent_stories()
                else:
                    print(f"❌ Failed to send story from @{story['username']}")
                
                # Clean up downloaded file
                try:
                    os.remove(filepath)
                except:
                    pass
                
                # Wait between sends to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error processing story: {e}")
    
    def start_monitoring(self):
        """Start monitoring Instagram stories"""
        print(f"🚀 Starting Instagram Story Monitor...")
        print(f"👤 Monitoring: @{self.instagram_username}")
        print(f"📱 Sending to Telegram chat: {self.chat_id}")
        print(f"⏱️ Checking every 5 minutes...")
        
        # Send startup message
        self.send_telegram_message(f"🤖 Instagram Story Bot הופעל!\n👤 עוקב אחר: @{self.instagram_username}")
        
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
