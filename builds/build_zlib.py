import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import build_utils as utils

def main() -> None:
    """
    Orchestrates the professional build process for Zlib using CMake.
    Adheres to CC-FLOW and CC-ARCH standards.
    """
    try:
        PRJ_NAME: str = "Zlib"
        
        # Directory Mapping
        ROOT_DIR: Path = Path(__file__).resolve().parent.parent
        MODULES_DIR: Path = ROOT_DIR / "modules"
        BIN_DIR: Path = ROOT_DIR / "bin"
        
        ZLIB_MODULE: Path = MODULES_DIR / "zlib"
        ZLIB_BIN: Path = BIN_DIR / "zlib"
        
        BUILDS_DIR: Path = Path(__file__).resolve().parent
        
        # --- 1. Dependency & Hash Validation ---
        utils.update_submodule(ZLIB_MODULE)
        
        sources: List[Path] = [ZLIB_MODULE, Path(__file__), BUILDS_DIR / "build_utils.py"]
        token_dir: Path = ZLIB_BIN / ".tokens"
        token_file: Path = token_dir / ".valid"
        
        if not utils.check_build_needed(sources, token_file):
            utils.Logger.success(f"{PRJ_NAME} is already up to date.")
            return

        utils.Logger.info(f"Starting Build: {PRJ_NAME} (Content change detected)")
        
        # Initialize Visual Studio Environment
        env_manager = utils.BuildEnv()
        cmake_gen: str = env_manager.get_cmake_generator()
        
        # --- 2. Build Matrix ---
        ARCH_MAP: Dict[str, str] = {
            "x86": "Win32",
            "x64": "x64"
        }
        CONFIGS: List[str] = ["Release", "Debug"]
        
        for arch_name, cmake_arch in ARCH_MAP.items():
            # Capture environment for this architecture
            utils.Logger.detail(f"Setting up environment for {arch_name}...")
            vs_env = env_manager.get_env_vars(arch_name)
            
            # Find CMake (Ref: CC-PATH-FALLBACK)
            cmake_exe = shutil.which("cmake", path=vs_env.get("PATH"))
            if not cmake_exe:
                potential_cmake = env_manager.vs_path / "Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe"
                if potential_cmake.exists():
                    cmake_exe = str(potential_cmake)
                else:
                    raise utils.BuildError(f"cmake.exe not found for {arch_name}")

            for config in CONFIGS:
                utils.Logger.detail(f"Processing Architecture: {arch_name} | Configuration: {config}")
                
                # Setup localized build directory
                build_temp: Path = ZLIB_MODULE / "build" / arch_name / config.lower()
                utils.clean_dir(build_temp)
                
                # Determine Runtime Library
                runtime: str = "MultiThreaded" if config == "Release" else "MultiThreadedDebug"
                
                # 1. Configure
                configure_cmd: List[str] = [
                    cmake_exe, str(ZLIB_MODULE),
                    "-B", str(build_temp),
                    "-G", cmake_gen,
                    "-A", cmake_arch,
                    "-DZLIB_BUILD_SHARED=OFF",
                    "-DZLIB_BUILD_STATIC=ON",
                    "-DZLIB_BUILD_TESTING=OFF",
                    f"-DCMAKE_MSVC_RUNTIME_LIBRARY={runtime}",
                    "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF",
                    "-DCMAKE_C_FLAGS=/GR- /MP"
                ]
                
                utils.Logger.detail(f"Configuring {arch_name} ({config})...")
                utils.run_process(configure_cmd, cwd=ZLIB_MODULE, env=vs_env)
                
                # 2. Build
                cpu_count = utils.get_cpu_limit()
                build_cmd: List[str] = [
                    cmake_exe, "--build", str(build_temp),
                    "--config", config,
                    "--target", "zlibstatic",
                    "--parallel", str(cpu_count)
                ]
                
                utils.Logger.detail(f"Building {arch_name} ({config})...")
                utils.run_process(build_cmd, cwd=ZLIB_MODULE, env=vs_env)
                
                # 3. Deploy Artifacts (Ref: CC-FIO-ORG)
                artifact_dst: Path = ZLIB_BIN / "lib" / arch_name / config.lower()
                utils.ensure_dir(artifact_dst)
                
                # Zlib outputs: zs.lib (Release) or zsd.lib (Debug)
                src_lib_name = "zs.lib" if config == "Release" else "zsd.lib"
                
                # Search specifically in the config subfolder
                lib_found = False
                for root, _, files in os.walk(build_temp):
                    if config in Path(root).parts:
                        if src_lib_name in files:
                            # Rename to zlib.lib for downstream compatibility
                            shutil.copy2(Path(root) / src_lib_name, artifact_dst / "zlib.lib")
                            # Also attempt to copy PDB
                            pdb_name = src_lib_name.replace(".lib", ".pdb")
                            if pdb_name in files:
                                shutil.copy2(Path(root) / pdb_name, artifact_dst / "zlib.pdb")
                            lib_found = True
                
                if not lib_found:
                    utils.Logger.warn(f"Library {src_lib_name} not found for {arch_name}/{config}")
                else:
                    utils.Logger.success(f"Deployed: {arch_name}/{config} zlib.lib")

        # --- 3. Export Headers ---
        utils.Logger.detail("Exporting headers...")
        inc_dst: Path = ZLIB_BIN / "include"
        utils.clean_dir(inc_dst)
        
        # We need zlib.h from source and generated zconf.h from one of the build folders (they are identical across configs)
        # Choosing x64/release as source for zconf.h
        zconf_src = ZLIB_MODULE / "build/x64/release/zconf.h"
        if zconf_src.exists():
            shutil.copy2(zconf_src, inc_dst)
        else:
            # Fallback to search if not found at specific path
            for root, _, files in os.walk(ZLIB_MODULE / "build"):
                if "zconf.h" in files:
                    shutil.copy2(Path(root) / "zconf.h", inc_dst)
                    break
        
        shutil.copy2(ZLIB_MODULE / "zlib.h", inc_dst)
        utils.Logger.success("Headers exported successfully.")

        # --- 4. Finalize ---
        utils.write_build_token(token_dir, sources)
        utils.Logger.success(f"Build of {PRJ_NAME} completed successfully.")

    except Exception as e:
        utils.Logger.fatal(f"Unexpected failure in {PRJ_NAME} build: {e}")

if __name__ == "__main__":
    main()
