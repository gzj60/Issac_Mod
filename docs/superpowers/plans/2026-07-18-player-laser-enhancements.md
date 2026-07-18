# Player Laser Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the installed `Player Homing Tears` mod so all player-owned and friendly-familiar-owned lasers receive unlimited range, piercing, spectral movement, and strong type-specific homing without affecting enemy attacks.

**Architecture:** Keep the mod in one Lua file and share ownership, target selection, flag application, and vector steering between tears and lasers. Use laser init for the first directional correction, laser update for flags/range and continued steering, angle blending for linear lasers, and velocity blending for moving circular lasers.

**Tech Stack:** The Binding of Isaac Repentance+ Lua API, XML metadata, Python 3 with pytest, PowerShell file synchronization.

## Global Constraints

- Preserve all existing friendly tear behavior.
- Cover Brimstone, Technology, Technology X, and other player/friendly-familiar lasers.
- Only attacks whose `SpawnerEntity` or `Parent` resolves to a player or player-owned familiar may change.
- Add homing, piercing, and spectral tear flags to friendly lasers.
- Call `laser:SetMaxDistance(0)` and never modify `laser.Timeout` or damage.
- Use the existing homing strength `0.30` and minimum vector length `0.001`.
- Use `MC_POST_LASER_INIT` for initial steering and `MC_POST_LASER_UPDATE` for effects and repeated steering.
- Keep enemy projectile callbacks absent.
- Set metadata version to `1.2`.
- The workspace is not a Git repository, so commit steps are unavailable.

---

### Task 1: Type-Specific Friendly Laser Enhancements

**Files:**
- Modify: `D:\Code\isaac\tests\test_player_homing_tears.py`
- Modify: `D:\Code\isaac\player_homing_tears\main.lua`
- Install: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua`

**Interfaces:**
- Consumes: `getPlayerOwner(entity) -> EntityPlayer|nil`, `findNearestTarget(position) -> Entity|nil`, constants `HOMING_STRENGTH` and `MIN_VECTOR_LENGTH`.
- Produces: `isPlayerOwnedAttack(attack) -> boolean`, `steerVelocityTowardTarget(entity, target)`, `steerLinearLaserTowardTarget(laser, target)`, `steerLaserTowardTarget(laser)`, `onLaserInit(_, laser)`, and `onLaserUpdate(_, laser)`.

- [ ] **Step 1: Add failing laser behavior tests**

In `D:\Code\isaac\tests\test_player_homing_tears.py`, replace the existing `test_strong_homing_uses_only_valid_hostile_targets` function with the first function below, then append the remaining three functions:

```python
def test_strong_homing_uses_only_valid_hostile_targets():
    lua = read_workspace_lua()

    assert "local HOMING_STRENGTH = 0.30" in lua
    assert "Isaac.GetRoomEntities()" in lua
    assert "entity:IsActiveEnemy(false)" in lua
    assert "entity:IsVulnerableEnemy()" in lua
    assert "not entity:IsDead()" in lua
    assert "EntityFlag.FLAG_FRIENDLY" in lua
    assert "target.Position - entity.Position" in lua
    assert "blendedVelocity:Resized(speed)" in lua


def test_player_lasers_receive_all_enhancements():
    lua = read_workspace_lua()

    assert "ModCallbacks.MC_POST_LASER_INIT" in lua
    assert "ModCallbacks.MC_POST_LASER_UPDATE" in lua
    assert "applyLaserEnhancements(laser)" in lua
    assert "addFlagIfMissing(laser, HOMING_FLAG)" in lua
    assert "addFlagIfMissing(laser, PIERCING_FLAG)" in lua
    assert "addFlagIfMissing(laser, SPECTRAL_FLAG)" in lua
    assert "laser:SetMaxDistance(0)" in lua
    assert "laser.Timeout" not in lua


def test_lasers_use_type_specific_strong_homing():
    lua = read_workspace_lua()

    assert "laser:IsCircleLaser()" in lua
    assert "steerVelocityTowardTarget(laser, target)" in lua
    assert "targetOffset:GetAngleDegrees()" in lua
    assert "(targetAngle - laser.AngleDegrees + 180) % 360 - 180" in lua
    assert "angleDifference * HOMING_STRENGTH" in lua


