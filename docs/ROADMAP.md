# KAZEX Catalog 将来設計 / Roadmap

このリポジトリは、当面は Priority Pitch を安定して作成するための公開カタログとして運用し、将来的には KAZEX Records 公式サイトやEPK等を同じ正本から自動生成するデータ基盤へ発展させる。

## 設計原則

### 1. 正本はひとつ

同じ情報を複数の場所へ手入力しない。

例：リリース日、UPC、トラック一覧などは `releases/<release-id>.yaml` を正本とし、Webサイト、Pitch、EPK、SNS告知等はそこから派生させる。

### 2. 人間とAIの両方が扱いやすい

当面は YAML を canonical source / flat-file catalog として使う。

- 人間がGitHub上で直接読める
- ChatGPT / Codex 等のAIが構造を把握しやすい
- Gitのdiffが読みやすい
- スクリプトから容易にパースできる
- 将来SQL等へ移行しやすい

YAMLを最終的なデータベース技術として固定する意図はない。

### 3. PUBLIC DATA ONLY

`kazex-catalog` は公開リポジトリのまま運用する。

非公開情報が必要になった場合は、別の private リポジトリまたは秘密管理先へ分離する。

### 4. GitHubは公開素材、Driveは制作原本

AIが日常的に扱う軽量な公開素材は `assets/` に置く。

- 公開アー写
- 公開ジャケット
- ロゴ
- コンセプト画像
- Web掲載前提の軽量画像
- 必要に応じて軽量PDF / EPK

Google Drive等には重い制作原本を置く。

- 高解像度原本
- PSD / AI等の編集原本
- 動画
- 音源
- 制作途中ファイル
- バックアップ

YAMLでは `github_path`、`web_url`、`drive_url` を分離し、公開素材・最終配信URL・制作原本を混同しない。

詳細は `docs/ASSETS.md` を正本とする。

---

# Phase 0 — 現在

## 目的

Priority Pitch と公開素材整理をAIが迷わず行える状態にする。

## 現在の実装

- アーティスト情報のYAML化
- リリース情報のYAML化
- Too Lost Priority Pitch仕様の保存
- Pitch作成に必要なフィールドの定義
- GitHub `assets/` / `assets/inbox/` の導入
- Google Driveを制作原本倉庫として役割分離
- `github_path` / `web_url` / `drive_url` の分離
- AI共同運用ルール
- `scripts/validate_catalog.py` による基本validation
- GitHub ActionsによるPR / main push時のvalidation

## 完了条件

ユーザーが「○○のPriority Pitchを作って」「この画像を整理して」と指示したとき、AIが本リポジトリを読み、既存情報を再質問せず、不足情報だけを確認して作業できる。

公開素材については、次の流れが成立すれば第一段階完了とする。

```text
assets/inbox/
    ↓ AIが内容確認
リネーム・分類
    ↓
assets/artists/ または assets/releases/
    ↓
必要ならYAML参照更新
```

正式アー写・正式ジャケット等の採用判断はAIが推測で確定しない。

---

# Phase 1 — データモデル安定化

実際の複数リリースを運用し、「本当に必要なフィールド」を確定する。

候補：

- artist_id
- release_id
- title
- release_type
- release_date
- status
- UPC / EAN
- tracks / ISRC
- genres
- credits
- descriptions
- streaming links
- cover / asset references
- promotion / priority_pitch
- website publication settings
- generation provenance（生成元・生成ページ・使用プロンプト等）
- lyrics（歌詞本文・言語・歌詞登録状況等）

最初から完璧なスキーマを作ろうとせず、実運用で不足したフィールドを追加する。

## Schema / Validation

2026-08-12時点で、Python validator + GitHub Actionsによる第一段階の検証を導入済み。

現在の検査項目：

- YAMLとして読み込めること
- IDが小文字kebab-caseであること
- ファイル名とIDが一致すること
- artist_id参照先が存在すること
- 日付形式
- UPC / ISRCの型
- Priority Pitch selected_trackが実在トラックと一致すること
- Release Summary / Past Awards & Milestonesの500文字上限
- `github_path` を登録した場合、そのファイルが存在すること
- 素材候補のstatusが許容値であること

今後、データモデルが安定したら JSON Schema 等を追加することを検討する。

追加候補：

- 必須キー
- URL形式
- release_type / status の許容値
- 不正なMarketing Elements
- website公開設定
- UPC / ISRC形式そのもの
- track単位データとの参照整合性

---

# Phase 1.5 — 楽曲生成履歴・歌詞をカタログ化

KAZEX Catalog は、完成したリリース情報だけでなく、将来的には「その楽曲がどのように作られたか」を追跡できる公開可能な制作 provenance も保持する。

## Suno等の生成情報

AI生成／AI支援楽曲について、トラック単位で以下を保持できる設計を検討する。

- 生成サービス名（例：Suno）
- 公開可能な生成ページURL
- 使用モデル／バージョン
- 生成日時
- style prompt / music prompt
- lyrics prompt / lyrics input
- instrumental指定等の主要設定
- 元生成物と最終リリース版の関係
- 備考

概念例：

```yaml
generation:
  provider: suno
  source_url: null
  model: null
  prompt: >
    ...
  lyrics_input: null
  generated_at: null
```

キー名・粒度は実際の運用を見てから確定する。

目的：

- 後から同系統の曲を制作するときに参照する
- AIがアーティスト／作品のサウンド傾向を理解する
- 制作手法そのものを公開知として蓄積する
- 作品解説・制作ノート・研究用途へ再利用する
- どの生成物が最終リリースへつながったか追跡する

本リポジトリはpublicのため、非公開プロンプト、個人情報、秘密URL等は保存しない。

