# Video Editing

An AI video-editing setup for Claude Code.

- `.claude/skills/video-editor/` is the **Video Editor** skill: house rules, saved brand (Orange `#FF5A1F`, Navy `#0B1F3A`, Montserrat), and a working caption example.
- `.claude/skills/hyperframes*`, `media-use` and related folders are HeyGen's HyperFrames skills (installed with `npx skills add heygen-com/hyperframes`; see `skills-lock.json`).
- `test-output/` holds the first 7-second branded caption test.

Tools used: FFmpeg, OpenAI Whisper, Node.js.
