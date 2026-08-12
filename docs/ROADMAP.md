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
- 公開API / JSON feed

生成文そのものを正本として保存するか、元データから毎回生成するかは用途ごとに判断する。

---

# Phase 4 — SQL / データベース導入の判断

現段階では SQL を導入しない。

以下の条件が出てきたら SQLite / PostgreSQL 等を検討する。

- リリースやトラック数が大幅に増え、flat-file検索が不便になる
- アーティスト、楽曲、作家、リリース等の多対多関係が複雑化する
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
2. 新releaseデータを追加する
3. Schemaで検証する
4. Priority Pitchを生成する
5. 必要な画像／EPK参照を確認する
6. Web公開設定を追加する
7. CIを通す
8. サイト側の自動ビルドへつなぐ

人間は、事実確認、作品判断、公開可否など本質的な判断に集中する。

---

# 当面やらないこと

- 最初からSQLデータベースを構築する
- 使うか分からない大量のフィールドを先回りして定義する
- 高解像度画像や動画をGit履歴へ大量投入する
- 非公開運用情報をpublic repoへ混在させる
- Priority PitchとWebサイト用データを別々に二重管理する

まず実際のKAZEX作品を数件運用し、データ構造を育てる。
