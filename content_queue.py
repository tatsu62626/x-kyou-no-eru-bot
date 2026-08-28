"""
投稿キュー管理モジュール
content_queue.csv を読み書きし、予約投稿の状態を管理する。

CSVカラム:
  id, scheduled_time (YYYY-MM-DD HH:MM), text, media_paths (|区切り, 任意),
  status (pending / posted / failed), tweet_id, posted_at, error
"""
import pandas as pd
from datetime import datetime
import os

COLUMNS = [
    "id", "scheduled_time", "text", "media_paths",
    "status", "tweet_id", "posted_at", "error",
]


class ContentQueue:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        if not os.path.exists(csv_path):
            pd.DataFrame(columns=COLUMNS).to_csv(csv_path, index=False)

    def _load(self):
        return pd.read_csv(self.csv_path, dtype=str).fillna("")

    def _save(self, df):
        df.to_csv(self.csv_path, index=False)

    def get_due_posts(self, now=None):
        """予約時刻を過ぎた未投稿(pending)の行を返す"""
        now = now or datetime.now()
        df = self._load()
        if df.empty:
            return []

        pending = df[df["status"] == "pending"].copy()
        due = []
        for _, row in pending.iterrows():
            try:
                scheduled = datetime.strptime(row["scheduled_time"], "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            if scheduled <= now:
                due.append(row.to_dict())
        return due

    def mark_posted(self, post_id, tweet_id):
        df = self._load()
        df.loc[df["id"] == post_id, "status"] = "posted"
        df.loc[df["id"] == post_id, "tweet_id"] = str(tweet_id)
        df.loc[df["id"] == post_id, "posted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save(df)

    def mark_failed(self, post_id, error_message):
        df = self._load()
        df.loc[df["id"] == post_id, "status"] = "failed"
        df.loc[df["id"] == post_id, "error"] = str(error_message)[:200]
        self._save(df)

    def mark_skipped(self, post_id, reason):
        """遅延しすぎた投稿など、投稿せずに見送る場合に使う"""
        df = self._load()
        df.loc[df["id"] == post_id, "status"] = "skipped"
        df.loc[df["id"] == post_id, "error"] = str(reason)[:200]
        self._save(df)

    def add_post(self, post_id, scheduled_time, text, media_paths=""):
        """コードから新規に予約投稿を追加するヘルパー"""
        df = self._load()
        new_row = {
            "id": post_id,
            "scheduled_time": scheduled_time,
            "text": text,
            "media_paths": media_paths,
            "status": "pending",
            "tweet_id": "",
            "posted_at": "",
            "error": "",
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        self._save(df)
