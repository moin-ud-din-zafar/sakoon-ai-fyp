"""Wav2Lip Setup Script — Sakoon AI.

Run this once before using the talking avatar:
    python backend/scripts/setup_wav2lip.py

What it does:
  1. Clones the Wav2Lip repo into  <project_root>/wav2lip/
  2. Installs Wav2Lip's Python dependencies
  3. Creates the checkpoints/ directory
  4. Prints download instructions for the model checkpoint (manual step)
  5. Copies face.jpg placeholder to frontend/public/avatars/

NOTE: The model checkpoint must be downloaded manually (Google Drive link).
"""

import subprocess
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]   # repo root
WAV2LIP_DIR  = PROJECT_ROOT / "wav2lip"
CHECKPOINTS  = WAV2LIP_DIR / "checkpoints"
AVATARS_DIR  = PROJECT_ROOT / "frontend" / "public" / "avatars"

WAV2LIP_REPO = "https://github.com/Rudrabha/Wav2Lip.git"

# Wav2Lip dependencies (from their requirements.txt)
WAV2LIP_DEPS = [
    "librosa==0.9.1",
    "numpy",
    "scipy",
    "opencv-python",
    "tqdm",
    "batch-face",
    "mediapipe",
    "filetype",
]

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║              Sakoon AI — Wav2Lip Setup Script                    ║
╚══════════════════════════════════════════════════════════════════╝
"""

CHECKPOINT_INSTRUCTIONS = """
╔══════════════════════════════════════════════════════════════════╗
║   MANUAL STEP REQUIRED — Download Model Checkpoint              ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Download ONE of these (wav2lip_gan.pth is recommended):         ║
║                                                                  ║
║  Wav2Lip GAN (better quality):                                   ║
║  https://iiitaphyd-my.sharepoint.com/:u:/g/personal/             ║
║  radrabha_m_research_iiit_ac_in/                                 ║
║  EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z57E4jN1DRRC7ad?e=n9Ujg3        ║
║                                                                  ║
║  Wav2Lip (original — faster):                                    ║
║  https://iiitaphyd-my.sharepoint.com/:u:/g/personal/             ║
║  radrabha_m_research_iiit_ac_in/                                 ║
║  Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?e=TBFBVW       ║
║                                                                  ║
║  After downloading, place the file at:                           ║
║                                                                  ║
║    wav2lip/checkpoints/wav2lip_gan.pth                           ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  FACE IMAGE SETUP:                                               ║
║  Place a clear frontal face photo (JPG) at:                      ║
║    frontend/public/avatars/face.jpg                              ║
║                                                                  ║
║  Requirements:                                                   ║
║   - Frontal face, good lighting                                  ║
║   - Min 256×256 px, JPG format                                   ║
║   - One visible face in frame                                    ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ADD TO backend/.env after completing above:                     ║
║                                                                  ║
║   WAV2LIP_DIR={wav2lip_dir}
║   WAV2LIP_CHECKPOINT={checkpoint}
║   AVATAR_FACE_IMAGE={face_image}
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""


def run(cmd: list, cwd=None, check=True):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=check)
    return result


def step(msg: str):
    print(f"\n{'─'*60}")
    print(f"  {msg}")
    print("─"*60)


def main():
    print(BANNER)

    # ── 1. Clone Wav2Lip ──────────────────────────────────────────────────────
    step("Step 1 / 4 — Clone Wav2Lip repo")
    if WAV2LIP_DIR.exists():
        print(f"  ✓ Already exists: {WAV2LIP_DIR}")
    else:
        run(["git", "clone", WAV2LIP_REPO, str(WAV2LIP_DIR)])
        print(f"  ✓ Cloned to {WAV2LIP_DIR}")

    # ── 2. Create checkpoints directory ──────────────────────────────────────
    step("Step 2 / 4 — Create checkpoints directory")
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    print(f"  ✓ {CHECKPOINTS}")

    # ── 3. Install dependencies ───────────────────────────────────────────────
    step("Step 3 / 4 — Install Wav2Lip dependencies")
    run([sys.executable, "-m", "pip", "install"] + WAV2LIP_DEPS, check=False)
    print("  ✓ Dependencies installed (warnings above are usually safe to ignore)")

    # ── 4. Face image placeholder ─────────────────────────────────────────────
    step("Step 4 / 4 — Check face image")
    AVATARS_DIR.mkdir(parents=True, exist_ok=True)
    face_jpg = AVATARS_DIR / "face.jpg"
    if face_jpg.exists():
        print(f"  ✓ Face image already present: {face_jpg}")
    else:
        print(f"  ⚠  No face image found at {face_jpg}")
        print("     Place a clear frontal face photo (JPG) there.")

    # ── Final instructions ─────────────────────────────────────────────────────
    print(CHECKPOINT_INSTRUCTIONS.format(
        wav2lip_dir=WAV2LIP_DIR,
        checkpoint=CHECKPOINTS / "wav2lip_gan.pth",
        face_image=face_jpg,
    ))


if __name__ == "__main__":
    main()
