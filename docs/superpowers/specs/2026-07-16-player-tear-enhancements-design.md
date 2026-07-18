# Player Tear Enhancements Design

## Goal

Extend the existing `Player Homing Tears` mod so every tear fired by a player or a friendly familiar has unlimited range, piercing, spectral movement, and strong smooth homing. Enemy projectiles and enemy-owned tears must remain unchanged.

## Scope

- Keep the existing independent mod folder and ownership filtering.
- Apply all enhancements from `MC_POST_TEAR_UPDATE` so newly spawned and already active friendly tears are covered.
- Do not add menus, configuration, auto-fire behavior, damage changes, or enemy projectile callbacks.

## Tear Effects

Friendly tears receive these native flags:

- `TearFlags.TEAR_HOMING`
- `TearFlags.TEAR_PIERCING`
- `TearFlags.TEAR_SPECTRAL`

Unlimited range is implemented by setting `Height` to `-23`, `FallingSpeed` to `0`, and `FallingAcceleration` to `0` on every update. Room boundaries and normal game cleanup still govern the tear lifetime.

## Strong Homing

On each friendly tear update, scan room entities and select the nearest entity that is alive, active, vulnerable, and an enemy. If no valid target exists, preserve the current velocity.

When a target exists:

1. Compute a desired velocity pointing from the tear to the target.
2. Preserve the tear's current speed magnitude.
3. Blend the current and desired velocity using a strong turn factor of `0.30` per update.
4. Resize the blended vector back to the original speed.

This produces visibly strong tracking without instant direction changes. Zero-speed tears and targets at the tear's exact position are left unchanged to avoid invalid vector resizing.

## Ownership And Safety

The current ownership rule remains the boundary: a tear is friendly only when its `SpawnerEntity` or `Parent` resolves to a player or to a familiar with a player owner. The mod continues to register no projectile callback, so enemy `EntityProjectile` objects are untouched.

## Files

- Update workspace source: `player_homing_tears/main.lua`
- Update installed source: `E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua`
- Update the metadata description and set version `1.1` in both copies.
- Extend `tests/test_player_homing_tears.py` with static checks for the three flags, range properties, target validation, and steering logic.

## Verification

Follow a red-green cycle: add expectations first and confirm they fail, implement the minimal Lua changes, synchronize the installed copy, then run the complete Python test. Also compare workspace and installed files byte-for-byte and scan the Lua source to confirm no projectile callback was introduced.

Runtime behavior must finally be checked in the game by enabling `Player Homing Tears`, entering a room with enemies, and observing strong curved tracking, wall/rock passage, enemy piercing, and no range-based falling.
