import requests
import time
import json
import os
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, BadPassword
import random

class InstagramStoryBot:
    def __init__(self, bot_token, chat_id, instagram_username, ig_username=None, ig_password=None):
        """
        Initialize the Instagram Story Bot with real Instagram Private API
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.instagram_username = instagram_username.replace('@', '')
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # Instagram credentials (optional for public accounts)
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
        """Initialize Instagram client with authentication"""
        try:
            prin
