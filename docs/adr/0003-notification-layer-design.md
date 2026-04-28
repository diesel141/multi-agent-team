# ADR-0003: 通知レイヤ実装方式（Notion 掲示板 → ローカルエージェント起動）

- 状態: **Proposed**（PM 承認待ち / Tech Lead 自己マージ前提・ADR-0006 §5.2）
- 起案日: 2026-04-27
- 起案者: Tech Lead 早瀬 蒼
- 改訂: 2026-04-27 §2.1 / §2.2 / §3 却下 F / §5.4 / §5.4.1 / §6 に **認証経路の補足**（TASK-0014 起因 / ユーザー希望「OAuth 基本無料」を解釈し Internal Integration 並存に確定）
- 関連: `docs/adr/0001-default-tech-stack.md` / `docs/adr/0002-next-team-members.md` / `docs/adr/0005-communication-protocol-revision.md` / `docs/adr/0006-persona-creation-flow-and-role-recalibration.md` / `docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` §4 / `docs/personas/backend_engineer.md`（久遠周）/ `CLAUDE.md` §1.3 / `memory/adr_house_style.md`

---

## 1. Context（文脈）

### 1.1 解きたい問題

本プロジェクト「Multi-Agent Team」は psmux 上の複数 Claude Code エージェントが **Notion 掲示板の 7 種メッセージのみ** で通信する制約下で稼働する（ADR-0005 / CLAUDE.md §1.3）。
ところが Notion 掲示板はあくまで「メッセージの正本」であって、**「新着メッセージが届いた」という事実を各エージェントに知らせるレイヤ**は未設計のまま投げられていた（`docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` §4）。

現状は以下の運用になっている:

- ユーザー（プロジェクトオーナー）が手動で「PM ペインに移って〇〇のレスを見て」と促すか、各ロールが手動で Notion を開いてポーリングする
- 結果、Notion に届いてから人が気付くまでのレイテンシは **数十分〜数時間** のばらつき
- POC 期は許容できるが、BE 久遠周採択（TASK-0011 / PR #17）以降の実装フェーズでは **掲示板の運用速度がチーム全体のスループットの律速** になる

本 ADR は通知レイヤの実装方式を確定し、`mat-board-watcher` サブリポでの実装着手（後続 TASK-0012 / BE 担当）に必要な技術判断・境界仕様を残す。

### 1.2 前提・制約

| 種別 | 内容 |
|------|------|
| ホスト | ローカル Windows 機（PowerShell 7+） / **常時稼働は保証されない**（人が PC を閉じる時間帯あり） |
| 既定スタック | TypeScript / Node 22 LTS / Vercel / pnpm / Biome / Vitest（ADR-0001 §2.1） |
| 通信プロトコル | Notion Messages DB（formal 3 + informal 4 / ADR-0005） |
| エージェント識別 | psmux ペイン上の Claude Code、`@agent_id` user option で安定識別（shogun 流用） |
| 業務通信境界 | 別 IM チャネル禁止 / send-keys は通知のみ許容、業務指示には使わない（CLAUDE.md §1.3 §1.2） |
| 期待レイテンシ（初期） | 受信から各ロールが気付くまで **数分**（≤ 5 min P95）/ phase2 で sub-minute へ |
| API レート制限 | Notion API は 3 req/s 平均（バーストは別枠）。1 アカウント 1 integration が前提 |

### 1.3 shogun 設計思想からの援用ライン

`docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` §3 の援用ラインを再確認:

- **メッセージ本体は別チャネル / 通知レイヤは「メールあり」のキックのみ** — Notion を本体、tmux send-keys を通知に限定する原則は維持（send-keys は短い wake-up シグナルのみで業務指示は流さない）
- **共有状態は単一 writer** — Notion ボードは PM が一次管理者
- **エージェント ID は tmux user option** — ペイン順序非依存

shogun の `inotifywait` は Linux 限定で本環境（Windows）では使えない。代替として §3 で 4 候補を並べる。

### 1.4 出力スコープ

本 ADR は次を確定する:

