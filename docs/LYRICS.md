# 歌詞管理

公開カタログには、本人の採用確認または既存の投稿完了記録から本文を一意に特定できた歌詞だけを格納する。
曲名、曲順、ISRC、アーティスト、作品の正本は既存の `artists/` と `releases/` に置く。

## 参照方法

- 人間向け入口: [歌詞索引](../lyrics/README.md)。アーティスト→作品→曲順。
- 機械向け入口: release YAML の `lyrics.index_path`。
- 作品索引: `lyrics/<release-id>/index.yaml`。`tracks[].isrc` を同じreleaseの曲に対応させる。
- 採用本文: `lyrics/<release-id>/<lowercase-isrc>.txt`。`text_path` はリポジトリルート相対。
- 集計: `lyrics/collection.yaml`。公開対象は `adopted_lyrics_only`。

## 状態

- `adopted`: 採用記録と本文の対応を照合済み。1曲につき本文1ファイル、SHA256、採用根拠の種別と照合日を持つ。
- `pending_selection`: 候補資料はあるが採用版を確定できない。本文パス・ハッシュ・採用情報は全てnull。
- `not_collected`: 本文未取得。同様に本文を参照しない。歌詞なし・インストという判定ではない。
- `no_lyrics`: 歌詞なし。収集対象外で、本文・ハッシュ・採用情報はnull。作品の `lyrics.has_lyrics: false` と一致させる。既存の原資料を削除する指示ではない。

作品の `lyrics.has_lyrics` は歌詞の有無で、本文の収録状態として使わない。本人確認で訂正する場合は `basis: owner_confirmation` と `confirmed_on` を記録する。
アーティストの `lyrics.default_has_lyrics: false` は今後の基本方針。明示的な作品の `lyrics.has_lyrics` が優先し、例外は本人の指定を受けて作品・索引を更新する。
2026-10-27の本人指定により、MRI・The Aerial Gravities・Satori Chandraは基本歌詞なし。MRIの15曲は未取得の収集対象から外した。
`collection.yaml` の件数は索引が存在する曲のみを集計する。歌詞なし作品全体の曲数とは異なる。

## インスト確認

曲単位の `releases/*.yaml` の `tracks[].instrumental` に、本人確認の根拠と日付を記録する。未確認は省略またはnullとし、アーティストや作品から継承しない。

```yaml
instrumental: {basis: owner_confirmation, confirmed_on: "2026-10-28"}
```

2026-10-28に本人がMRI・The Aerial Gravities・Satori Chandraの現存全110曲をインストと確認した。この時点の各曲へ記録し、将来追加される曲には自動適用しない。
サイトでは有効な曲別確認がある場合だけ `Instrumental` と表示する。`no_lyrics`、歌詞本文の空欄、配信管理画面のバッジだけからインスト判定しない。公開用データには確認結果だけを渡し、分類・採用状態や原資料を変えない。

## 採用版の照合

採用記録の照合は配信音源との音声同一性の検証とは異なる。日付が新しい、再生数が多い、候補が1件という理由だけで採用しない。
投稿完了記録があっても、対応する複数原稿の本文が異なり一意に特定できない曲は保留する。

## 原資料と公開範囲

全版の原資料、出典URL、元ファイルパス、詳細比較、個別の採用照合根拠は私的保管先で保全する。
公開カタログにはそれらの写し、リンク、版ID、候補本文、出典ハッシュを含めない。
本文は読みやすい確認版から抽出し、構成・歌唱指示、付加ふりがなの除去以外に改作しない。

リポジトリへpushした内容は一般閲覧可能になる。`website.publish: false` はGitHubへのアクセス制限ではない。
GitHub Pagesや公式サイトへの公開は別の作業とし、既存の公開設定を変更しない。

## 検証

```bash
python scripts/validate_catalog.py
python -m unittest discover -s tests -p 'test_lyrics.py'
```

作品・ISRC・曲順、本文パス、UTF-8、SHA256、採用記録、未採用曲の本文参照禁止、
孤立ファイル、件数、出典メタデータ混入、制作サービスのURL混入を検査する。
private資料を公開フォルダへコピーしてから削除する運用は避け、採用本文と必要最小限の項目だけを明示的に抽出する。
