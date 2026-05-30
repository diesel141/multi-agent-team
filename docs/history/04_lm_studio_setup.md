# LM Studio セットアップと最適化

## サーバー起動

### コマンド
```bash
lms server start
```

### 結果
```
Success! Server is now running on port 1234
```

### 確認
```bash
lms status
# Server:  ON
```

## モデルロード手順

### ステップ1: 初期ロード（デフォルト設定）
```bash
lms load qwen/qwen2.5-coder-14b
```

**結果:**
- ロード時間: 15.56秒
- メモリ使用: 8.37 GiB
- ステータス: IDLE
- デバイス: Local

### ステップ2: GPU最適化ロード
```bash
lms unload qwen/qwen2.5-coder-14b
lms load qwen/qwen2.5-coder-14b --gpu max -y
```

**結果:**
- ロード時間: 12.90秒（17.1% 高速化）
- メモリ使用: 8.37 GiB
- GPU オフロード: 有効化

### ステップ3: 最適コンテキスト長でのロード
```bash
lms unload qwen/qwen2.5-coder-14b
lms load qwen/qwen2.5-coder-14b --gpu max --context-length 32768 --parallel 4 -y
```

**結果:**
```
IDENTIFIER                MODEL                     STATUS    SIZE       CONTEXT    PARALLEL    DEVICE
qwen/qwen2.5-coder-14b    qwen/qwen2.5-coder-14b    IDLE      8.99 GB    32768      4           Local
```

- ロード時間: 30.27秒
- コンテキスト長: 32,768 トークン
- パラレル: 4 リクエスト同時処理

## LM Studio CLI コマンドリファレンス

### サーバー管理
```bash
lms server start          # サーバー起動
lms server stop           # サーバー停止
lms status                # サーバーステータス確認
```

### モデル管理
```bash
lms ls                    # ダウンロード済みモデル一覧
lms ps                    # ロード済みモデル表示
lms load <model-key>      # モデルロード
lms unload <model-key>    # モデルアンロード
lms get <model-key>       # モデルダウンロード
```

### ロードオプション
```bash
lms load <model> --gpu <offload-ratio>
  # off (GPU無効) | max (フルオフロード) | 0.0-1.0 (カスタム比率)

lms load <model> --context-length <length>
  # コンテキスト長設定（例：32768）

lms load <model> --parallel <count>
  # 並列処理数設定（例：4）

lms load <model> --identifier <id>
  # カスタム識別子設定

lms load <model> --estimate-only
  # リソース推定のみ（ロードしない）
```

## 自動起動スクリプト

### Batch スクリプト（start-qwen-optimized.bat）
```batch
@echo off
lms server start
timeout /t 3 /nobreak
lms load qwen/qwen2.5-coder-14b --gpu max --context-length 32768 --parallel 4 -y
echo API is ready at: http://localhost:1234/v1/
pause
```

### PowerShell スクリプト（start-qwen-optimized.ps1）
```powershell
# サーバー状態確認
$status = & lms status
if ($status -match "OFF") {
    & lms server start
    Start-Sleep -Seconds 3
}

# 最適設定でロード
& lms load qwen/qwen2.5-coder-14b --gpu max --context-length 32768 --parallel 4 -y

# 最終確認
& lms ps
```

**保存位置:**
- `C:\Users\141di\start-qwen-optimized.bat`
- `C:\Users\141di\start-qwen-optimized.ps1`

## API エンドポイント

### 基本情報
- **URL**: `http://localhost:1234/v1`
- **タイプ**: OpenAI 互換 API
- **認証**: なし（ローカル）

### 利用可能なエンドポイント
```
POST /v1/chat/completions      # チャット補完
POST /v1/completions            # テキスト補完
POST /v1/embeddings             # 埋め込み生成
GET  /v1/models                 # モデル一覧
```

### テスト例（curl）
```bash
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen2.5-coder-14b",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

## トラブルシューティング

### ポート 1234 が既に使用されている場合
```bash
# ポート確認
netstat -ano | findstr :1234

# 既存プロセス終了
taskkill /PID <PID> /F
```

### モデルロード失敗時
```bash
# メモリ推定で確認
lms load --estimate-only qwen/qwen2.5-coder-14b --context-length 32768

# リソースガード設定確認
# GUI で Settings > Model Loading Guardrails を確認
```

### GPU が認識されない場合
1. ドライバ更新を確認
2. Vulkan が正しくインストールされているか確認
3. VRAM の空き容量を確認（`nvidia-smi` または GPU管理ツール）

## 性能測定

### 初回実行時の結果
| パラメータ | 値 |
|----------|-----|
| モデルロード時間 | 30.27秒 |
| VRAM使用量 | 12.62 GB |
| コンテキスト長 | 32,768 トークン |
| パラレル数 | 4 |
| 推論レイテンシ | < 100ms |

## 次のステップ
IDE との統合設定（続きは `05_antigravity_integration.md` を参照）
