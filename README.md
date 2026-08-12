# KAZEX Catalog

KAZEX Records のアーティスト情報・リリース情報・公開素材・プロモーション情報を、AIと人間が共同で扱える形で蓄積する公開カタログです。

現在の主目的は、制作中の会話から作品情報を随時蓄積し、Too Lost の **Priority Pitch** や Spotify for Artists 等の外部サービス操作へ再利用できる状態を作ることです。外部サービス操作は、カタログ正本から生成した安全なbrowser task packetとしてChatGPT等のブラウザ操作担当へ渡せるようにします。

将来的には、このリポジトリを KAZEX Records 公式サイトのデータソースとして利用し、リリース情報や公開素材の追加・更新からサイト更新までを自動化することを目指します。

## このリポジトリの役割

- 制作会話で決まったartist / release / track情報を随時保存する
- アーティスト情報の正本を管理する
- リリース情報・トラック情報を管理する
- Too Lost Priority Pitch の作成に必要な情報を管理する
- 外部サービス操作用のbrowser task packetを生成する
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
│   ├── BROWSER_TASKS.md
│   ├── INTAKE_WORKFLOW.md
│   ├── PRIORITY_PITCH.md
│   ├── ROADMAP.md
│   └── WEBSITE_AUTOMATION_SPEC.md
├── scripts/
│   ├── check_readiness.py
│   ├── render_browser_task.py
│   └── validate_catalog.py
└── templates/
    ├── artist.yaml
    └── release.yaml
```

当面は **YAML を構造化データの正本**として使用します。文章そのものが成果物になる長文資料は Markdown を使用します。

## 制作中の会話から登録する

普段の制作チャットで、例えば次のように指示できます。

- 「それカタログに入れといて」
- 「この曲もアルバムに追加しといて」
- 「このプロンプト残しといて」

AIは会話と既存catalogから対象を特定し、分かっている公開情報を先に保存します。release date、UPC、ISRC、Spotify URL等がまだ存在しない場合でも、既知情報の保存は止めません。

制作中は必要以上に質問せず、保存先や確定状態が曖昧な場合だけ確認します。ユーザーが「ピッチ準備」「Spotify登録できる状態にして」等と指示した段階で、外部サービスに必要な不足だけをまとめて確認します。

詳細は `docs/INTAKE_WORKFLOW.md` を参照してください。

## Readiness check

外部登録に必要な不足を機械的に確認できます。

```bash
python scripts/check_readiness.py release unseen-dragon
python scripts/check_readiness.py artist mri-music-resonance-imaging
```

`CAPTURE`、`TOO LOST PRIORITY PITCH`、`SPOTIFY FOR ARTISTS CLAIM / PROFILE` 等について、`READY` または `BLOCKED` と不足項目を表示します。

## Browser Task Packets

外部サービスへ同じ事実を手入力し直す代わりに、catalogからブラウザ操作担当AIへ渡す自己完結型の指示文を生成できます。

Too Lost Priority Pitch:

```bash
python scripts/render_browser_task.py priority-pitch unseen-dragon
```

Spotify for Artists:

```bash
python scripts/render_browser_task.py spotify-profile mri-music-resonance-imaging
```

必須値が欠けている場合は、パケット自体がSubmit禁止や停止条件を明示します。詳細は `docs/BROWSER_TASKS.md` を参照してください。

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

重要なのは、**入力した公開情報を一度だけ正本として保持し、そこからサイト、Priority Pitch、Spotifyプロフィール作業、EPK、SNS告知などへ派生させること**です。

## ドキュメント

- `docs/ASSETS.md` — GitHub公開素材とGoogle Drive原本の役割分担・Inbox運用
- `docs/BROWSER_TASKS.md` — 外部サービスをブラウザ操作するための作業パケット仕様
- `docs/INTAKE_WORKFLOW.md` — 制作会話から随時catalogへ登録し、外部登録準備へつなぐ運用
- `docs/PRIORITY_PITCH.md` — Too Lost Priority Pitch 作成仕様
- `docs/ROADMAP.md` — 将来設計と段階的な実装方針
- `docs/WEBSITE_AUTOMATION_SPEC.md` — KAZEX Records公式サイト自動更新の将来実装仕様
- `AGENTS.md` — ChatGPT / Codex などAIが作業する際のルール

## Credits

- System Designer: **月野テンプレクス (Tsukino Templex)**

## ステータス

初期運用段階です。まずは実際の制作会話からrelease / track / promptを蓄積し、Priority Pitch、Spotify for Artists作業、素材整理が安定して回るところまで運用を固めます。その知見をもとに、Schema validation、Webサイト連携、必要に応じたデータベース化を段階的に進めます。
