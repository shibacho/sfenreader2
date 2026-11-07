# SFEN Reader — クラウド将棋局面図ジェネレーター

[English](README.md)

## 概要

SFEN 文字列を含む URL から、将棋の局面図を PNG 画像で生成するサービスです。

現在は
https://sfenreader2.appspot.com/
で稼働しています。旧URLの https://sfenreader.appspot.com/ でも同じように利用できます。

## 構成

```
ブラウザ / SNS
   │  https://sfenreader2.appspot.com/      https://sfenreader.appspot.com/ (旧URL)
   ▼                                        ▼
App Engine: sfenreader2 プロジェクト    App Engine: sfenreader プロジェクト
   (appengine-proxy/)                       (appengine-proxy/ を同じくデプロイ)
   │                                        │
   └──────────────┬─────────────────────────┘   … 公開URLを受けて Cloud Run へ中継
                  ▼
Cloud Run (リポジトリ直下)          … 本体 (Flask + Pillow, コンテナ)
```

| コンポーネント | 場所 | 役割 |
|---|---|---|
| Cloud Run `sfenreader2` (asia-northeast1) | リポジトリ直下 (`Dockerfile`, `main.py` ほか) | 局面図の生成 (`/sfen`, `/resize`, `/twiimg`) と静的ページ (`htdocs/`) の配信 |
| App Engine `default` サービス (プロジェクト `sfenreader2`) | `appengine-proxy/` | `sfenreader2.appspot.com` へのアクセスを Cloud Run へ中継。ブラウザの URL は appspot のまま |
| App Engine `default` サービス (プロジェクト `sfenreader`) | `appengine-proxy/` | 旧URL `sfenreader.appspot.com` へのアクセスを同じ Cloud Run へ中継 |

- 対局者名・タイトルの描画はコンテナ内の Noto Sans CJK フォントで行います
  (以前利用していた Google Charts Image API は提供終了しました)。
- 共有用 URL (`/twiimg` の出力、局面作成ページのリンク) は
  `https://sfenreader2.appspot.com` に統一しています (旧URLからアクセスした場合も同じ)。

## デプロイ

### 本体 (Cloud Run)

```sh
gcloud run deploy sfenreader2 --source . --project sfenreader2 --region asia-northeast1
```

### 中継 (App Engine)

```sh
# sfenreader2.appspot.com
gcloud app deploy appengine-proxy/app.yaml --project sfenreader2 --version proxy-to-cloudrun
# sfenreader.appspot.com (旧URL)
gcloud app deploy appengine-proxy/app.yaml --project sfenreader --version proxy-to-cloudrun
```

### 環境変数

| 変数 | 対象 | 説明 |
|---|---|---|
| `PUBLIC_BASE_URL` | Cloud Run | `/twiimg` が生成する URL の基点 (Dockerfile で `https://sfenreader2.appspot.com` を設定) |
| `SFEN_FONT_PATH` | Cloud Run | 文字描画に使うフォントのパス (未指定時は Noto Sans CJK などを自動検出) |
| `LOG_LEVEL` | Cloud Run | ログレベル (既定: `INFO`) |
| `UPSTREAM_URL` | App Engine | 中継先の Cloud Run の URL (`appengine-proxy/app.yaml` で設定) |

## License

このソフトウェアはApache 2.0ライセンスで配布されます。以下を参照してください。
http://www.apache.org/licenses/LICENSE-2.0.

Copyright (c) 2011-2026 shibacho
