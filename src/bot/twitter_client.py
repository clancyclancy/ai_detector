import tweepy
import requests
import os


from src.config import (
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_BEARER_TOKEN
)

# twitter randomly times out and sends 500 errors so nothing here should cause a crash
# handle exceptions ~gracefully~

class TwitterClient:


    def __init__(self):
        # this should cause a crash
        if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_BEARER_TOKEN]):
            raise ValueError("Missing Twitter API credentials. Please check the .env file. .env file not in github repository")


        # for read access 
        self.client = tweepy.Client(
            bearer_token        = TWITTER_BEARER_TOKEN,
            consumer_key        = TWITTER_API_KEY,
            consumer_secret     = TWITTER_API_SECRET,
            access_token        = TWITTER_ACCESS_TOKEN,
            access_token_secret = TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit  = True
        )

        # need 4 write access
        self.auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY, TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
        )


        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)

        # actually i think i can avoid this but w/e
        self.my_id = self.get_me().data.id 


    def get_me(self):
        return self.client.get_me()


    def get_mentions(self, since_id=None):  
        return self.client.get_users_mentions(
            id           = self.my_id,      
            since_id     = since_id, 
            expansions   = ['attachments.media_keys', 'author_id'],
            media_fields = ['url', 'variants', 'type'],            
            user_fields  = ['username']   
        )  

    # handle exceptions and continue
    def reply_to_tweet(self, tweet_id, text, media_ids=None):
        try:
            self.client.create_tweet(text=text, in_reply_to_tweet_id=tweet_id, media_ids=media_ids)
            print(f"Replied to {tweet_id}: {text}")
        except Exception as e:
            print(f"Error replying to tweet {tweet_id}: {e}")


    # handle exceptions and continuie     
    def upload_media(self, filename):
        #TODO: handle video uploads? idk maybe only upload the frame of the video that has the highest confidence ai detection
        # or maybe lowest confidence?
        try:
            media = self.api.media_upload(filename)
            print(f"Uploaded media {filename}, media_id: {media.media_id}")    
            return media.media_id
        except Exception as e: 
            print(f"Error in upload {filename}: {e}") 
            return None  


    def download_media(self, media_obj, destination_folder):   
        if media_obj.type == 'photo':
            url = media_obj.url
            ext = '.jpg'

        elif media_obj.type == 'video' or media_obj.type == 'animated_gif':
            print("Unable to process videos and gifs")
            #TODO: handle video processing, frame extraction      
            return None
        
        else:
            return None

        filename = f"{media_obj.media_key}{ext}"   
        filepath = os.path.join(destination_folder, filename)

        response = requests.get(url, stream=True)           
        if response.status_code == 200: # TODO: might have to expand to other 2xx codes 
            with open(filepath, 'wb') as f:

                # allegedly saving the file in chunks will avoid memory spikes
                for chunk in response.iter_content(1024):
                    f.write(chunk)  
            return filepath  
        return None  
