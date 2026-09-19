#!/usr/bin/env bash
# Build the Thunderstore-format package zip into dist/.
set -euo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.asdf/shims:$PATH"
export DOTNET_CLI_TELEMETRY_OPTOUT=1

VERSION=$(python3 -c "import json;print(json.load(open('package/manifest.json'))['version_number'])")

dotnet build src/TameProtection.csproj -c Release
rm -rf dist/stage && mkdir -p dist/stage/plugins/TameProtection
cp package/manifest.json package/icon.png package/README.md dist/stage/
cp src/bin/Release/TameProtection.dll dist/stage/plugins/TameProtection/

python3 - "$VERSION" <<'PY'
import json, os, re, struct, sys, zipfile
v = sys.argv[1]; root = "dist/stage"
m = json.load(open(f"{root}/manifest.json"))
assert re.fullmatch(r"[a-zA-Z0-9_]{1,128}", m["name"]), "bad name"
assert len(m["description"]) <= 250, "description too long"
assert re.fullmatch(r"\d+\.\d+\.\d+", m["version_number"]), "bad version"
icon = open(f"{root}/icon.png", "rb").read()
assert icon[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", icon[16:24]) == (256, 256), "icon must be 256x256 PNG"
out = f"dist/TameProtection-{v}.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(root):
        for f in fs:
            full = os.path.join(dp, f)
            z.write(full, os.path.relpath(full, root))
print("built", out)
for n in zipfile.ZipFile(out).namelist():
    print("   ", n)
PY
rm -rf dist/stage
