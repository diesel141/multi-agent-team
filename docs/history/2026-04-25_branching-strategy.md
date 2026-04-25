---
date: 2026-04-25
type: decision / process
title: ブランチ戦略を trunk-based + integration に決定
status: 決定済（CLAUDE.md §5 に反映）
tags: [git, workflow, branching, governance]
---

# ブランチ戦略を trunk-based + integration に決定

## 1. 背景

キックオフ時点では「PR 運用、main 直 push 禁止」とだけ決め、`feature → main` の単線フロー
を CLAUDE.md §5 に記載していた。

その後 `development` ブランチを切る運用要望があり、3 つの選択肢を比較検討した。

## 2. 検討した選択肢

| 戦略 | フロー | 評価 |
|------|-------|------|
| GitHub Flow | feature → main | 単純。リリース管理レイヤがない |
| GitFlow（標準） | feature → develop → release → main + hotfix | 複雑。release ブランチは小規模では過剰 |
| **trunk-based + integration**（採用） | feature → development → main | 中庸。development を常時 deployable に保つ規律 |

## 3. 決定

**trunk-based + integration** を採用。

### 3.1 ブランチ役割

- `main`: リリース済み・本番安定版。タグを切る基点。直接 PR 不可（development からのみ）
- `development`: 統合ブランチ。常時 deployable を維持
- `feature/* / fix/* / docs/* / chore/*`: 短命の作業ブランチ。`development` へ PR

### 3.2 フロー

```
feature/* ─┐
fix/*     ─┤
docs/*    ─┼─PR─▶ development ─PR(リリース時)─▶ main ─tag─▶ release
chore/*   ─┘
```

### 3.3 PR ルール

- マージ方式は squash 基本（develop でコミット履歴を再現する必要がない限り）
- long-lived branch は定期的に development を取り込んで drift を防ぐ
- 緊急 hotfix は main から `fix/hotfix-*` を切り、main と development 双方にマージ

## 4. 採用理由

1. **リリース管理を分離**: `main` をデプロイ済みの信頼できる状態に保つ
2. **統合の可視化**: 日々のマージ先 `development` を見れば直近の変更が一目で分かる
3. **少数精鋭との相性**: GitFlow ほど重くなく、GitHub Flow より統合段階が明示される
4. **trunk-based の精神を維持**: 短命ブランチ + 頻繁な統合 = 大規模 conflict を予防

## 5. 却下理由

- **GitHub Flow**: リリース可能ラインと開発ラインを区別できない。production の事故時に
  「どこまで安定なのか」が曖昧になる
- **標準 GitFlow**: release ブランチを別途運用する必要があり、本プロジェクト規模では過剰

## 6. 運用上の留意点

- **GitHub の既定ブランチを `development` に変更する**（PR 作成時のデフォルト base が
  development になり、ヒューマンエラーで main を base に PR を切る事故を防げる）
  - 設定箇所: GitHub Settings → Branches → Default branch → Switch to development
  - もしくは gh CLI 導入後 `gh repo edit --default-branch development`
- 既存の `docs/tech-lead-persona` PR は base を `development` に明示指定
- リリース作業の最初の 1 回は development → main の PR を起こし、運用を整備しながら習熟

## 7. 関連ドキュメント

- `CLAUDE.md` §5 Git 運用（具体ルールはこちらが正）
- 本ファイル（決定の経緯と却下理由）
