"""
X API v2 クライアントラッパー
投稿、メディアアップロード、投稿実績（メトリクス）取得を行う。

注意:
- メディアアップロードは現時点でv1.1エンドポイントが必要なためtweepy.APIを併用する
- 投稿実績（インプレッション数等）の取得にはBasic以上の有料プランが必要
"""
import tweepy
from config import Config


class XClient:
    def __init__(self):
        Config.validate()

        # v2エンドポイント用クライアント（投稿・削除・メトリクス取得）
        self.client = tweepy.Client(
            bearer_token=Config.BEARER_TOKEN,
            consumer_key=Config.API_KEY,
            consumer_secret=Config.API_SECRET,
            access_token=Config.ACCESS_TOKEN,
            access_token_secret=Config.ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True,
        )

        # v1.1エンドポイント用クライアント（メディアアップロードのみ使用）
        auth = tweepy.OAuth1UserHandler(
            Config.API_KEY,
            Config.API_SECRET,
            Config.ACCESS_TOKEN,
            Config.ACCESS_TOKEN_SECRET,
        )
        self.api_v1 = tweepy.API(auth)

    def upload_media(self, media_paths):
        """画像・動画ファイルをアップロードしmedia_idリストを返す（最大4件）"""
        media_ids = []
        for path in media_paths[:4]:
            media = self.api_v1.media_upload(filename=path)
            media_ids.append(media.media_id)
        return media_ids

    def post_tweet(self, text, media_paths=None, in_reply_to_id=None):
        """テキスト（＋任意でメディア）を投稿し、投稿IDを返す"""
        media_ids = None
        if media_paths:
            media_ids = self.upload_media(media_paths)

        response = self.client.create_tweet(
            text=text,
            media_ids=media_ids,
            in_reply_to_tweet_id=in_reply_to_id,
        )
        return response.data["id"]

    def get_tweet_metrics(self, tweet_id):
        """
        投稿の公開メトリクス（いいね・リポスト等）と非公開メトリクス
        （インプレッション数等、自分の投稿かつ有料プランのみ取得可）を返す
        """
        response = self.client.get_tweet(
            id=tweet_id,
            tweet_fields=["public_metrics", "non_public_metrics", "created_at"],
        )
        return response.data

    def get_recent_tweets(self, user_id, max_results=20):
        """自分の直近投稿一覧をメトリクス付きで取得"""
        response = self.client.get_users_tweets(
            id=user_id,
            max_results=max_results,
            tweet_fields=["public_metrics", "non_public_metrics", "created_at"],
        )
        return response.data or []
