"""
タイムゾーン共通ユーティリティ

GitHub Actionsの実行環境はUTC（協定世界時）で動くため、
「7:30に投稿」のような日本時間(JST)ベースの予約時刻をそのまま
datetime.now()と比較すると9時間ズレてしまう。
このモジュールで必ずJSTの現在時刻を取得するようにする。
"""
import datetime
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")


def now_jst():
    """現在時刻をJSTの素朴な(タイムゾーン情報なしの)datetimeで返す"""
    return datetime.datetime.now(JST).replace(tzinfo=None)
