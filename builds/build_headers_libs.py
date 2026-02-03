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

import re

# (Name, Source Subpath, Pattern)
HEADER_ONLY_LIBS = [
    ("JSON", "json/include", "*.hpp"),
    ("PHNT", "phnt", "*.h"),
    ("LazyImporter", "lazy_importer/include", "*.hpp"),

    ("Neargye/magic_enum", "magic_enum/include", "*.hpp"),
    ("Neargye/nameof", "nameof/include", "*.hpp"),
    ("Neargye/scope_guard", "scope_guard/include", "*.hpp"),
    ("Neargye/semver", "semver/include", "*.hpp"),
    ("Neargye/yacppl", "yacppl/include", "*.hpp"),
    # Obfuscation & Security
    ("Obfuscate", "Obfuscate", "obfuscate.h"),
    ("obfuscxx", "obfuscxx/obfuscxx/include", "*"),
    ("obfusheader.h", "obfusheader.h/include", "obfusheader.h"),
    ("XorStr", "xorstr/include", "*.hpp"),
]

def post_process_lib(name: str, install_root: Path):
    """
    Applies custom patches or macro replacements for specific libraries.
    (Ref: CC-PATCH-INJECT)
    """
    # 1. XorStr: Inject Macros & Disable AVX
    if name == "XorStr":
        # No nesting for XorStr (Standard behavior)
        target_file = install_root / "include" / "xorstr.hpp"
        if not target_file.exists():
            utils.Logger.warn(f"[{name}] Post-process failed: {target_file} not found")
            return
            
        utils.Logger.detail(f"[{name}] Injecting custom macros...")
        try:
            content = target_file.read_text(encoding="utf-8")
            modified = False
            
            # Disable AVX
            if "JM_XORSTR_DISABLE_AVX_INTRINSICS" not in content:
                content = content.replace(
                    "#define JM_XORSTR_HPP", 
                    "#define JM_XORSTR_HPP\n#define JM_XORSTR_DISABLE_AVX_INTRINSICS"
                )
                modified = True
            
            # Inject XS Macros
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
                modified = True
                
            if modified:
                target_file.write_text(content, encoding="utf-8")
                utils.Logger.success(f"[{name}] Patches applied.")
        except Exception as e:
            utils.Logger.error(f"[{name}] Patch failed: {e}")

    # 2. obfusheader.h: Keyword Sanitization
    elif name == "obfusheader.h":
        # Location: bin/obfusheader.h/include/obfusheader.h (Non-nested)
        target_file = install_root / "include" / "obfusheader.h"

        if not target_file.exists():
            utils.Logger.warn(f"[{name}] Post-process failed: {target_file} not found")
            return

        utils.Logger.detail(f"[{name}] Sanitizing keywords...")
        try:
            content = target_file.read_text(encoding="utf-8")
            
            replacements = [
                (r'#define if\(', r'#define if_('),
                (r'#define for\(', r'#define for_('),
                (r'#define while\(', r'#define while_('),
                (r'#define switch\(', r'#define switch_('),
                (r'#define return ', r'#define return_ '),
                (r'#define else ', r'#define else_ ')
            ]
            
            original_content = content
            for pattern, repl in replacements:
                content = re.sub(pattern, repl, content)
            
            if content != original_content:
                target_file.write_text(content, encoding="utf-8")
                utils.Logger.success(f"[{name}] Keywords sanitized.")
        except Exception as e:
             utils.Logger.error(f"[{name}] Sanitization failed: {e}")


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
             # Special case for Neargye family
             parts = name.split('/')
             family = parts[0].lower()
             lib_name = parts[1]
             base_dir = utils.BIN_DIR / family
             target_base = base_dir / "include" / family
             if (src_path / lib_name).exists() and (src_path / lib_name).is_dir():
                 dst_inc = target_base
             else:
                 dst_inc = target_base / lib_name
             token_dir = target_base / lib_name
             lib_root = token_dir
        else:
            # Standard module-based structure
            lib_root = utils.BIN_DIR / module_name
            
            has_loose_files = any(f.is_file() for f in src_path.glob(pattern) if f.name != ".git")
            
            # Explicitly disable nesting for: PHNT, obfusheader.h, XorStr, Obfuscate
            # to maintain backward compatibility and clean include paths (<Header.h> vs <Lib/Header.h>)
            no_nest_modules = {"phnt", "obfusheader.h", "xorstr", "obfuscate"}
            should_nest = has_loose_files and module_name.lower() not in no_nest_modules

            if should_nest:
                 dst_inc = lib_root / "include" / module_name
            else:
                 dst_inc = lib_root / "include"
                 
            token_dir = lib_root / ".tokens"
        
        # 2. Check rebuild
        if not utils.check_build_needed([src_path], token_dir / ".valid", clean_on_rebuild_path=lib_root):
            utils.Logger.success(f"[{name}] Already up to date.")
            return

        # 3. Export Headers
        utils.Logger.info(f"[{name}] Exporting headers to {dst_inc}...")
        utils.ensure_dir(dst_inc)
        utils.clean_dir(dst_inc) # Clean target include to be safe
        utils.copy_files(src_path, dst_inc, pattern, recursive=True)
        
        # 4. Post-Process (New Step)
        post_process_lib(name, lib_root)

        # 5. Finalize
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
