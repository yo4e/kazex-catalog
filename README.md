# KAZEX Catalog

KAZEX Records のアーティスト情報・リリース情報・公開素材・プロモーション情報を、AIと人間が共同で扱える形で蓄積する公開カタログです。

現在の主目的は、Too Lost の **Priority Pitch** を作成・更新しやすくすることです。将来的には、このリポジトリを KAZEX Records 公式サイトのデータソースとして利用し、リリース情報や公開素材の追加・更新からサイト更新までを自動化することを目指します。

## このリポジトリの役割

- アーティスト情報の正本を管理する
- リリース情報・トラック情報を管理する
- Too Lost Priority Pitch の作成に必要な情報を管理する
- Web掲載・Pitch・EPK等で利用する軽量な公開素材を管理する
- 高解像度原本等がある場合はGoogle Drive上の原本所在を記録する
- 将来の KAZEX Records 公式サイト自動更新に使える構造化データを育てる
- AI（ChatGPT、Codex など）が同じ情報を読み、継続して作業できる状態を保つ

## 公開リポジトリとしての原則

**このリポジトリは PUBLIC DATA ONLY です。**

ここにコミットする情報・素材は、世界に公開されても問題がないものに限ります。パスワード、API キー、個人の非公開連絡先、契約上の秘密、公開前に秘匿する必要がある企画情報などは置きません。

将来、非公開情報を扱う必要が生じた場合は、このリポジトリを非公開化するのではなく、原則として別の private リポジトリまたは適切な秘密管理先へ分離します。

## 現在の構成

```text
kazex-catalog/
├── README.md
├── AGENTS.md
├── artists/
│   └── <artist-id>.yaml
├── releases/
│   └── <release-id>.yaml
├── assets/
│   ├── README.md
│   ├── inbox/
│   ├── artists/
│   │   └── <artist-id>/...
│   └── releases/
│       └── <release-id>/...
├── docs/
│   ├── ASSETS.md
│   ├── PRIORITY_PITCH.md
│   ├── ROADMAP.md
│   └── WEBSITE_AUTOMATION_SPEC.md
└── templates/
    ├── artist.yaml
    └── release.yaml
```

当面は **YAML を構造化データの正本**として使用します。文章そのものが成果物になる長文資料は Markdown を使用します。

## 画像・EPKなどのファイル

公開アー写、公開ジャケット、ロゴ、コンセプト画像、Web掲載前提の軽量画像など、AIが日常的に整理・参照する公開素材は原則として `assets/` で管理します。

高解像度原本、PSD / AI等の編集原本、動画、音源、制作途中ファイル、バックアップなどの重い制作資産はGoogle Drive等の外部ストレージで管理します。

つまり、基本的な役割分担は次のとおりです。

- GitHub: 公開カタログの正本 + 軽量な公開素材
- Google Drive: 重い制作原本・バックアップ

未整理の公開素材は `assets/inbox/` へ投入し、AIが後から分類できます。正式採用状態をAIが推測で確定することはしません。

素材管理の詳細は `docs/ASSETS.md` を正本とします。

## データの考え方

現時点では小規模なため、YAML を Git で管理する flat-file 型のカタログとして運用します。ただし、YAML を最終的な技術選択として固定する意図はありません。

将来、サイト内検索、複雑な関連付け、大量データ、複数サービスからの同時更新などが必要になった場合は、SQLite / PostgreSQL 等の SQL データベースや、別のCMS・データストアへの移行／同期も視野に入れます。

重要なのは、**入力した公開情報を一度だけ正本として保持し、そこからサイト、Priority Pitch、EPK、SNS告知などへ派生させること**です。

## ドキュメント

- `docs/ASSETS.md` — GitHub公開素材とGoogle Drive原本の役割分担・Inbox運用
- `docs/PRIORITY_PITCH.md` — Too Lost Priority Pitch 作成仕様
- `docs/ROADMAP.md` — 将来設計と段階的な実装方針
- `docs/WEBSITE_AUTOMATION_SPEC.md` — KAZEX Records公式サイト自動更新の将来実装仕様
- `AGENTS.md` — ChatGPT / Codex などAIが作業する際のルール

## ステータス

初期運用段階です。まずは実際のリリースと公開素材を登録し、Priority Pitch と素材整理が安定して回るところまで運用を固めます。その知見をもとに、Schema validation、Webサイト連携、必要に応じたデータベース化を段階的に進めます。
