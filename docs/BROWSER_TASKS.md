# Browser Task Packets

最終更新: 2026-08-12

`kazex-catalog` の正本データから、ブラウザ操作担当のChatGPT等へそのまま渡せる自己完結型の作業指示を生成する。

目的はブラウザ自動化そのものをこのリポジトリへ実装することではない。まず、**カタログの事実を一度だけ入力し、その情報から外部サービス操作用の安全な指示文を再生成できること**を成立させる。

## 基本原則

- 外部サービスの画面で不足情報を推測しない。
- カタログに存在しない実績、数値、SNS、広告、プレス、ツアー等を作らない。
- 必須値が不足している場合は、可能なところまで進めても最終Submit / 申請は行わない。
- ブラウザ上で新しい必須項目や仕様が判明した場合は、作業完了報告に含め、後でYAML / templates / validationへ還元する。
- 正式採用が未確定の画像候補を、ブラウザAIが独断で正式アー写等へ昇格させない。

## 生成コマンド

### Too Lost Priority Pitch

```bash
python scripts/render_browser_task.py priority-pitch unseen-dragon
```

`releases/<release-id>.yaml` と対応artist YAMLから、以下を含む作業パケットを標準出力する。

- 対象artist / release / release date / UPC
- Selected Track
- Release Summary
- Spotify Artist
- Marketing Elements
- Past Awards / Milestones
- optional social / tour fields
- image / EPK候補
- 必須欠落項目
- `READY FOR FORM ENTRY` または `BLOCKED — DO NOT SUBMIT`
- ブラウザ担当AI向け安全ルールと完了報告フォーマット

フォーム必須値が1つでも不足している場合、パケットはSubmit禁止を明示する。

### Spotify for Artists

```bash
python scripts/render_browser_task.py spotify-profile mri-music-resonance-imaging
```

`artists/<artist-id>.yaml` と関連release YAMLから、以下を含む作業パケットを生成する。

- artist name
- 現在登録済みSpotify Artist URL
- 関連release / release date / UPC/EAN
- Bio作成に使えるdescription / concept / genres
- 登録済みSNS
- 正式採用artist image
- artist-photo candidates（参照専用）
- claim / access または既存profile updateの作業モード
- 不足情報がある場合の停止条件

`assets.artist_image` が未設定で候補しか存在しない場合、ブラウザ担当AIには画像を独断で選ばず変更しないよう指示する。

## Spotify for Artistsについての運用メモ

Spotifyのアーティストページ自体は、音楽がSpotifyへ初めて納品された際に作成される。KAZEX側では、ページをゼロから作るのではなく、Spotify for Artistsへのアクセス取得（claim）と、その後のプロフィール管理を行う。

初回リリース前にアクセスを取得する場合、Spotify Artist link / URI と今後のreleaseのUPCまたはEANが必要になる場合がある。そのため、`platforms.spotify_artist_url` と `identifiers.upc_ean` はclaim準備に重要なカタログ項目として扱う。

プロフィール整備では、Bio、SNSリンク、アバター、ヘッダー、画像ギャラリー等を扱える。ただし、画像変更はKAZEX Catalog側で正式素材が選ばれてから行う。

## ブラウザ作業後のフィードバック

ブラウザ担当AIから最低限、以下を回収する。

- 操作したサービス / 対象artist / release
- 入力・更新できた項目
- 入力できなかった項目
- 不足していたカタログ情報
- サービス側で新たに確認できた必須項目、文字数、選択肢、ファイル条件等
- Submit / claim / saveを実行したか
- 実行後のstatus

その報告を人間またはAIが確認し、必要ならcatalogへ反映する。

## 将来

ブラウザ機能の安定性や外部サービスの仕様が十分に分かった段階で、以下を検討できる。

- ブラウザタスクパケットをChatGPTブラウザ機能へ直接渡す運用
- release / artist単位のワンクリック生成
- 作業結果をYAMLへ戻す半自動フロー
- APIが正式提供されているサービスではUI操作からAPI連携へ移行

最初から完全自動化せず、まず「正本 → 安全な作業パケット → ブラウザ操作 → 差分報告」の循環を安定させる。
