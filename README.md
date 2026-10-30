# ✈️ Air Attack

A fast-paced 2D air-combat shooter built with Python and pygame. Pilot a jet fighter,
dodge incoming fire, and blast through endless waves of enemy aircraft that get
faster and more aggressive as your score climbs.

![Air Attack gameplay](images/screenshot.png)

## Features

- **Endless arcade action** — enemies spawn continuously and difficulty scales with your score
- **Three weapon levels** — single shot, twin cannons, and a three-way spread shot
- **Power-ups** — weapon upgrades, temporary shields, and extra lives
- **Two enemy types** — nimble fighters and tougher, slower gunships
- **Particle explosions**, a scrolling starfield, and a damage-flash effect
- **Lives & invulnerability** — you get a brief grace period after taking a hit
- **Pause and restart** without leaving the game
- **Single-file, zero assets** — every graphic is drawn in code, no image files needed

## Requirements

- **Python 3.9 or newer** (tested on Python 3.14)
- **[pygame-ce](https://pypi.org/project/pygame-ce/)** — the community-maintained fork of pygame.
  It's a drop-in replacement and the recommended choice, especially on Python 3.13+.

> ⚠️ **Note on Python 3.14:** the original `pygame` package does not yet support
> Python 3.14. Use `pygame-ce` instead — the code works with it unchanged.

## Installation

1. **Clone or download the project**

   ```bash
   git clone https://github.com/YOUR-USERNAME/air-attack.git
   cd air-attack
   ```

   Or simply download `air_attack.py` directly.

2. **Install the dependency**

   ```bash
   pip install pygame-ce
   ```

   If you have multiple Python installations, install into the right interpreter:

   ```bash
   py -m pip install pygame-ce
   ```

## Running the game

```bash
python air_attack.py
```

On Windows, if your `python` command points to a different interpreter, use the launcher:

```bash
py air_attack.py
```

## Controls

| Action      | Keys                       |
| ----------- | -------------------------- |
| Move        | Arrow keys or `W` `A` `S` `D` |
| Fire        | `Space`                    |
| Pause       | `P` or `Esc`               |
| Start / Restart | `Enter`                |

## Gameplay

- **Survive** as long as you can and rack up points. Your best score is tracked for the session.
- **Shoot enemies** to earn points: 80 for a fighter, 150 for a gunship.
- **Collect power-ups** dropped by destroyed enemies:

  | Icon | Power-up  | Effect                              |
  | ---- | --------- | ----------------------------------- |
  | `P`  | Weapon    | Upgrades your gun (max level 3)     |
  | `S`  | Shield    | Absorbs one hit                     |
  | `+`  | Extra life| Adds a life (max 5)                 |

- **Getting hit** costs a life *and* downgrades your weapon by one level.
- **Difficulty rises** every ~1500 points: enemies spawn faster and fly quicker.

## Project structure

```
air-attack/
├── air_attack.py     # The entire game — single file, no assets
├── requirements.txt  # Python dependencies
└── README.md
```

## Troubleshooting

**`ModuleNotFoundError: No module named 'pygame'`**
pygame isn't installed in the Python that's running the script. Install it with the
matching interpreter:

```bash
py -m pip install pygame-ce
```

**Build error mentioning `distutils.msvccompiler`**
You're on Python 3.14 and trying to install the original `pygame`, which doesn't
support it yet. Install `pygame-ce` instead:

```bash
pip install pygame-ce
```

**Nothing happens / window doesn't appear**
Make sure you're not running the file inside an environment that blocks window
creation (some remote sessions). Run it from a normal local terminal.

## License

This project is released under the **MIT License** — feel free to use, modify, and
share it. See `LICENSE` for details.

## Credits

Built with [pygame-ce](https://pyga.me/). Inspired by classic arcade vertical shooters.
