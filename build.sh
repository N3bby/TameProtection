#!/usr/bin/env bash
# Rebuild TameProtection against the CURRENTLY INSTALLED Valheim/BepInEx assemblies.
# Run this after a Valheim update if the mod stops working.
set -euo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.asdf/shims:$PATH"
export DOTNET_CLI_TELEMETRY_OPTOUT=1

echo "==> refreshing reference assemblies from the running container"
C=/opt/valheim/bepinex
for f in valheim_server_Data/Managed/assembly_valheim.dll \
         valheim_server_Data/Managed/UnityEngine.dll \
         valheim_server_Data/Managed/UnityEngine.CoreModule.dll \
         BepInEx/core/BepInEx.dll BepInEx/core/0Harmony.dll; do
  docker cp "valheim:$C/$f" lib/
done

echo "==> building"
dotnet build src/TameProtection.csproj -c Release

echo "==> deploying to /config/bepinex/plugins (and staging copy)"
docker exec valheim mkdir -p /config/bepinex/plugins/TameProtection
docker cp src/bin/Release/TameProtection.dll \
          valheim:/config/bepinex/plugins/TameProtection/TameProtection.dll
cp -f src/bin/Release/TameProtection.dll ../new-plugins/TameProtection/

echo "==> done. restart with: docker compose restart"
echo "    verify with: docker logs valheim 2>&1 | grep -i tameprotection"
