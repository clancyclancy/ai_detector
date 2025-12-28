import os
from collections import namedtuple
from src.config import TEST_TWEET_ID, USE_REAL_REPLY_IN_TEST
from src.bot.twitter_client import TwitterClient

# fake tweet data
MockUser     = namedtuple('MockUser', ['id', 'username'])
MockMedia    = namedtuple('MockMedia', ['media_key', 'type', 'url', 'variants'])
MockTweet    = namedtuple('MockTweet', ['id', 'author_id', 'text', 'attachments'])
MockResponse = namedtuple('MockResponse', ['data', 'includes'])

class MockTwitterClient:
    # can only poll twitter api every 15 minutes, limnited to 300 requested per month
    # need a testing environment that can simulate tweets without hitting api limits  
    # the every 15 minutes is hilariously brutal for testing 

    def __init__(self):
        print("Mock: Initializing MockTwitterClient..")

        self.my_id = "mock_bot_id"
        
        self.real_client = None
        if USE_REAL_REPLY_IN_TEST:
            print("Mock: WARNING: Real Reply Mode Enabled in Test Environment!")
            confirm = input("Mock: WARNING: Press 'y' to confirm you want to post to twitter: ").strip().lower() # wish i added this before i posted the same reply 50 times... oops
            if confirm != 'y':
                raise ValueError("canceled real reply initialization.")
                
            try:
                self.real_client = TwitterClient()
            except Exception as e:
                print(f"Failed to initialize TwitterClient: {e}")

    def get_me(self):
        return type('obj', (object,), {'data': MockUser(id=self.my_id, username="MockBot")})

    def get_mentions(self, since_id=None, max_retries=None, base_sleep=None):
        
        print("Mock: Fetching mentions...")
        
        # Create mock tweet
        tweet_id = TEST_TWEET_ID if TEST_TWEET_ID else "mock_tweet_123"
        media_key = "mock_media_456"
           
        tweet = MockTweet(
            id          = tweet_id,
            author_id   = "mock_user_789",          
            text        = "@MockBot is this AI?",
            attachments = {'media_keys': [media_key]}       
        )   
        
        test_image_path = os.path.abspath("C:\\Users\\clanc\\VSCode\\ai_detector\\data\\single_imgs\\ai_05.jpg") # relative path was causing issues. TODO: fix
        
        media = MockMedia(
            media_key   = media_key,
            type        = 'photo',
            url         = f"file://{test_image_path}",
            variants    = []
        )
        
        return MockResponse(
            data     = [tweet],
            includes = {'media': [media]}
        )
          
    def reply_to_tweet(self, tweet_id, text, media_ids=None):  
        # need a secondary confirmation.. ask me how i know
        # the first confirmation is for initializing the real client
        # without this second check, can send same messages infinite times. until elon muskrat bans me 
        if self.real_client and tweet_id != "mock_tweet_123":   
            confirm = input("Mock: WARNING: Press 'y' to confirm you want to send the tweet: ").strip().lower() # wish i added this before i posted the same reply 50 times... oops
            if confirm != 'y':
                raise ValueError("canceled sending real reply tweet.")              
            
            print(f"Mock: Sending REAL reply to {tweet_id}...")
            self.real_client.reply_to_tweet(tweet_id, text, media_ids)

        else:
            print(f"Mock: pretending to reply to tweet {tweet_id}")
            print(f"Mock: Text: {text}")

            if media_ids: 
                print(f"Mock: Media IDs attached: {media_ids}")  
     
    def upload_media(self, filename):
        if self.real_client:   
            print(f"Mock: Uploading REAL media  {filename}...")
            return self.real_client.upload_media(filename)          
        
        else:
            print(f"Mock: pretending to upload media {filename}")       
            return "mock_media_id_uploaded"

   # have a fake download as well
   # TODO: idk if this is necessary
   # also handle videos and gifs in mock mode?  
    def download_media(self, media_obj, destination_folder):   
        print(f"Mock: Downloading media {media_obj.media_key}")
        
        # Handle files in mock mode, MM, mmmock mode           
        if media_obj.url.startswith("file://"):   
            src_path = media_obj.url.replace("file://", "") 
            if not os.path.exists(src_path):
                print(f"Mock: Test file not found at {src_path}")
                return None
                
            import shutil    
  
            filename = f"{media_obj.media_key}.jpg"      
            dst_path = os.path.join(destination_folder, filename)

            # cpoy file so bot treats as downloaded img  
            shutil.copy2(src_path, dst_path)  
            return dst_path
            
        return None  
