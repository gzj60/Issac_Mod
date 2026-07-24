# Native Tear Range Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore native range for friendly tears while preserving all tear combat enhancements and keeping friendly lasers at unlimited distance.

**Architecture:** Remove only the constant and three per-frame tear flight assignments that override native range. Keep tear flags, manual homing, laser flags, laser steering, and `laser:SetMaxDistance(0)` unchanged, then update metadata to version 1.3.

**Tech Stack:** The Binding of Isaac Repentance+ Lua API, XML metadata, Python 3 with pytest, PowerShell file synchronization, local Git.

## Global Constraints

- Friendly tears retain homing, piercing, spectral movement, and `HOMING_STRENGTH = 0.30` steering.
- `FLIGHT_HEIGHT`, `tear.Height`, `tear.FallingSpeed`, and `tear.FallingAcceleration` must be absent from `main.lua`.
- Friendly lasers retain `laser:SetMaxDistance(0)` and all existing enhancements.
- Enemy tears, lasers, and projectiles remain unchanged.
- Metadata version becomes `1.3` with separate tear and laser effect wording.
- Workspace and installed mod files remain byte-for-byte synchronized.
- Execute implementation on branch `feature/native-tear-range`.

Before Task 1, run:

```powershell
git switch -c feature/native-tear-range
```

Expected: Git reports a new branch named `feature/native-tear-range`.

---

### Task 1: Restore Native Tear Range

**Files:**
- Modify: `D:\Code\isaac\tests\test_player_homing_tears.py`
- Modify: `D:\Code\isaac\player_homing_tears\main.lua`
- Install: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua`

**Interfaces:**
- Consumes: `applyTearEnhancements(tear)` and the existing tear callback.
- Produces: tear enhancement behavior that adds three flags but leaves all range physics untouched.

- [ ] **Step 1: Write the failing native-range test**

Replace `test_player_tears_receive_all_enhancements` with:

```python
def test_player_tears_keep_native_range_and_receive_other_enhancements():
    lua = read_workspace_lua()

    assert "TearFlags.TEAR_HOMING" in lua
    assert "TearFlags.TEAR_PIERCING" in lua
    assert "TearFlags.TEAR_SPECTRAL" in lua
    assert "FLIGHT_HEIGHT" not in lua
    assert "tear.Height" not in lua
    assert "tear.FallingSpeed" not in lua
    assert "tear.FallingAcceleration" not in lua
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
python -m pytest tests/test_player_homing_tears.py::test_player_tears_keep_native_range_and_receive_other_enhancements -q
```

Expected: FAIL because `FLIGHT_HEIGHT` and the three tear flight assignments are still present.

- [ ] **Step 3: Remove the tear range overrides**

Apply this exact change to `D:\Code\isaac\player_homing_tears\main.lua`:

```diff
-local FLIGHT_HEIGHT = -23

 local function applyTearEnhancements(tear)
     addFlagIfMissing(tear, HOMING_FLAG)
     addFlagIfMissing(tear, PIERCING_FLAG)
     addFlagIfMissing(tear, SPECTRAL_FLAG)
-
-    tear.Height = FLIGHT_HEIGHT
-    tear.FallingSpeed = 0
-    tear.FallingAcceleration = 0
 end
```

- [ ] **Step 4: Synchronize the installed Lua file**

Run:

```powershell
Copy-Item -Force -LiteralPath 'D:\Code\isaac\player_homing_tears\main.lua' -Destination 'E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua'
```

Expected: exit code `0`.

- [ ] **Step 5: Run all tests and verify GREEN**

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass; metadata remains version `1.2` at this checkpoint.

- [ ] **Step 6: Commit the behavior change**

Run:

```powershell
git add tests/test_player_homing_tears.py player_homing_tears/main.lua
git commit -m "fix: restore native tear range"
```

Expected: one commit containing only the tear test and Lua behavior change.

---

### Task 2: Version 1.3 Metadata

**Files:**
- Modify: `D:\Code\isaac\tests\test_player_homing_tears.py`
- Modify: `D:\Code\isaac\player_homing_tears\metadata.xml`
- Install: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\metadata.xml`

**Interfaces:**
- Consumes: workspace and installed mod directory constants in the test file.
- Produces: version `1.3` metadata that distinguishes native-range tears from unlimited-distance lasers.

- [ ] **Step 1: Update metadata expectations**

Replace `test_metadata_describes_enhanced_tears_and_lasers` with:

```python
def test_metadata_describes_native_range_tears_and_unlimited_lasers():
    xml = (WORKSPACE_MOD_DIR / "metadata.xml").read_text(encoding="utf-8")

    assert "<name>Player Homing Tears</name>" in xml
    assert "<id>0</id>" in xml
    assert "<version>1.3</version>" in xml
    assert "tears gain piercing, spectral movement, and strong homing" in xml
    assert "lasers also gain unlimited range" in xml
    assert "Enemy attacks are unchanged" in xml
```

- [ ] **Step 2: Run the metadata test and verify RED**

Run:

```powershell
python -m pytest tests/test_player_homing_tears.py::test_metadata_describes_native_range_tears_and_unlimited_lasers -q
```

Expected: FAIL because metadata is version `1.2` and says tears have unlimited range.

- [ ] **Step 3: Update workspace metadata**

Replace `D:\Code\isaac\player_homing_tears\metadata.xml` with:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<metadata>
    <name>Player Homing Tears</name>
    <directory>player_homing_tears</directory>
    <id>0</id>
    <description>Player and friendly familiar tears gain piercing, spectral movement, and strong homing. Their lasers also gain unlimited range. Enemy attacks are unchanged.</description>
    <version>1.3</version>
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

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit the metadata change**

Run:

```powershell
git add tests/test_player_homing_tears.py player_homing_tears/metadata.xml
git commit -m "docs: describe native tear range"
```

Expected: one commit containing only metadata and its test expectations.

---

### Task 3: Final Verification

**Files:**
- Verify: `D:\Code\isaac\player_homing_tears\main.lua`
- Verify: `D:\Code\isaac\player_homing_tears\metadata.xml`
- Verify: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua`
- Verify: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\metadata.xml`

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: fresh test, installation, Git, and scope evidence.

- [ ] **Step 1: Run the complete test suite**

Run: `python -m pytest -q`

Expected: all tests pass with exit code `0`.

- [ ] **Step 2: Verify removed and retained Lua behavior**

Run:

```powershell
rg -n 'FLIGHT_HEIGHT|tear\.Height|tear\.FallingSpeed|tear\.FallingAcceleration|laser:SetMaxDistance\(0\)' 'E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua'
```

Expected: exactly one match for `laser:SetMaxDistance(0)` and no matches for the four removed tear range terms.

- [ ] **Step 3: Compare workspace and installed hashes**

Run:

```powershell
Get-FileHash -Algorithm SHA256 'D:\Code\isaac\player_homing_tears\main.lua','E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua','D:\Code\isaac\player_homing_tears\metadata.xml','E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\metadata.xml'
```

Expected: the two Lua hashes match and the two metadata hashes match.

- [ ] **Step 4: Verify branch state**

Run:

```powershell
git status --short
git log -3 --oneline
```

Expected: clean status with the two implementation commits above the design and plan commits.

- [ ] **Step 5: Record runtime verification boundary**

Report that normal tears must be fired in game to confirm they fall at the character's native range while lasers retain unlimited distance.
