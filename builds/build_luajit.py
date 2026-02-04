import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import build_utils as utils

def clean_luajit_src(src_path: Path) -> None:
    """Cleans up internal build artifacts from LuaJIT source (Ref: CC-FS-PURGE)."""
    extensions = ["*.obj", "*.lib", "*.dll", "*.exe", "*.exp", "*.pdb", "*.manifest"]
    for ext in extensions:
        for f in src_path.glob(ext):
            try: f.unlink()
            except: pass
        for f in (src_path / "host").glob(ext):
            try: f.unlink()
            except: pass

def main() -> None:
    """
    Orchestrates the build process for LuaJIT using its internal msvcbuild.bat.
    Adheres to CC-FLOW and CC-ARCH standards.
    """
    try:
        PRJ_NAME: str = "LuaJIT"
        
        # Directory Mapping
        ROOT_DIR: Path = Path(__file__).resolve().parent.parent
        MODULES_DIR: Path = ROOT_DIR / "modules"
        BIN_DIR: Path = ROOT_DIR / "bin"
        
        LUAJIT_MODULE: Path = MODULES_DIR / "luajit"
        LUAJIT_SRC: Path = LUAJIT_MODULE / "src"
        LUAJIT_BIN: Path = BIN_DIR / "luajit"
        
        BUILDS_DIR: Path = Path(__file__).resolve().parent
        
        # --- 1. Dependency & Hash Validation ---
        utils.update_submodule(LUAJIT_MODULE)
        
        sources: List[Path] = [LUAJIT_MODULE, Path(__file__), BUILDS_DIR / "build_utils.py"]
        token_dir: Path = LUAJIT_BIN / ".tokens"
        token_file: Path = token_dir / ".valid"
        
        if not utils.check_build_needed(sources, token_file, clean_on_rebuild_path=LUAJIT_BIN):
            utils.Logger.success(f"{PRJ_NAME} is already up to date.")
            return

        utils.Logger.info(f"Starting Build: {PRJ_NAME} (Content change detected)")
        
        # Initialize Visual Studio Environment
        env_manager = utils.BuildEnv()
        
        # --- 2. Build Matrix ---
        ARCHS: List[str] = ["x86", "x64"]
        CONFIGS: List[str] = ["Release", "Debug"]
        
        for arch in ARCHS:
            # Capture environment for this architecture
            utils.Logger.detail(f"Setting up environment for {arch}...")
            vs_env = env_manager.get_env_vars(arch)
            
            for config in CONFIGS:
                utils.Logger.detail(f"Processing Architecture: {arch} | Configuration: {config}")
                
                # 1. Clean Source (LuaJIT builds in-tree)
                clean_luajit_src(LUAJIT_SRC)
                
                # 2. Setup Flags (Ref: CC-FLAGS)
                # LuaJIT uses 'LJCOMPILE' env var to inject custom flags in msvcbuild.bat
                lj_flags: str = "/GR- /EHsc"
                msvc_args: str = "static"
                
                if config == "Release":
                    lj_flags += " /MT /O2"
                else:
                    # Ref: USR-REQ-EMBED-PDB
                    lj_flags += " /MTd /Z7 /Od"
                    msvc_args = "debug static"
                
                # Setup compile command injection
                compile_cmd = f"cl /MP{utils.get_cpu_limit()} /nologo /c /W3 /D_CRT_SECURE_NO_DEPRECATE /D_CRT_STDIO_INLINE=__declspec(dllexport)__inline {lj_flags}"
                
                current_env = vs_env.copy()
                current_env["LJCOMPILE"] = compile_cmd
                
                # 3. Execute msvcbuild.bat
                utils.Logger.detail(f"Executing msvcbuild.bat for {arch} ({config})...")
                # msvcbuild.bat must be run from the src directory
                # Using cmd /c ensuring batch execution standard
                cmd_list = ["cmd", "/c", "msvcbuild.bat"] + msvc_args.split()
                
                utils.run_process(cmd_list, cwd=LUAJIT_SRC, env=current_env)
                
                # 4. Deploy Artifacts
                artifact_dst: Path = LUAJIT_BIN / "lib" / arch / config.lower()
                utils.ensure_dir(artifact_dst)
                
                lib_name = "lua51.lib"
                pdb_name = "lua51.pdb"
                
                src_lib = LUAJIT_SRC / lib_name
                src_pdb = LUAJIT_SRC / pdb_name
                
                if src_lib.exists():
                    shutil.move(src_lib, artifact_dst / "lua51.lib") # Rename for consistency
                    utils.Logger.success(f"Deployed: {arch}/{config} lua51.lib")
                else:
                    utils.Logger.error(f"Missing artifact: {src_lib}")

                # Clean PDBs (Embedded only)
                if src_pdb.exists():
                     src_pdb.unlink(missing_ok=True) # Ensure it's gone from source/temp
                
                if (artifact_dst / pdb_name).exists():
                     (artifact_dst / pdb_name).unlink(missing_ok=True)

        # --- 3. Export Headers ---
        utils.Logger.detail("Exporting headers...")

        inc_dst: Path = LUAJIT_BIN / "include"
        utils.clean_dir(inc_dst)
        
        # Copy core headers
        for h in ["lua.h", "luaconf.h", "lualib.h", "lauxlib.h", "luajit.h", "lua.hpp"]:
            src_h = LUAJIT_SRC / h
            if src_h.exists():
                shutil.copy2(src_h, inc_dst)
                
        # Copy JIT lua files
        jit_dst: Path = inc_dst / "jit"
        utils.ensure_dir(jit_dst)
        utils.copy_files(LUAJIT_SRC / "jit", jit_dst, "*.lua")
        
        utils.Logger.success("Headers and JIT scripts exported successfully.")

        # --- 4. Finalize ---
        utils.write_build_token(token_dir, sources)
        utils.Logger.success(f"Build of {PRJ_NAME} completed successfully.")

    except Exception as e:
        utils.Logger.fatal(f"Unexpected failure in {PRJ_NAME} build: {e}")

if __name__ == "__main__":
    main()
