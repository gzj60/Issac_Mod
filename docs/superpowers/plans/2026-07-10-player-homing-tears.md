# Player Homing Tears Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a standalone Binding of Isaac mod that gives player-fired tears homing without affecting enemy projectiles.

**Architecture:** The mod lives in its own `player_homing_tears` folder. `main.lua` listens to tear updates, filters tears by player or player familiar spawner, and adds `TearFlags.TEAR_HOMING`; `metadata.xml` registers the local private mod with id `0`.

**Tech Stack:** The Binding of Isaac Repentance+ Lua mod API, PowerShell file operations, Python pytest-style static validation.

## Global Constraints

- Do not modify the existing `autoaim_3759966365` mod.
- Install the new mod under `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears`.
- Player and friendly familiar tears should become homing.
- Enemy projectiles and enemy-spawned tears should not be changed.

---

### Task 1: Standalone Homing Mod

**Files:**
- Create: `tests/test_player_homing_tears.py`
- Create: `player_homing_tears/main.lua`
- Create: `player_homing_tears/metadata.xml`
- Install: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua`
- Install: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\metadata.xml`

**Interfaces:**
- Consumes: Isaac Lua globals `RegisterMod`, `ModCallbacks.MC_POST_TEAR_UPDATE`, `TearFlags.TEAR_HOMING`, `EntityType.ENTITY_PLAYER`, `EntityType.ENTITY_FAMILIAR`.
- Produces: Lua callback `onTearUpdate(_, tear)` that adds homing only when `tear.SpawnerEntity` or `tear.Parent` resolves to a player or a familiar owned by a player.

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

MOD_DIR = Path(r"E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears")

def test_player_homing_tears_mod_files_and_filters():
    main_lua = MOD_DIR / "main.lua"
    metadata = MOD_DIR / "metadata.xml"

    assert main_lua.exists()
    assert metadata.exists()

    lua = main_lua.read_text(encoding="utf-8")
    xml = metadata.read_text(encoding="utf-8")

    assert 'RegisterMod("Player Homing Tears", 1)' in lua
    assert "ModCallbacks.MC_POST_TEAR_UPDATE" in lua
    assert "TearFlags.TEAR_HOMING" in lua
    assert "EntityType.ENTITY_PLAYER" in lua
    assert "EntityType.ENTITY_FAMILIAR" in lua
    assert "MC_POST_PROJECTILE_UPDATE" not in lua
    assert "<name>Player Homing Tears</name>" in xml
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_player_homing_tears.py -q`
Expected: FAIL because `main.lua` and `metadata.xml` do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `main.lua` with player/familiar source filtering and `metadata.xml` with local mod metadata.

- [ ] **Step 4: Install mod files**

Copy the two files from `D:\Code\isaac\player_homing_tears` into `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears`.

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_player_homing_tears.py -q`
Expected: PASS.