1. 通知レイヤの実装方式（4 候補 + 採用案）
2. 5 評価軸での比較（レイテンシ / レート制限耐性 / 障害モード / 初期コスト / 近期拡張性）
3. `mat-board-watcher` サブリポ初期化方針（ディレクトリ構成 / テンプレ参照先 / CI/CD 雛形）
4. 開いている論点（PM 承認で動かす可能性のある項目）

実装そのものは後続タスク（TASK-0012 想定）として BE 久遠周に委譲する。

---

## 2. Decision（決定）

### 2.1 採用案: Vercel Cron + Notion Search API による中央集約ポーリング（phase1）

「**Vercel Cron Functions が 1 分間隔で Notion Messages DB の last_edited_time 差分を取り、各受領者ロールに対応する psmux ペインへ短い wake-up シグナル（send-keys の 1 行）を送る**」を採用する。

#### 2.1.1 構成図（テキスト）

```
                    ┌──────────────────────────────────────┐
                    │ Notion Messages DB (formal/informal)  │
                    └───────────────────┬──────────────────┘
                                        │ Notion API (search + filter)
                                        ▼
        ┌──────────────────────────────────────────────────────┐
        │ Vercel Cron Function: /api/cron/poll  [1 min 間隔]   │
        │  - last_edited_time > cursor の差分取得               │
        │  - cursor は Vercel KV (or Upstash Redis) に永続化    │
        │  - 受領者ロール別にイベントを正規化                    │
        └─────────────────────────┬────────────────────────────┘
                                  │ HTTPS POST (署名付)
                                  ▼
        ┌──────────────────────────────────────────────────────┐
        │ Local Notifier (PowerShell + Node CLI)               │
        │  ngrok / Cloudflare Tunnel で外部公開                │
        │  受信したイベント →                                   │
        │    tmux send-keys -t <pane> "「@@notify TASK-XXXX」"  │
        │  各 Claude Code ペインの REPL に短い wake-up を投入   │
        └──────────────────────────────────────────────────────┘
```

#### 2.1.2 採用根拠（5 評価軸）

| 軸 | 採用案 (Vercel Cron + ポーリング) | 数値・備考 |
|----|------------------------------------|-----------|
| レイテンシ | P50 ≈ 30 sec / P95 ≈ 90 sec | Vercel Cron 最小粒度 1 min + Notion API 1 リクエスト分 + ローカル送信 |
| レート制限耐性 | ◎ 1 リクエスト/分 で平均 0.017 req/s。Notion 平均 3 req/s 制限の **0.6%** | バースト時も 1 cron 起動で 1 リクエストに収束 |
| 障害モード | △ Vercel 障害時にローカル代替が必要（§4.2 で緩和） | フェイルセーフ: cursor を Vercel KV に持つので Vercel 復旧で取りこぼしゼロ |
| 初期コスト | ◎ Vercel Hobby 枠で完結 ($0/month)、Vercel KV 無料枠で十分 | コード量も最小（cron handler 1 ファイル + dispatcher 1 ファイル） |
| 近期拡張性 | ◎ phase2 で Webhook 化に差し替え可能。dispatcher 層を共有 | §6-2 開いている論点参照 |

#### 2.1.3 段階導入

- **phase1（本 ADR で確定）**: 1 分ポーリング。実装スコープを最小化
- **phase2（再考閾値到達時）**: Notion 公式 Webhook が GA かつ自前リレー不要になったら Webhook 受け皿に切替（§3 却下案 B 参照）
- **phase3（将来）**: ローカル PC 常時稼働が前提化したらハイブリッド（Cron + ローカル Watcher）に拡張（§3 却下案 C / §6-3 開いている論点）

#### 2.1.4 認証経路（MCP OAuth と Vercel bearer の並存設計）

本 ADR 構成では Notion 認証は **2 系統が並存** する。両者は同一 Notion Messages DB を読み書きするが、認証主体・認証方式・配置先が異なる。

