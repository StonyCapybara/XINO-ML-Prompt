# Tetris ML Bot Challenge

Build an AI/ML bot that plays Tetris!

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Mac/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 main.py
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
python main.py
```

The Tetris game window will open. You can play manually with keyboard controls or let your bot play automatically.

## Keyboard Controls (Manual Play)

- **↑ / W** - Rotate piece
- **← / A** - Move left
- **→ / D** - Move right
- **↓ / S** - Soft drop (faster fall)
- **Space** - Hard drop (instant drop)

## Building Your Bot

### Edit `player/bot.py`

Open `player/bot.py` and implement your bot logic in the `decide()` method:

```python
def decide(self, obs: Optional[dict]) -> Optional[str]:
    # Your bot logic here
    grid = obs["grid"]              # 20x10 game board
    current_piece = obs["current_piece"]  # Current falling piece
    next_piece = obs["next_piece"]        # Next piece in queue
    level = obs["level"]                  # Current difficulty
    
    # Return one of: 'w', 'a', 's', 'd', ' ', or None
    return 'a'  # Example: move left
```

### Game State Structure

Your bot receives an `obs` dictionary with:
- **`grid`**: 20x10 matrix (0=empty, 1-7=occupied)
- **`current_piece`**: Current falling piece info (type, x, y, rotation, color, cells)
- **`next_piece`**: Next piece coming (type, rotation, color)
- **`level`**: Current game level/difficulty

See `player/bot.py` for detailed documentation and examples.

## Project Structure

```
auto-cognito/
├── main.py              # Entry point - run this
├── player/
│   ├── bot.py          # YOUR BOT IMPLEMENTATION GOES HERE
│   └── player.py       # Bot injection system (don't modify)
├── tetris/
│   └── tetris.py       # Core game logic (don't modify)
└── requirements.txt    # Dependencies
```

## Requirements

- Python 3.7+
- pygame-ce (or pygame)

## Tips

1. Start with simple rule-based logic before adding ML
2. Use print statements to debug your bot's decisions
3. The bot is called every ~120ms (8-9 times per second)
4. Keep your decision logic fast to avoid lag
5. Test incrementally - add one feature at a time
