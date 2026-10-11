# Arcadewisp

Original fullscreen offline terminal arcade for Linux and SSH. All games are included, no ads, API keys, accounts, network requests or paid unlocks. This is not the Apple Watch app and doesn't copy its code or artwork.

## Games

- Paddle duel: classic, moving gate and accelerating sprint modes, easy/normal/hard AI, local two-player mode, serve countdown, rally records and first-to-7 matches.
- Brick breaker: three lives, multi-hit bricks, five starting layouts, local best score.
- Invaders: moving enemy waves, firing cooldown, incoming shots, five speed levels, local best score.
- Drop: steer through gaps in rising platforms. Movement has inertia and speed increases as the run goes on. Local best score.
- Local badges: first run, score 150, clear a wave where applicable. These aren't Game Center achievements or online leaderboards.

This is a four-game collection with paddle variants, not a claimed replica of all 13 Watch modes, 86 hand-designed stages, Apple Watch controls or online multiplayer. "Better" is a design goal, not a measured superiority claim.

## Controls

Main menu: 1 paddles, 2 bricks, 3 invaders, 4 drop. +/- sets a bricks/invaders level from 1 to 5. Q quits.

Paddles: menu 1/2/3 difficulty, M switches solo/two players, C cycles classic/gate/sprint, Enter starts. W/S moves the left paddle. Arrows move the right paddle in two-player or left in solo. Space pause, R restart, H paddle menu, Q collection menu.

Other games: A/D or arrows move, F or Up fires in Invaders. Space pause, R retry, Q returns to collection. Letter controls accept either casing. Keyboard taps glide briefly for SSH. Two-player uses interleaved input; terminals don't reliably report simultaneous held keys. Resize restarts the current round paused, because the playfield changes. Narrow screens pause; 50x25 minimum, 80x30 or larger recommended.

## Install and run

Pi App Store: Games -> Arcadewisp. Root marker included. Installer adds Python/curses with apt/apk/pacman only if missing; no pip or extra libraries. Arch recipe can upgrade the whole system and preserves pacman's normal confirmation. Package-manager use requires root; unknown distributions fail with instructions, not a guessed recipe.

    bash app-store.sh INSTALL
    bash app-store.sh RUN
    python3 arcade.py --version
    python3 -m unittest -v

Marker actions accept any casing and in-game letter controls accept upper/lowercase. Linux filenames and executable names remain case-sensitive; no hundreds of command aliases are installed.

Scores stay in ~/.local/share/arcadewisp. No gameplay or personal data is sent anywhere. Records are best effort: symlinks are refused, files are private and saves use atomic replace. If saving fails the game tells you. Shared root sessions share one score file; concurrent sessions aren't a synchronized leaderboard.

## Verification and license

Linux unit tests and real fullscreen terminal captures, controls and quit/restoration checked. No physical Raspberry Pi or non-Linux test yet. SSH latency/font differences can affect smoothness. No sound or Watch hardware integration.

MIT code, copyright 2026 Greenisus1. Original game logic and text glyphs, no copied commercial assets.
