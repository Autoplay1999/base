import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import build_utils as utils

# --- Configuration ---
ROOT_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = ROOT_DIR / "modules"
BIN_DIR = ROOT_DIR / "bin"
BUILDS_DIR = ROOT_DIR / "builds"

# (Name, ModuleDir, ProjectPath, HeaderDir, HeaderPattern, CustomStepsFunc)
MSBUILD_LIBS = [
    ("SimdJSON", "simdjson", "simdjson/simdjson.vcxproj", "include", "*.h", None),
    ("TurboBase64", "turbo-base64", "turbo-base64/turbo-base64.vcxproj", ".", "*.h", None),
    ("Yaml-CPP", "yaml-cpp", "yaml-cpp/yaml-cpp.vcxproj", "include", "*.h", "patch_yaml_cpp"),
    ("SlimDetours", "knsoft.slimdetours", None, None, None, "build_knsoft_batch"),
    ("Syscall", "knsoft.syscall", None, None, None, "build_knsoft_batch"),
]

def patch_yaml_cpp(dst_inc: Path):
    """Applies YAML_CPP_STATIC_DEFINE patch (Ref: CC-PATCH)."""
    dll_h = dst_inc / "yaml-cpp" / "dll.h"
    if dll_h.exists():
        utils.Logger.info("Patching yaml-cpp/dll.h for static define...")
        content = dll_h.read_text()
        if "#define YAML_CPP_STATIC_DEFINE" not in content:
            # Insert after the guard
            new_content = content.replace("#define DLL_H_", "#define DLL_H_\n#define YAML_CPP_STATIC_DEFINE")
            dll_h.write_text(new_content)
            utils.Logger.success("Patch applied.")

def build_knsoft_batch(name: str):
    """Fallback for knsoft libs that have complex original bat logic."""
    # For now, we'll keep them in their original bats if too complex, 
    # but the goal is to port them. Let's look at syscall/slimdetours.
    pass

def build_msbuild_lib(name: str, mod_dir: str, vcxproj: str, header_dir: str, pattern: str, custom_func: str):
    try:
        utils.Logger.info(f"[{name}] Starting MSBuild-based build...")
        
        module_path = MODULES_DIR / mod_dir
        dst_bin = BIN_DIR / name.lower()
        
        utils.update_submodule(module_path)
        
        sources = [module_path, Path(__file__), BUILDS_DIR / "build_utils.py"]
        token_file = dst_bin / ".valid"
        
        if not utils.check_build_needed(sources, token_file):
            utils.Logger.success(f"[{name}] Already up to date.")
            return

        env_manager = utils.BuildEnv()
        ARCHS = ["x86", "x64"]
        CONFIGS = ["Release", "Debug"]
        
        project_full = BUILDS_DIR / vcxproj

        for arch in ARCHS:
            vs_env = env_manager.get_env_vars(arch)
            platform = "Win32" if arch == "x86" else "x64"
            
            for config in CONFIGS:
                utils.Logger.info(f"[{name}] Building {arch} | {config}...")
                
                # Standard MSBuild properties for static libs
                props = {
                    "RuntimeLibrary": "MultiThreaded" if config == "Release" else "MultiThreadedDebug",
                    "WholeProgramOptimization": "false" # For stability during migration
                }
                
                utils.Logger.info(f"Executing MSBuild for {arch} ({config})...")
                # We use build_utils.run_msbuild for consistency
                env_manager.run_msbuild(project_full, config, platform, env=vs_env, properties=props)
                
                # Deploy (Ref: CC-FIO-ORG)
                artifact_dst = dst_bin / "lib" / arch / config.lower()
                utils.ensure_dir(artifact_dst)
                
                # Heuristic for output name (usually lib name)
                out_name = f"{name.split('.')[0].lower()}.lib"
                # Some might be different, we'll check common dirs
                # vcxproj usually defines OutDir. We look in vcxproj dir / bin/lib/Platform/Config
                src_search_dir = project_full.parent / "bin" / "lib" / platform / config
                if not src_search_dir.exists():
                    src_search_dir = project_full.parent / platform / config
                
                # Copy found .lib
                found = False
                if src_search_dir.exists():
                    for f in src_search_dir.glob("*.lib"):
                        shutil.copy2(f, artifact_dst)
                        # Copy PDB
                        pdb = f.with_suffix(".pdb")
                        if pdb.exists(): shutil.copy2(pdb, artifact_dst)
                        found = True
                
                if not found:
                    utils.Logger.warn(f"[{name}] Could not find output library in {src_search_dir}")

        # Export Headers
        if header_dir:
            utils.Logger.info(f"[{name}] Exporting headers...")
            dst_inc = dst_bin / "include"
            utils.clean_dir(dst_inc)
            utils.copy_files(module_path / header_dir, dst_inc, pattern)
            
            # Apply custom patching if needed
            if custom_func == "patch_yaml_cpp":
                patch_yaml_cpp(dst_inc)

        utils.write_build_token(dst_bin, sources)
        utils.Logger.success(f"[{name}] Build completed.")

    except Exception as e:
        utils.Logger.error(f"[{name}] Failed: {e}")

def main():
    utils.Logger.info("=" * 60)
    utils.Logger.info("  Unified MSBuild Build System")
    utils.Logger.info("=" * 60)

    for item in MSBUILD_LIBS:
        if item[2]: # Has vcxproj
            build_msbuild_lib(*item)

if __name__ == "__main__":
    main()
