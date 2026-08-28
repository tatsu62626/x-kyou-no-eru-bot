"""
自動投稿スケジューラー

使い方:
  1. .env.example を .env にコピーし、X Developer Portal で取得したキーを設定
  2. content_queue.csv に投稿予定を記入（content_queue_template.csv を参照）
  3. python scheduler.py で常駐起動（一定間隔でキューを確認し、時刻が来たものを自動投稿）

Ctrl+C で停止できます。cron / systemd / タスクスケジューラ等に登録して
バックグラウンドで動かすことも可能です。
"""
import time
import logging
from datetime import datetime

from config import Config
from x_client import XClient
from content_queue import ContentQueue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_once(client, queue):
    """1回分のチェック処理：期限が来た投稿をすべて投稿する（古すぎるものはスキップ）"""
    due_posts = queue.get_due_posts()
    if not due_posts:
        logger.info("投稿予定なし")
        return

    now = datetime.now()
    for post in due_posts:
        scheduled = datetime.strptime(post["scheduled_time"], "%Y-%m-%d %H:%M")
        delay_minutes = (now - scheduled).total_seconds() / 60

        if delay_minutes > Config.MAX_STALE_MINUTES:
            reason = f"予定時刻から{int(delay_minutes)}分経過のためスキップ"
            queue.mark_skipped(post["id"], reason)
            logger.warning(f"スキップ: id={post['id']} {reason}")
            continue

        media_paths = [p for p in post["media_paths"].split("|") if p] if post["media_paths"] else None
        try:
            tweet_id = client.post_tweet(text=post["text"], media_paths=media_paths)
            queue.mark_posted(post["id"], tweet_id)
            logger.info(f"投稿成功: id={post['id']} tweet_id={tweet_id}")
        except Exception as e:
            queue.mark_failed(post["id"], e)
            logger.error(f"投稿失敗: id={post['id']} error={e}")


def main():
    client = XClient()
    queue = ContentQueue(Config.QUEUE_CSV)

    logger.info(f"スケジューラー起動。{Config.CHECK_INTERVAL_SECONDS}秒間隔でキューを確認します。")
    try:
        while True:
            run_once(client, queue)
            time.sleep(Config.CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.info("停止しました。")


if __name__ == "__main__":
    main()
