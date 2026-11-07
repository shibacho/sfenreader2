# SFEN Reader for Google App Engine (スタンダード環境)

[English](README.md)

## 概要

Google App Engine 上で将棋の局面図をpng形式で生成するサービスです

現在は
https://sfenreader2.appspot.com/
で稼働しています。

## デプロイ (Cloud Run)

App Engine の `python37` ランタイムは廃止されたため、Cloud Run 上でコンテナとして動かします。

```sh
gcloud run deploy sfenreader2 --source . --region asia-northeast1 --allow-unauthenticated
```

- 対局者名・タイトルの描画はコンテナ内の Noto Sans CJK フォントで行います
  (以前利用していた Google Charts Image API は提供終了しました)。
  別のフォントを使う場合は環境変数 `SFEN_FONT_PATH` にパスを指定してください。
- ログレベルは環境変数 `LOG_LEVEL` (既定: `INFO`) で変更できます。

## License

このソフトウェアはApache 2.0ライセンスで配布されます。以下を参照してください。
http://www.apache.org/licenses/LICENSE-2.0.

Copyright (c) 2011-2020 shibacho
