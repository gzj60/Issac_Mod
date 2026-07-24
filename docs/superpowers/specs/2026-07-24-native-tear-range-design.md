# Native Tear Range Design

## Goal

Remove unlimited range from player-owned and friendly-familiar-owned tears while preserving their homing, piercing, spectral, and strong steering effects. Friendly lasers must keep unlimited distance and all existing laser enhancements.

## Tear Behavior

Delete the `FLIGHT_HEIGHT` constant and stop assigning `tear.Height`, `tear.FallingSpeed`, or `tear.FallingAcceleration` in `applyTearEnhancements`. The game will once again determine tear range from the player, familiar, items, and other native effects.

Keep these tear behaviors unchanged:

- `TearFlags.TEAR_HOMING`
- `TearFlags.TEAR_PIERCING`
- `TearFlags.TEAR_SPECTRAL`
- Manual velocity steering with `HOMING_STRENGTH = 0.30`
- Player/friendly-familiar ownership filtering

## Laser Behavior

Do not modify laser callbacks or steering. `applyLaserEnhancements` will continue calling `laser:SetMaxDistance(0)`, so friendly lasers retain unlimited distance, homing, piercing, spectral behavior, and type-specific steering.

## Enemy Behavior

Enemy tears, lasers, and projectiles remain unchanged. No projectile update callback will be added.

## Metadata

Set the mod version to `1.3`. Replace the description with wording that distinguishes the effects:

`Player and friendly familiar tears gain piercing, spectral movement, and strong homing. Their lasers also gain unlimited range. Enemy attacks are unchanged.`

## Tests

Update the tear enhancement test to require the three tear flags and to assert that `FLIGHT_HEIGHT`, `tear.Height`, `tear.FallingSpeed`, and `tear.FallingAcceleration` are absent from `main.lua`.

Keep the laser test requirement for `laser:SetMaxDistance(0)`. Update metadata expectations to version `1.3` and the new split description. Continue verifying workspace and installed copies byte-for-byte.

## Verification

Use a red-green cycle: change tests first and confirm they fail against version 1.2, remove only the tear range overrides, synchronize `main.lua`, update and synchronize metadata, then run all tests. Compare workspace and installed hashes and confirm the installed Lua still includes `SetMaxDistance(0)` but none of the removed tear range properties.

Runtime verification requires firing normal tears in game and confirming they fall according to the current character's range while lasers still reach their existing unlimited distance.
