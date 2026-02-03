import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import build_utils as utils

def main() -> None:
    """
    Orchestrates the professional build process for TinyCC using CMake.
    Adheres to CC-FLOW and CC-ARCH standards.
    """
    try:
        PRJ_NAME: str = "TinyCC"
        
        # Directory Mapping
        ROOT_DIR: Path = Path(__file__).resolve().parent.parent
        MODULES_DIR: Path = ROOT_DIR / "modules"
        BIN_DIR: Path = ROOT_DIR / "bin"
        
        TINYCC_MODULE: Path = MODULES_DIR / "tinycc"
        TINYCC_BIN: Path = BIN_DIR / "tinycc"
        
        BUILDS_DIR: Path = Path(__file__).resolve().parent
        
        # --- 1. Dependency & Hash Validation ---
        utils.update_submodule(TINYCC_MODULE)
        
        sources: List[Path] = [TINYCC_MODULE, Path(__file__), BUILDS_DIR / "build_utils.py"]
        token_dir: Path = TINYCC_BIN / ".tokens"
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
                build_temp: Path = TINYCC_MODULE / "build" / arch_name / config.lower()
                utils.clean_dir(build_temp)
                
                # Determine Runtime Library
                runtime: str = "MultiThreaded" if config == "Release" else "MultiThreadedDebug"
                
                # 1. Configure
                configure_cmd: List[str] = [
                    cmake_exe, str(TINYCC_MODULE),
                    "-B", str(build_temp),
                    "-G", cmake_gen,
                    "-A", cmake_arch,
                    f"-DCMAKE_MSVC_RUNTIME_LIBRARY={runtime}",
                    "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF",
                    "-DCMAKE_C_FLAGS=/GR- /MP"
                ]
                
                utils.Logger.detail(f"Configuring {arch_name} ({config})...")
                utils.run_process(configure_cmd, cwd=TINYCC_MODULE, env=vs_env)
                
                # 2. Build
                cpu_count = utils.get_cpu_limit()
                build_cmd: List[str] = [
                    cmake_exe, "--build", str(build_temp),
                    "--config", config,
                    "--target", "tinycc",
                    "--parallel", str(cpu_count)
                ]
                
                utils.Logger.detail(f"Building {arch_name} ({config})...")
                utils.run_process(build_cmd, cwd=TINYCC_MODULE, env=vs_env)
                
                # 3. Deploy Artifacts
                artifact_dst: Path = TINYCC_BIN / "lib" / arch_name / config
                utils.ensure_dir(artifact_dst)
                
                # Search specifically in the config subfolder
                lib_found = False
                for root, _, files in os.walk(build_temp):
                    if config in Path(root).parts:
                        if "tinycc.lib" in files:
                            shutil.copy2(Path(root) / "tinycc.lib", artifact_dst / "tinycc.lib")
                            lib_found = True
                
                if not lib_found:
                    utils.Logger.warn(f"Library tinycc.lib not found for {arch_name}/{config}")
                else:
                    utils.Logger.success(f"Deployed: {arch_name}/{config} tinycc.lib")

        # --- 3. Export Headers ---
        utils.Logger.detail("Exporting headers...")
        inc_dst: Path = TINYCC_BIN / "include"
        utils.ensure_dir(inc_dst)
        shutil.copy2(TINYCC_MODULE / "libtcc.h", inc_dst)
        utils.Logger.success("Headers exported successfully.")

        # --- 4. Finalize ---
        utils.write_build_token(token_dir, sources)
        utils.Logger.success(f"Build of {PRJ_NAME} completed successfully.")

    except Exception as e:
        utils.Logger.fatal(f"Unexpected failure in {PRJ_NAME} build: {e}")

if __name__ == "__main__":
    main()
