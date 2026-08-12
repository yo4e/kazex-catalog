# KAZEX Catalog 将来設計 / Roadmap

このリポジトリは、当面は Priority Pitch を安定して作成するための公開カタログとして運用し、将来的には KAZEX Records 公式サイトを自動更新するデータ基盤へ発展させる。

## 設計原則

### 1. 正本はひとつ

同じ情報を複数の場所へ手入力しない。

例：リリース日、UPC、トラック一覧などは `releases/<release-id>.yaml` を正本とし、Webサイト、Pitch、EPK、SNS告知等はそこから派生させる。

### 2. 人間とAIの両方が扱いやすい

当面は YAML を採用する。

理由：

- 人間がGitHub上で直接読める
- ChatGPT / Codex 等のAIが構造を把握しやすい
- Gitのdiffが読みやすい
- スクリプトから容易にパースできる
- 将来SQL等へ移行しやすい

YAMLは「最終的なデータベース技術」として固定するものではなく、現段階の canonical source / flat-file catalog として使う。

### 3. 公開情報だけを置く

`kazex-catalog` は公開リポジトリのまま運用することを基本とする。

非公開情報が必要になった場合は別の private リポジトリまたは秘密管理先へ分離する。

### 4. バイナリ原本は外部ストレージ

高解像度ジャケット、アーティスト写真、動画、EPK等の原本は Google Drive 等で管理する。

このリポジトリには、公開可能な参照URLやメタデータを保存する。

将来Web配信用画像については、GitHub、Cloudflare R2、CDN等へ軽量版を配置する構成を検討する。

---

# Phase 0 — 現在

## 目的

Priority Pitch をAIが迷わず作れる状態にする。

## 実装範囲

- アーティスト情報のYAML化
- リリース情報のYAML化
- Too Lost Priority Pitch仕様の保存
- Pitch作成に必要なフィールドの定義
- Google Drive上の画像／EPK等への参照情報
- AI共同運用ルール

## 完了条件

ユーザーが「○○のPriority Pitchを作って」と指示したとき、AIが本リポジトリを読み、既存情報を再質問せず、不足情報だけを確認して申請用データを作成できる。

---

# Phase 1 — データモデル安定化

実際の複数リリースを運用し、「本当に必要なフィールド」を確定する。

候補：

- artist_id
- release_id
- title
- artist_id
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

この段階では、最初から完璧なスキーマを作ろうとせず、実運用で不足したフィールドを追加する。

## Schema / Validation

データモデルが安定したら JSON Schema 等を導入し、YAMLを機械的に検証する。

例：

- 必須キーの欠落
- 日付形式
- UPC等の型
- 重複ID
- 存在しないartist_id参照
- Priority Pitchの文字数上限
- 不正なMarketing Elements

GitHub Actions でPull Request／push時に検証することを想定する。

---

# Phase 1.5 — 楽曲生成履歴・歌詞をカタログ化

KAZEX Catalog は、完成したリリースの情報だけでなく、将来的には「その楽曲がどのように作られたか」を追跡できる制作 provenance も保持する。

## Suno等の生成情報

AI生成／AI支援楽曲について、トラック単位で以下を保持できる設計を検討する。

候補：

- 生成サービス名（例：Suno）
- 公開可能な生成ページURL
- 使用モデル／バージョン（取得できる場合）
- 生成日時（必要な場合）
- style prompt / music prompt
- lyrics prompt / lyrics input
- instrumental指定など主要設定
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

キー名・粒度は実際の運用を見てから確定し、現段階では固定しない。

この情報を残す目的は、単なる制作メモではない。

- 後から同系統の曲を制作するときに参照できる
- AIがアーティスト／作品のサウンド傾向を理解できる
- 制作手法そのものを公開知として蓄積できる
- 将来の作品解説・制作ノート・研究用途へ再利用できる
- どの生成物が最終リリースへつながったかを追跡できる

本リポジトリは public のため、非公開プロンプト、個人情報、秘密URL等は保存しない。公開できない制作情報が必要になった場合は private 側へ分離する。

## 歌詞データ

ボーカル曲については、歌詞をカタログ正本に保持できるようにする。

候補：

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

将来的には以下へ展開できることを目指す。

- KAZEX公式サイトの歌詞表示
- EPK／作品資料への歌詞掲載
- 歌詞カード等の生成
- プチリリ等の外部歌詞サービスへの登録支援
- 登録済み／未登録の管理
- 必要に応じた同期歌詞・時間情報への拡張

外部歌詞サービスへの自動登録を実装する場合は、その時点の正式な登録方法、利用規約、API／画面仕様等を調査してから設計する。現段階では特定サービスの現在仕様にデータモデルを強く依存させない。

## トラック単位のデータを重視する

生成ページ、プロンプト、歌詞はリリース全体ではなく各トラックに紐づく情報である。

そのため、将来トラック情報が増えた場合は、1つの `release.yaml` 内にすべて抱える方式だけでなく、次のような分離も検討する。

```text
tracks/
  ghost-velocity.yaml
  slipstream-memorial.yaml
  ...

releases/
  ghost-velocity.yaml
```

リリースはトラックIDを参照し、トラック側が歌詞・生成履歴・ISRC・クレジット等を持つ。この構造は将来SQLへ移行するときにも自然に対応しやすい。

ただし、現段階ではファイル分割を先行実装しない。実際に歌詞・生成情報を数曲分登録して、1ファイル方式が不便になった時点で判断する。

---

# Phase 2 — KAZEX Records Webサイト連携

## 目標

リリースYAMLを追加・更新すると、KAZEX Records公式サイトが自動で更新される。

概念フロー：

```text
artists/*.yaml + releases/*.yaml
              ↓
          validation
              ↓
       website build data
              ↓
       KAZEX Records Web
```

Webサイト側は公開に必要なフィールドだけを読む。

想定する自動生成先：

- トップページの New Release
- Releases一覧
- 個別リリースページ
- Artist一覧
- 個別アーティストページ
- Discography
- News / Release announcement
- Lyrics / Track information（将来）
- RSS / Atom
- sitemap
- JSON-LD / structured data

## 公開制御

将来的には以下のような状態管理を検討する。

```yaml
status: upcoming
website:
  publish: true
  publish_at: 2026-08-20
  featured: true
```

ただしキー名は実運用で確定する。現段階で固定しない。

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

YAMLの意味構造を安定させた上で、以下のいずれかを選択する。

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

移行時点で、どちらが適切か再評価する。

---

# AI自動運用の将来像

最終的には、ChatGPT / Codex等へ例えば以下のように依頼できる状態を目指す。

> The Aerial Gravities の新作をカタログへ登録して。Too Lost用Priority Pitchを作成し、公開日に合わせてKAZEXサイトへ掲載できる状態にして。

AIは以下を行う。

1. 既存artistデータを読む
2. 新release／trackデータを追加する
3. Suno等の生成ページ、使用プロンプト、歌詞等の公開可能な制作情報を記録する
4. Schemaで検証する
5. Priority Pitchを生成する
6. 必要な画像／EPK参照を確認する
7. Web公開設定を追加する
8. 必要なら歌詞登録用データを生成する
9. CIを通す
10. サイト側の自動ビルドへつなぐ

人間は、事実確認、作品判断、公開可否など本質的な判断に集中する。

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
