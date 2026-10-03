# KazeX Records Instagram音楽宣伝の調査

調査日: 2026-10-03

運用手順: [Instagram宣伝ワークフロー](INSTAGRAM_PROMOTION_WORKFLOW.md)

## 結論

短い映像と詩的な一文は作品の雰囲気を伝えられる。一方、それだけでSpotify流入が生まれたとは判断できない。次回は作品らしい冒頭を残し、正式artist名と曲名、実在する聴取導線への短い案内を追加する。公開後は映像への反応とSpotifyの聴取を別々に記録する。

## KazeXカタログの確認結果

調査時の公開カタログには、Unseen Dragonの15曲とGhost Velocityの11曲が登録されていた。両リリースのstatusはupcoming、release-levelのSpotify URLはnull。記載発売日はそれぞれ2026-08-22と2026-08-24で、調査日より前である。これだけで現在の未配信・配信済みを断定できず、選曲前に配信ページでの照合が必要。

MRIの正式名は「MRI_Music Resonance Imaging」。公開コンセプトは機械音、金属音、静寂、共鳴で、industrial techno、electronic、experimentalに位置付けられている。captionでは「MRI」だけの略称より正式名を併記する方が、曲を探す手掛かりが明確になる。

選曲根拠として利用できるのは、この作品情報、実際の試聴、原本の準備状況、既に公開した内容や取得できる反応である。カタログには曲別のSpotify反応データがなく、26曲の中で最も流入が期待できる曲を統計的に選べる状態ではない。

