import os
import sys
import shutil
from pathlib import Path
import build_utils as utils

# --- Configuration ---
ROOT_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = ROOT_DIR / "modules" / "xorstr"
BIN_DIR = ROOT_DIR / "bin" / "xorstr"
BUILDS_DIR = Path(__file__).resolve().parent

def build_xorstr():
    try:
        utils.Logger.detail("[XorStr] Starting build & patch...")
        
        dst_inc = BIN_DIR / "include"
        utils.update_submodule(MODULES_DIR)
        
        sources = [MODULES_DIR, Path(__file__), BUILDS_DIR / "build_utils.py"]
        token_dir = BIN_DIR / ".tokens"
        token_file = token_dir / ".valid"
        
        if not utils.check_build_needed(sources, token_file, clean_on_rebuild_path=BIN_DIR):
            utils.Logger.success("[XorStr] Already up to date.")
            return

        # 1. Export Original Headers
        utils.Logger.detail("[XorStr] Exporting headers...")
        utils.clean_dir(dst_inc)
        utils.copy_files(MODULES_DIR / "include", dst_inc, "*.hpp")
        
        # 2. Apply Patches (Ref: CC-PATCH-INJECT)
        target_file = dst_inc / "xorstr.hpp"
        if target_file.exists():
            utils.Logger.detail("[XorStr] Injecting custom macros and disable AVX...")
            content = target_file.read_text()
            
            # Pattern: Disable AVX
            if "JM_XORSTR_DISABLE_AVX_INTRINSICS" not in content:
                content = content.replace(
                    "#define JM_XORSTR_HPP", 
                    "#define JM_XORSTR_HPP\n#define JM_XORSTR_DISABLE_AVX_INTRINSICS"
                )
            
            # Pattern: Inject XS Macros
            if "XS(x)" not in content:
                macros = (
                    "\n#ifndef XS\n"
                    "#    define _XSW(x) (PCWCH)XS(L##x)\n"
                    "#    define _XS8(x) (PCCH)XS(u8##x)\n"
                    "#    define XS(x) xorstr_(x)\n"
                    "#    define XSA(x) (PCCH)XS(x)\n"
                    "#    define XSW(x) _XSW(x)\n"
                    "#    define XS8(x) _XS8(x)\n"
                    "#endif"
                )
                content = content.replace("#include <type_traits>", f"#include <type_traits>\n{macros}")
            
            target_file.write_text(content)
            utils.Logger.success("[XorStr] Patches applied successfully.")

        utils.write_build_token(token_dir, sources)
        utils.Logger.success("[XorStr] Completed.")

    except Exception as e:
        utils.Logger.error(f"[XorStr] Failed: {e}")

if __name__ == "__main__":
    build_xorstr()