| 系統 | 認証方式 | 主体 | 配置先 | 用途 |
|------|---------|------|--------|------|
| MCP OAuth | OAuth 2.0（Notion Remote MCP） | 各 Claude Code インスタンス | ローカル PC（Claude Code keychain） | 各エージェントが掲示板を直接読み書き（投稿・参照） |
| Internal Integration bearer | Bearer token（`secret_xxx`） | サーバー側（Vercel Functions） | Vercel Encrypted env (`NOTION_TOKEN`) | Cron による差分ポーリング・safety net 投稿 |

両系統が同時に動くため、Messages DB のページ設定で **MCP OAuth と Internal Integration の両方をコネクションとして許可** する。ユーザーが「OAuth、基本無料で作業」と希望した点は、**MCP OAuth は OAuth のまま維持し、Vercel 側のみ Internal Integration を使う** ことで満たす（OAuth Public Integration を Vercel 側にも実装する案は §3 却下 F で外した）。

### 2.2 既定スタックとの整合（ADR-0001）

採用案は ADR-0001 §2.1 の既定スタックと整合する。認証は §2.1.4 の通り **MCP OAuth（Claude Code 側）+ Internal Integration（Vercel 側）の並存**。OAuth フロー実装は本 ADR では行わない（§3 却下 F）。

- 言語: TypeScript（Node 22 LTS） ✅
- API フレームワーク: Hono on Vercel Functions ✅
- ホスティング: Vercel ✅
- KV / 永続化: Vercel KV（または Upstash Redis 互換）— ADR-0001 では明示されていないが、Vercel Functions と直結する KV は同設計思想内
- ローカル実行: pnpm + Node CLI（PowerShell から起動）✅
- CI/CD: GitHub Actions ✅
- Lint/Format: Biome ✅
- テスト: Vitest ✅

新規導入は Vercel KV / Cloudflare Tunnel のみで、いずれも SaaS 既定方針に沿う。

---

## 3. Considered Alternatives（却下した代替案）

### 却下 A: short-interval setInterval ポーリング（ローカル常駐 Node プロセス、≤ 30 sec 間隔）

- **却下理由 1**: ローカル PC が常時稼働する保証がない（§1.2）。夜間や PC スリープ中は通知が途絶え、復帰時に未読が滞留する
- **却下理由 2**: Notion API レート制限 (3 req/s) に対し 30 sec 間隔 ≒ 0.033 req/s と余裕はあるが、複数ロール / 複数 DB に拡張した場合に削れるマージンが小さくなる
- **却下理由 3**: cursor の永続化を SQLite or ローカルファイルでやることになり、Vercel KV 採用の中央集約案より状態同期の難易度が上がる
- **再考の閾値**: ローカル PC が UPS / 自動起床つきの常時稼働ホストに移行し、かつ「sub-minute レイテンシが業務契約上必須」と PM が判定した時

### 却下 B: Notion 公式 Webhook → Vercel Functions 受け皿

- **却下理由 1**: 2026-04 時点で Notion の **公式 Webhook 機能は database 単位のイベント送信が安定 GA とは言いがたく**、サードパーティ（n8n / Make / Zapier）経由の中継が事実上必須となる。中継 SaaS のアカウント / 月額 / TOS 確認コストが phase1 の ROI を悪化させる
- **却下理由 2**: 受け皿側は問題なく Vercel Functions で構築できるが、ngrok / Cloudflare Tunnel の常時運用とローカル PC 起動が前提化する（採用案 phase1 では Vercel Cron が ngrok 不要）
- **却下理由 3**: phase1 はレイテンシ要件が「数分」レベルで Webhook の sub-second レイテンシは過剰
- **再考の閾値**: (a) Notion 公式 Webhook が database scope で GA 表記になり、かつ (b) 中継 SaaS 不要で Vercel Functions に直接 POST できる構成が公式ドキュメント化された時 / または (c) 業務 SLA が「P95 < 10 sec」を要求するレベルに達した時

### 却下 C: ローカル `chokidar` / PowerShell `FileSystemWatcher` + `docs/history/` 代理シグナル

