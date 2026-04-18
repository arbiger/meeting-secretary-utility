# Meeting Secretary Utility

A local-first meeting recording and AI-powered summary service with speaker diarization.

## Features

- **Audio Upload** - Upload meeting recordings (.m4a, .mp3, .wav) via Web UI
- **Speaker Diarization** - Automatically identifies different speakers (VibeVoice-ASR)
- **AI Summary** - Generates structured meeting minutes in Traditional Chinese
- **Full Transcript** - Preserves original recording text for reference
- **Web UI** - Simple browser-based interface for upload and review
- **MCP Server** - Integrate with OpenClaw or other MCP-compatible tools

## Recommended Models

This tool works best with:

| Purpose | Model | Notes |
|---------|-------|-------|
| **ASR + Speaker Diarization** | [VibeVoice-ASR-4bit](https://huggingface.co/mlx-community/VibeVoice-ASR-4bit) | Automatically identifies speakers, optimized for meetings |
| **LLM Summarization** | Gemma-4-26b-a4b-it-oQ4 | Fast inference, good quality summaries |

## Requirements

- **macOS** (Apple Silicon optimized)
- **Python 3.9+** (3.11+ recommended)
- **FFmpeg** (`brew install ffmpeg`)
- **omlx** - Local LLM/ASR server (includes VibeVoice-ASR and Gemma models)

## Installation

```bash
# Clone the repository
git clone https://github.com/arbiger/meeting-secretary-utility.git
cd meeting-secretary-utility

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your settings (omlx server URL)
```

## Configuration

Edit `.env`:

```env
ASR_URL=http://127.0.0.1:8000/v1/audio/transcriptions
LLM_URL=http://127.0.0.1:8000/v1/chat/completions
ASR_MODEL=VibeVoice-ASR-4bit
LLM_MODEL=gemma-4-26b-a4b-it-oQ4
MEETINGS_DIR=~/Documents/Meetings
PORT=6076
```

## Usage

### 1. Start omlx server

```bash
# In one terminal - start omlx (ASR + LLM server)
omlx serve
```

### 2. Start FastAPI

```bash
# In another terminal
python3 -m app.main
```

### 3. Access Web UI

Open browser: **http://localhost:6076**

- Click "📤 Upload Audio File" to upload a recording
- Select from your recorder app or file manager
- Wait for AI analysis (VibeVoice-ASR → Gemma LLM)
- View summary and full transcript

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recordings/upload` | Upload audio file |
| GET | `/api/meetings` | List all meetings |
| GET | `/api/meetings/{id}` | Get meeting details + summary |
| DELETE | `/api/meetings/{id}` | Delete a meeting |
| POST | `/internal/analyze` | Trigger analysis |

## OpenClaw Integration

Add to OpenClaw MCP servers:

```json
{
  "mcp": {
    "servers": {
      "secretary": {
        "command": "/path/to/python3.11",
        "args": ["/path/to/meeting-secretary-utility/mcp/server.py"]
      }
    }
  }
}
```

Available MCP tools:
- `list_meetings()` - List all meetings
- `get_summary(meeting_id)` - Get meeting summary
- `analyze_meeting(filePath)` - Analyze a local audio file

## Output Format

Generated summaries include:

```markdown
# Meeting Minutes: [Title]

## Participants
- Speaker 0
- Speaker 1

## Summary
[AI-generated summary in Traditional Chinese]

## TODOs
- [ ] Task description

---

## 原始錄音文字 (Full Transcript)
[Complete transcript with speaker labels and timestamps]
```

## Development

```bash
# Run tests
pytest tests/ -v

# Check code style
python3 -m py_compile app/**/*.py
```

## License

MIT

## Acknowledgments

- [VibeVoice-ASR](https://huggingface.co/mlx-community/VibeVoice-ASR-4bit) - Meeting-optimized ASR with speaker diarization
- [Gemma](https://ai.google.dev/gemma) - Google's open LLM models
- [omlx](https://github.com/...) - Local MLX server for Apple Silicon
