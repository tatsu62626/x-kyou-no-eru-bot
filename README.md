# X自動投稿ツール

X API v2（公式）を使って、あらかじめ用意した投稿を予約時刻に自動投稿し、
投稿後の実績（いいね・リポスト・インプレッション等）をCSVに記録するツールです。

## できること

- `content_queue.csv` に登録した投稿を、指定時刻になったら自動投稿
- 画像・動画の同時投稿（最大4枚）
- 投稿済みツイートの実績（いいね・リポスト・返信・引用・ブックマーク数、
  有料プランならインプレッション数）を定期取得してCSVに記録
- 投稿の成功/失敗をログとCSVステータスで管理

## できないこと・含めていないもの

- いいね・フォロー・リポストの自動化、リプライへの自動大量返信など、
  X利用規約でスパム行為とみなされうる操作は含めていません
- インプレッション数を人為的に水増しする機能はありません（規約違反かつ技術的にも不可能です）
- 複数アカウントを使った自演エンゲージメントの仕組みは含めていません

## 事前準備

1. [X Developer Portal](https://developer.x.com) でプロジェクト・アプリを作成し、
   API Key/Secret、Access Token/Secret、Bearer Tokenを取得
   - アプリの権限は「Read and Write」に設定してください
2. Python 3.9以上をインストール
3. 依存パッケージをインストール

   ```bash
   pip install -r requirements.txt
   ```

4. `.env.example` を `.env` にコピーし、取得したキーを記入

   ```bash
   cp .env.example .env
   ```

## 使い方

### 1. 投稿を予約する

投稿内容は2通りの方法で登録できます。

**A. Excelの投稿カレンダーから登録する（推奨）**

「今日のエール_投稿カレンダー.xlsx」をこのフォルダに置き、`投稿カレンダー` シートの
「投稿内容」欄に文面を、「ステータス」欄を `下書き` のままにしておきます。

```bash
python excel_to_queue.py
```

ステータスが `下書き` かつ投稿内容が入っている行だけを `content_queue.csv` に登録し、
登録が終わった行はExcel側のステータスを自動で `予約済み` に更新します。
（同じ行を二重に登録することはありません。何度実行しても安全です。）

Excelでファイル名が違う場合は `python excel_to_queue.py ファイル名.xlsx` のように指定してください。

**B. content_queue.csv を直接編集する**

`content_queue_template.csv` を参考に `content_queue.csv` を作成し、
`scheduled_time`（YYYY-MM-DD HH:MM）と `text` を記入してください。
画像を添付する場合は `media_paths` にファイルパスを `|` 区切りで記入します。

### 2. 自動投稿を動かす

PCやサーバーを常時起動しておける環境がある場合は「A. 常駐スケジューラー」、
そうでない場合は「B. GitHub Actions（推奨・無料・PC常時起動不要）」を選んでください。

#### A. 常駐スケジューラー（PC/サーバーを起動しっぱなしにできる場合）

```bash
python scheduler.py
```

デフォルトで60秒ごとにキューを確認し、時刻が来た投稿を自動投稿します。
`nohup python scheduler.py &` や systemd 等で常駐させてください。

#### B. GitHub Actions（PCを起動しっぱなしにできない場合・推奨）

GitHub上でコードを10分おきに自動実行し、期限が来た投稿だけ投稿します。
PCの電源やネット接続に依存しません。

**手順**

1. GitHubで新しいリポジトリを作成する（**Public（公開）を推奨** — 詳しくは下の注意点を参照）
2. このフォルダの中身一式（`.github/workflows/auto_post.yml` を含む）をそのリポジトリにpushする
   - `.env` ファイルは絶対にpushしないこと（`.env.example` だけをpushする）
3. リポジトリの `Settings → Secrets and variables → Actions` で、以下のSecretsを登録する
   - `X_API_KEY` / `X_API_SECRET` / `X_ACCESS_TOKEN` / `X_ACCESS_TOKEN_SECRET` / `X_BEARER_TOKEN`
4. `Actions` タブを開き、ワークフローを有効化する
5. あとは自動で10分おきに `post_due.py` が実行され、期限が来た投稿だけ自動投稿されます

**注意点**

- **Publicリポジトリを推奨する理由**: GitHub ActionsはPublicリポジトリなら実行時間が無料無制限ですが、
  Privateリポジトリだと月2,000分までしか無料枠がなく、10分おき実行だと簡単に超過します。
  投稿内容はどのみちXで公開されるものなので、Publicリポジトリで公開されても実害はありません。
  （APIキーはSecretsとして暗号化されるため、Publicでも他人には見えません。ただし `.env` を
  誤ってpushしないよう注意してください。）
- GitHub Actionsの`schedule`は、リポジトリに60日間まったく動きがないと自動的に無効化されます。
  その場合は `Actions` タブから手動で再度有効化するか、何かを1回commitしてください。
- `cron` の実行タイミングはGitHub側の混雑状況により数分〜十数分ずれることがあります。
  そのため `config.py` の `MAX_STALE_MINUTES`（デフォルト180分）を超えて遅れた投稿は、
  「今さら投稿しても意味がない」と判断して自動的にスキップされます（`content_queue.csv`の
  ステータスが `skipped` になります）。この閾値は`.env`の `MAX_STALE_MINUTES` で調整できます。

### 3. 実績を取得する

```bash
python analytics.py
```

投稿済みの各ツイートについて実績を取得し `analytics_log.csv` に追記します。
定期実行したい場合はcron等で1日1回程度回すのがおすすめです。

## X API利用プランについての注意（2026年8月時点）

| プラン | 月額目安 | 投稿上限 | 読み取り上限 | インプレッション数取得 |
|---|---|---|---|---|
| Free | $0 | 500件/月 | 実験的な読み取りAPIのみ（100リクエスト） | 不可 |
| Basic | $200 | 15,000件/月 | あり | 可能 |
| Pro | $5,000 | 300,000件/月 | あり（大規模） | 可能 |

- **インプレッション数（non_public_metrics）を取得するにはBasic以上のプランが必要です。**
  Freeプランのままでも投稿の自動化自体は可能ですが、`analytics.py` の
  `impressions` 列は空欄になります。
- 料金・上限はXが随時変更するため、実際の契約前に必ず
  [公式の最新料金ページ](https://developer.x.com/en/products/x-api)を確認してください。
- 大量の同一文面投稿や短時間の連投は、規約上・アルゴリズム上どちらの観点でも
  避けることを推奨します。

## ファイル構成

```
x_auto_poster/
├── .github/workflows/auto_post.yml  # GitHub Actionsで10分おきに自動実行する設定
├── config.py                   # .env / 環境変数から設定を読み込み
├── x_client.py                 # X API v2ラッパー（投稿・メディア・実績取得）
├── content_queue.py            # 予約投稿CSVの読み書き
├── excel_to_queue.py           # Excel投稿カレンダー → content_queue.csv 同期
├── scheduler.py                # 常駐実行する自動投稿本体（run_once関数を共用）
├── post_due.py                 # cron/GitHub Actions向けの単発実行エントリーポイント
├── analytics.py                # 投稿実績の定期取得・記録
├── content_queue_template.csv  # 投稿予約の記入例
├── requirements.txt
└── .env.example
```

## 全体の運用フロー

```
Excel(投稿カレンダー) --[excel_to_queue.py]--> content_queue.csv
                                                     │
                                    [GitHub Actionsが10分おきに post_due.py を実行]
                                                     │
                                                  X に自動投稿
                                                     │
                                            [analytics.py 定期実行]
                                                     │
                                            analytics_log.csv（実績）
                                                     │
                                     手動で「実績ログ」シートに転記
                                                     │
                                    「ダッシュボード」シートが自動集計
```

1. Excelの「投稿カレンダー」シートに文面を書き足す
2. `python excel_to_queue.py` でキューに反映し、GitHubにpush
3. GitHub Actionsが自動で時刻通りに投稿（PCを起動しておく必要なし）
4. 定期的に `python analytics.py` で実績を取得（自分のPCで手動実行、またはこれも
   GitHub Actionsに組み込み可能）
5. `analytics_log.csv` の数字を「実績ログ」シートに転記すると、「ダッシュボード」シートで
   朝・昼・夜・土日どのスロットが伸びているか自動集計される
