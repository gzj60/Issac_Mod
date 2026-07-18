# Player Tear Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every player-owned or friendly-familiar-owned tear unlimited range, piercing, spectral movement, and strong smooth homing while leaving enemy projectiles unchanged.

**Architecture:** Keep `MC_POST_TEAR_UPDATE` as the only gameplay callback and reuse the existing owner filter. Apply native tear flags and stable flight properties to each friendly tear, then steer its velocity toward the nearest valid hostile entity with a `0.30` blend while preserving speed.

**Tech Stack:** The Binding of Isaac Repentance+ Lua mod API, XML metadata, Python 3 with pytest, PowerShell file synchronization.

## Global Constraints

- Keep the independent mod directory name `player_homing_tears`.
- Only player and friendly familiar tears may be changed.
- Register no `MC_POST_PROJECTILE_UPDATE` callback.
- Use `Height = -23`, `FallingSpeed = 0`, and `FallingAcceleration = 0` for unlimited range.
- Use a homing turn factor of exactly `0.30` and preserve current tear speed.
- Set metadata version to `1.1`.
- The workspace is not a Git repository, so commit steps are unavailable.

---

### Task 1: Friendly Tear Enhancements

**Files:**
- Modify: `D:\Code\isaac\tests\test_player_homing_tears.py`
- Modify: `D:\Code\isaac\player_homing_tears\main.lua`
- Install: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua`

**Interfaces:**
- Consumes: existing `isPlayerOwnedTear(tear) -> boolean` ownership boundary.
- Produces: `isValidTarget(entity) -> boolean`, `findNearestTarget(position) -> Entity|nil`, `steerTowardTarget(tear, target)`, and an enhanced `onTearUpdate(_, tear)` callback.

- [ ] **Step 1: Write failing behavior tests**

Replace the current test file with:

```python
from pathlib import Path


WORKSPACE_MOD_DIR = Path(r"D:\Code\isaac\player_homing_tears")
INSTALLED_MOD_DIR = Path(
    r"E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears"
)


def read_workspace_lua():
    return (WORKSPACE_MOD_DIR / "main.lua").read_text(encoding="utf-8")


def test_player_tears_receive_all_enhancements():
    lua = read_workspace_lua()

    assert "TearFlags.TEAR_HOMING" in lua
    assert "TearFlags.TEAR_PIERCING" in lua
    assert "TearFlags.TEAR_SPECTRAL" in lua
    assert "tear.Height = FLIGHT_HEIGHT" in lua
    assert "tear.FallingSpeed = 0" in lua
    assert "tear.FallingAcceleration = 0" in lua
    assert "local FLIGHT_HEIGHT = -23" in lua


def test_strong_homing_uses_only_valid_hostile_targets():
    lua = read_workspace_lua()

    assert "local HOMING_STRENGTH = 0.30" in lua
    assert "Isaac.GetRoomEntities()" in lua
    assert "entity:IsActiveEnemy(false)" in lua
    assert "entity:IsVulnerableEnemy()" in lua
    assert "not entity:IsDead()" in lua
    assert "EntityFlag.FLAG_FRIENDLY" in lua
    assert "target.Position - tear.Position" in lua
    assert "blendedVelocity:Resized(speed)" in lua


def test_enemy_projectiles_remain_unchanged():
    lua = read_workspace_lua()

    assert "EntityType.ENTITY_PLAYER" in lua
    assert "EntityType.ENTITY_FAMILIAR" in lua
    assert "ModCallbacks.MC_POST_TEAR_UPDATE" in lua
    assert "MC_POST_PROJECTILE_UPDATE" not in lua
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m pytest tests/test_player_homing_tears.py -q`

Expected: `test_player_tears_receive_all_enhancements` and `test_strong_homing_uses_only_valid_hostile_targets` fail because piercing, spectral, range, target selection, and manual steering are absent.

- [ ] **Step 3: Implement the minimal Lua behavior**

Replace `D:\Code\isaac\player_homing_tears\main.lua` with:

```lua
local mod = RegisterMod("Player Homing Tears", 1)

