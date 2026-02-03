import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import build_utils as utils

# --- Configuration ---
ROOT_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = ROOT_DIR / "modules" / "imgui"
BIN_DIR = ROOT_DIR / "bin" / "imgui"
BUILDS_DIR = Path(__file__).resolve().parent

IMGUI_VARIANTS = ["master", "docking", "win98"]

def build_imgui_variant(variant: str):
    try:
        utils.Logger.info(f"[ImGui-{variant}] Starting CMake-based build...")
        
        mod_src = MODULES_DIR / variant / "imgui"
        dst_bin = BIN_DIR / variant
        dst_inc = dst_bin / "include"
        dst_lib = dst_bin / "lib"
        
        utils.reset_submodule(mod_src, f"modules/imgui/{variant}/imgui")
        
        # Custom Injection for 'master', 'docking' and 'win98' if missing (Ref: USR-REQ-INJECT-CMAKE)
        injected_cmake = False
        resource_cmake = BUILDS_DIR / "resources" / "imgui_master_CMakeLists.txt"
        
        # We always check for resource_cmake and inject if target doesn't have it or if it's one of the primary variants
        if resource_cmake.exists() and (variant in ["master", "docking", "win98"]):
            utils.Logger.detail(f"[ImGui-{variant}] Injecting CMakeLists.txt from resources...")
            shutil.copy2(resource_cmake, mod_src / "CMakeLists.txt")
            injected_cmake = True

        # Check if CMakeLists.txt is there
        cmake_file = mod_src / "CMakeLists.txt"
        if not cmake_file.exists():
             utils.Logger.error(f"[ImGui-{variant}] CMakeLists.txt missing at {cmake_file}")
             return

        sources = [mod_src, Path(__file__), BUILDS_DIR / "build_utils.py"]
        token_dir = dst_bin / ".tokens"
        token_file = token_dir / ".valid"
        
        if not utils.check_build_needed(sources, token_file, clean_on_rebuild_path=dst_bin):
            utils.Logger.success(f"[ImGui-{variant}] Already up to date.")
            if injected_cmake:
                try:
                    (mod_src / "CMakeLists.txt").unlink()
                except Exception:
                    pass
            return

        # 1. Export Headers
        utils.Logger.detail(f"[ImGui-{variant}] Exporting headers...")
        utils.clean_dir(dst_inc)
        utils.copy_files(mod_src, dst_inc, "*.h")
        
        # Backends
        backend_src = mod_src / "backends"
        backend_dst = dst_inc / "backends"
        utils.ensure_dir(backend_dst)
        utils.copy_files(backend_src, backend_dst, "*.h")
        
        # MISC
        misc_src = mod_src / "misc"
        if misc_src.exists():
            for sub in ["cpp", "freetype"]:
                s = misc_src / sub
                if s.exists():
                    utils.copy_files(s, dst_inc / "misc" / sub, "*.h")

        # 2. Build via CMake
        env_manager = utils.BuildEnv()
        cmake_gen = env_manager.get_cmake_generator()
        
        ARCH_MAP = {"x86": "Win32", "x64": "x64"}
        
        for arch_name, cmake_arch in ARCH_MAP.items():
            vs_env = env_manager.get_env_vars(arch_name)
            
            for config in ["Release", "Debug"]:
                utils.Logger.detail(f"[ImGui-{variant}] Processing {arch_name} | {config}...")
                
                build_temp = mod_src / "build" / arch_name / config.lower()
                utils.clean_dir(build_temp)
                
                runtime = "MultiThreaded" if config == "Release" else "MultiThreadedDebug"
                
                # Resolve CMake
                cmake_exe = env_manager.get_cmake_path(vs_env.get("PATH"))
                
                # Configure
                configure_cmd = [
                    cmake_exe, str(mod_src),
                    "-B", str(build_temp),
                    "-G", cmake_gen,
                    "-A", cmake_arch,
                    f"-DCMAKE_MSVC_RUNTIME_LIBRARY={runtime}",
                    "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF",
                    "-DCMAKE_CXX_FLAGS=/GR- /EHsc /MP",
                    "-DCMAKE_C_FLAGS=/MP"
                ]
                utils.run_process(configure_cmd, cwd=mod_src, env=vs_env)
                
                # Build (Target all defined libs)
                cpu_count = utils.get_cpu_limit()
                build_cmd = [
                    cmake_exe, "--build", str(build_temp),
                    "--config", config,
                    "--parallel", str(cpu_count)
                ]
                utils.run_process(build_cmd, cwd=mod_src, env=vs_env)
                
                # Deploy
                lib_dst = dst_bin / "lib" / arch_name / config.lower()
                utils.ensure_dir(lib_dst)
                
                # Deploy all libs found (imgui.lib, imgui_dx9.lib, etc.)
                deployed_libs = 0
                for root, _, files in os.walk(build_temp):
                    if config in Path(root).parts:
                        for f in files:
                            if f.endswith(".lib"):
                                src_lib = Path(root) / f
                                shutil.copy2(src_lib, lib_dst / f)
                                
                                # Try copy matching PDB
                                pdb_name = f.replace(".lib", ".pdb")
                                if pdb_name in files:
                                    shutil.copy2(Path(root) / pdb_name, lib_dst / pdb_name)
                                
                                deployed_libs += 1

                if deployed_libs > 0:
                    utils.Logger.success(f"[ImGui-{variant}] Deployed {deployed_libs} libs to {arch_name}/{config}")

        utils.write_build_token(token_dir, sources)
        utils.Logger.success(f"[ImGui-{variant}] Completed successfully.")

        if injected_cmake:
             utils.Logger.detail(f"[ImGui-{variant}] Cleaning up injected CMakeLists.txt...")
             try:
                 (mod_src / "CMakeLists.txt").unlink()
             except Exception:
                 pass

    except Exception as e:
        utils.Logger.error(f"[ImGui-{variant}] Failed: {e}")

def main():
    utils.Logger.info("=" * 60)
    utils.Logger.info("  ImGui Multi-Variant CMake Build System")
    utils.Logger.info("=" * 60)
    
    for v in IMGUI_VARIANTS:
        build_imgui_variant(v)
    
    utils.Logger.info("=" * 60)

if __name__ == "__main__":
    main()
