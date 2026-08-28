"""
投稿実績ロガー

posted 済みの投稿について、インプレッション数・いいね数・リポスト数などを
取得してanalytics_log.csvに追記する。

※ non_public_metrics（インプレッション数含む）の取得には
   X APIのBasic以上の有料プランが必要です（2026年8月時点）。
   Freeプランの場合は public_metrics（いいね・リポスト・返信数等、
   インプレッションは含まれない）のみ取得できます。

使い方:
  python analytics.py
  → content_queue.csv の status=posted な投稿すべてについて最新実績を取得し記録
"""
import pandas as pd
from datetime import datetime
import logging

from config import Config
from x_client import XClient
from content_queue import ContentQueue

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ANALYTICS_COLUMNS = [
    "fetched_at", "post_id", "tweet_id", "impressions",
    "likes", "reposts", "replies", "quotes", "bookmarks",
]


def fetch_and_log():
    client = XClient()
    queue = ContentQueue(Config.QUEUE_CSV)

    df = pd.read_csv(Config.QUEUE_CSV, dtype=str).fillna("")
    posted = df[df["status"] == "posted"]

    if posted.empty:
        logger.info("投稿済みデータがありません。")
        return

    rows = []
    for _, row in posted.iterrows():
        tweet_id = row["tweet_id"]
        if not tweet_id:
            continue
        try:
            tweet = client.get_tweet_metrics(tweet_id)
            public = tweet.public_metrics or {}
            non_public = tweet.non_public_metrics or {}
            rows.append({
                "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "post_id": row["id"],
                "tweet_id": tweet_id,
                "impressions": non_public.get("impression_count", ""),
                "likes": public.get("like_count", ""),
                "reposts": public.get("retweet_count", ""),
                "replies": public.get("reply_count", ""),
                "quotes": public.get("quote_count", ""),
                "bookmarks": public.get("bookmark_count", ""),
            })
            logger.info(f"取得成功: tweet_id={tweet_id}")
        except Exception as e:
            logger.error(f"取得失敗: tweet_id={tweet_id} error={e}")

    if not rows:
        return

    new_df = pd.DataFrame(rows, columns=ANALYTICS_COLUMNS)
    try:
        existing = pd.read_csv(Config.ANALYTICS_CSV)
        combined = pd.concat([existing, new_df], ignore_index=True)
    except FileNotFoundError:
        combined = new_df
    combined.to_csv(Config.ANALYTICS_CSV, index=False)
    logger.info(f"{len(rows)}件の実績を {Config.ANALYTICS_CSV} に記録しました。")


if __name__ == "__main__":
    fetch_and_log()
