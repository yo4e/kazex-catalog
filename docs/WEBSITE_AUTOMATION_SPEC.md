# KAZEX Records 公式サイト自動更新 仕様書（将来実装用）

この文書は、`kazex-catalog` をKAZEX Records公式サイトのデータソースとして利用する将来実装のための仕様書です。

現時点ではサイト側の技術構成・リポジトリ・デプロイ方式を前提にせず、実装時にCodex等が既存サイトを調査した上で適切な方式へ落とし込めるよう、要求事項と境界だけを定義します。

## 目的

アーティストやリリース情報を `kazex-catalog` に一度登録すれば、その情報と公開素材を正本としてKAZEX Records公式サイトへ反映できるようにする。

人間がWeb管理画面へ同じ情報を二重入力する運用をなくす。

## 基本要件

1. `artists/*.yaml` と `releases/*.yaml` を読み込めること
2. `assets/` の公開素材を参照またはサイト側へコピーできること
3. YAMLをサイトへ反映する前にvalidationできること
4. 公開対象だけをサイトへ出力できること
5. 内部運用用フィールドが将来追加されても、サイトへ無条件に露出しないこと
6. 既存サイトのデザイン・URL・SEOを不必要に壊さないこと
7. リリース情報や公開素材の修正がサイトへ再反映されること
8. AIが安全にデータ追加できること

## 想定する公開情報

### Artist

- id
- name
- short / long description
- concept
- genres
- streaming platform links
- social links
- public asset references

### Release

- id
- title
- artist_id
- release_type
- release_date
- cover image
- streaming links
- tracks
- credits
- public descriptions
- website publication settings

`promotion.priority_pitch` 等は、原則としてWebサイトへ自動表示しない。

## 公開制御

将来的に `website` セクションで公開可否を制御する。

暫定例：

```yaml
website:
  publish: true
  publish_at: 2026-08-20
  featured: true
```

実装時には、実際のサイト要件に合わせてSchemaを確定する。

### 必須の安全策

- `publish: false` のデータは公開しない
- `publish_at` が未来の場合は、その時刻以前に公開しない方式を検討する
- YAML内の全キーをテンプレートへ丸ごと渡して表示しない
- 表示許可するフィールドを明示的に選ぶ

## 生成・更新対象の候補

最低限：

- Releases一覧
- 個別リリースページ
- Artists一覧
- 個別アーティストページ

次段階：

- トップページ New Release
- Featured release
- Discography
- News / release announcement
- RSS / Atom
- sitemap
- JSON-LD
- 公開JSON feed / API

## データ整合性

サイト連携の前にSchema validationを導入する。

現在は `scripts/validate_catalog.py` と `.github/workflows/catalog-validation.yml` により、基本的なYAML整合性を検査する。将来必要に応じてJSON Schema等へ拡張する。

検査候補：

- `id` の一意性
- `artist_id` が存在すること
- 日付形式
- URL形式
- `tracks` の構造
- `release_type` の許容値
- `status` の許容値
- GitHub素材参照先の存在
- Priority Pitch文字数制限
- website公開設定の整合性

## 実装方式の選択

Codexは実装開始時に、まずKAZEX Records公式サイトの現状を調査すること。

確認事項：

- サイトのリポジトリ
- フレームワーク / CMS
- ホスティング先
- ビルド方式
- デプロイ方式
- 現在のコンテンツ管理方法
- URL構造
- 画像配信方式
- GitHub Actions等の既存CI/CD

その上で、最も小さく安全な方式を選ぶ。

候補：

### パターンA：ビルド時にkazex-catalogを取得

静的サイト等に向く。

```text
kazex-catalog
      ↓ fetch
website build
      ↓
deploy
```

YAMLと `assets/` を同じコミットから取得すれば、メタデータと画像の対応を再現しやすい。

### パターンB：公開用JSONを生成

サイト実装とカタログを疎結合にしたい場合。

```text
YAML
 ↓ validate
public JSON
 ↓
website
```

画像は `github_path` を基準にサイトビルド時にコピーするか、別の公開URLへ解決する。

### パターンC：SQL等へimport

将来、動的検索や複数サービスからの更新が必要になった場合。

```text
YAML → import → SQLite/PostgreSQL → Website/API
```

## SQL導入について

SQLは現時点の必須要件ではない。

ただし、以下が必要になれば再評価する。

- 多対多関係が増える
- 複雑な検索が増える
- データ件数が大幅に増える
- 外部APIから頻繁に更新する
- 複数主体が同時に書き込む
- Git/YAMLを正本とすることが不便になる

SQLへ移行するときも、既存YAMLから再現可能なmigration/importを用意し、意味構造を失わないこと。

## 画像

公開アー写、公開ジャケット、ロゴ、コンセプト画像、Web掲載前提の軽量画像は、原則として `kazex-catalog/assets/` を公開素材の正本とする。

高解像度原本、PSD / AI、動画、音源、制作途中ファイル等はGoogle Drive等の原本倉庫に残す。

YAMLでは役割を分離する。

- `github_path` — `kazex-catalog` 内の公開素材
- `web_url` — サイト上の最終公開URL。実装未決定なら `null`
- `drive_url` — 制作原本または高解像度原本への参照

サイト自動更新を実装するときは、次の方式から既存サイトに適したものを選ぶ。

- GitHub上の公開画像をそのまま利用
- サイトビルド時に `kazex-catalog` からコピー
- GitHubを正本としてCloudflare R2 / CDNへ同期
- 既存サイトの画像管理機能を利用

原本、カタログ上の公開素材、Web配信用URLは分離してよい。

## Codex向け実装手順

1. `README.md`、`AGENTS.md`、`docs/ROADMAP.md`、`docs/ASSETS.md`、本仕様書を読む
2. KAZEX公式サイトの既存実装を調査する
3. 既存サイトに合わせた具体設計をIssueまたは設計文書へ提示する
4. 最小実装を選ぶ
5. 既存validationを確認し、不足があればSchema等を追加する
6. 1アーティスト・1リリースで試験する
7. 公開素材の解決方法を試験する
8. 既存ページとの差分を確認する
9. 自動デプロイを接続する
10. README / docsを実装内容に合わせて更新する

## 受け入れ条件

最低限、以下を満たしたらPhase 2の初期実装完了とする。

- 新しいrelease YAMLを追加すると、手作業で同じ内容をサイトへ再入力せずページを生成できる
- release YAMLを修正するとサイト側にも反映できる
- artistとの関連付けが `artist_id` で機械的に行われる
- `github_path` で指定した公開素材をサイトへ反映できる
- 非公開設定のリリースは公開されない
- validation失敗時にデプロイが止まる
- 既存サイトの主要ページやURLを壊さない
- 実装方法がドキュメント化されている

## 非目標

初期実装では以下を無理に行わない。

- 独自CMS管理画面の開発
- 大規模SQLシステムの構築
- すべてのSNSへの自動投稿
- Too Lostへのブラウザ自動入力
- 高解像度制作資産のGit管理

まず「カタログへ一度入力すればWebサイトへ出る」を成立させる。
