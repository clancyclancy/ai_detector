import time
import os
import cv2
from src.bot.twitter_client        import TwitterClient
from src.bot.mock_twitter_client   import MockTwitterClient
from src.inference.detector        import AIDetector
from src.inference.video_processor import VideoProcessor
from src.inference.explainability  import GradCAMExplainer
from src.config                    import CHECK_INTERVAL, CONFIDENCE_THRESHOLD, TEST_MODE, MAX_TWEETS_PER_RUN


class BotHandler:

    #handle 
    # polling mentions
    # downloading media 
    # running model
    # gen gradcam
    # reply

    def __init__(self):
        if TEST_MODE:
            print("IN TESTING CONFIG")
            self.twitter = MockTwitterClient()
        else:
            self.twitter = TwitterClient()
            
        # core comps
        self.detector        = AIDetector()
        self.video_processor = VideoProcessor(self.detector)
        self.explainer       = GradCAMExplainer(model_instance=self.detector.model)
        
        # specifically track last processed tweet
        self.last_seen_id    = self.load_last_seen_id()
        
        # Temp folder for downloads
        self.temp_dir = "temp_downloads"
        os.makedirs(self.temp_dir, exist_ok=True)

    def load_last_seen_id(self):

        if os.path.exists("last_seen_id.txt"):

            with open("last_seen_id.txt", "r") as f:

                last_id = f.read().strip()
                # If not in test mode, ensure ID is numeric
                if not TEST_MODE and not last_id.isdigit():

                    print(f"Invalid last_seen_id for production: {last_id}. Ignoring.")
                    return None
                
                return last_id
            
        return None
  
    
    def save_last_seen_id(self, tweet_id):   

        with open("last_seen_id.txt", "w") as f:  
   
            f.write(str(tweet_id))  
  
        self.last_seen_id = tweet_id    

  
    def process_mentions(self):         
        print("Checking for mentions...")
        response = self.twitter.get_mentions(since_id=self.last_seen_id)
        
        if not response.data: # type: ignore
            print("No new mentions ")   
            return
  
        # create a quick lookup table for media objects
        media_lookup = (
            {m.media_key: m for m in response.includes['media']}   
                if 'media' in response.includes   
                else {}  
        )
        

        # Process oldest to newest, but limit to at most 5 new tweets per run. not trying to get banned
        # TODO: implement a nice queue system later if any living soul besides me uses this

        processed_count = 0

        for tweet in reversed(response.data):

            if processed_count >= MAX_TWEETS_PER_RUN:
                print(f"Reached processing limit of {MAX_TWEETS_PER_RUN} tweets this run.")
                break

            print(f"Processing tweet {tweet.id} from {tweet.author_id}")
            
            
            if not tweet.attachments or 'media_keys' not in tweet.attachments:
                self.twitter.reply_to_tweet(tweet.id, "Homie tag me in a tweet with an image or video. 6 7")
                self.save_last_seen_id(tweet.id)
                continue

            media_keys = tweet.attachments['media_keys']
            results = []
            reply_media_ids = []

            for key in media_keys:
                media = media_lookup.get(key)
                if not media:
                    continue

                filepath = self.twitter.download_media(media, self.temp_dir)
                if not filepath:
                    continue

                try:
                    if media.type == 'photo':
                        label, conf = self.detector.predict_image(filepath)
                        
                        # if ai generate the grad cam overlay
                        if label == 'ai':
                            print(f"Generating Grad-CAM for {filepath}...")
                            cam_img = self.explainer.cam_heatmap(filepath)
                            cam_filename = f"gradcam_{os.path.basename(filepath)}"
                            cam_path = os.path.join(self.temp_dir, cam_filename)

                            # save heatmap (BGR!!) not rgb. i will never understand bgr formatting, like just switch to rgb. please
                            cv2.imwrite(cam_path, 
                                        cv2.cvtColor(cam_img, cv2.COLOR_RGB2BGR)
                                        )
                            
                            media_id = self.twitter.upload_media(cam_path)
                            if media_id:
                                reply_media_ids.append(media_id)
                            
                            # cleanup temp 
                            if os.path.exists(cam_path):
                                os.remove(cam_path)

                    elif media.type == 'video':
                        label, conf = self.video_processor.process_video(filepath)
                    else:
                        continue
                    
                    results.append((media.type, label, conf))

                except Exception as e:
                    print(f"Error processing media: {e}")

                finally:
                    # Cleanup
                    if os.path.exists(filepath):
                        os.remove(filepath)

            if results:
                # Construct reply
                reply_text = "Analysis Results:\n"   
                for m_type, label, conf in results:            
                         
                    # slapping a robot emoji under a politicans tweet would go so hard
                    bot_emoji = "🤖" if label == 'ai' else ""

                    reply_text += f"{bot_emoji} {m_type.capitalize()}: {label.upper()} ({conf:.1%})\n"  

                self.twitter.reply_to_tweet(tweet.id, reply_text, media_ids=reply_media_ids)
            else:
                self.twitter.reply_to_tweet(tweet.id, "Could not process media, current accepted file formats are .jpg, .jpeg, .png")

            self.save_last_seen_id(tweet.id)
            processed_count += 1


    def run(self):

        print("Starting bot...")
        print(f"Monitoring mentions every {CHECK_INTERVAL} seconds.")
           
        while True:
            try:
                self.process_mentions()
            except Exception as e:
                print(f"Error in main loop: {e}")
            
            time.sleep(CHECK_INTERVAL)
