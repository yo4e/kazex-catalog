# KAZEX Records 素材管理仕様

最終更新: 2026-08-12

KAZEX Records の素材は、**GitHubを公開素材の正本、Google Driveを重い制作原本の倉庫**として役割分担する。

`kazex-catalog` は PUBLIC DATA ONLY を維持する。GitHubに置く素材も、YAMLへ記録するDrive URLも、世界に公開されて問題ないものに限る。

## 役割分担

### GitHub (`kazex-catalog`)

AIが日常的に整理・参照し、Web、Priority Pitch、EPK等へ再利用する公開素材を置く。

- 公開アー写
- 公開ジャケット
- ロゴ
- コンセプト画像・設定画
- Web掲載前提の軽量画像
- 必要に応じて軽量PDF / EPK

### Google Drive

制作・保管用の重い原本を置く。

- 高解像度原本
- PSD / AI 等の編集用制作データ
- 動画原本
- 音源
- 大容量 EPK 原本
- 制作途中データ
- バックアップ

GitHub上の公開素材は、Drive原本から派生したWeb用コピーでもよい。原本と公開配信用データは同一ファイルである必要はない。

## GitHub の公開素材構造

```text
assets/
├── inbox/
├── artists/
│   ├── the-aerial-gravities/
│   │   ├── artist-photos/
│   │   ├── logos/
│   │   └── concept-art/
│   └── mri-music-resonance-imaging/
│       ├── artist-photos/
│       ├── logos/
│       └── concept-art/
└── releases/
    ├── ghost-velocity/
    │   ├── cover/
    │   ├── visuals/
    │   └── other-assets/
    └── unseen-dragon/
        ├── cover/
        ├── visuals/
        └── other-assets/
```

Gitは空ディレクトリを保持しないため、各サブディレクトリは最初の素材が入った時点で作成してよい。

## GitHub Asset Inbox 運用

`assets/inbox/` は、人間が公開素材を素早く投入するための未整理置き場とする。

山田は整理・命名を気にせず、例えば `MRIのジャケ.png`、`Aerialアー写候補.jpg` のような暫定名で素材を置いてよい。

ChatGPT / Codex 等のAIが素材整理を行う際は、原則として次の順に処理する。

1. ファイル内容を実際に確認する。
2. ファイル名、画像内容、既存の artist / release YAML、会話文脈から所属を判断する。
3. artist / release / asset type が十分に判定できる場合だけ、一貫した名前へリネームする。
4. `assets/artists/<artist-id>/...` または `assets/releases/<release-id>/...` の適切な場所へ移動する。
5. 正式採用素材としてカタログから参照すべき場合は、対応するYAMLの `github_path` / `web_url` 等を更新する。
6. 判定に十分な根拠がない場合は推測で分類せず、山田に必要な点だけ確認する。
7. 確認待ちの素材は `assets/inbox/` に残す。

### 採用状態

AIは、明示されていない素材を正式採用へ勝手に昇格させない。

- `candidate` — 候補。公開リポジトリに置いてよいが正式採用未確定。
- `selected` — 山田が正式採用した素材。
- `archived` — 過去素材。削除せず参照を残す必要がある場合。

YAMLで候補素材を列挙する場合は、各素材に `status` を持たせる。

### リネーム方針

厳密な命名規則は実運用を見ながら育てる。当面は以下を優先する。

- 人間が見て内容を識別できる。
- 必要に応じてアーティスト名／作品名／用途が分かる。
- `final`, `master`, `web`, `alt`, `01` 等は意味が明確な場合だけ使う。
- 元ファイル名に含まれる有用な情報を不用意に失わない。
- 「最新版」が複数発生する曖昧な名前を避ける。
- 内容を確認せず、名前だけを根拠に破壊的な上書き・削除をしない。

Inboxは一時置き場であり、長期保管場所にはしない。ただし、AIが分類できないものを人間の確認前に追い出すこともしない。

## Google Drive 原本倉庫

KAZEX Records Assets:
https://drive.google.com/drive/folders/1AZM9PH-E-ilGq5CayJ6ZC78kCQQ7tMub

旧Asset Inbox:
https://drive.google.com/drive/folders/1Hx-1Ky2kuzKnjzgD-RcSCZE53HkGrxHg

既存のDrive構造は原本保管先として利用できる。

```text
KAZEX Records Assets/
├── Inbox/
├── Artists/
│   ├── The Aerial Gravities/
│   │   ├── Artist Photos/
│   │   ├── Logos/
│   │   ├── EPK/
│   │   └── Releases/
│   │       └── Ghost Velocity/
│   │           ├── Cover Art/
│   │           ├── Visuals/
│   │           └── Other Assets/
│   └── MRI_Music Resonance Imaging/
│       ├── Artist Photos/
│       ├── Logos/
│       ├── EPK/
│       └── Releases/
│           └── Unseen Dragon/
│               ├── Cover Art/
│               ├── Visuals/
│               └── Other Assets/
└── Label Assets/
    ├── Logos/
    ├── Brand Guide/
    └── Templates/
```

Drive上の `Inbox/` は今後、制作原本を素早く投げ込む用途では利用してよいが、AIが日常的に整理する公開素材Inboxの正本は `assets/inbox/` とする。

## YAML の素材参照

GitHub上の公開素材、将来のWeb配信用URL、Drive原本URLを混同しない。

Artist例:

```yaml
assets:
  github_asset_dir: assets/artists/example-artist/
  drive_folder_url: https://drive.google.com/...
  artist_image:
    github_path: assets/artists/example-artist/artist-photos/example.jpg
    web_url: null
    drive_url: https://drive.google.com/...
```

Release例:

```yaml
cover:
  github_path: assets/releases/example-release/cover/example-cover.png
  web_url: null
  drive_url: https://drive.google.com/...
```

意味は次のとおり。

- `github_path` — このリポジトリ内の公開素材パス
- `web_url` — KAZEX公式サイト等で利用する最終公開URL。未決定なら `null`
- `drive_url` — 制作原本または高解像度原本への公開可能な参照URL
- `github_asset_dir` — artist / release のGitHub素材ルート
- `drive_folder_url` — artist / release のDrive原本ルート

同じ素材について、GitHubパスとDrive原本URLを両方保持してよい。用途が異なるため二重管理とはみなさない。

## Webサイト画像配信

現時点では、`github_path` を公開素材の正本として保持し、`web_url` はサイト実装時に決定する。

候補は以下。

1. GitHub上の画像をそのまま利用
2. サイトビルド時に `kazex-catalog` からコピー
3. GitHubを正本としてCloudflare R2 / CDNへ同期
4. 将来の専用アセット配信層へ移行

判断基準は、実装の簡単さ、表示速度、コスト、AIの扱いやすさ、キャッシュ/CDN、将来規模とする。

KAZEX Records公式サイトの実装に着手する時点で、既存サイトのスタックを確認して決定する。