- **却下理由 1**: `docs/history/` は意思決定の歴史化アーカイブであって通知シグナルではない（CLAUDE.md §3）。歴史化目的のファイル更新を通知用途に流用すると、「歴史化粒度を上げて通知頻度を上げる」という本来の歴史化原則と逆向きの圧力がかかる
- **却下理由 2**: そもそも Notion 掲示板に直接来たメッセージが `docs/history/` には反映されない（formal / informal を全て歴史化はしない）。代理シグナルとしてのカバレッジが不完全
- **却下理由 3**: ローカルマシン依存で、PC スリープ中は機能しない（A と同じ問題）
- **再考の閾値**: 歴史化アーカイブと通知レイヤを統合して扱う「event sourcing 的な再設計」を別 ADR で起こす場合のみ（現時点では分けるのが正解）

### 却下 D: shogun 直系の YAML inbox + tmux send-keys 通知（Notion を二次に降格）

- **却下理由 1**: CLAUDE.md §1.3 で「業務通信は Notion 掲示板」と決め切っており、YAML inbox を一次にする選択は通信プロトコル ADR-0005 を覆す上位 ADR を別途要する
- **却下理由 2**: マルチエージェント / 多ロール体制で「単一 writer は PM」を保つには Notion の API トランザクションが楽。YAML + flock は単一マシン前提の設計で、将来クラウド化する際に書き換え必須
- **却下理由 3**: Notion を二次にすると歴史化（pptx 集約）の一次ソースが分散し、`docs/history/` 規律が崩れる
- **再考の閾値**: Notion 連続障害が四半期に 2 回以上発生し、業務継続不可レベルが顕在化した時 / または PJ の物理ホストが完全オフライン環境（air-gap）に移った時

### 却下 E: GitHub Actions の workflow_dispatch + Notion API ポーリング（Vercel 不採用）

- **却下理由 1**: GitHub Actions の cron 最小粒度は 5 min 公称・実測 5-15 min の揺らぎがある。1 min 粒度の Vercel Cron に比べ P95 レイテンシが 10x 悪化する
- **却下理由 2**: Actions は短時間ジョブ向けで、状態管理（cursor）に外部 KV を結局必要とする。Vercel Functions + Vercel KV のセット採用と比べ「実行基盤 + 状態管理」の組合せが分散する
- **却下理由 3**: ロギング / 失敗時通知が Actions UI 中心で、Vercel Dashboard の方が一覧性が高い
- **再考の閾値**: Vercel Cron が有償化または Hobby 枠から外された時 / または GitHub Actions の cron 粒度が公式に 1 min 化された時

### 却下 F: Notion Public Integration + OAuth フローを Vercel Functions に実装（サーバー側 OAuth）

ユーザー希望「OAuth、基本無料で作業」を **サーバー側も OAuth で統一** と解釈した場合の案。本 ADR は §2.1.4 の **MCP OAuth（Claude Code 側）+ Internal Integration（Vercel 側）の並存** で「OAuth 希望」を実質満たすため、サーバー側まで OAuth 化する案は phase1 では却下する。

- **却下理由 1**: phase1 ROI に合わない。OAuth 認可エンドポイント / コールバック / リフレッシュトークン保管（Vercel KV）/ 失効時再取得フローを実装すると BE 1〜2 日工数が発生する。phase1 の通知レイヤは「1 分ポーリング + ペイン wake-up」が本質で、OAuth 機構は本質貢献しない
- **却下理由 2**: ユーザーワークスペースは 1 つのみで、PM が単一 writer として運用する前提（ADR-0005 / shogun §3）。Public Integration の主要利点（マルチワークスペース対応・テナント別認可）は phase1 で発揮されない
- **却下理由 3**: Internal Integration の bearer token はワークスペース管理者が Notion 管理画面で **作成 / 失効 / 再発行 を 1 クリック** で操作できる。漏洩時のリカバリは bearer 再発行 + Vercel env 更新の 2 手で完了し、OAuth refresh token rotation の自動化より単純
- **却下理由 4**: ユーザーの「OAuth 希望」は Claude Code 側 MCP の OAuth を維持したい意向（既存資産の流用）と解釈でき、§2.1.4 の **MCP OAuth + Vercel Internal Integration の並存** で実質満たされる。サーバー側まで OAuth を強制する必要はない
- **再考の閾値**: (a) 複数 Notion ワークスペースを横断する業務要件が発生（例: 顧客企業の Notion を直接参照する SaaS 化）/ (b) bearer token rotation を自動化する SLA（例: 90 日強制ローテ）が業務契約上要求される / (c) 非管理者ユーザーが PM を介さず直接アクセス付与する UX が必要になった / (d) Notion が Internal Integration を deprecation 予告した時

