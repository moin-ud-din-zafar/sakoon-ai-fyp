"""Download a free ready-to-use human avatar GLB for Sakoon AI."""
import urllib.request, pathlib, sys, time

DEST = pathlib.Path(r"E:\Ai Virtual Assistant\frontend\public\models\sakoon-avatar.glb")
DEST.parent.mkdir(parents=True, exist_ok=True)

# Candidates (tried in order — first successful download wins)
SOURCES = [
    # Ready Player Me — public demo half-body avatars
    ("ReadyPlayerMe demo 1",
     "https://models.readyplayer.me/64bfa15f0e72c63d7c3934a6.glb?morphTargets=ARKit,Oculus Visemes&textureAtlas=1024"),
    ("ReadyPlayerMe demo 2",
     "https://models.readyplayer.me/638df693d72bffc6fa17943c.glb?morphTargets=ARKit,Oculus Visemes"),
    ("ReadyPlayerMe demo 3",
     "https://models.readyplayer.me/6460d95df9c2c4325ae46f73.glb?morphTargets=ARKit"),
    # Three.js bundled humanoid models (MIT)
    ("Three.js Michelle (female humanoid)",
     "https://threejs.org/examples/models/gltf/Michelle.glb"),
    ("Three.js Soldier",
     "https://threejs.org/examples/models/gltf/Soldier.glb"),
    ("Three.js Xbot (neutral humanoid)",
     "https://threejs.org/examples/models/gltf/Xbot.glb"),
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
}

for name, url in SOURCES:
    print(f"\nTrying: {name}")
    print(f"  URL: {url[:80]}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        elapsed = round(time.time() - t0, 1)
        size_kb = len(data) / 1024
        # Basic GLB validation: must start with glTF magic bytes
        if data[:4] != b"glTF":
            print(f"  Not a valid GLB (magic: {data[:4]}) — skipping")
            continue
        DEST.write_bytes(data)
        print(f"  Saved {size_kb:.0f} KB in {elapsed}s → {DEST}")
        sys.exit(0)
    except Exception as e:
        print(f"  Failed: {e}")

print("\nAll sources failed.")
sys.exit(1)
