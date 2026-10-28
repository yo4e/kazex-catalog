# ローカルのカタログ確認画面

アーティスト・画像・作品・曲・歌詞を一つの画面から確認する、読み取り専用のビューワー。
修正依頼は表示中のURLや曲名・ISRCを使って会話で伝える。画面の選択でカタログを書き換えない。

## 起動

Python 3.12とPyYAMLを使用する。フロントエンドのビルドや外部CDNは不要。

```bash
python viewer/server.py --port 8767
```

`http://127.0.0.1:8767/` を同じMacのブラウザで開く。上記は公開カタログ内の情報だけを読む。

私的な確認候補も読む場合は、リポジトリ外に設定JSONを作って指定する。

```json
{
  "private_index": "/path/to/private/index.json",
  "review_validation": "/path/to/private/validation.json",
  "review_file": "/path/to/private/lyrics-review.txt"
}
```

```bash
python viewer/server.py --port 8767 --private-config /path/to/private/config.json
```

私的入力は収集索引の `tracks[].versions` と、確認TXTの検証記録 `bodies[]` のバイト範囲・SHA256を照合する。
設定ファイルと3入力ファイルは必ずリポジトリ外に置く。実パスを含む起動メモ、スクリーンショット、テスト結果もリポジトリ外へ保存する。

## 使い方

1. アーティストや「確認待ち」で絞り込む。曲名・作品名・ISRCの検索も使える。
2. 作品を開き、左の曲一覧から曲を選ぶ。
3. ローカルの私的候補が複数ある曲は「表示する歌詞」で選ぶ。「2つの本文を並べて比較する」で差のある行を確認する。
4. 修正依頼には表示中のURLを使う。曲・候補・比較対象の選択はURLに保持される。候補の完全なIDと本文SHA256はローカルの詳細から確認できる。
5. 画像は「画像を確認」を開く。確認前の候補には「確認待ち」を表示する。旧版はチェックを入れたときだけ表示する。

状態バッジと状態の絞り込みは「確認待ち」だけを表示する。内部の採用済み・確認待ち・未取得・歌詞なし、画像のcandidate / selected / archived等は変更しない。
採用済みの曲でも私的原稿を比較できるが、選択しても採用状態は変わらない。歌詞がない曲に制作管理の説明は表示しない。未取得や確認待ちを歌詞なしと解釈しない。
歌詞が1本文だけなら選択欄を省略して本文を表示する。依頼文コピー、クリップボード書込み、手動コピー用ダイアログは設けない。
ブラウザの戻る・再読み込みで曲と候補の選択を再現できる。一覧へ戻ると検索条件も復元する。

## 公開データとの境界

- リポジトリに置くのは汎用のコードだけ。私的な候補本文や出典をJavaScript・HTML・公開YAMLへ埋め込まない。
- 公開カタログと採用本文は `/api/catalog`、`/api/track`、私的候補は `/api/candidates` で分ける。
- 私的データはメモリで読む。出典は候補の詳細内で必要時に見る。NAS生パス・原本の補助資料はAPIに出さない。
- サーバーは `127.0.0.1` にだけ接続を受け付ける。外部ホスト・別オリジンからの読み取り、任意ファイル参照、更新リクエストを拒否する。
- 他のアプリから本人がリンクを開く場合は、Originなし・ユーザー操作ありのトップレベル遷移に限り、データを含まない入口HTMLだけを表示する。Chromeがその遷移を再読み込みしても開ける。歌詞API・画像・スクリプトにはこの例外を適用せず、外部Originやiframeからのアクセスも許可しない。
- キャッシュ保存・外部フォント・解析タグ・外部画像読み込み・Service Workerは使わない。
- ローカルサーバーは私的資料を公開用に出力しない。Pagesは下記の別ビルドで、公開カタログのみから生成する。
- `website.publish: false` の作品も本人のローカル確認には表示する。公開設定を変更したことにはならない。

ローカルURLは同じMac用。他の端末へ公開するトンネルやLAN公開は、この実装の対象外。

## 検証

```bash
python -m unittest discover -s tests -p 'test_viewer.py'
python scripts/validate_catalog.py
```

`test_viewer.py` は合成データでAPI分離、入力ハッシュ、設定の配置、読み取り専用、loopback・Host/Origin制約、画像状態を検証する。
実データを使うブラウザ検証とスクリーンショットは私的な作業ディレクトリで実行・保存する。

## レーベル表示と聴取先

- `assets/label/brand.yaml` がロゴ・配色の参照元。ロゴ・ジャケットは正方形枠のcontain表示。代表アー写と画像一覧のアー写は正方形枠をcoverで埋め、中央を基準に端を切り取る。原画像は変更しない。
- アーティストのトップには `assets.artist_image.github_path` の指定済み画像を1枚表示する。candidateや複数selectedから勝手に代表を選ばない。未指定は未選択／未登録と表示する。
- 公開プロフィールは `description.long` から折りたたみ表示する。「作品情報」はrelease YAMLの形式・ジャンル・レーベル・識別子・C/Pを表示する。曲の表示時間とSongwriter原表記もYAMLから読み、不明値は補わない。詳細は [カタログ補完手順](../docs/CATALOG_COMPLETION.md) を参照。
- Spotify / Apple Music / Amazon Musicの作品・曲リンク、Spotify / Apple Musicのアーティストリンクは登録済みの正規URLのみ表示する。任意URLや追跡クエリ、原資料の出典リンクは転送しない。
- MRI・TAG・Satori Chandraは本人指定により基本歌詞なし。作品の個別指定をアーティストの基本値より優先する。
- Too Lostは `releases/*.yaml` の `links.smartlink` のみ使用する。Spotifyは各曲の正式な `tracks[].links.spotify` にあるtrack IDのみ。検索やアルバムIDからの推測を行わない。
- 曲の聴取先は「Spotify ↗」「Apple Music ↗」「Amazon Music ↗」の順に、登録があるサービスだけを表示する。Spotifyのプレーヤーと重複導線は表示しない。
- 外部リンクはnoopener/noreferrer、referrerpolicy=no-referrer。私的候補本文・出典・ローカルURLは渡さず、ローカルAPIのHost/Origin制限を維持する。

## GitHub Pages版

2026-10-27の本人指示に基づく公開カタログ。`scripts/build_public_viewer.py` は私的設定を受け付けず、リポジトリにある公開データと採用本文だけから静的ファイルを生成する。

```bash
python scripts/build_public_viewer.py --output /tmp/kazex-public-preview
```

出力先は新規ディレクトリを指定する。既存ディレクトリは上書きしない。公開版にはAPIサーバーも非公開資料も含めず、未採用曲は「確認待ち」と表示する。公開前に本文ハッシュ、候補データ0件、出典URL・ローカルパスなしを検査する。

`catalog-pages.yml` はmain更新時に検証・生成した専用ディレクトリだけをPagesへ配置する。リポジトリ全体のアップロードは行わない。
公開カタログ掲載の本人承認は全19作品を対象とする。既存の `website.publish` は将来の公式サイト連携設定として値を保持する。
ローカル比較版は引き続き `--private-config` で利用でき、公開版への切替で私的原稿が消えることはない。