def test_enemy_lasers_remain_unchanged():
    lua = read_workspace_lua()

    assert "local function isPlayerOwnedAttack(attack)" in lua
    assert "if not isPlayerOwnedAttack(laser) then" in lua
    assert "MC_POST_PROJECTILE_UPDATE" not in lua
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m pytest tests/test_player_homing_tears.py -q`

Expected: laser tests fail because neither laser callback, range handling, nor type-specific steering exists.

- [ ] **Step 3: Implement shared tear and laser behavior**

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

local function isPlayerOwnedAttack(attack)
    if attack == nil then
        return false
    end

    if getPlayerOwner(attack.SpawnerEntity) ~= nil then
        return true
    end

    if getPlayerOwner(attack.Parent) ~= nil then
        return true
    end

    return false
end

local function addFlagIfMissing(attack, flag)
    if not attack:HasTearFlags(flag) then
        attack:AddTearFlags(flag)
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

local function applyLaserEnhancements(laser)
    addFlagIfMissing(laser, HOMING_FLAG)
    addFlagIfMissing(laser, PIERCING_FLAG)
    addFlagIfMissing(laser, SPECTRAL_FLAG)
    laser:SetMaxDistance(0)
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

local function steerVelocityTowardTarget(entity, target)
    local speed = entity.Velocity:Length()
    local targetOffset = target.Position - entity.Position

    if speed <= MIN_VECTOR_LENGTH or targetOffset:Length() <= MIN_VECTOR_LENGTH then
        return
    end

    local desiredVelocity = targetOffset:Resized(speed)
    local blendedVelocity = entity.Velocity * (1 - HOMING_STRENGTH)
        + desiredVelocity * HOMING_STRENGTH

    if blendedVelocity:Length() > MIN_VECTOR_LENGTH then
        entity.Velocity = blendedVelocity:Resized(speed)
    end
end

local function steerLinearLaserTowardTarget(laser, target)
    local targetOffset = target.Position - laser.Position
    if targetOffset:Length() <= MIN_VECTOR_LENGTH then
        return
    end

    local targetAngle = targetOffset:GetAngleDegrees()
    local angleDifference = (targetAngle - laser.AngleDegrees + 180) % 360 - 180
    laser.AngleDegrees = laser.AngleDegrees
        + angleDifference * HOMING_STRENGTH
end

local function steerLaserTowardTarget(laser)
    local target = findNearestTarget(laser.Position)
    if target == nil then
        return
    end

    if laser:IsCircleLaser() then
        steerVelocityTowardTarget(laser, target)
    else
        steerLinearLaserTowardTarget(laser, target)
    end
end

local function onTearUpdate(_, tear)
    if not isPlayerOwnedAttack(tear) then
        return
    end

    applyTearEnhancements(tear)

    local target = findNearestTarget(tear.Position)
    if target ~= nil then
        steerVelocityTowardTarget(tear, target)
    end
end

local function onLaserInit(_, laser)
    if not isPlayerOwnedAttack(laser) then
        return
    end

    steerLaserTowardTarget(laser)
end

local function onLaserUpdate(_, laser)
    if not isPlayerOwnedAttack(laser) then
        return
    end

    applyLaserEnhancements(laser)
    steerLaserTowardTarget(laser)
end

mod:AddCallback(ModCallbacks.MC_POST_TEAR_UPDATE, onTearUpdate)
mod:AddCallback(ModCallbacks.MC_POST_LASER_INIT, onLaserInit)
mod:AddCallback(ModCallbacks.MC_POST_LASER_UPDATE, onLaserUpdate)

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

Expected: all behavior and synchronization tests pass while metadata remains version `1.1`.

---

### Task 2: Version 1.2 Metadata

**Files:**
- Modify: `D:\Code\isaac\tests\test_player_homing_tears.py`
- Modify: `D:\Code\isaac\player_homing_tears\metadata.xml`
- Install: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\metadata.xml`

**Interfaces:**
- Consumes: workspace and installed mod directory constants from the test file.
- Produces: synchronized metadata describing enhanced tears and lasers at version `1.2`.

- [ ] **Step 1: Update metadata expectations to fail on version 1.1**

Replace `test_metadata_describes_enhanced_tears` with:

```python
def test_metadata_describes_enhanced_tears_and_lasers():
    xml = (WORKSPACE_MOD_DIR / "metadata.xml").read_text(encoding="utf-8")

    assert "<name>Player Homing Tears</name>" in xml
    assert "<id>0</id>" in xml
    assert "<version>1.2</version>" in xml
    assert "tears and lasers gain unlimited range" in xml
    assert "Enemy attacks are unchanged" in xml
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m pytest tests/test_player_homing_tears.py -q`

Expected: the metadata test fails because the current metadata is version `1.1` and does not mention lasers.

- [ ] **Step 3: Update workspace metadata**

Replace `D:\Code\isaac\player_homing_tears\metadata.xml` with:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<metadata>
    <name>Player Homing Tears</name>
    <directory>player_homing_tears</directory>
    <id>0</id>
    <description>Player and friendly familiar tears and lasers gain unlimited range, piercing, spectral movement, and strong homing. Enemy attacks are unchanged.</description>
    <version>1.2</version>
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

- [ ] **Step 5: Run the complete test file and verify GREEN**

Run: `python -m pytest tests/test_player_homing_tears.py -q`

Expected: every test passes.

---

### Task 3: Final Static Verification

**Files:**
- Verify: `D:\Code\isaac\player_homing_tears\main.lua`
- Verify: `D:\Code\isaac\player_homing_tears\metadata.xml`
- Verify: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua`
- Verify: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\metadata.xml`

**Interfaces:**
- Consumes: completed artifacts from Tasks 1 and 2.
- Produces: fresh evidence for tests, copy integrity, callback scope, and unchanged laser lifetime.

- [ ] **Step 1: Run all tests**

Run: `python -m pytest tests/test_player_homing_tears.py -q`

Expected: all tests pass with exit code `0`.

- [ ] **Step 2: Compare workspace and installed hashes**

Run:

```powershell
Get-FileHash -Algorithm SHA256 'D:\Code\isaac\player_homing_tears\main.lua','E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua','D:\Code\isaac\player_homing_tears\metadata.xml','E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\metadata.xml'
```

Expected: the two `main.lua` hashes match and the two `metadata.xml` hashes match.

- [ ] **Step 3: Confirm callback and lifetime scope**

Run:

```powershell
rg -n 'MC_POST_TEAR_UPDATE|MC_POST_LASER_INIT|MC_POST_LASER_UPDATE|MC_POST_PROJECTILE_UPDATE|laser.Timeout' 'E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua'
```

Expected: one tear update callback, one laser init callback, one laser update callback, and no projectile callback or `laser.Timeout` assignment.

- [ ] **Step 4: Record runtime verification boundary**

Report that static verification is complete, but the user must verify Brimstone/Technology and Technology X in game because no standalone Isaac Lua runtime is available.
