# Antigravity IDE との統合試行記録

## 環境確認

### インストール位置
```
C:\Users\141di\AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe
```

### 設定ディレクトリ
- ローミング: `C:\Users\141di\AppData\Roaming\Antigravity IDE\User\settings.json`
- ローカル: `C:\Users\141di\.gemini\config\mcp_config.json`

### バージョン
```
Antigravity IDE 1.107.0
```

## 試行1: 標準設定ファイルによる統合（失敗）

### 試み
`~/.antigravity/config.json` に LM Studio 設定を記述

### 設定内容
```json
{
  "provider": "openai",
  "model": "qwen/qwen2.5-coder-14b",
  "baseUrl": "http://localhost:1234/v1",
  "temperature": 0.7,
  "maxTokens": 4096,
  "contextLength": 32768,
  "parallelAgents": 2
}
```

### 結果
❌ **失敗** - IDE で認識されず、モデルが利用不可

### 原因分析
- 設定ファイルが正しく読み込まれていない
- Antigravity IDE のネイティブ機能では LM Studio 統合が未サポート

---

## 試行2: MCP（Model Context Protocol）設定（失敗）

### 試み
`C:\Users\141di\.gemini\config\mcp_config.json` に MCP サーバー設定

### 初期設定
```json
{
    "mcpServers": {
        "lm_studio": {
            "command": "python",
            "args": ["/path/to/your/lm_studio_mcp.py"],
            "env": {
                "LM_STUDIO_API_URL": "http://localhost:1234/v1"
            }
        }
    }
}
```

### 修正試行
```json
{
    "mcpServers": {
        "lm_studio": {
            "command": "node",
            "args": [
                "-e",
                "require('child_process').spawn('lms', ['server', 'status']).on('exit', () => process.exit(0))"
            ],
            "env": {
                "LM_STUDIO_API_URL": "http://localhost:1234/v1",
                "LM_STUDIO_MODEL": "qwen/qwen2.5-coder-14b"
            }
        }
    }
}
```

### エラー
```
error: lm_studio: calling "initialize": EOF
```

### 原因分析
- MCP サーバーコマンド実行に失敗
- 正しい MCP サーバー実装がない
- IDE が MCP をサポートしていない可能性

---

## 試行3: 環境変数による統合（部分的成功）

### 試み
OS レベルで環境変数を設定

### 設定コマンド
```powershell
[Environment]::SetEnvironmentVariable("ANTIGRAVITY_LM_PROVIDER", "openai", "User")
[Environment]::SetEnvironmentVariable("ANTIGRAVITY_LM_BASE_URL", "http://localhost:1234/v1", "User")
[Environment]::SetEnvironmentVariable("ANTIGRAVITY_LM_MODEL", "qwen/qwen2.5-coder-14b", "User")
[Environment]::SetEnvironmentVariable("ANTIGRAVITY_LM_API_KEY", "", "User")
```

### 結果
⚠️ **部分的成功**
- IDE は正常に起動
- エラーメッセージなし
- しかし AI アシスタント機能は Qwen を使用していない
- ネイティブ AI 機能は別のモデル（Gemini等）を使用

---

## 結論：Antigravity IDE ネイティブ統合の限界

### 発見事項
1. Antigravity IDE のネイティブ機能では、ローカル LM Studio の直接統合をサポートしていない可能性
2. MCP による統合は理論的だが、実装上の課題あり
3. 設定ファイル形式やキー名が不明確

### 代替案への転換
⚝ **続きは `06_continue_extension_integration.md` を参照**

Antigravity IDE に組み込まれた Continue 拡張機能を使用する方針に変更し、成功を達成した。

---

## リファレンス

### Antigravity × Gemma 4 ドキュメント
参照: https://antigravitylab.net/articles/agents/antigravity-gemma4-multi-agent-local-workflow-2026

> "The guide explains that Antigravity supports two approaches: Gemini API or local LLM via Ollama."

このドキュメントでは Ollama を使用した例が示されていたが、LM Studio への直接統合は明記されていない。

---

## 今後の改善検討事項
1. Antigravity IDE 公式ドキュメントで LM Studio 統合方法を確認
2. MCP サーバーの正規実装の取得
3. Ollama ラッパーの使用検討（Ollama で LM Studio をプロキシ）
