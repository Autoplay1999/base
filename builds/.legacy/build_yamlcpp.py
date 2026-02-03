import os
import sys
import shutil
import subprocess
from pathlib import Path

# Fix import path for build_utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import build_utils as utils

def build_yamlcpp():
    module_name = "yaml-cpp"
    source_dir = utils.Config.MODULES_DIR / "yaml-cpp"
    temp_install = source_dir / "temp_install"
    
    utils.Logger.info(f"[{module_name}] Starting build...")

    if not source_dir.exists():
        utils.Logger.error(f"[{module_name}] Source directory not found: {source_dir}")
        return False

    # 1. Check if build is needed
    token_dir = utils.Config.TOKENS_DIR / module_name.lower()
    if not utils.check_build_needed([source_dir, Path(__file__)], token_dir / ".valid"):
        utils.Logger.success(f"[{module_name}] Already up to date.")
        return True

    # 2. Update Submodule
    utils.update_submodule(source_dir)

    # 3. Environment & Build Loop
    try:
        env_manager = utils.BuildEnv()
        PLATFORM_MAP = {"x86": "Win32", "x64": "x64"}
        success = True

        for arch_name, cmake_arch in PLATFORM_MAP.items():
            for config in ["Release", "Debug"]:
                utils.Logger.info(f"[{module_name}] Building {arch_name}|{config}...")
                
                build_dir = source_dir / "build" / arch_name / config
                utils.ensure_dir(build_dir)
                
                env = env_manager.get_env_vars(arch_name)
                cmake_exe = env_manager.get_cmake_path(env.get("PATH"))
                generator = env_manager.get_cmake_generator()

                # CMake Configure
                cmake_args = [
                    cmake_exe,
                    "-S", str(source_dir),
                    "-B", str(build_dir),
                    "-G", generator,
                    "-A", cmake_arch,
                    f"-DCMAKE_BUILD_TYPE={config}",
                    "-DYAML_BUILD_SHARED_LIBS=OFF",
                    "-DYAML_CPP_BUILD_TESTS=OFF",
                    "-DYAML_CPP_BUILD_TOOLS=OFF",
                    "-DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded",
                    f"-DCMAKE_INSTALL_PREFIX={temp_install}"
                ]

                subprocess.run(cmake_args, cwd=build_dir, env=env, check=True)
                subprocess.run([cmake_exe, "--build", ".", "--config", config], cwd=build_dir, env=env, check=True)
                subprocess.run([cmake_exe, "--install", ".", "--config", config], cwd=build_dir, env=env, check=True)

                # Move Artifacts to Centralized Location
                lib_dst = utils.Config.BIN_DIR / "lib" / arch_name / config.lower()
                utils.ensure_dir(lib_dst)
                
                # yaml-cpp installs to temp_install/lib
                for f in temp_install.rglob("*.lib"):
                    shutil.copy2(f, lib_dst / f.name)
                for f in build_dir.rglob("*.pdb"):
                    shutil.copy2(f, lib_dst / f.name)
                
                # Patch for static define if needed
                if config == "Release":
                     dll_h = temp_install / "include" / "yaml-cpp" / "dll.h"
                     if dll_h.exists():
                         content = dll_h.read_text()
                         if "#define YAML_CPP_STATIC_DEFINE" not in content:
                             new_content = content.replace("#define DLL_H_", "#define DLL_H_\n#define YAML_CPP_STATIC_DEFINE")
                             dll_h.write_text(new_content)

                if (temp_install / "lib").exists():
                    shutil.rmtree(temp_install / "lib")

        # Export Headers (Unified)
        utils.Logger.info(f"[{module_name}] Exporting headers...")
        dst_inc = utils.Config.BIN_DIR / "include"
        # Move yaml-cpp headers to bin/include
        utils.copy_files(temp_install / "include", dst_inc, "*", recursive=True)
        
        # Final Cleanup
        if temp_install.exists():
            shutil.rmtree(temp_install)
        # Finalize
        utils.write_build_token(token_dir, [source_dir, Path(__file__)])
        utils.Logger.success(f"[{module_name}] Completed.")
        return True

    except Exception as e:
        utils.Logger.error(f"[{module_name}] Build Failed: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if build_yamlcpp() else 1)
