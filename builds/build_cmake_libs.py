import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import build_utils as utils

# --- Configuration ---
ROOT_DIR = utils.Config.ROOT_DIR
MODULES_DIR = utils.Config.MODULES_DIR
BIN_DIR = utils.Config.BIN_DIR
BUILDS_DIR = utils.Config.BUILDS_DIR

# (Name, ModuleDir, HeaderDir, HeaderPattern, CustomStepsFunc)
CMAKE_LIBS = [
    ("SimdJSON", "simdjson", "include", "*", None),
    ("Turbo-Base64", "Turbo-Base64", "include", "*", None),
    ("Yaml-CPP", "yaml-cpp", "include", "*", "patch_yaml_cpp"),
]

def patch_yaml_cpp(dst_inc: Path):
    """Applies YAML_CPP_STATIC_DEFINE patch (Ref: CC-PATCH)."""
    dll_h = dst_inc / "yaml-cpp" / "dll.h"
    if dll_h.exists():
        utils.Logger.info("Patching yaml-cpp/dll.h for static define...")
        content = dll_h.read_text()
        if "#define YAML_CPP_STATIC_DEFINE" not in content:
            new_content = content.replace("#define DLL_H_", "#define DLL_H_\n#define YAML_CPP_STATIC_DEFINE")
            dll_h.write_text(new_content)
            utils.Logger.success("Patch applied.")

