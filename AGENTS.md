# AGENTS.md

## Run

Both LLM and scripted mode run simultaneously—toggle with `F1`.

```bash
pip install -r requirements.txt
cd client && python main.py
```

## Structure

- `client/main.py` - entry point, game loop
- `client/game/` - game logic (state.py, screen.py, userinput.py, people.py, background.py, assets.py, prison.py)
- `client/chat/` - NPC chat (api.py, chat.py, history.py, story.py)
- `client/color.py` - colors
- `client/logs.py` - logging

## Game states

`client/game/state.py:GameState`: INTRO → OPTIONS → CHALLENGE → ARREST → OUTRO → QUIT

## LLM API

`client/chat/api.py` contains hardcoded API key/URL. **Do not commit changes.** See `.gitignore`.

## No tests

`client/test.py` exists for manual LLM testing but is not automated. Run with `cd client && python test.py`.

## Controls

- `F1` - toggle LLM/scripted mode
- `Escape` - go back
- `Tab` - clear input

## Skills

Optional type checking: `.opencode/skills/ty/SKILL.md` (run `ty check` if `ty` is installed globally)
