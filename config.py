"""
設定読み込みモジュール
.env ファイルから X API の認証情報を読み込む。
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_KEY = os.getenv("X_API_KEY")
    API_SECRET = os.getenv("X_API_SECRET")
    ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
    BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
    USER_ID = os.getenv("X_USER_ID")

    # ファイルパス
    QUEUE_CSV = os.getenv("QUEUE_CSV", "content_queue.csv")
    LOG_CSV = os.getenv("LOG_CSV", "post_log.csv")
    ANALYTICS_CSV = os.getenv("ANALYTICS_CSV", "analytics_log.csv")

    # スケジューラーがキューを確認する間隔（秒）※常駐実行時のみ使用
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))

    # 予定時刻からこの分数以上遅れた投稿は「stale（古すぎる）」として投稿せずスキップする
    # 例: 朝7:30の投稿が、実行環境の不調で夜まで実行されなかった場合に、今さら投稿しないようにする
    MAX_STALE_MINUTES = int(os.getenv("MAX_STALE_MINUTES", "180"))

    @classmethod
    def validate(cls):
        required = {
            "X_API_KEY": cls.API_KEY,
            "X_API_SECRET": cls.API_SECRET,
            "X_ACCESS_TOKEN": cls.ACCESS_TOKEN,
            "X_ACCESS_TOKEN_SECRET": cls.ACCESS_TOKEN_SECRET,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise EnvironmentError(
                f".envに以下の値が設定されていません: {', '.join(missing)}\n"
                f".env.example を参考に .env を作成してください。"
            )