local HOMING_FLAG = TearFlags.TEAR_HOMING
local PIERCING_FLAG = TearFlags.TEAR_PIERCING
local SPECTRAL_FLAG = TearFlags.TEAR_SPECTRAL
local HOMING_STRENGTH = 0.30
local FLIGHT_HEIGHT = -23
local MIN_VECTOR_LENGTH = 0.001

local function getPlayerOwner(entity)
    if entity == nil then
        return nil
    end

    if entity.Type == EntityType.ENTITY_PLAYER then
        return entity:ToPlayer()
    end

    if entity.Type == EntityType.ENTITY_FAMILIAR then
        local familiar = entity:ToFamiliar()
        if familiar ~= nil then
            return familiar.Player
        end
    end

    return nil
end

local function isPlayerOwnedTear(tear)
    if tear == nil then
        return false
    end

    if getPlayerOwner(tear.SpawnerEntity) ~= nil then
        return true
    end

    if getPlayerOwner(tear.Parent) ~= nil then
        return true
    end

    return false
end

local function addFlagIfMissing(tear, flag)
    if not tear:HasTearFlags(flag) then
        tear:AddTearFlags(flag)
    end
end

local function applyTearEnhancements(tear)
    addFlagIfMissing(tear, HOMING_FLAG)
    addFlagIfMissing(tear, PIERCING_FLAG)
    addFlagIfMissing(tear, SPECTRAL_FLAG)

    tear.Height = FLIGHT_HEIGHT
    tear.FallingSpeed = 0
    tear.FallingAcceleration = 0
end

local function isValidTarget(entity)
    return entity:IsActiveEnemy(false)
        and entity:IsVulnerableEnemy()
        and not entity:IsDead()
        and not entity:HasEntityFlags(EntityFlag.FLAG_FRIENDLY)
end

local function findNearestTarget(position)
    local nearestTarget = nil
    local nearestDistance = math.huge

    for _, entity in ipairs(Isaac.GetRoomEntities()) do
        if isValidTarget(entity) then
            local distance = position:DistanceSquared(entity.Position)
            if distance < nearestDistance then
                nearestTarget = entity
                nearestDistance = distance
            end
        end
    end

    return nearestTarget
end

local function steerTowardTarget(tear, target)
    local speed = tear.Velocity:Length()
    local targetOffset = target.Position - tear.Position

    if speed <= MIN_VECTOR_LENGTH or targetOffset:Length() <= MIN_VECTOR_LENGTH then
        return
    end

    local desiredVelocity = targetOffset:Resized(speed)
    local blendedVelocity = tear.Velocity * (1 - HOMING_STRENGTH)
        + desiredVelocity * HOMING_STRENGTH

    if blendedVelocity:Length() > MIN_VECTOR_LENGTH then
        tear.Velocity = blendedVelocity:Resized(speed)
    end
end

local function onTearUpdate(_, tear)
    if not isPlayerOwnedTear(tear) then
        return
    end

    applyTearEnhancements(tear)

    local target = findNearestTarget(tear.Position)
    if target ~= nil then
        steerTowardTarget(tear, target)
    end
end

mod:AddCallback(ModCallbacks.MC_POST_TEAR_UPDATE, onTearUpdate)

Isaac.DebugString("[Player Homing Tears] loaded")
```

- [ ] **Step 4: Synchronize the installed Lua file**

Run:

```powershell
Copy-Item -Force -LiteralPath 'D:\Code\isaac\player_homing_tears\main.lua' -Destination 'E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua'
```

Expected: exit code `0`.

- [ ] **Step 5: Run behavior tests and verify GREEN**

Run: `python -m pytest tests/test_player_homing_tears.py -q`

Expected: `3 passed`.

---

### Task 2: Metadata And Copy Integrity

**Files:**
- Modify: `D:\Code\isaac\tests\test_player_homing_tears.py`
- Modify: `D:\Code\isaac\player_homing_tears\metadata.xml`
- Install: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\metadata.xml`

