# Workflow Example

制作チャットでは、例えば次のように運用する。

1. ユーザーが曲名・アルバム名・creative prompt等を決める。
2. 「それカタログに入れといて」と指示する。
3. AIは既知情報をすぐartist / release YAMLへ保存する。
4. 未決定のrelease date、UPC、ISRC、Spotify URL等は `null` のまま維持する。
5. 「ピッチ準備して」「Spotify登録できる状態にして」と指示されたら、AIはreadinessを確認し、ユーザー判断が必要な不足だけをチャットで要求する。
6. 必要値が揃ったらbrowser task packetを生成する。
7. ブラウザ操作担当AIが外部サービスを操作し、結果と新たに判明した仕様を報告する。
8. 必要な新情報をcatalogへ戻す。

目的は、制作中に決まった情報を一度だけ正本へ入れ、その後の登録・Pitch・プロフィール更新で再利用すること。
