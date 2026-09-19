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

Every player needs it, **including the dedicated server**. Creature AI only runs on
whoever owns the creature's network object — normally the nearest player's client — so a
server-only install will not reliably stop mobs from targeting tames.

- **r2modman / Thunderstore Mod Manager**: Settings → Import local mod → pick the release zip.
- **Manual**: copy `plugins/TameProtection/` into `BepInEx/plugins/`.

There is no version handshake. A client without the mod simply does not get the
protection; nothing breaks for anyone else.

## Configuration

`BepInEx/config/com.n3bby.tameprotection.cfg`

| Setting | Default | Meaning |
| --- | --- | --- |
| `ProtectTamedFromEnemies` | `true` | Master switch. |
| `ProtectedPrefabs` | empty | Comma-separated prefab names (e.g. `Asksvin,Lox`). Empty protects every tamed creature. |
| `DebugLogging` | `false` | Logs every suppressed hostility check. Noisy; testing only. |

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
