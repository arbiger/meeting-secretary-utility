---
name: meeting-taker-flow
description: Use when Codex needs to process George's meeting audio clips with the local Meeting Secretary MCP, check service health, produce or inspect transcript/extraction artifacts, or use meeting transcript outputs for downstream agent workflows such as Agentic TaskPad. Trigger on meeting recordings, Meetings Inbox, transcript extraction, meeting action items, Meeting Secretary MCP, VibeVoice, or local meeting extraction workflows.
---

# Meeting Taker Flow

Operate George's local meeting transcription/extraction workflow. Keep the MCP boundary simple: audio in, local transcript/extraction artifacts out. Downstream systems are handled by the agent, not by the MCP.

## Hard Boundary

- Treat Meeting Secretary MCP as a local transcription and extraction service only.
- Do not ask or expect the MCP to write Agentic TaskPad, dictionary files, project files, emails, or durable operational state.
- Use MCP outputs as evidence for downstream agent workflows.
- If TaskPad updates are needed, the agent must review the meeting output, prepare candidates, get George's confirmation unless already explicit in the current turn, then use the Agentic TaskPad workflow.
- It is valid to stop after transcript/extraction artifacts are produced.

## Paths And Services

- Repo: `/Users/george/Documents/Georges/01 🎯 Projects/meeting-taker-mcp` or a clone of `arbiger/meeting-secretary-utility`
- Default meetings directory: `~/Documents/Meetings`
- Recordings: `~/Documents/Meetings/recordings`
- Summaries: `~/Documents/Meetings/summaries`
- Index: `~/Documents/Meetings/index.json`
- Local model endpoint: `http://127.0.0.1:8000/v1`
- FastAPI service: `http://127.0.0.1:6076`
- MCP server entrypoint: `mcp/server.py`
- Optional downstream TaskPad repo: `/Users/george/Documents/Georges/01 🎯 Projects/agentic-taskpad`

## Health Check First

Before processing audio, check the local dependencies that can fail independently:

```bash
cd "/path/to/meeting-secretary-utility"
python3 - <<'PY'
from app.config import settings
print("asr_url=", settings.asr_url)
print("llm_url=", settings.llm_url)
print("asr_model=", settings.asr_model)
print("llm_model=", settings.llm_model)
print("meetings_dir=", settings.meetings_dir)
print("port=", settings.port)
PY
command -v ffmpeg || test -x /opt/homebrew/bin/ffmpeg
curl -fsS http://127.0.0.1:8000/v1/models >/tmp/meeting-secretary-models.json
curl -fsS http://127.0.0.1:6076/api/meetings >/tmp/meeting-secretary-meetings.json
test -w "$HOME/Documents/Meetings" || mkdir -p "$HOME/Documents/Meetings"
```

Interpretation:

- `127.0.0.1:8000` is the local OpenAI-compatible OMLX endpoint for VibeVoice/LLM.
- `127.0.0.1:6076` is the FastAPI service used by the MCP server.
- The MCP server in this repo is a stdio MCP process; do not expect a separate MCP HTTP port unless the local deployment added one.
- If OMLX is down, stop and tell George the local model service must be started before transcription/extraction.
- If FastAPI is down, start it with `python3 -m app.main` from the repo before using MCP tools that call the API.

## Use The MCP

Prefer the MCP tools when they are exposed in the current agent environment:

- `analyze_meeting(filePath)`: copy/analyze a local audio file.
- `list_meetings()`: list known meetings.
- `get_summary(meeting_id)`: read generated meeting summary and transcript content.

Example MCP call shape:

```json
{
  "filePath": "/Users/george/Documents/Meetings/Inbox/FILE.m4a"
}
```

`analyze_meeting` starts analysis asynchronously. Poll with `list_meetings()` or `get_summary(meeting_id)` until the meeting is complete. If only HTTP access is available, use the FastAPI endpoints described in the repo README.

## Artifact Review

After analysis, inspect the generated meeting record and summary:

- `~/Documents/Meetings/index.json`: meeting id, title, status, recording path, summary path.
- `~/Documents/Meetings/summaries/{meeting_id}.md`: generated summary plus full transcript.
- `~/Documents/Meetings/recordings/{meeting_id}.*`: copied source recording.
- FastAPI `GET /api/meetings/{meeting_id}`: meeting metadata and `summary_content`.

If the meeting status is `failed`, read the service logs or rerun from the API/MCP after checking OMLX and ffmpeg. Do not fabricate action items from a failed transcript.

## Downstream Use

Use the artifacts according to George's request:

- Transcript only: return or summarize the full transcript section; do not create tasks.
- Meeting summary: use the summary markdown and quote transcript evidence when making operational claims.
- TaskPad candidates: convert decisions/action items into proposed task/follow-up/evidence rows, then ask George to confirm before writing unless he already gave explicit disposition in the current turn.
- TaskPad writeback: use the Agentic TaskPad workflow and its write helpers. Verify after writing with a targeted SQLite query or `/health`.

Never let Meeting Secretary MCP perform TaskPad writeback. The agent owns that orchestration.

## Failure Handling

- Audio missing: confirm the absolute path or list likely files in the user's meeting inbox.
- OMLX down: report that local model service on `127.0.0.1:8000` is unavailable.
- FastAPI down: start or ask George to start the service on `127.0.0.1:6076`.
- MCP tool unavailable: use FastAPI directly if running, or explain that the MCP server is not configured in the current agent environment.
- Summary missing: inspect `index.json` status and avoid downstream writeback until transcript/summary exists.
- Long audio: wait for background analysis and preserve uncertainty if the transcript appears incomplete.

## Validation

For repo changes, run:

```bash
cd "/path/to/meeting-secretary-utility"
pytest tests/ -v
python3 -m py_compile app/**/*.py mcp/server.py
```

Real ASR/model calls are operator workflows, not unit tests.
