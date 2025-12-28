import os
from dotenv import load_dotenv

load_dotenv()

# Twitter Credentials saved in .env file, dont commit .env but can now commit config.py
TWITTER_API_KEY             = os.getenv("TWITTER_API_KEY") 
TWITTER_API_SECRET          = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN        = os.getenv("TWITTER_ACCESS_TOKEN") 
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN        = os.getenv("TWITTER_BEARER_TOKEN")   

MODEL_PATH           = "models/ai_detector_run/weights/best.pt"    
CONFIDENCE_THRESHOLD = 0.25    
 
CHECK_INTERVAL = 600 # in seconds (increased to avoid rate limits)


# If TEST_MODE is True, you can specify a real Tweet ID to reply to, 
# and enable real replies to test the posting functionality without hitting mention limits.
TEST_MODE              = True
USE_REAL_REPLY_IN_TEST = True

TEST_TWEET_ID = 2005055484123136399 # None


BASE_DIR           = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR           = os.path.join(BASE_DIR, "data")   
RAW_DATA_DIR       = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

MAX_TWEETS_PER_RUN = 5

MODEL_TRAIN_IMAGE_SIZE = 320