**Interfaces:**
- Consumes: the workspace and installed mod directory constants from Task 1.
- Produces: synchronized workspace/install copies and metadata version `1.1`.

- [ ] **Step 1: Add failing synchronization and metadata tests**

Append:

```python
def test_workspace_and_installed_mod_are_synchronized():
    for filename in ("main.lua", "metadata.xml"):
        workspace_content = (WORKSPACE_MOD_DIR / filename).read_bytes()
        installed_content = (INSTALLED_MOD_DIR / filename).read_bytes()
        assert installed_content == workspace_content


def test_metadata_describes_enhanced_tears():
    xml = (WORKSPACE_MOD_DIR / "metadata.xml").read_text(encoding="utf-8")

    assert "<name>Player Homing Tears</name>" in xml
    assert "<id>0</id>" in xml
    assert "<version>1.1</version>" in xml
    assert "unlimited range, piercing, spectral movement, and strong homing" in xml
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m pytest tests/test_player_homing_tears.py -q`

Expected: metadata test fails because the version is `1.0` and the old description only mentions homing.

- [ ] **Step 3: Update workspace metadata**

Replace `D:\Code\isaac\player_homing_tears\metadata.xml` with:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<metadata>
    <name>Player Homing Tears</name>
    <directory>player_homing_tears</directory>
    <id>0</id>
    <description>Player and friendly familiar tears gain unlimited range, piercing, spectral movement, and strong homing. Enemy projectiles are unchanged.</description>
    <version>1.1</version>
    <visibility>Private</visibility>
    <tag id="Lua"/>
</metadata>
```

- [ ] **Step 4: Synchronize installed metadata**

Run:

```powershell
Copy-Item -Force -LiteralPath 'D:\Code\isaac\player_homing_tears\metadata.xml' -Destination 'E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\metadata.xml'
```

Expected: exit code `0`.

- [ ] **Step 5: Run all tests and verify GREEN**

Run: `python -m pytest tests/test_player_homing_tears.py -q`

Expected: `5 passed`.

---

### Task 3: Final Static Verification

**Files:**
- Verify: `D:\Code\isaac\player_homing_tears\main.lua`
- Verify: `D:\Code\isaac\player_homing_tears\metadata.xml`
- Verify: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua`
- Verify: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\metadata.xml`

**Interfaces:**
- Consumes: completed artifacts from Tasks 1 and 2.
- Produces: fresh evidence that tests pass, installed files match, and enemy projectile callbacks remain absent.

- [ ] **Step 1: Run the complete test file**

Run: `python -m pytest tests/test_player_homing_tears.py -q`

Expected: `5 passed` with exit code `0`.

- [ ] **Step 2: Compare workspace and installed hashes**

Run:

```powershell
Get-FileHash -Algorithm SHA256 'D:\Code\isaac\player_homing_tears\main.lua','E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua','D:\Code\isaac\player_homing_tears\metadata.xml','E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\metadata.xml'
```

Expected: the two `main.lua` hashes match and the two `metadata.xml` hashes match.

- [ ] **Step 3: Confirm callback scope**

Run: `rg -n "MC_POST_TEAR_UPDATE|MC_POST_PROJECTILE_UPDATE" 'E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua'`

Expected: exactly one `MC_POST_TEAR_UPDATE` line and no `MC_POST_PROJECTILE_UPDATE` line.

- [ ] **Step 4: Record the runtime verification boundary**

Report that static verification is complete, but in-game observation remains for the user: enable `Player Homing Tears`, fire across a room with enemies and rocks, and confirm strong curved tracking, piercing, spectral passage, and no range-based falling.
