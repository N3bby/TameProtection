# TameProtection

A tiny Valheim BepInEx plugin: **wild creatures and tamed creatures ignore each other.**

Mobs stop hunting your tames, and your tames stop picking fights with mobs. Wild-vs-wild
and tame-vs-tame hostility is untouched, so normal combat and your own attacks on tames
behave exactly as in vanilla.

Built against **Valheim 1.0.15** / **BepInExPack 5.4.2350**.

> **AI disclosure.** This mod was written with AI assistance (Claude). The Harmony patch,
> plugin scaffolding, configuration, build scripts and documentation were all AI-generated,
> then reviewed and tested against a live Valheim 1.0.15 dedicated server. It is published
> on Thunderstore under the **AI Generated** category.

## Why

This restores the `ProtectTamedFromEnemies` behaviour from
[Wendigo's CreatureCarry 1.3.0](https://thunderstore.io/c/valheim/p/Wendigo/CreatureCarry/),
which the Valheim 1.0 fork
([Eradorn's CustomCreatureCarry](https://thunderstore.io/c/valheim/p/Eradorn/CustomCreatureCarry/))
deliberately left out — its README states there are "no egg-hatching, OdinMounts,
ChebsNecromancy or general tame-protection changes". This plugin fills only that gap and
is meant to sit alongside it.

## How it works

A single Harmony postfix on `BaseAI.IsEnemy(Character, Character)`. The instance overload
compiles to `return BaseAI.IsEnemy(this.m_character, other)`:

```
IL_0000: ldarg.0
IL_0001: ldfld    Character BaseAI::m_character
IL_0006: ldarg.1
IL_0007: call     System.Boolean BaseAI::IsEnemy(Character,Character)
IL_000c: ret
```

so patching the static method covers every caller. When exactly one of the two characters
is tamed, the result is forced to `false`.

See [`src/Plugin.cs`](src/Plugin.cs) — the whole plugin is about 100 lines.

## Install

Published on Thunderstore as
**[N3bby-TameProtection](https://thunderstore.io/c/valheim/p/N3bby/TameProtection/)**.
To depend on it from another package's `manifest.json`:

```json
"dependencies": ["N3bby-TameProtection-1.0.0"]
```


**Install it on the server and on every client.** The two halves do different jobs:

| Installed on | Gameplay effect | Configuration |
| --- | --- | --- |
| Client only | Works, for creatures that client owns | Local, per-player |
| Server only | Almost nothing | — |
| **Both** | Works | **Server-authoritative, admins can edit live** |

The patch itself runs client-side: `BaseAI.UpdateAI` is gated on `IsOwner`, so hostility
checks happen on whichever peer owns the creature — on a dedicated server that is the
nearby player's client, never the server. So every player needs it, and a player without
it still sees their own creatures hunt tames.

The server copy is what makes the settings authoritative. `ProtectTamedFromEnemies` and
`ProtectedPrefabs` are synced, and a client only stops using its local values once the
server sends them (`IsSourceOfTruth` flips on `RPC_FromServerConfigSync`). Without the mod
on the server nothing is pushed and every player silently keeps their own config — which
matters here, because each client owns different creatures, so divergent settings make
tames protected or not depending on who is standing nearest.

- **r2modman / Thunderstore Mod Manager**: Settings → Import local mod → pick the release zip.
- **Manual**: copy `plugins/TameProtection/` into `BepInEx/plugins/`.

There is no version handshake. A client without the mod simply does not get the
protection; nothing breaks for anyone else.

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

## Building

Requires the .NET SDK (8.x is fine) and a copy of Valheim or a Valheim dedicated server
with BepInEx installed.

The Valheim, Unity and BepInEx assemblies are **not** in this repository — they are
proprietary and `lib/` is gitignored. Populate it yourself with:

```
lib/assembly_valheim.dll
lib/UnityEngine.dll
lib/UnityEngine.CoreModule.dll
lib/BepInEx.dll
lib/0Harmony.dll
```

taken from your own game or server install, then:

```bash
dotnet build src/TameProtection.csproj -c Release   # -> src/bin/Release/TameProtection.dll
./pack.sh                                           # -> dist/TameProtection-<version>.zip
```

`build.sh` additionally pulls the reference assemblies out of a running
`valheim` Docker container and redeploys to it; it is specific to that setup.

Note the project targets `netstandard2.1`, not `2.0` — Valheim 1.0 runs on Unity 6 and
its assemblies reference `netstandard 2.1`.

## Credits

Original idea and hook: **Wendigo**, CreatureCarry 1.3.0. That package shipped without a
license file or source-repository URL, so no upstream code was reused — this is an
independent implementation written against the decompiled `BaseAI.IsEnemy` signature.

See the AI disclosure at the top of this README.

## License

[MIT](LICENSE)