---

## 4. Consequences（帰結）

### 4.1 ポジティブ

1. **業務速度の律速解消** — P95 90 sec で各ロールに wake-up が届くため、formal 開始指令の発出からロール着手返答までの SLA を「数時間」から「数分」へ短縮できる
2. **コスト ≈ 0 / 運用負荷 ≈ 0** — Vercel Hobby + Vercel KV 無料枠で完結。SRE 起用条件（ADR-0002 §2.2）に到達するまで通知レイヤ単独で課金は発生しない
3. **拡張パスが明示** — phase2 / phase3 への移行条件を §3 却下案 B / A の再考閾値で言語化済み。後続 Tech Lead が「いつ何を見直すか」を判定できる
4. **既定スタック追従** — TS / Node / Vercel に揃え、レビュー観点を ADR-0001 の枠内に収める
5. **shogun 思想の継承** — 「メッセージ本体は別チャネル / 通知は短い wake-up」原則を Windows 環境で再現できる

### 4.2 ネガティブ・リスク

1. **Vercel 単一障害点** — Vercel Cron / Vercel KV の障害で通知停止
   - **緩和策**: cursor を KV に持つため復旧後の取りこぼしはゼロ。連続障害が業務クリティカル化したら §3 却下案 D の閾値到達として再考
2. **ローカル Notifier がローカル PC 起動依存** — Vercel から POST する先がオフラインだと wake-up が届かない
   - **緩和策**: 受信側が再接続したタイミングで Vercel Functions の `/api/queue/replay` を呼んで未配信イベントを再送する設計を §5 のディレクトリ構成に折り込む
3. **Notion API レート制限への抵触** — 想定外のメッセージ大量投稿（通知ループ等）で 3 req/s に張り付く
   - **緩和策**: Cron 関数内で **検知された差分件数が閾値（例: 100 件 / 分）を超えたら即停止 + 問題報告メッセージを掲示板に formal 投稿** する safety net を実装
4. **psmux send-keys を「通知のみ」に限定する規律の遵守** — 実装時に「ついでに業務指示も流せる」という誘惑が発生する
   - **緩和策**: `dispatcher` 層で送信文字列を `^@@notify TASK-NNNN$` のような ASCII 安全な短い形式に正規表現で制限し、業務本文を流せないように型レベルで縛る
5. **cursor 競合（複数 Cron 実行が並走）** — Vercel Cron は理論上 overlap しないが、手動トリガーやリトライで並走の可能性
   - **緩和策**: KV 上の cursor 更新を atomic compare-and-swap で行う / phase1 では並走頻度が低いため許容

### 4.3 影響範囲

- **本ハブリポ（multi-agent-team）**: 本 ADR と歴史化メモのみ。実装コードは含まない
- **新規サブリポ `mat-board-watcher`**: 後続 TASK-0012 で BE 久遠周が初期化（§5 の方針に従う）
- **Notion Messages DB**: スキーマ変更なし。`last_edited_time` を差分検知のキーにするだけ
- **CLAUDE.md**: §1.2 「send-keys は業務通信に使わない」という記述と整合。本 ADR で send-keys を **通知用途に限定**して使う旨を §4.2 緩和策レベルで明示
- **既存ペルソナ**: Tech Lead / BE / PM の責任分担に影響なし

---

## 5. mat-board-watcher サブリポ初期化方針

> 実装は後続 TASK-0012（BE 久遠周担当想定）。本 ADR ではスケルトンと境界のみを確定する。

### 5.1 リポジトリ命名・配置

