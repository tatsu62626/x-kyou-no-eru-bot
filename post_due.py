"""
単発実行用エントリーポイント（cron や GitHub Actions から呼び出す用）

常駐する scheduler.py とは違い、1回だけキューを確認して
期限が来た投稿があれば投稿し、すぐに終了する。

使い方:
  python post_due.py
"""
import logging

from x_client import XClient
from content_queue import ContentQueue
from config import Config
from scheduler import run_once

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    client = XClient()
    queue = ContentQueue(Config.QUEUE_CSV)
    run_once(client, queue)
