"""
Twitter/X crawler for NVIDIA official tweets
"""
from typing import List, Dict, Any
from datetime import datetime
from .base_crawler import BaseCrawler


class TwitterCrawler(BaseCrawler):
    """Crawler for NVIDIA official Twitter/X posts"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("twitter", config)
        self.handle = config.get("handle", "nvidia")
        self.max_tweets = config.get("max_tweets", 100)
        
        try:
            import tweepy
            self.bearer_token = config.get("bearer_token", "")
            if self.bearer_token:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
            else:
                self.client = None
                self.logger.warning("Twitter API credentials not configured")
        except ImportError:
            self.logger.warning("tweepy not installed, Twitter crawler disabled")
            self.client = None
    
    async def extract_data(self, html_content: str = "") -> List[Dict[str, Any]]:
        """
        Extract tweets from Twitter/X
        
        Args:
            html_content: Not used for Twitter API
            
        Returns:
            List of tweets
        """
        tweets = []
        
        if not self.client:
            self.logger.warning("Twitter API client not initialized")
            return tweets
        
        try:
            user = self.client.get_user(username=self.handle)
            if not user.data:
                self.logger.error(f"User {self.handle} not found")
                return tweets
            
            user_id = user.data.id
            
            tweets_response = self.client.get_users_tweets(
                id=user_id,
                max_results=min(self.max_tweets, 100),
                tweet_fields=["created_at", "public_metrics"],
                expansions=["author_id"],
            )
            
            if not tweets_response.data:
                self.logger.info(f"No tweets found for {self.handle}")
                return tweets
            
            for tweet in tweets_response.data:
                try:
                    tweet_data = self._create_article(
                        title=tweet.text[:100] if len(tweet.text) > 100 else tweet.text,
                        url=f"https://twitter.com/{self.handle}/status/{tweet.id}",
                        content=tweet.text,
                        summary=tweet.text[:200],
                        publish_date=tweet.created_at if hasattr(tweet, 'created_at') else datetime.now(),
                        author=self.handle,
                        tags=["twitter", "x", "official"]
                    )
                    
                    if hasattr(tweet, 'public_metrics'):
                        metrics = tweet.public_metrics
                        tweet_data['metrics'] = {
                            'likes': metrics.get('like_count', 0),
                            'retweets': metrics.get('retweet_count', 0),
                            'replies': metrics.get('reply_count', 0),
                        }
                    
                    tweets.append(tweet_data)
                    self.logger.debug(f"Extracted tweet: {tweet.text[:50]}...")
                
                except Exception as e:
                    self.logger.warning(f"Error extracting tweet: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(tweets)} tweets")
            
        except Exception as e:
            self.logger.error(f"Error fetching tweets: {str(e)}")
        
        return tweets
