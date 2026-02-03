import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import build_utils as utils

def main() -> None:
    """
    Orchestrates the professional build process for Zydis using CMake.
    Adheres to CC-FLOW and CC-ARCH standards.
    """
    try:
        PRJ_NAME: str = "Zydis"
        
        # Directory Mapping
        ROOT_DIR: Path = Path(__file__).resolve().parent.parent
        MODULES_DIR: Path = ROOT_DIR / "modules"
        BIN_DIR: Path = ROOT_DIR / "bin"
        
        ZYDIS_MODULE: Path = MODULES_DIR / "zydis"
        ZYDIS_BIN: Path = BIN_DIR / "zydis"
        
        BUILDS_DIR: Path = Path(__file__).resolve().parent
        
        # --- 1. Dependency & Hash Validation ---
        utils.update_submodule(ZYDIS_MODULE)
        
        sources: List[Path] = [ZYDIS_MODULE, Path(__file__), BUILDS_DIR / "build_utils.py"]
        token_dir: Path = ZYDIS_BIN / ".tokens"
        token_file: Path = token_dir / ".valid"
        
        if not utils.check_build_needed(sources, token_file, clean_on_rebuild_path=ZYDIS_BIN):
            utils.Logger.success(f"{PRJ_NAME} is already up to date.")
            return

        utils.Logger.info(f"Starting Build: {PRJ_NAME} (Content change detected)")
        
        # Initialize Visual Studio Environment
        env_manager = utils.BuildEnv()
        cmake_gen: str = env_manager.get_cmake_generator()
        utils.Logger.info(f"Using CMake Generator: {cmake_gen}")
        
        # --- 2. Build Matrix ---
        ARCH_MAP: Dict[str, str] = {
            "x86": "Win32",
            "x64": "x64"
        }
        CONFIGS: List[str] = ["Release", "Debug"]
        
        # Common CMake Arguments (Ref: CC-FLAGS)
        COMMON_ARGS: List[str] = [
            "-DZYDIS_BUILD_EXAMPLES=OFF",
            "-DZYDIS_BUILD_TOOLS=OFF",
            "-DZYDIS_BUILD_TESTS=OFF",
            "-DZYDIS_BUILD_SHARED_LIB=OFF",
            "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF",
            "-DCMAKE_CXX_FLAGS=/GR- /EHsc /MP",
            "-DCMAKE_C_FLAGS=/GR- /MP"
        ]
        
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
                build_temp: Path = ZYDIS_MODULE / "build" / arch_name / config.lower()
                utils.clean_dir(build_temp)
                
                # Determine Runtime Library
                runtime: str = "MultiThreaded" if config == "Release" else "MultiThreadedDebug"
                
                # 1. Configure
                configure_cmd: List[str] = [
                    cmake_exe, str(ZYDIS_MODULE),
                    "-B", str(build_temp),
                    "-G", cmake_gen,
                    "-A", cmake_arch,
                    f"-DCMAKE_MSVC_RUNTIME_LIBRARY={runtime}"
                ] + COMMON_ARGS
                
                utils.Logger.detail(f"Configuring {arch_name} ({config})...")
                utils.run_process(configure_cmd, cwd=ZYDIS_MODULE, env=vs_env)
                
                # 2. Build
                cpu_count = utils.get_cpu_limit()
                build_cmd: List[str] = [
                    cmake_exe, "--build", str(build_temp),
                    "--config", config,
                    "--target", "Zydis",
                    "--parallel", str(cpu_count)
                ]
                
                utils.Logger.detail(f"Building {arch_name} ({config})...")
                utils.run_process(build_cmd, cwd=ZYDIS_MODULE, env=vs_env)
                
                # 3. Deploy Artifacts (Ref: CC-FIO-ORG)
                artifact_dst: Path = ZYDIS_BIN / "lib" / arch_name / config.lower()
                utils.ensure_dir(artifact_dst)
                
                # Zydis includes Zycore as a dependency, so we copy both
                libs_to_copy: List[str] = ["Zydis.lib", "Zycore.lib"]
                
                for lib in libs_to_copy:
                    # Search specifically in the config subfolder
                    lib_found = False
                    for root, _, files in os.walk(build_temp):
                        if config in Path(root).parts:
                            if lib in files:
                                shutil.copy2(Path(root) / lib, artifact_dst / lib)
                                # Also attempt to copy PDB
                                pdb_name = lib.replace(".lib", ".pdb")
                                if pdb_name in files:
                                    shutil.copy2(Path(root) / pdb_name, artifact_dst / pdb_name)
                                lib_found = True
                    
                    if not lib_found:
                        utils.Logger.warn(f"Library {lib} not found for {arch_name}/{config}")
                    else:
                        utils.Logger.success(f"Deployed: {arch_name}/{config} {lib}")

        # --- 3. Export Headers (Ref: CC-SDK-EXPORT) ---
        utils.Logger.detail("Exporting headers...")

        inc_dst: Path = ZYDIS_BIN / "include"
        utils.clean_dir(inc_dst)
        
        # Zydis headers
        # Zydis headers
        zydis_inc: Path = ZYDIS_MODULE / "include" / "Zydis"
        dst_inc_zydis: Path = inc_dst / "Zydis"
        
        # Copy main Zydis headers (e.g., Zydis.h, Decoder.h)
        utils.copy_files(zydis_inc, dst_inc_zydis, "*.h")
        
        # Copy subdirectories
        for sub in ["Generated", "Internal"]:
            if (zydis_inc / sub).exists():
                utils.copy_files(zydis_inc / sub, dst_inc_zydis / sub, "*.h")
        
        # Zycore headers (nested in dependencies)
        zycore_inc: Path = ZYDIS_MODULE / "dependencies" / "zycore" / "include"
        if zycore_inc.exists():
            utils.copy_files(zycore_inc, inc_dst, "*.h")
            
        utils.Logger.success("Headers exported successfully.")

        # --- 4. Finalize ---
        utils.write_build_token(token_dir, sources)
        utils.Logger.success(f"Build of {PRJ_NAME} completed successfully.")

    except Exception as e:
        utils.Logger.fatal(f"Unexpected failure in {PRJ_NAME} build: {e}")

if __name__ == "__main__":
    main()
