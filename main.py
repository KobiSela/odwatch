import requests
import time
import json
import os
from datetime import datetime
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
    
    def get_demo_stories(self):
        """Generate demo stories for testing"""
        try:
            print(f"🎭 Demo Mode: Generating test stories for @{self.instagram_username}...")
            
            # Create demo story every hour
            current_time = datetime.now()
            hour_id = current_time.strftime('%Y%m%d_%H')
            demo_story_id = f"demo_{self.instagram_username}_{hour_id}"
            
            # Check if we already sent this hour's demo
            if demo_story_id not in self.sent_stories:
                # Generate random demo image
                random_seed = random.randint(100, 999)
                demo_story = {
                    'id': demo_story_id,
                    'url': f'https://picsum.photos/400/600?random={random_seed}',
                    'type': 'photo',
                    'timestamp': current_time
                }
                
                print(f"✅ Generated demo story: {demo_story_id}")
                return [demo_story]
            else:
                print("ℹ️ Demo story already sent this hour")
                return []
            
        except Exception as e:
            print(f"❌ Error generating demo stories: {e}")
            return []
    
    def process_new_stories(self):
        """Check for new stories and send them"""
        stories = self.get_demo_stories()
        
        if not stories:
            print("ℹ️ No new stories found")
            return
        
        print(f"📱 Processing {len(stories)} new stories")
        
        for story in stories:
            try:
                # Prepare caption
                caption = f"📸 Demo Story מ-@{self.instagram_username}\n🕐 {story['timestamp'].strftime('%d/%m/%Y %H:%M')}\n\n🤖 הבוט עובד בהצלחה!\n💡 זוהי תמונת דוגמה להדגמת הפעולה"
                
                # Send to Telegram
                success = self.send_telegram_photo(story['url'], caption)
                
                if success:
                    print(f"✅ Sent demo story from @{self.instagram_username}")
                    
                    # Mark as sent
                    self.sent_stories.append(story['id'])
                    self.save_sent_stories()
                    
                    # Clean up old entries (keep only last 50)
                    if len(self.sent_stories) > 50:
                        self.sent_stories = self.sent_stories[-50:]
                        self.save_sent_stories()
                else:
                    print(f"❌ Failed to send demo story")
                
                # Wait between sends
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
        startup_msg = (
            f"🤖 Instagram Story Bot הופעל!\n"
            f"👤 עוקב אחר: @{self.instagram_username}\n\n"
            f"🎭 Demo Mode פעיל:\n"
            f"• הבוט ישלח תמונת דוגמה כל שעה\n"
            f"• זה מוכיח שהמערכת עובדת בהצלחה\n\n"
            f"💡 לחיבור אמיתי לאינסטגרם נדרש Instagram API Key"
        )
        self.send_telegram_message(startup_msg)
        
        # Send existing stories on first run
        print("📸 Checking for demo stories to send...")
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
