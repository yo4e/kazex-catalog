# アーティスト情報を整える手順

NoZomを最初の例として、既存のYAMLを正本に情報を補います。サイト用に同じ値を手入力しません。他アーティストの不足値を一括で推定補完するものではありません。

## 正本と表示の対応

| 情報 | 正本 | 表示 |
| --- | --- | --- |
| 短い紹介・公開プロフィール | `artists/<id>.yaml` の `description.short/long` | アーティスト見出し・「プロフィールを読む」 |
| アーティスト配信ページ | 同ファイルの `platforms` | Spotify / Apple Musicへのリンク |
| 代表アー写 | 同ファイルの `assets.artist_image.github_path` | 明示指定された1枚のみ。未指定なら空欄 |
| 画像候補 | 同ファイルの `assets.artist_photo_candidates` | 公開許可済み素材のみ。`candidate`を自動採用しない |
| ジャケット | `releases/<id>.yaml` の `cover.github_path` | 一覧と作品見出しの正方形枠 |
| 作品形式・ジャンル・レーベル・識別子・C/P | 同ファイルの既存フィールド | 折りたたみの「作品情報」 |
| 配信先 | 同ファイルの `links` / `tracks[].links` | 作品／曲単位のリンク。smartlinkを維持 |
| 曲の表示時間 | `tracks[].duration_seconds` | 分:秒。正の整数、未確認なら省略またはnull |
| Songwriter登録表記 | `tracks[].credits.songwriters` | 名前の配列。表記を保持し、作詞・作曲やartist IDを推定しない |
| 歌詞 | `lyrics.index_path` → 曲ごとの状態と採用本文 | 採用済み／確認待ち／未取得／歌詞なしを区別 |
| インスト確認 | `tracks[].instrumental` の本人確認と日付 | 明示確認された曲だけInstrumentalと表示。将来曲へ継承しない |
| 確認元・差異 | `notes_public`、公開素材のREADME | 保守用根拠。サイト生成時は丸ごと転送しない |

既存レコードに新しい任意フィールドがなくても読み込めます。リンク表示はサービス・対象種別・URL形式を許可リストで制限し、任意の出典URLや追跡クエリは表示しません。

## 確認順

1. 作品名と名義だけで決めず、既存UPC・ISRC・アルバム／曲ID、レーベル、発売日を照合する。同名アーティストの混在を確認する。
2. 登録済み配信先から公開プロフィール・ジャケット・リンクを調べる。既存素材保管場所も確認し、「素材未発見」と「素材はあるが代表未指定」を分ける。
3. 公開済み本文は出典を記録して取り込む。新しいBIOを創作して確定扱いにしない。未公開候補素材・未採用歌詞は公開repoに入れない。
4. 日付・時間・クレジットが食い違う場合は根拠を残す。時間はDSPの丸め表示差があり、音源原本の厳密な長さとは区別する。新しい役割や本人設定は推測しない。
5. 本人確認は代表画像や歌詞の採用など、助手だけでは決められない判断にまとめる。既存の候補があれば新規制作を要求しない。

NoZomの具体値と出典は `artists/nozom.yaml`、`releases/sense-of-wonder.yaml`、素材READMEを参照します。代表アー写・歌詞の現在の採用状態はそれぞれの正本で確認します。公開カタログに本文候補は格納しません。

## 検証と反映

```bash
python scripts/validate_catalog.py
python -m unittest discover -s tests
python scripts/build_public_viewer.py --output /tmp/kazex-pages-check
```

出力先は新しいディレクトリを指定します。公開生成は正本YAMLと採用済み歌詞だけを読み、私的設定を受け取りません。公開許可の範囲内でmainへ反映すると、既存のPagesワークフローが再生成します。最終headのCI・デプロイと、配信されたJSON・画像・画面を照合します。`website.publish`、pitch、未採用資料の状態は補完のために変更しません。
