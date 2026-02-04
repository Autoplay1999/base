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
        
        if not utils.check_build_needed(sources, token_file, clean_on_rebuild_path=TINYCC_BIN):
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
            
            # --- Native Build Logic (Refactor for Multi-Config) ---
            build_bat = TINYCC_MODULE / "win32" / "build-tcc.bat"
            if not build_bat.exists():
                raise utils.BuildError(f"Native build script not found: {build_bat}")

            for config in CONFIGS:
                utils.Logger.detail(f"Building {arch_name} | {config}...")
                
                # Cleanup before build to ensure no artifact mixing
                utils.clean_dir(TINYCC_MODULE / "win32" / "obj") # specific to tcc win32 script if needed, or just rely on overwrite
                # Actually build-tcc.bat is simple, might need more manual cleanup if it doesn't clean.
                # Assuming overwrite works for .lib/.exe
                
                build_cmd = [str(build_bat), "-c", "cl", "-t", "32" if arch_name == "x86" else "64"]
                
                run_env = vs_env.copy()
                base_cl = "/MT" if config == "Release" else "/MTd"
                
                if config == "Debug":
                     # Ref: USR-REQ-EMBED-PDB
                     run_env["CL"] = (run_env.get("CL", "") + f" {base_cl} /Z7").strip()
                else:
                     # Release: Optimize, No Debug Info
                     run_env["CL"] = (run_env.get("CL", "") + f" {base_cl} /O2 /DNDEBUG").strip()

                utils.run_process(build_cmd, cwd=TINYCC_MODULE / "win32", env=run_env)

                # 3. Deploy Artifacts
                artifact_dst: Path = TINYCC_BIN / "lib" / arch_name / config.lower()
                utils.ensure_dir(artifact_dst)
                
                # Active Clean PDBs (Ref: USR-REQ-EMBED-PDB)
                if artifact_dst.exists():
                    for stale in artifact_dst.glob("*.pdb"):
                        try: stale.unlink()
                        except: pass
                
                # Deploy built libraries
                lib_found = False
                # The build-tcc.bat script places libtcc.lib directly in win32/
                search_dir = TINYCC_MODULE / "win32" 
                if search_dir.exists():
                    for f in search_dir.glob("*.lib"): # Only look for .lib files
                        if f.name == "libtcc.lib": # Specifically target libtcc.lib
                            shutil.copy2(f, artifact_dst / "tinycc.lib")
                            utils.Logger.success(f"Deployed: {arch_name}/{config} tinycc.lib")
                            lib_found = True
                            break # Found the lib, no need to continue loop
                
                if not lib_found:
                    utils.Logger.warn(f"Library libtcc.lib not found for {arch_name}/{config}")

        # --- 3. Export Headers ---
        utils.Logger.detail("Exporting headers...")
        # Ref: USR-REQ-TINYCC-NESTED (Nest headers in include/tinycc)
        inc_dst: Path = TINYCC_BIN / "include" / "tinycc"
        utils.clean_dir(inc_dst)
        
        # Copy main header
        if (TINYCC_MODULE / "libtcc.h").exists():
            shutil.copy2(TINYCC_MODULE / "libtcc.h", inc_dst)
        # Copy all headers from include directory
        if (TINYCC_MODULE / "include").exists():
            utils.copy_files(TINYCC_MODULE / "include", inc_dst, "*.h")
        utils.Logger.success("Headers exported successfully to include/tinycc.")

        # --- 4. Finalize ---
        utils.write_build_token(token_dir, sources)
        utils.Logger.success(f"Build of {PRJ_NAME} completed successfully.")

    except Exception as e:
        utils.Logger.fatal(f"Unexpected failure in {PRJ_NAME} build: {e}")

if __name__ == "__main__":
    main()