def build_cmake_lib(name: str, mod_dir: str, header_dir: str, pattern: str, custom_func: str):
    try:
        utils.Logger.info(f"[{name}] Starting CMake build...")
        
        module_path = MODULES_DIR / mod_dir
        temp_install = module_path / "temp_install"
        
        utils.update_submodule(module_path)
        
        sources = [module_path, Path(__file__), BUILDS_DIR / "build_utils.py"]
        token_dir = BIN_DIR / name.lower() / ".tokens"
        if not utils.check_build_needed([module_path, Path(__file__)], token_dir / ".valid"):
            utils.Logger.success(f"[{name}] Already up to date.")
            return

        env_manager = utils.BuildEnv()
        PLATFORM_MAP = {"x86": "Win32", "x64": "x64"}
        CONFIGS = ["Release", "Debug"]

        for arch_name, cmake_arch in PLATFORM_MAP.items():
            for config in CONFIGS:
                # Clean temp install before each config build to prevent artifacts mixing
                if temp_install.exists():
                    shutil.rmtree(temp_install)

                utils.Logger.detail(f"[{name}] Building {arch_name}|{config}...")
                
                build_temp = module_path / "build" / arch_name / config
                utils.ensure_dir(build_temp)
                
                vs_env = env_manager.get_env_vars(arch_name)
                cmake_exe = env_manager.get_cmake_path(vs_env.get("PATH"))
                generator = env_manager.get_cmake_generator()
                
                # Configure
                # Configure
                runtime_lib = "MultiThreadedDebug" if config == "Debug" else "MultiThreaded"
                configure_cmd = [
                    cmake_exe,
                    "-S", str(module_path),
                    "-B", str(build_temp),
                    "-G", generator,
                    "-A", cmake_arch,
                    f"-DCMAKE_BUILD_TYPE={config}",
                    f"-DCMAKE_MSVC_RUNTIME_LIBRARY={runtime_lib}",
                    "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF",
                    "-DCMAKE_CXX_FLAGS=/GR- /MP",
                    "-DCMAKE_C_FLAGS=/MP",
                    "-DCMAKE_DEBUG_POSTFIX=",

                    f"-DCMAKE_INSTALL_PREFIX={temp_install}",
                    # Optimization & Speed (Ref: CC-OPT-SPEED)
                    "-DBUILD_TESTING=OFF",
                    "-DBUILD_EXAMPLES=OFF",
                    "-DBUILD_SHARED_LIBS=OFF"
                ]
                
                # Add specific standard for SimdJSON
                if name == "SimdJSON":
                    configure_cmd.append("-DCMAKE_CXX_STANDARD=20")
                
                # Add flag neutralizing for Turbo-Base64
                if name == "Turbo-Base64":
                    configure_cmd.extend([
                        "-DMARCH=\"\"",
                        "-DMSSE=\"\"",
                        "-DCMAKE_C_FLAGS_RELEASE=\"/O2 /Ob2 /DNDEBUG /MP\"",
                        "-DCMAKE_C_FLAGS_DEBUG=\"/Zi /RTC1 /DDEBUG /MP\""

                    ])
                
                # Use parallel build (Ref: CC-BUILD-PARALLEL)
                cpu_count = utils.get_cpu_limit()
                build_cmd = [cmake_exe, "--build", str(build_temp), "--config", config, "--parallel", str(cpu_count)]
                install_cmd = [cmake_exe, "--install", str(build_temp), "--config", config]

                utils.run_process(configure_cmd, cwd=module_path, env=vs_env)
                utils.run_process(build_cmd, cwd=module_path, env=vs_env)
                utils.run_process(install_cmd, cwd=module_path, env=vs_env)
                
                # Unified Deploy (lib)
                lib_base_dir = BIN_DIR / name.lower()
                lib_dst = lib_base_dir / "lib" / arch_name / config.lower()
                utils.ensure_dir(lib_dst)
                
                # Copy Libs and collect names for PDB matching (Ref: CC-DEPLOY-LIB)
                installed_stems = set()
                for f in temp_install.rglob("*.lib"):
                    target_name = f.name
                    
                    # Deduplicate SimdJSON: Keep simdjson.lib, skip simdjson_static.lib
                    if name == "SimdJSON" and f.stem.lower() == "simdjson_static":
                        utils.Logger.info(f"[{name}] Skipping redundant lib: {f.name}")
                        continue
                        
                    # Rename Turbo-Base64 lib to turbo-base64.lib
                    if name == "Turbo-Base64":
                        target_name = "turbo-base64.lib"
                        utils.Logger.info(f"[{name}] Renaming lib to: {target_name}")

                    shutil.copy2(f, lib_dst / target_name)
                    installed_stems.add(Path(target_name).stem.lower())
                
                # Copy only relevant PDBs
                for f in build_temp.rglob("*.pdb"):
                    # For Turbo-Base64, PDB name should also match renamed lib name
                    if name == "Turbo-Base64":
                        if f.stem.lower() == "turbo-base64":
                            shutil.copy2(f, lib_dst)
                        elif f.stem.lower() == "turbo_base64": # Original name likely
                            shutil.copy2(f, lib_dst / "turbo-base64.pdb")
                    elif f.stem.lower() in installed_stems:
                        shutil.copy2(f, lib_dst)

        # Export Headers (Unified)
        utils.Logger.detail(f"[{name}] Exporting headers...")

        dst_inc = BIN_DIR / name.lower() / "include"
        
        # SimdJSON requires headers to be in include/simdjson/
        if name == "SimdJSON":
            dst_inc = dst_inc / "simdjson"
            
        src_inc = temp_install / "include"
        utils.ensure_dir(dst_inc)

        utils.copy_files(src_inc, dst_inc, "*", recursive=True)
            
        # Fix Turbo-Base64 include subfolder rename (Ref: CC-PATH-REN)
        if name == "Turbo-Base64":
            incorrect_sub = dst_inc / "turbobase64"
            correct_sub = dst_inc / "turbo-base64"
            if incorrect_sub.exists() and not correct_sub.exists():
                utils.Logger.info(f"[{name}] Renaming include subfolder to: {correct_sub.name}")
                incorrect_sub.rename(correct_sub)

        if custom_func == "patch_yaml_cpp":
            patch_yaml_cpp(dst_inc)

        # Cleanup
        if temp_install.exists():
            shutil.rmtree(temp_install)
        # 5. Finalize
        utils.write_build_token(token_dir, [module_path, Path(__file__)])
        utils.Logger.success(f"[{name}] Completed.")

    except Exception as e:
        utils.Logger.error(f"[{name}] Failed: {e}")

def main():
    utils.Logger.info("=" * 60)
    utils.Logger.info("  Unified CMake Build System (Consolidated)")
    utils.Logger.info("=" * 60)

    for item in CMAKE_LIBS:
        build_cmake_lib(*item)

if __name__ == "__main__":
    main()
