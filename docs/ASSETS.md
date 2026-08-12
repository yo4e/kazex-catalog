# KAZEX Records 素材管理仕様

最終更新: 2026-08-12

KAZEX Records の高解像度ジャケット、アーティスト写真、ロゴ、EPK、動画等の原本は Google Drive で管理する。
`kazex-catalog` には、公開可能な素材そのものではなく、原則として素材フォルダ／個別素材への参照URLとメタデータを保存する。

## 素材庫ルート

KAZEX Records Assets:
https://drive.google.com/drive/folders/1AZM9PH-E-ilGq5CayJ6ZC78kCQQ7tMub

## 現在のフォルダ構造

```text
KAZEX Records Assets/
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
│   │
│   └── MRI_Music Resonance Imaging/
│       ├── Artist Photos/
│       ├── Logos/
│       ├── EPK/
│       └── Releases/
│           └── Unseen Dragon/
│               ├── Cover Art/
│               ├── Visuals/
│               └── Other Assets/
│
└── Label Assets/
    ├── Logos/
    ├── Brand Guide/
    └── Templates/
```

## 運用ルール

- アーティスト固有の素材は `Artists/<Artist Name>/` に置く。
- アー写は `Artist Photos/`、アーティストロゴは `Logos/`、EPK原本は `EPK/` に置く。
- 作品固有の素材は `Releases/<Release Title>/` に置く。
- ジャケット原本は `Cover Art/`、Canvas・Visualizer・MV等の映像／視覚素材は `Visuals/`、その他の公開素材は `Other Assets/` に置く。
- KAZEX Records 自体のロゴ、ブランドガイド、共通テンプレートは `Label Assets/` に置く。
- 高解像度画像、PSD、動画、音源等の重いバイナリ原本は GitHub に大量保存しない。
- GitHub側の artist / release YAML には、対応するDriveフォルダURLを登録する。
- 個別の「採用アー写」「正式ジャケット」「正式EPK」等が確定したら、フォルダURLとは別に個別素材URLをYAMLへ登録できる。
- `kazex-catalog` は public repository であるため、YAMLへ保存するDrive URLや素材情報は公開されても問題ないものに限定する。
- 非公開素材・個人情報・契約情報等を扱う必要が生じた場合は、public catalogとは別の非公開管理先を使用する。

## 将来

将来KAZEX Records公式サイトと連携するときは、Google DriveをWeb画像配信元として直接使用するとは限らない。
公開用の軽量画像をGitHub、Cloudflare R2、CDN等へ複製し、YAMLの公開用URLと原本参照URLを分離することを検討する。

例:

```yaml
cover:
  web_url: https://assets.example/.../cover.webp
  drive_url: https://drive.google.com/...
```

Google Driveは制作原本・保管庫、`kazex-catalog` は作品メタデータと参照情報の正本、Web配信用ストレージは公開配信層として分離できる設計を維持する。