出典: [MRI artist情報](https://github.com/yo4e/kazex-catalog/blob/main/artists/mri-music-resonance-imaging.yaml)、[Unseen Dragon](https://github.com/yo4e/kazex-catalog/blob/main/releases/unseen-dragon.yaml)、[Ghost Velocity](https://github.com/yo4e/kazex-catalog/blob/main/releases/ghost-velocity.yaml)

## アーティスト本人の公開資料にある投稿例

以下は成功率のランキングではなく、文章と導線の使い方の比較である。Instagram上の動画再生、画面内字幕、Stories本体、投稿時のプロフィールリンク先は直接確認できていない。確認できたcaptionと資料の範囲を分けて記載する。

### Van Horton

本人サイトのInstagramフィードで、synthwave・electronic系の楽曲告知を確認した。短い雰囲気型の予告と、音を出して聴くよう促し、曲名、プロフィールリンク、SoundCloudやBandcampという配信先を示す投稿を使い分けている。別のcaptionでは、紹介記事はStory、曲はプロフィール、と目的別に行き先を分けている。

「I’m All Alone」の告知には2026-09-18の発売日と事前保存への案内がある。これは発売日の記載であり、投稿日時の確認ではない。個別投稿のpermalinkと反応数は未確認。

KazeXで試すこと: 短い世界観重視の文章を残しつつ、正式な曲名と聴く場所を省かない。全部の投稿を長い説明文にする必要はない。

出典: [Van Horton本人サイトのInstagram埋め込み](https://www.vanhortonmusic.com/)

### [dunkelbunt] のVelavan

本人サイトに埋め込まれた2019-02-23 11:30 PSTのInstagram投稿で、冒頭に曲名、公開済みであること、プロフィールリンクへの案内がある。続いてレゲエ、インド、中国の音を結ぶ作品世界を説明し、配信先を示している。歴史的なcaption構成の例であり、現在の推薦アルゴリズムを実証する例ではない。

KazeXで試すこと: 情景を伝える一文と、聴く先を伝える一文は同居できる。詩的な説明があること自体を流入の弱さの原因にしない。

出典: [本人サイトのStudio-Video紹介](https://www.dunkelbunt.org/category/news/new-track/)、[埋め込みに記載された元Instagram投稿](https://www.instagram.com/p/BuQZSwhhf15/)。元投稿URLは公式サイトのリンクから確認したが、Instagram本体の取得はできていない。

### Fantomacsの補助例

本人公開のOne-Sheet（2025年8月版）に転載されたInstagram投稿カードの検索索引では、「Beachday」の2024-11-01投稿は夏の暖かさを思い出す問いから新曲告知へ、「On The Road」の2024-09-01投稿はドライブの情景から曲名と発売情報へつなげている。

これは本人公開資料の索引で確認した補助例に限る。PDF本体、captionの全文、個別post URL、動画、反応数を直接確認できていないため、前2例と同じ強さの証拠とは扱わない。

出典: [Fantomacs本人のOne-Sheet案内](https://www.fantomacs.de/epk/data-facts/)、[検索索引で確認した公開PDF](https://s63e0163a73c915ec.jimcontent.com/download/version/1755026853/module/10341090450/name/Fantomacsmusic-One-Sheet%20Aug%202025.pdf)

### 比較から分かることと未確認のこと

本人公開のcaptionには、雰囲気・情景、作品の識別情報、聴く先への案内を組み合わせる例がある。動画冒頭や字幕の優劣、現在の反応数、Spotify流入、売上の因果は今回の資料から判断できない。AI音楽アーティスト固有の成功例として十分に検証できる事例は得られておらず、上記の電子音楽例をAI音楽の成功証拠に置き換えない。

## 導線の現行機能

- **SpotifyからInstagram Storiesへの共有**。Spotifyは2025-08-21、共有した曲の音声プレビューと、曲ステッカーからSpotifyへ移動する機能を案内した。2020年のCanvas共有記事にある「Instagramでは音声が再生されない」という旧情報を現在の一般仕様として使わない。実際の曲とアカウントで利用できるかは投稿時に確認する。[Spotify公式発表](https://newsroom.spotify.com/2025-08-21/spotify-takes-instagram-sharing-to-the-next-level-with-audio-previews-and-real-time-listening-notes/)
- **Storyのリンクスタンプ**。Metaは広く利用可能な外部リンク導線として提供している。ただし新規アカウント等への制限があり、すべての場面で使えると断定しない。[Meta公式案内](https://about.fb.com/ja/news/2021/10/linkaccessstickers/)
- **公式音源**。Metaはアカウント種別、投稿種別、国・地域によるライブラリ制限を説明している。WAVを動画に焼き込むことと公式音源の選択は別の操作。デスクトップで追加できなかった体験から、全利用者・全画面で永続的に不可能という結論は出さない。[Metaヘルプ](https://www.facebook.com/help/instagram/402084904469945)
- **視聴時間**。MetaはReelsの総視聴時間と平均視聴時間を説明している。投稿の見え方を改善する指標であり、Spotify流入や売上の指標ではない。[Meta公式案内](https://about.fb.com/news/2023/04/instagram-reels-trending-audio-and-gifts-updates/)

## 次回の映像と文章で試すこと

1. 冒頭1〜2秒で音か映像の特徴を提示する。実際に音源を聴いて区間を選び、文字だけで過剰に煽らない。
2. 音声なしでも作品の入口が分かる短い画面内文字を検討する。8秒なら説明文を詰めず、一文と曲名程度を出発点にする。
3. captionの最初は作品の空気、次に正式名・曲名、最後に行動1つ。聴取・保存・コメント・フォローを一度に求めない。
4. プロフィールのリンク先が対象曲へ到達することを確認できた場合だけ、その導線を案内する。未設定なら検索用の正式名を示すか、承認のうえで導線を整える。
5. 追加投稿の手間が許せばSpotify曲のStory共有を併用する。新しい映像を毎回もう1本作る必要はない。

これは改善仮説であり、特定の再生数や売上を保証するものではない。ハッシュタグの数や汎用的な人気タグを増やすだけで流入効果が得られるという根拠は今回確認していない。

## Unseen Dragonのcaption案

下記はいずれも未投稿の提案。artist名・曲名を保ち、聴取導線の実態に合わせて選ぶ。

### 案1 現状の詩的な一文を残す

見えない竜の気配。

MRI_Music Resonance Imaging / Unseen Dragon
続きはSpotifyで。artist名と曲名で探せます。

AI-generated visual.
#UnseenDragon #IndustrialTechno #KazeXRecords

### 案2 プロフィールのリンク確認後

金属音と静寂のあいだに、見えない竜。

MRI_Music Resonance Imaging / Unseen Dragon
フルはプロフィールのリンクから。

AI-generated visual.
#UnseenDragon #ElectronicMusic #KazeXRecords

### 案3 Storyを同時に公開する場合

この8秒の続きへ。

MRI_Music Resonance Imaging / Unseen Dragon
Spotifyで聴くリンクはストーリーズに。

AI-generated visual.
#UnseenDragon #IndustrialTechno #KazeXRecords

案3はStory公開が完了しているときだけ使用する。Story失効後も残るcaptionなので、長期運用では案2の安定した導線を優先する。実際に8秒以外の動画なら案3冒頭の秒数も修正する。

## 効果の見方

Instagramではリーチ、再生、平均視聴時間、保存、シェアを記録する。取得可能ならプロフィール訪問や外部リンクのタップも別に記録する。公開されている「いいね」やコメントは参考になっても、Spotifyの聴取数には換算できない。

Spotifyでは対象曲のlisteners、streams、savesの直前7日と公開後7日を、既存アクセスで見られる範囲で比較する。Spotifyの曲再生は30秒以上が条件。8秒のInstagram映像が見られただけでは、このSpotify再生数にはならない。[Spotifyの再生定義](https://support.spotify.com/bj-en/artists/article/how-your-streams-are-counted/)

SpotifyのSource of streamsはSpotify内の再生場所の分類で、Instagramの特定投稿へ帰属する計測ではない。外部リンクのクリックとSpotify再生も一対一とは限らない。小規模な1投稿での増減には曜日、他の投稿、プレイリスト等が影響する。[Spotifyの再生元の定義](https://support.spotify.com/dk-en/artists/article/source-of-streams/)

記録時点は投稿前、24時間後、7日後を出発点とする。Spotifyは通常日次更新でUTC基準なので、更新前の当日値を完成値として比較しない。閲覧できない統計や未計測クリックを0と置かない。[Spotify統計更新](https://support.spotify.com/de-en/artists/article/when-stats-update/)
