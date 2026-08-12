# Conversational Catalog Intake Workflow

最終更新: 2026-08-12

KAZEX Recordsでは、作品情報を完成後にまとめて転記するのではなく、制作中の会話から継続的に `kazex-catalog` へ蓄積する。

典型的なトリガー:

- 「それカタログに入れといて」
- 「この曲も登録しといて」
- 「アルバムに追加しといて」
- 「このプロンプト残しといて」

AIは、現在の会話と既存catalogから対象artist / release / trackを特定し、既知の公開可能情報を即時に正本へ反映する。

## 基本原則

### 1. まず保存する

不足情報があっても、既知の事実を保存すること自体は止めない。

例:

- アルバム名が決まった → releaseを作成または更新
- 曲名が決まった → `tracks` へ追加
- creative promptが決まった → 該当trackへ保存
- release dateが未定 → `null` のまま保存
- UPC / ISRCがまだ発行されていない → `null` のまま保存

「全項目が揃うまでcatalogへ入れない」は禁止する。

### 2. 同じ事実を再質問しない

現在の会話、既存artist / release YAML、catalog内の他の正本から分かる情報は再質問しない。

### 3. 推測で穴埋めしない

不明なrelease date、UPC、ISRC、Spotify URL、実績、広告施策、正式画像等を推測で埋めない。

### 4. 制作会話を質問攻めにしない

制作中のcapture段階では、まだ存在しない識別子や将来のsubmission用情報を毎回要求しない。

AIがその場で質問するのは、主に以下のような「今の情報を正しく保存するために本当に必要な曖昧さ」がある場合。

- どのartistの作品か判断できない
- どのreleaseへ入る曲か判断できない
- 曲名が候補なのか確定なのか判断できない
- promptがどのtrackに対応するか不明
- 画像が正式採用かcandidateか不明で、正式参照へ昇格させる必要がある

release date、UPC、ISRC、Spotify Artist URL等が単に未発行・未決定なだけなら、capture時点では `null` のままでよい。

---

# 3つの運用段階

## Stage 1 — CAPTURE / 制作中

目的: 制作会話で決まった情報を失わない。

AIの処理:

1. 対象artist / release / trackを特定する。
2. 既存ファイルがあれば更新する。
3. なければtemplateを基に最小構造を作る。
4. 会話で確定した公開可能情報だけ保存する。
5. `null` を推測で埋めない。
6. 保存に必要な曖昧さだけ質問する。
7. 更新後、短く「何を入れたか」を報告する。

新しいtrackの最低限の例:

```yaml
tracks:
  - title: Example Track
    isrc: null
    creative_prompt: >
      ...
```

アルバム制作中はtrackを1曲ずつ増やしてよい。

## Stage 2 — PREPARE / 外部登録準備

ユーザーが次のような指示をしたら、対象サービスに必要な不足情報をチェックする。

- 「ピッチ準備して」
- 「Priority Pitch出せる状態にして」
- 「Spotifyアーティストページ登録できるようにして」
- 「ブラウザに投げられる状態にして」

この段階では、AIは不足項目をまとめてチャットで要求する。

### Too Lost Priority Pitch

`docs/PRIORITY_PITCH.md` を正本とし、最低限以下を確認する。

- selected track
- release summary
- Spotify Artist
- marketing elements
- past awards / milestones

既存catalogから作れるRelease SummaryやMilestonesはAIが事実ベースで作成してよい。ユーザー判断が必要なMarketing Elements等だけを質問する。

### Spotify for Artists

`docs/BROWSER_TASKS.md` を参照する。

- Spotify Artist URL / URIがまだ存在しない場合は、その時点で正規の取得元を確認する。
- 初回release前claim等でUPC/EANが必要なら、catalogに登録済みか確認する。
- Bioはcatalogのdescription / concept / genresから事実ベースで生成できる。
- SNSはcatalogに存在する公式URLだけを使う。
- 正式artist imageが未選定ならcandidateから勝手に選ばず、画像更新だけ保留する。

## Stage 3 — READY / Browser execution

対象サービスに必要な値が揃ったら、`scripts/render_browser_task.py` でbrowser task packetを生成する。

```bash
python scripts/render_browser_task.py priority-pitch <release-id>
python scripts/render_browser_task.py spotify-profile <artist-id>
```

ブラウザ操作担当AIはpacketだけを読んでも作業できる状態を目指す。

最終Submit / claim / saveを行うかどうかはpacket内のreadinessと安全ルールに従う。

---

# AIへの会話上の期待動作

## ユーザー: 「それカタログに入れといて」

AI:

1. 既知情報をcatalogへ反映する。
2. validationを通す。
3. 必要なら曖昧な1点だけ質問する。
4. そうでなければ「入れた」と短く報告する。

## ユーザー: 「ピッチ出せる？」

AI:

1. catalogを読む。
2. 既知情報から生成できる項目は生成・保存する。
3. 不足しているユーザー判断だけをまとめて質問する。
4. 揃えばbrowser task packetを生成できる状態にする。

## ユーザー: 「Spotify登録しといて」

AI:

1. artist YAMLと関連releaseを読む。
2. claim / profile updateのどちらかを判定する。
3. 不足情報をチャットで要求する。
4. catalogを更新する。
5. browser task packetを生成する。
6. ブラウザ担当AIが操作した結果を回収し、必要な新情報をcatalogへ戻す。

---

# フィードバックループ

```text
制作会話
  ↓
CAPTURE: catalogへ随時保存
  ↓
PREPARE: 外部サービス別に不足確認
  ↓
READY: browser task packet生成
  ↓
ブラウザAIが操作
  ↓
画面で判明した新情報・statusを報告
  ↓
catalogへ反映
```

人間の役割は、作品判断、正式採用、未決定情報の決定、外部サービス上でしか得られない情報の提供に寄せる。
