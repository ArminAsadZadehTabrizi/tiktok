"""Twitter Automation Module for Dark Facts TikTok Generator"""
import tweepy
import openai
import json
import time
import config
from pathlib import Path


class TwitterManager:
    """Handles Twitter thread generation and posting using Tweepy v1.1 and v2.0"""
    
    def __init__(self):
        """Initialize Twitter API clients (v1.1 for media, v2.0 for tweets)"""
        print("🐦 Initializing Twitter API connection...")
        
        # Validate credentials
        if not all([
            config.TWITTER_API_KEY,
            config.TWITTER_API_SECRET,
            config.TWITTER_ACCESS_TOKEN,
            config.TWITTER_ACCESS_TOKEN_SECRET,
            config.TWITTER_BEARER_TOKEN
        ]):
            raise ValueError(
                "❌ Missing Twitter API credentials. Please set all required "
                "environment variables in .env file:\n"
                "  - TWITTER_API_KEY\n"
                "  - TWITTER_API_SECRET\n"
                "  - TWITTER_ACCESS_TOKEN\n"
                "  - TWITTER_ACCESS_TOKEN_SECRET\n"
                "  - TWITTER_BEARER_TOKEN"
            )
        
        # API v2.0 Client (for posting tweets)
        self.client = tweepy.Client(
            bearer_token=config.TWITTER_BEARER_TOKEN,
            consumer_key=config.TWITTER_API_KEY,
            consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        
        # API v1.1 (for media upload)
        auth = tweepy.OAuth1UserHandler(
            config.TWITTER_API_KEY,
            config.TWITTER_API_SECRET,
            config.TWITTER_ACCESS_TOKEN,
            config.TWITTER_ACCESS_TOKEN_SECRET
        )
        self.api = tweepy.API(auth)
        
        print("  ✓ Twitter API initialized successfully")
    
    def generate_thread_from_script(self, script_data):
        """
        Transform video script into a viral Twitter thread using OpenAI.
        
        Args:
            script_data (dict): Script data with 'hook' and 'body' keys
            
        Returns:
            list: List of tweet strings (max 280 chars each)
        """
        print("\n📝 Generating Twitter thread from script...")
        
        hook = script_data.get('hook', '')
        body = script_data.get('body', '')
        
        system_prompt = """You are an expert Twitter content strategist specializing in Dark Psychology threads.
        Your threads are analytical, revealing, and go viral because they teach uncomfortable truths about human nature.
        You create text-native Twitter content that EXPANDS on video concepts, not just copies them."""
        
        user_prompt = f"""Transform this video script into a viral Twitter thread.

VIDEO SCRIPT:
Hook: {hook}
Body: {body}

THREAD REQUIREMENTS:
- Exactly 6 tweets
- Tweet 1: The hook + mention that there's a video (e.g., "Watch the full breakdown 👇")
- Tweets 2-4: Deep analytical dive into the psychology/concept (expand beyond the video, add extra insights)
- Tweet 5: Specific real-world application or tactical takeaway
- Tweet 6: CTA ("Follow me for more dark psychology")

CRITICAL RULES:
- Each tweet MUST be under 280 characters (strict limit)
- Use line breaks for readability where appropriate
- Don't just copy the video script - EXPAND on it with additional insights
- Use numbering (1/6, 2/6, etc.) at the END of each tweet
- Make it feel text-native (not like a video transcript)

EMOJI USAGE:
- Use 1-2 relevant emojis per tweet to break up text visually
- Place them at line breaks or for emphasis
- Do NOT overuse (no emoji walls)
- Tone: Serious/Mysterious emojis only (e.g., 🧠, 👁️, ♟️, 🌑, ⚖️, 🎭, 🔬, 💀, ⚡, 🎯)
- Avoid casual/playful emojis (no 😊, 🎉, 💪, etc.)

OUTPUT FORMAT (JSON):
{{
    "tweets": ["tweet 1 text (1/6)", "tweet 2 text (2/6)", ... "tweet 6 text (6/6)"]
}}
"""
        
        try:
            client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            thread_data = json.loads(content)
            tweets = thread_data.get('tweets', [])
            
            # Validate tweet lengths
            for i, tweet in enumerate(tweets, 1):
                if len(tweet) > 280:
                    print(f"  ⚠️  Warning: Tweet {i} is {len(tweet)} chars (truncating to 280)")
                    tweets[i-1] = tweet[:277] + "..."
            
            print(f"  ✓ Generated {len(tweets)} tweets")
            return tweets
            
        except Exception as e:
            print(f"❌ Error generating thread: {e}")
            raise
    
    def post_thread(self, video_path, thread_content):
        """
        Upload video and post Twitter thread using hybrid API approach.
        
        Args:
            video_path (str or Path): Path to video file
            thread_content (list): List of tweet strings
            
        Returns:
            str: URL of the first tweet in the thread
        """
        print("\n📤 Uploading video and posting thread to Twitter...")
        
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        try:
            # Step 1: Upload video using API v1.1 with chunked upload
            print("  📹 Uploading video (this may take a while)...")
            media = self.api.chunked_upload(
                filename=str(video_path),
                file_type='video/mp4',
                media_category='tweet_video'
            )
            media_id = media.media_id
            print(f"  ✓ Video uploaded successfully (media_id: {media_id})")
            
            # Step 2: Wait for video processing
            print("  ⏳ Waiting for video processing...")
            max_wait = 300  # 5 minutes max
            waited = 0
            while waited < max_wait:
                processing_info = self.api.get_media_upload_status(media_id)
                
                if processing_info is None:
                    # Processing complete
                    break
                
                state = processing_info.processing_info.get('state', 'unknown')
                
                if state == 'succeeded':
                    print("  ✓ Video processing complete")
                    break
                elif state == 'failed':
                    error = processing_info.processing_info.get('error', {})
                    raise Exception(f"Video processing failed: {error}")
                elif state == 'in_progress':
                    check_after = processing_info.processing_info.get('check_after_secs', 5)
                    print(f"    Processing... (checking again in {check_after}s)")
                    time.sleep(check_after)
                    waited += check_after
                else:
                    # Unknown state, wait a bit
                    time.sleep(5)
                    waited += 5
            
            # Step 3: Post thread using API v2.0
            print("  🐦 Posting thread...")
            tweet_ids = []
            first_tweet_id = None
            
            for i, tweet_text in enumerate(thread_content, 1):
                try:
                    # First tweet gets the video
                    if i == 1:
                        response = self.client.create_tweet(
                            text=tweet_text,
                            media_ids=[media_id]
                        )
                        first_tweet_id = response.data['id']
                        tweet_ids.append(first_tweet_id)
                        print(f"    ✓ Posted tweet 1/{len(thread_content)} (with video)")
                    else:
                        # Subsequent tweets are replies to the previous tweet
                        response = self.client.create_tweet(
                            text=tweet_text,
                            in_reply_to_tweet_id=tweet_ids[-1]
                        )
                        tweet_ids.append(response.data['id'])
                        print(f"    ✓ Posted tweet {i}/{len(thread_content)}")
                    
                    # Small delay to avoid rate limits
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"    ❌ Error posting tweet {i}: {e}")
                    raise
            
            # Get username for URL construction
            me = self.client.get_me()
            username = me.data.username
            thread_url = f"https://twitter.com/{username}/status/{first_tweet_id}"
            
            print(f"\n  ✅ Thread posted successfully!")
            print(f"  🔗 {thread_url}")
            
            return thread_url
            
        except Exception as e:
            print(f"\n❌ Error posting to Twitter: {e}")
            raise
