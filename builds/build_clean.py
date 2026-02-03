import shutil
import os
from pathlib import Path
import build_utils as utils

# --- Configuration ---
BUILD_DIR = Path(__file__).parent.absolute()
ROOT_DIR = BUILD_DIR.parent
BIN_DIR = ROOT_DIR / "bin"
LOG_DIR = ROOT_DIR / "logs"

MODULES = [
    "curl", "imgui", "json", "lazy_importer", "neargye.magic_enum", 
    "neargye.nameof", "neargye.semver", "neargye.yacppl", 
    "neargye.scope_guard", "nirvana", "phnt", "tinycc", 
    "turbo_base64", "vmp", "xorstr", "obfuscate", "obfuscxx", 
    "obfusheader.h", "zlib", "zydis", "knsoft.ndk", 
    "knsoft.slimdetours", "knsoft.syscall", "asmjit", 
    "simdjson", "yaml-cpp"
]

def clean():
    utils.Logger.info("=" * 60)
    utils.Logger.info("  CLEAN SYSTEM")
    utils.Logger.info("=" * 60)
    
    count = 0
    
    # 1. Base Directories
    for d in [BIN_DIR, LOG_DIR]:
        if d.exists():
            utils.Logger.info(f"Cleaning {d.name}...")
            try:
                shutil.rmtree(d)
                count += 1
                utils.Logger.success(f"Removed: {d}")
            except Exception as e:
                utils.Logger.error(f"Failed to remove {d}: {e}")

    # 2. Module Directories
    for mod in MODULES:
        mod_path = BUILD_DIR / mod
        if mod_path.exists():
            # Standard temp dirs
            for sub in ["bin", "obj", "tmp", "OutDir"]:
                target = mod_path / sub
                if target.exists():
                    try:
                        shutil.rmtree(target)
                        count += 1
                        utils.Logger.success(f"Removed: {target}")
                    except Exception as e:
                        utils.Logger.error(f"Failed to remove {target}: {e}")

    # Special cases for imgui
    imgui_path = BUILD_DIR / "imgui"
    if imgui_path.exists():
        for branch in ["master", "docking", "win98"]:
            target = imgui_path / branch / "bin"
            if target.exists():
                shutil.rmtree(target)
                count += 1

    utils.Logger.info("-" * 60)
    utils.Logger.success(f"Done. Removed {count} items.")
    utils.Logger.info("=" * 60)

if __name__ == "__main__":
    clean()
