import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import build_utils as utils

def main() -> None:
    """
    Orchestrates the professional build process for AsmJit using CMake.
    Adheres to CC-FLOW and CC-ARCH standards.
    """
    try:
        PRJ_NAME: str = "AsmJit"
        
        # Directory Mapping
        ROOT_DIR: Path = Path(__file__).resolve().parent.parent
        MODULES_DIR: Path = ROOT_DIR / "modules"
        BIN_DIR: Path = ROOT_DIR / "bin"
        
        ASMJIT_MODULE: Path = MODULES_DIR / "asmjit"
        ASMJIT_BIN: Path = BIN_DIR / "asmjit"
        
        BUILDS_DIR: Path = Path(__file__).resolve().parent
        
        # --- 1. Dependency & Hash Validation (Ref: CC-DEP, CC-VAL-HASH) ---
        utils.update_submodule(ASMJIT_MODULE)
        
        sources: List[Path] = [ASMJIT_MODULE, Path(__file__), BUILDS_DIR / "build_utils.py"]
        token_dir: Path = ASMJIT_BIN / ".tokens"
        token_file: Path = token_dir / ".valid"
        
        if not utils.check_build_needed(sources, token_file, clean_on_rebuild_path=ASMJIT_BIN):
            utils.Logger.success(f"{PRJ_NAME} is already up to date.")
            return

        utils.Logger.info(f"Starting Build: {PRJ_NAME} (Content change detected)")
        
        # Initialize Visual Studio Environment
        env_manager = utils.BuildEnv()
        cmake_gen: str = env_manager.get_cmake_generator()
        
        # --- 2. Build for each Architecture & Config (Ref: CC-MULTI-ARCH) ---
        PLATFORMS: List[Tuple[str, str]] = [("x86", "Win32"), ("x64", "x64")]
        CONFIGS: List[str] = ["Release", "Debug"]
        
        for arch_name, cmake_arch in PLATFORMS:
            # Capture environment for this architecture (Ref: CC-ENV-ISOLATION)
            utils.Logger.detail(f"Setting up environment for {arch_name}...")
            vs_env = env_manager.get_env_vars(arch_name)
            cmake_exe: str = env_manager.get_cmake_path(vs_env.get("PATH"))

            for config in CONFIGS:
                utils.Logger.detail(f"Processing Architecture: {arch_name} | Configuration: {config}")

                
                build_temp: Path = ASMJIT_MODULE / "build" / arch_name / config.lower()
                utils.clean_dir(build_temp)

                # CMake Configure
                # Enforce Standard: Static Runtime, No RTTI, No Interprocedural Optimization (for stability)
                cmd_conf = [
                    cmake_exe,
                    "-S", str(ASMJIT_MODULE),
                    "-B", str(build_temp),
                    "-G", cmake_gen,
                    "-A", cmake_arch,
                    f"-DCMAKE_BUILD_TYPE={config}",
                    "-DASMJIT_STATIC=ON",
                    "-DASMJIT_TEST=OFF",
                    "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF",
                    f"-DCMAKE_MSVC_RUNTIME_LIBRARY={'MultiThreadedDebug' if config == 'Debug' else 'MultiThreaded'}", # CC-RT-STATIC
                    "-DCMAKE_CXX_FLAGS=/GR- /EHsc /MP",
                    "-DCMAKE_C_FLAGS=/GR- /MP",

                    # Ref: USR-REQ-EMBED-PDB
                    "-DCMAKE_CXX_FLAGS_DEBUG=/MTd /Z7 /Ob0 /Od /RTC1 /EHsc",
                    "-DCMAKE_C_FLAGS_DEBUG=/MTd /Z7 /Ob0 /Od /RTC1",

                    # Force Clean Release (Ref: USR-REQ-NO-DEBUG-INFO)
                    "-DCMAKE_CXX_FLAGS_RELEASE=/MT /O2 /Ob2 /DNDEBUG",
                    "-DCMAKE_C_FLAGS_RELEASE=/MT /O2 /Ob2 /DNDEBUG"
                ]
                
                utils.Logger.detail(f"Configuring {arch_name}/{config}...")
                utils.run_process(cmd_conf, cwd=ASMJIT_MODULE, env=vs_env)
                
                # CMake Build
                cpu_count = utils.get_cpu_limit()
                cmd_build = [
                    cmake_exe,
                    "--build", str(build_temp),
                    "--config", config,
                    "--parallel", str(cpu_count)
                ]
                
                utils.Logger.detail(f"Building {arch_name}/{config}...")
                utils.run_process(cmd_build, cwd=ASMJIT_MODULE, env=vs_env)
                
                # Manual Artifact Deployment (Ref: CC-DEPLOY)
                artifact_dst: Path = ASMJIT_BIN / "lib" / arch_name / config.lower()
                utils.ensure_dir(artifact_dst)
                
                # Known lib names for AsmJit
                artifact_src: Path = build_temp / config / "asmjit.lib"
                pdb_src: Path = build_temp / config / "asmjit.pdb"
                
                lib_found = False
                if artifact_src.exists():
                    shutil.copy2(artifact_src, artifact_dst)
                    utils.Logger.success(f"Deployed: {arch_name}/{config} library")
                    lib_found = True
                
                if not lib_found:
                    utils.Logger.error(f"Missing artifact: {artifact_src}")
                
                # Active Clean PDBs
                if artifact_dst.exists():
                     for stale in artifact_dst.glob("*.pdb"):
                         try: stale.unlink()
                         except: pass

                # No PDB Copy - Embedded Only

        # --- 3. Export Headers (Ref: CC-SDK-EXPORT) ---
        utils.Logger.detail("Exporting headers...")

        header_src: Path = ASMJIT_MODULE / "asmjit"
        header_dst: Path = ASMJIT_BIN / "include" / "asmjit"
        
        utils.clean_dir(header_dst)
        # Recursively copy all headers to preserve structure (core, arm, x86, etc.)
        utils.copy_files(header_src, header_dst, "*.h", recursive=True)
            
        utils.Logger.success("Headers exported successfully.")

        # --- 4. Finalize ---
        utils.write_build_token(token_dir, sources)
        utils.Logger.success(f"Build of {PRJ_NAME} completed successfully.")

    except subprocess.CalledProcessError as e:
        utils.Logger.fatal(f"CMake Process failed: {e}")
    except utils.BuildError as e:
        utils.Logger.fatal(f"Build Failure: {e}")
    except Exception as e:
        utils.Logger.fatal(f"Unexpected failure: {e}")

if __name__ == "__main__":
    main()