## 歌詞データ

ボーカル曲については、歌詞をカタログ正本に保持できるようにする。

概念例：

```yaml
lyrics:
  language: ja
  text: |
    ...
  instrumental: false
  registration:
    petitlyrics:
      status: null
      url: null
      external_id: null
```

将来的な利用先：

- KAZEX公式サイトの歌詞表示
- EPK／作品資料
- 歌詞カード
- プチリリ等の外部歌詞サービスへの登録支援
- 登録済み／未登録管理
- 必要に応じた同期歌詞・時間情報

外部歌詞サービスへの自動登録を実装する場合は、その時点の正式な登録方法、利用規約、API／画面仕様を調査してから設計する。

## トラック単位ファイルの検討

生成ページ、プロンプト、歌詞は各トラックに紐づく。

情報量が増えたら、次のような分離を検討する。

```text
tracks/
  ghost-velocity.yaml
  slipstream-memorial.yaml
  ...

releases/
  ghost-velocity.yaml
```

リリースはトラックIDを参照し、トラック側が歌詞・生成履歴・ISRC・クレジット等を持つ。

現段階ではファイル分割を先行実装しない。実際に数曲分を登録し、1ファイル方式が不便になった時点で判断する。

---

# Phase 2 — KAZEX Records Webサイト連携

## 目標

リリースYAMLや公開素材を追加・更新すると、KAZEX Records公式サイトへ二重入力なしで反映できる。

概念フロー：

```text
artists/*.yaml + releases/*.yaml + assets/
                    ↓
                validation
                    ↓
             website build data
                    ↓
             KAZEX Records Web
```

Webサイト側は公開に必要なフィールドだけを読む。

想定する自動生成先：

- トップページ New Release
- Releases一覧
- 個別リリースページ
- Artists一覧
- 個別アーティストページ
- Discography
- News / Release announcement
- Lyrics / Track information（将来）
- RSS / Atom
- sitemap
- JSON-LD / structured data

## 画像配信方式

`assets/` を公開素材の正本とし、サイト実装時に以下から選択する。

1. GitHub上の素材を直接参照
2. サイトビルド時にコピー
3. GitHubからCloudflare R2 / CDN等へ同期
4. 既存サイトの画像管理機能へ取り込む

判断基準：

- 実装の簡単さ
- 表示速度
- コスト
- AIの扱いやすさ
- キャッシュ / CDN
- 将来の規模

既存サイトのスタックを調査してから決める。

## 公開制御

暫定構造：

```yaml
status: upcoming
website:
  publish: true
  publish_at: 2026-08-20
  featured: true
```

実装時に実運用へ合わせて確定する。

詳細は `docs/WEBSITE_AUTOMATION_SPEC.md` を参照する。

---

# Phase 3 — 派生物の自動生成

同じ正本から以下を生成する。

- Priority Pitch申請文
- EPK
- プレスリリース
- SNS告知文
- 配信用メタデータ確認表
- アーティスト／リリース一覧
- 歌詞カード／歌詞掲載データ
- 外部歌詞サービス登録用データ
- 制作ノート／生成プロンプト一覧
- 公開API / JSON feed

生成文そのものを正本として保存するか、元データから毎回生成するかは用途ごとに判断する。

---

# Phase 4 — SQL / データベース導入の判断

現段階では SQL を導入しない。

以下の条件が出てきたら SQLite / PostgreSQL 等を検討する。

- リリースやトラック数が大幅に増え、flat-file検索が不便になる
- アーティスト、楽曲、作家、リリース等の多対多関係が複雑化する
- トラック単位の歌詞、生成履歴、クレジット、外部サービス登録状態などの関係管理が複雑化する
- Webサイトから動的で複雑な検索が必要になる
- 複数サービス／複数ユーザーが同時に書き込む
- API経由の頻繁な更新が必要になる
- Gitファイルを正本にすることが運用上のボトルネックになる

## 移行方針

### A. YAMLを正本のまま維持

```text
YAML → build/import → SQLite/PostgreSQL → Website/API
```

Git履歴を正本として残したい場合に向く。

### B. SQLを正本へ移行

```text
Admin / AI / API → SQL Database → Website/API
                         ↓
                  export / archive
```

複数箇所から頻繁に更新する段階に向く。

移行時点で再評価する。

---

# AI自動運用の将来像

最終的には、ChatGPT / Codex等へ例えば以下のように依頼できる状態を目指す。

> The Aerial Gravities の新作をカタログへ登録して。Too Lost用Priority Pitchを作成し、公開日に合わせてKAZEXサイトへ掲載できる状態にして。

AIは以下を行う。

1. 既存artistデータを読む
2. 新release／trackデータを追加する
3. `assets/inbox/` の公開素材を確認・分類する
4. Suno等の生成ページ、使用プロンプト、歌詞等の公開可能な制作情報を記録する
5. validationを通す
6. Priority Pitchを生成する
7. 必要な画像／EPK参照を整える
8. Web公開設定を追加する
9. 必要なら歌詞登録用データを生成する
10. CIを通す
11. サイト側の自動ビルドへつなぐ

人間は、事実確認、作品判断、正式採用、公開可否など本質的な判断に集中する。

---

# 当面やらないこと

- 最初からSQLデータベースを構築する
- 使うか分からない大量のフィールドを先回りして定義する
- Suno／歌詞用の詳細スキーマを実運用前に固定する
- 外部歌詞サービスへの自動登録を先回りして実装する
- 高解像度画像や動画をGit履歴へ大量投入する
- 非公開運用情報をpublic repoへ混在させる
- Priority PitchとWebサイト用データを別々に二重管理する

まず実際のKAZEX作品を数件運用し、データ構造を育てる。