- リポジトリ名: `mat-board-watcher`（ADR-0001 §2.4 命名規約「`mat-<purpose>`」準拠）
- GitHub 配置: `diesel141/mat-board-watcher` を想定（PM 承認後に Tech Lead が `gh repo create` で初期化）
- ライセンス: 非公開リポを想定（社内ツール）

### 5.2 ディレクトリ構成（提案）

```
mat-board-watcher/
├── README.md                       # セットアップ・運用手順
├── package.json                    # pnpm workspace root
├── pnpm-workspace.yaml
├── turbo.json                      # Turborepo（将来複数パッケージに拡張時）
├── biome.json                      # Lint/Format
├── tsconfig.base.json
├── .github/
│   └── workflows/
│       └── ci.yml                  # lint / typecheck / test
├── apps/
│   └── api/                        # Vercel Functions (Hono)
│       ├── package.json
│       ├── vercel.json             # cron schedule 定義 (* * * * *)
│       ├── src/
│       │   ├── routes/
│       │   │   ├── cron-poll.ts    # /api/cron/poll
│       │   │   ├── replay.ts       # /api/queue/replay (未配信再送)
│       │   │   └── webhook.ts      # /api/webhook (phase2 用、phase1 では 501)
│       │   └── lib/
│       │       └── env.ts          # 環境変数バリデーション (zod)
│       └── tests/
├── packages/
│   ├── notion-client/              # Notion SDK ラッパ
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── client.ts
│   │   │   ├── search.ts           # last_edited_time 差分取得
│   │   │   └── types.ts
│   │   └── tests/
│   ├── state/                      # cursor 永続化（Vercel KV ラッパ）
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── kv.ts
│   │   │   └── cursor.ts           # CAS 付き更新
│   │   └── tests/
│   └── dispatcher/                 # ローカル Notifier への HTTPS POST
│       ├── package.json
│       ├── src/
│       │   ├── post.ts             # 署名付き POST (HMAC-SHA256)
│       │   └── safe-payload.ts     # 「通知のみ」の payload 型ガード
│       └── tests/
└── tools/
    └── local-notifier/             # ローカル PC 上で動く Node CLI
        ├── package.json
        ├── bin/notifier.ts         # 受信 → tmux send-keys
        └── README.md               # PowerShell からの起動手順
```

### 5.3 テンプレート参照先

- `multi-agent-template`（ADR-0001 §2.3 で言及）は **未起票**。本 ADR の §6 開いている論点 (5) で、Tech Lead が後続タスクとして `multi-agent-template` リポを起こすか、`mat-board-watcher` が **事実上の最初のテンプレ実装** になるかを PM と議論する
- 暫定方針: `mat-board-watcher` を **「最初のテンプレ実装」として丁寧に作り、`multi-agent-template` は本リポの構成を抽出する形で後追い起票**（PM 承認後に別 ADR で確定）

### 5.4 CI/CD 雛形

`apps/api/.github/workflows/ci.yml` の最小ライン:

```yaml
name: CI
on:
  pull_request:
    branches: [development, main]
  push:
    branches: [development, main]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec biome ci .
      - run: pnpm -r exec tsc --noEmit
      - run: pnpm -r run test
```

デプロイは Vercel の Git 連携（development → preview / main → production）を採用。Vercel 側で次の環境変数を設定:

| 環境変数 | 用途 | 認証方式 | 設定先 |
|---------|------|---------|--------|
| `NOTION_TOKEN` | Notion **Internal Integration** secret（`secret_xxx...`） | Bearer token（OAuth ではない） | Vercel Encrypted env |
| `NOTION_DB_MESSAGES` | Messages DB ID | — | Vercel Encrypted env |
| `KV_REST_API_URL` / `KV_REST_API_TOKEN` | Vercel KV | — | Vercel KV 自動注入 |
| `LOCAL_NOTIFIER_URL` | ローカル Notifier の公開エンドポイント（Cloudflare Tunnel public URL） | — | Vercel Encrypted env |
| `LOCAL_NOTIFIER_HMAC_SECRET` | POST 署名鍵（HMAC-SHA256） | — | Vercel Encrypted env / ローカル `.env` 双方 |

