# Player Laser Enhancements Design

## Goal

Extend `Player Homing Tears` version 1.1 so every laser created by a player or friendly familiar receives the same unlimited-range, piercing, spectral, and strong-homing treatment as friendly tears. Enemy lasers and enemy projectiles must remain unchanged.

## Scope

- Keep the independent `player_homing_tears` mod folder.
- Preserve all existing friendly tear behavior.
- Cover linear lasers such as Brimstone and Technology, moving circular lasers such as Technology X, and other player-owned circular lasers.
- Do not replace, respawn, extend the lifetime of, or change the damage of any laser.

## Callbacks And Ownership

Register `MC_POST_LASER_INIT` for the first directional adjustment of newly created linear or moving circular lasers. This gives one-frame Technology-style lasers a target before their normal lifetime ends. Do not apply tear flags in this callback because the API warns that they may not be complete during laser initialization.

Register `MC_POST_LASER_UPDATE` for native flags, maximum distance, and repeated smooth steering of longer-lived lasers. Reuse the existing ownership resolution in both callbacks: an attack is friendly only when its `SpawnerEntity` or `Parent` resolves to a player or to a familiar with a player owner.

Rename `isPlayerOwnedTear` to `isPlayerOwnedAttack` so tears and lasers share exactly one ownership boundary. Enemy-owned lasers return before any properties are modified.

## Shared Laser Effects

Every friendly laser update will:

- Add `TearFlags.TEAR_HOMING` if missing.
- Add `TearFlags.TEAR_PIERCING` if missing.
- Add `TearFlags.TEAR_SPECTRAL` if missing.
- Call `laser:SetMaxDistance(0)` to disable range trimming.

The mod will not modify `laser.Timeout`, so one-frame, timed, and continuous lasers retain their normal duration. Piercing is already natural for many lasers, but the flag is added consistently for supported item interactions. Spectral behavior is delegated to the game's laser handling through the native flag.

## Strong Homing

Reuse `findNearestTarget(position)` and the existing hostile-target filter. If there is no valid target, preserve the laser's current direction and velocity. Run the same classification and steering helper once from laser initialization and again on each laser update.

### Linear Lasers

For `laser:IsCircleLaser() == false`, calculate the angle from the laser position to the nearest target. Normalize the difference from the current `AngleDegrees` to the range `[-180, 180]`, then add `angleDifference * 0.30`. This gives the shortest strong, smooth turn without an instantaneous snap.

### Moving Circular Lasers

For circular lasers whose inherited `Velocity` length is greater than `0.001`, steer the velocity toward the target using the same `0.30` vector blend already used for tears, then resize the blended vector to preserve the original speed. This covers Technology X-style moving rings.

### Stationary Circular Lasers

For circular lasers with zero or near-zero velocity, do not force a position or angle. They retain the native homing flag because stationary and parent-following rings do not have a safe travel direction to rewrite.

## Edge Cases

- Skip manual steering when the target is at the laser's exact position.
- Skip vector steering when laser velocity is zero or the blended vector is too small to resize safely.
- Do not steer enemy lasers even if they already carry homing tear flags.
- Do not register or modify projectile callbacks.

## Files

- Update `D:\Code\isaac\player_homing_tears\main.lua`.
- Update `D:\Code\isaac\player_homing_tears\metadata.xml` to version `1.2` and describe tears and lasers.
- Synchronize both files to `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears`.
- Extend `D:\Code\isaac\tests\test_player_homing_tears.py` with static checks for both laser callbacks, ownership filter, flags, distance, linear angle steering, circular velocity steering, unchanged timeout, and enemy projectile isolation.

## Verification

Use a red-green test cycle before modifying production files. Finish by running the complete Python test, comparing workspace and installed files byte-for-byte, and confirming callbacks include tear update plus laser init/update but no projectile update.

Runtime verification must be performed in game with at least Brimstone or Technology and Technology X. Confirm that linear lasers curve strongly toward enemies, moving rings alter course while retaining speed, laser duration remains normal, range trimming is removed, and enemy lasers behave normally.
