# Too Lost Priority Pitch 作成仕様 v1.0

確認日：2026-08-12

この文書は、Too Lost の Priority Pitch を ChatGPT / Codex 等のAIと人間が継続して作成できるようにするための運用仕様です。

## 基本ルール

- 対象は Too Lost 経由で配信される未リリース作品
- 1リリースにつき代表曲1曲のみPitch可能
- アルバム／EPでも全曲分は提出しない
- 同一リリースについて複数回Pitchしない
- Too Lost 推奨提出時期はリリース3〜4週間前
- Pitch採択やプレイリスト掲載等は保証されない
- 自由記述は特に指定がなければ自然な英語で作成する
- 実績、広告、プレス、ツアー等を捏造・誇張しない

Too Lost公式ヘルプ：
https://help.toolost.com/hc/en-us/articles/360054367112-What-Is-Priority-Pitch

## 必須項目

### 1. Release Summary / リリース概要

500文字以内。

代表曲について、以下から重要なものを盛り込む。

- 曲／作品のコンセプト
- インスピレーション
- 音楽的特徴
- ジャンル／サウンド
- アルバム内での役割
- 他作品と区別できる特徴

単なる形容詞の羅列ではなく、「何の曲なのか」「なぜこの音なのか」が短く伝わる文章にする。

### 2. Spotify Artist

対象アーティストの正しい Spotify Artist 情報を入力する。

不明な場合は推測せず、ユーザーまたは既存データへ確認する。

### 3. Marketing Elements / マーケティング要素

1つ以上選択必須。

選択肢：

- `advertising spends`
- `social media campaigns`
- `radio promo plans`
- `expected/confirmed press support`
- `visual content strategy`

実際に予定しているものだけ選ぶ。

例：

- SNSでリリース告知をする → `social media campaigns`
- Canvas、MV、Visualizer、ジャケット展開等を行う → `visual content strategy`
- 広告出稿しない → `advertising spends` は選ばない
- ラジオ施策がない → `radio promo plans` は選ばない
- プレス掲載の予定／見込みがない → `expected/confirmed press support` は選ばない

### 4. Past Awards / Milestones / 過去の受賞・マイルストーン

500文字以内。必須。

賞がなくてもよい。すでに達成した活動上の節目・実績を書く。

使用可能な材料の例：

- デビュー／過去作品のリリース
- アルバム／EP／シングルの発表
- ストリーミング実績
- チャート実績
- メディア／ラジオ掲載
- コラボレーション
- ライブ／ツアー実績
- その他、すでに実現した重要な活動

未来の予定を「Milestone」として書かない。

受賞歴がなければ、受賞歴があるように見せず、既存リリースなど事実だけで構成する。

## 任意項目

### 5. Upcoming Tour Dates / 今後のツアー日程

空欄可。予定がなければ無理に入力しない。

### 6. Social Media

各URL最大200文字。空欄可。

- Facebook
- Instagram
- Twitter / X
- TikTok

存在する公式アカウントのみ入力。

### 7. Attachments / 添付ファイル

任意。

#### Upload image

- `image/*`
- 1ファイル
- アーティスト宣材写真、公式キービジュアル等

#### Upload EPK

- PDF
- `.doc`
- `.docx`
- 1ファイル

サイズ上限は2026-08-12時点の確認では不明。

## EPKを作る場合の推奨内容

1〜2ページ程度でよい。

- Artist Name
- Artist Image / Key Visual
- Short Bio
- Musical Style / Concept
- Current Release
- Selected Track
- Past Releases / Milestones
- Streaming / Social Links
- Contact

Priority Pitch専用品ではなく、今後のリリースでも再利用できるアーティスト汎用EPKとして作る。

## AIがPitchを作る際に必要な情報

最低限、以下を確認する。

- アーティスト名
- リリース名
- リリース日
- 収録曲一覧
- Priority Pitchに出す代表曲
- その曲の音楽生成プロンプト／ジャンル／サウンド情報
- 曲またはアルバムのコンセプト
- Spotify Artist情報
- 実際に行うマーケティング施策
- 過去作品・実績・マイルストーン
- SNS（あれば）
- EPK／画像を添付するか

既存の `artists/`、`releases/`、会話、ユーザー提供資料などから確認できる事項は、ユーザーに再質問しない。

## 最終出力フォーマット

```text
Selected Track
[代表曲]

Release Summary — max 500 characters
[英語本文]

Spotify Artist
[情報]

Marketing Elements
[選択する項目]

Past Awards / Milestones — max 500 characters
[英語本文]

Optional fields
Tour Dates: [入力／空欄]
Facebook: [...]
Instagram: [...]
Twitter/X: [...]
TikTok: [...]
Image: [添付／なし]
EPK: [添付／なし]
```

## 最終チェック

- Release Summary が500文字以内か
- Milestones が500文字以内か
- 代表曲が1曲だけか
- Spotify Artist が正しいか
- Marketing Elements を最低1つ選んでいるか
- Marketing Elements は実際の施策だけか
- Milestones がすべて過去／達成済みの事実か
- 架空の受賞、プレス、数字、ツアー等が混入していないか
- 任意項目を埋めるためだけに情報を捏造していないか

## 2026-08-12 UI確認メモ

ブラウザ上の実画面確認では、以下が確認された。

- リリース概要：500文字、空欄でエラー
- Spotify Artist：空欄でエラー
- Marketing Elements：空欄でエラー
- Past Awards / Milestones：500文字、空欄でエラー
- Upcoming Tour Dates：空欄で進行可能
- Social Media：Facebook / Instagram / Twitter / TikTok、各URL200文字、空欄で進行可能
- Attachments：Upload image / Upload EPK、必須表示なし