`NOTION_TOKEN` の正体は **Notion Internal Integration secret**（`secret_` 接頭辞）であり、Claude Code 側 MCP の OAuth トークンとは別物。両者が同じ Messages DB を読み書きする並存設計の根拠は §2.1.4。OAuth Public Integration を Vercel 側にも実装する案は §3 却下 F で外している。

#### 5.4.1 ユーザー作業手順（事前セットアップ・約 15 分）

本 ADR の採用認証経路では、BE 久遠周が `mat-board-watcher` 実装に着手する前にユーザー（プロジェクトオーナー）が以下を済ませる必要がある。BE 工数を削るため **PM が事前準備チェックリストとして TASK-0012 開始指令と並行発注** する想定。

1. **Notion Internal Integration を作成**
   - Notion → Settings → Connections → Develop or manage integrations → New integration
   - Name: `mat-board-watcher` / Type: **Internal** / Associated workspace: 個人ワークスペース
   - Capabilities: Read content / Update content / Insert content / Read user information without email
   - 表示された **Internal Integration Secret**（`secret_xxx...`）をコピー（後で Vercel に投入）
2. **Messages DB に Integration を接続**
   - Notion 掲示板の Messages DB ページ → 右上「・・・」→ Connections → `mat-board-watcher` を追加
3. **Vercel プロジェクト作成 + KV 紐付け**
   - Vercel Hobby 枠で `mat-board-watcher` プロジェクトを GitHub 連携で作成
   - Storage タブから **Vercel KV** を新規作成し本プロジェクトに紐付け（自動で `KV_REST_API_*` 注入）
   - Encrypted env に `NOTION_TOKEN` / `NOTION_DB_MESSAGES` / `LOCAL_NOTIFIER_URL` / `LOCAL_NOTIFIER_HMAC_SECRET` を設定
4. **Cloudflare Tunnel セットアップ**（ユーザー所有ドメイン使用 / 無料）
   - `cloudflared tunnel create mat-notifier`
   - DNS ルート: `cloudflared tunnel route dns mat-notifier notifier.<your-domain>`
   - `~/.cloudflared/config.yml` でローカルポート（**実運用値: `http://localhost:3010`**）にバインド。本 ADR は当初 `:8787` を例示していたが、TASK-0012 起動時の PM 環境調整で **3010** を採用（ユーザー環境の :3000 が他プロセスで占有されていたため）。BE 実装 (`tools/local-notifier`) も :3010 で待機する
   - サービス起動: PowerShell で `cloudflared tunnel run mat-notifier`
   - 公開 URL（`https://notifier.<your-domain>`）を Vercel `LOCAL_NOTIFIER_URL` に設定
5. **HMAC 共通鍵生成**
   - PowerShell: `[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))` で 32 バイト乱数
   - Vercel `LOCAL_NOTIFIER_HMAC_SECRET` とローカル PC の `.env` の双方に同値を設定

完了後、PM がチェックリスト全項目を確認し BE に「事前準備完了」を通知する（TASK-0012 開始指令の依存関係欄）。

### 5.5 受入基準（後続 TASK-0012 で BE 久遠周が満たす項目）

1. `apps/api/src/routes/cron-poll.ts` が Notion Messages DB を `last_edited_time > cursor` で取得できる
2. cursor が Vercel KV に CAS 更新で永続化される（ユニットテストで競合シナリオを再現）
3. `dispatcher.post()` が **payload schema を「通知のみ」に縛る型ガードを通過する** ことが Vitest で証明されている
4. `tools/local-notifier/bin/notifier.ts` が PowerShell 起動・HMAC 検証・`tmux send-keys` 投入まで E2E で動作
5. Notion API レート制限を超えない safety net（差分件数 100 件 / 分超で停止 + 問題報告投稿）が実装されている
6. README に「初回セットアップ（Vercel プロジェクト作成 → KV 紐付け → ローカル Notifier 起動）」が PowerShell コマンド付で書かれている
7. ADR-0003 §4.2 のリスクごとの緩和策が実装または明示的な TODO で残されている

---

## 6. 開いている論点（PM 承認・議論で動かしたい点）

