# Public Assets

`assets/` は、KAZEX Records の公開カタログから参照する軽量な公開素材を置く場所です。

## 原則

- PUBLIC DATA ONLY。
- Web掲載・Priority Pitch・EPK等でAIが日常的に扱う公開素材を置く。
- 高解像度原本、PSD / AI、動画、音源、制作途中ファイル、バックアップは原則としてGoogle Drive側へ置く。
- GitHub上の素材は公開配信用・参照用のコピーであり、制作原本とは分離してよい。
- 正式採用が未確定の画像は、YAML上で `candidate` と明示する。

## 構造

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

Gitは空ディレクトリを保持しないため、各サブディレクトリは最初の素材が入った時点で作成してよい。未整理素材は `assets/inbox/` へ投入する。

詳細は `docs/ASSETS.md` を参照してください。
