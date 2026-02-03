import os
import sys
from pathlib import Path
from typing import List, Dict
import build_utils as utils

# --- Configuration ---
ROOT_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = ROOT_DIR / "modules"
BIN_DIR = ROOT_DIR / "bin"
BUILDS_DIR = Path(__file__).resolve().parent

# (Name, Source Subpath, Pattern)
HEADER_ONLY_LIBS = [
    ("JSON", "json/include", "*.hpp"),
    ("PHNT", "phnt", "*.h"),
    ("LazyImporter", "lazy_importer/include", "*.hpp"),
    ("Nirvana", "nirvana", "*.h"),
    ("Neargye/magic_enum", "magic_enum/include", "*.hpp"),
    ("Neargye/nameof", "nameof/include", "*.hpp"),
    ("Neargye/scope_guard", "scope_guard/include", "*.hpp"),
    ("Neargye/semver", "semver/include", "*.hpp"),
    ("Neargye/yacppl", "yacppl/include", "*.hpp"),
]

def build_header_lib(name: str, src_rel: str, pattern: str):
    try:
        utils.Logger.info(f"[{name}] Starting migration/export...")
        
        src_path = MODULES_DIR / src_rel
        if not src_path.exists():
            utils.Logger.warn(f"[{name}] Source path not found: {src_path}")
            return

        # 1. Update Submodule
        module_name = src_rel.split('/')[0]
        submodule_root = MODULES_DIR / module_name
        utils.update_submodule(submodule_root)

        # Standardize: Export to Standard Structure
        if name.startswith("Neargye/"):
             # Special case for Neargye family: bin/neargye/include/<lib-name>
             parts = name.split('/')
             family = parts[0].lower() # neargye
             lib_name = parts[1]       # magic_enum
             
             base_dir = utils.BIN_DIR / family
             
             # Extra Nesting: bin/neargye/include/neargye/<lib-name>
             target_base = base_dir / "include" / family
             
             # Smart Nesting Detection:
             # If source (e.g. include/) already has the lib folder (e.g. include/magic_enum),
             # then we export to target_base to get .../include/neargye/magic_enum.
             # If source is flat (e.g. include/header.hpp), we export to target_base/<libname>.
             if (src_path / lib_name).exists() and (src_path / lib_name).is_dir():
                 dst_inc = target_base
             else:
                 dst_inc = target_base / lib_name
             
             # Token always goes in the canonical lib folder: bin/neargye/include/neargye/<lib-name>
             token_dir = target_base / lib_name
             
             # Set lib_root for generic compatibility (e.g. logging)
             lib_root = token_dir
             
             # Logger check for clarity
             # utils.Logger.info(f"[{name}] Target: {dst_inc}")
        else:
            # Standard module-based structure: bin/<module>/include
            lib_root = utils.BIN_DIR / module_name
            
            # Smart Nesting Detection for Standard Modules:
            # Check if src_path has any files matching pattern directly (loose files).
            # If yes (like nirvana/*.h, lazy_importer/include/*.hpp), nest them in include/<modname>.
            # If no (like json/include/nlohmann/), keep them in include/.
            # EXCEPTION: phnt should NOT be nested.
            has_loose_files = any(f.is_file() for f in src_path.glob(pattern) if f.name != ".git")
            
            if has_loose_files and module_name.lower() != "phnt":
                 dst_inc = lib_root / "include" / module_name
            else:
                 dst_inc = lib_root / "include"
                 
            token_dir = lib_root
        
        # Token goes in the lib root's .tokens subdirectory
        token_dir = lib_root / ".tokens"
        
        # 2. Check rebuild
        # 2. Check rebuild
        if not utils.check_build_needed([src_path], token_dir / ".valid", clean_on_rebuild_path=lib_root):
            utils.Logger.success(f"[{name}] Already up to date.")
            return

        # 3. Export Headers
        utils.Logger.info(f"[{name}] Exporting headers to {dst_inc}...")
        
        utils.ensure_dir(dst_inc)
        # Note: No 'lib' folder created for header-only libraries as requested

        # Use recursive copy for these libs to preserve their structure
        utils.copy_files(src_path, dst_inc, pattern, recursive=True)
        
        # 4. Finalize
        utils.write_build_token(token_dir, [src_path])
        utils.Logger.success(f"[{name}] Successfully exported to {lib_root}")

    except Exception as e:
        utils.Logger.error(f"[{name}] Failed: {e}")

def main():
    utils.Logger.info("=" * 60)
    utils.Logger.info("  Unified Header-Only Build System")
    utils.Logger.info("=" * 60)

    for name, src_rel, pattern in HEADER_ONLY_LIBS:
        build_header_lib(name, src_rel, pattern)

    utils.Logger.info("=" * 60)

if __name__ == "__main__":
    main()