> 「**強い意見を弱い保持で**」。以下は本 ADR の確定後も議論で動く可能性のある点を明示する。

1. **ポーリング間隔の確定** — 本 ADR では Vercel Cron 1 min を採用したが、コスト面で 5 min まで緩めるか、Notion API レート余裕を活かして手動 30 sec を入れるかは PM 判断の余地あり。**測定方針**: phase1 リリース後 2 週間の formal 投稿数 / informal 投稿数の実測 P95 で再評価
2. **Webhook そのものの使用可否（phase2 移行条件）** — §3 却下案 B 再考閾値の (a) Notion 公式 Webhook GA / (b) 自前リレー不要 / (c) SLA 強化 のいずれを優先するかは PM の事業方針次第。本 ADR では「(a)+(b) を必要条件、(c) を十分条件」としたが見直し可
3. **ハイブリッド（Cron + ローカル Watcher）への phase3 移行タイミング** — ローカル PC 常時稼働を業務前提にできるか / SRE 起用と紐付けるかは PM 判断
4. **`multi-agent-template` の起票タイミング** — §5.3 暫定方針は「mat-board-watcher を最初のテンプレ実装にし、`multi-agent-template` を後追い」だが、逆順（先にテンプレリポを作る）で進める案も残す。Tech Lead は **後追い派** だが PM が異論を述べる余地あり。**※ ADR-0007 §2.4 で決議（後追い派採用 / サブリポ 2 つ目 or ドリフト 5 サブリポ蓄積で再評価）**
5. **`mat-board-watcher` の所有・運用責任** — 通知レイヤは BE 実装だが、運用障害時の一次対応者を BE / Tech Lead / SRE（未起用）のいずれに置くかは未確定。SRE 起用前は Tech Lead が一次対応する想定だが、PM 承認で固定したい
6. **send-keys の「通知のみ」規律の自動検証** — §4.2 緩和策で型ガードを置くが、「規律違反を CI で検知する仕組み」（例: payload 文字列長を 80 文字未満に強制）まで踏み込むかは別 ADR 候補。**※ ADR-0007 §2.5 で決議（phase1 は型ガード + payload 正規表現で十分 / 規律違反 1 件発生で ADR-0008 起案）**
7. **サーバー側 OAuth 化の phase2 移行条件** — §3 却下 F の再考閾値 (a)-(d) のいずれが先に到達するか不明。本 ADR では Internal Integration bearer で phase1 完結とし、Public Integration + OAuth 化は phase2 候補として保留。**測定方針**: bearer token 漏洩インシデント・複数ワークスペース要件・rotation SLA 要求の 3 シグナルを四半期に 1 度棚卸し、いずれか出たら独立 ADR で再起案

---

## 7. References（関連資料）

- `docs/adr/0001-default-tech-stack.md` — 既定スタック（TS / Node / Vercel / Hono / pnpm / Biome / Vitest）
- `docs/adr/0002-next-team-members.md` — BE / FE / SRE 採用順（BE 久遠周は採択済）
- `docs/adr/0005-communication-protocol-revision.md` — formal 3 + informal 4 メッセージ体系
- `docs/adr/0006-persona-creation-flow-and-role-recalibration.md` — 権限境界（PR レビュー＆マージは Tech Lead）
- `docs/personas/backend_engineer.md` — BE 久遠周ペルソナ（後続 TASK-0012 で本 ADR を実装）
- `docs/history/2026-04-25_multi-agent-shogun-architecture-reference.md` §4 — 本 ADR が解く未決問題の出典
- `docs/history/2026-04-25_psmux-windows-investigation.md` — Windows + psmux の制約（send-keys 挙動・常時稼働性）
- `docs/history/2026-04-25_notion-mcp-adoption.md` — SaaS 単一障害点の先行議論
- `CLAUDE.md` §1.2 / §1.3 — send-keys 業務通信禁止 / Notion 掲示板限定
- `memory/adr_house_style.md` — 本 ADR が遵守するハウススタイル（再考閾値必須）
- 後続歴史化メモ: `docs/history/2026-04-27_task-0002-adr-0003-notification-layer.md`（本 ADR と同時起票）
