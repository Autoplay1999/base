
import os
import sys
import shutil
from pathlib import Path
from typing import List
import build_utils as utils

def main() -> None:
    """
    Orchestrates the deployment of VMP module (VMProtect SDK).
    Standardizes directory layout and ensures strict Release purity.
    """
    try:
        PRJ_NAME: str = "VMP"
        
        # Directory Mapping
        ROOT_DIR: Path = Path(__file__).resolve().parent.parent
        MODULES_DIR: Path = ROOT_DIR / "modules"
        BIN_DIR: Path = ROOT_DIR / "bin"
        
        VMP_MODULE: Path = MODULES_DIR / "vmp"
        VMP_BIN: Path = BIN_DIR / "vmp"
        
        BUILDS_DIR: Path = Path(__file__).resolve().parent
        
        # --- 1. Validation ---
        sources: List[Path] = [VMP_MODULE, Path(__file__), BUILDS_DIR / "build_utils.py"]
        token_dir: Path = VMP_BIN / ".tokens"
        token_file: Path = token_dir / ".valid"
        
        if not utils.check_build_needed(sources, token_file, clean_on_rebuild_path=VMP_BIN):
            utils.Logger.success(f"{PRJ_NAME} is already up to date.")
            return

        utils.Logger.info(f"Starting Build: {PRJ_NAME}")
        
        # --- 2. Build Matrix (Deployment Only) ---
        ARCH_MAP = {
            "x86": "x86",
            "x64": "x64"
        }
        # VMP is used only in Release builds (Ref: USR-REQ-VMP-RELEASE-ONLY)
        CONFIGS = ["Release"]
        
        for arch_name, arch_dir in ARCH_MAP.items():
            src_lib_dir = VMP_MODULE / "lib" / arch_dir
            if not src_lib_dir.exists():
                utils.Logger.warn(f"Source lib dir not found: {src_lib_dir}")
                continue

            for config in CONFIGS:
                # Setup destination
                lib_dst = VMP_BIN / "lib" / arch_name / config.lower()
                utils.ensure_dir(lib_dst)
                
                # Active Clean PDBs (Ref: USR-REQ-EMBED-PDB)
                if lib_dst.exists():
                    for stale in lib_dst.glob("*.pdb"):
                        try: stale.unlink()
                        except: pass
                
                # Copy Lib (Pre-built, assume same for Release/Debug)
                src_lib = src_lib_dir / "VMProtectSDK.lib"
                dst_lib = lib_dst / "vmp.lib"
                
                if src_lib.exists():
                    shutil.copy2(src_lib, dst_lib)
                    utils.Logger.success(f"Deployed: {arch_name}/{config} vmp.lib")
                else:
                    utils.Logger.error(f"Missing artifact: {src_lib}")

        # --- 3. Export Headers ---
        utils.Logger.detail("Exporting headers...")

        inc_dst: Path = VMP_BIN / "include" / "vmp"
        utils.clean_dir(inc_dst)
        
        src_inc = VMP_MODULE / "include"
        if src_inc.exists():
             utils.copy_files(src_inc, inc_dst, "*.h")
             utils.Logger.success("Headers exported successfully.")
        else:
             utils.Logger.warn(f"Header Source not found: {src_inc}")

        # --- 4. Finalize ---
        utils.write_build_token(token_dir, sources)
        utils.Logger.success(f"Build of {PRJ_NAME} completed successfully.")

    except Exception as e:
        utils.Logger.fatal(f"Unexpected failure in {PRJ_NAME} build: {e}")

if __name__ == "__main__":
    main()
