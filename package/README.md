# TameProtection

Wild creatures and tamed creatures no longer treat each other as enemies.

> **AI disclosure.** This mod was written with AI assistance (Claude) — the Harmony patch,
> configuration, build tooling and documentation. It was reviewed and tested against a live
> Valheim 1.0.15 dedicated server. Listed under the **AI Generated** category.

This restores the `ProtectTamedFromEnemies` behaviour from Wendigo's CreatureCarry
1.3.0, which Eradorn's CustomCreatureCarry fork deliberately left out ("There are no
egg-hatching, OdinMounts, ChebsNecromancy or general tame-protection changes").

The effect is **mutual**: enemies will not target your tames, and your tames will not
start fights with enemies. Wild-vs-wild and tame-vs-tame hostility is untouched, so
normal combat and your own attacks on tames work exactly as in vanilla.

## Install

**Install on the server and on every client.**

The patch runs client-side - `BaseAI.UpdateAI` is gated on `IsOwner`, so hostility checks
happen on whichever peer owns the creature, which on a dedicated server is the nearby
player's client. Every player therefore needs it; a player without it still sees their own
creatures hunt tames.

The server copy makes the configuration authoritative. Without it, nothing is synced and
each player silently keeps their own local settings - which matters here, because clients
own different creatures, so mismatched settings protect tames or not depending on who is
standing nearest.

- **r2modman / Thunderstore Mod Manager**: search for `TameProtection` by `N3bby` and install.
- **Manual**: copy `plugins/TameProtection/` into `BepInEx/plugins/`.
- **Dedicated server**: copy the same folder into the server's BepInEx plugins directory.

There is no version handshake. A client without the mod simply does not get the
protection; nothing breaks.

## Configuration

`BepInEx/config/com.n3bby.tameprotection.cfg`

| Setting | Default | Synced | Meaning |
| --- | --- | --- | --- |
| `ProtectTamedFromEnemies` | `true` | yes | Master switch. |
| `ProtectedPrefabs` | empty | yes | Comma-separated prefab names (e.g. `Asksvin,Lox`). Empty protects every tamed creature. |
| `LockConfiguration` | `true` | yes | While connected, only server admins may change synced settings. |
| `DebugLogging` | `false` | no | Logs every suppressed hostility check. Noisy; testing only. |

Synced settings are owned by the server and pushed to clients on connect. Admins can
change them live from an in-game configuration manager. Clients joining a server without
the mod keep their own local values.

## How it works

A single Harmony postfix on `BaseAI.IsEnemy(Character, Character)`. The instance
overload compiles to `return BaseAI.IsEnemy(this.m_character, other)`, so patching the
static method covers every caller. When exactly one of the two characters is tamed, the
result is forced to `false`.

Built against Valheim 1.0.15 / BepInExPack 5.4.2350.

## Credits

The `ProtectTamedFromEnemies` behaviour originates in
[Wendigo's CreatureCarry 1.3.0](https://thunderstore.io/c/valheim/p/Wendigo/CreatureCarry/).
That package shipped without a license file or source-repository URL, so no upstream code
was reused here: this plugin is an independent implementation written against the
decompiled `BaseAI.IsEnemy` signature in Valheim 1.0.15. Credit for the original idea and
for identifying the right hook belongs to Wendigo.

Eradorn's [CustomCreatureCarry](https://thunderstore.io/c/valheim/p/Eradorn/CustomCreatureCarry/)
is a 1.0 fork of CreatureCarry that keeps the carrying and deliberately omits the
tame-protection feature. This plugin exists to fill that gap and is meant to sit
alongside it, not replace it.

See the AI disclosure at the top of this page.
