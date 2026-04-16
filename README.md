# Meeting Secretary Service

本地端會議錄音 + AI 摘要分析 service。

## 需求

- Python 3.10+
- FFmpeg
- mlx_audio (ASR server)
- omlx (LLM server)

## 安裝

```bash
pip install -r requirements.txt
cp .env.example .env
# 編輯 .env 填入你的服務 URL
```

## 啟動

```bash
# 啟動 ASR/LLM server（分開的 terminal）
mlx_audio server
omlx server

# 啟動 FastAPI
python -m app.main
```

## 使用

- Web UI: http://localhost:8080
- API: http://localhost:8080/api/meetings

## MCP

```bash
openclaw mcp set secretary '{"command": "python3", "args": ["/path/to/meeting-secretary-utility/mcp/server.py"]}'
```

## 開發

```bash
pytest tests/ -v
```