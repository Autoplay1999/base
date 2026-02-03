import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import build_utils as utils

def main() -> None:
    """
    Orchestrates the professional build process for CURL using CMake.
    Adheres to CC-FLOW and CC-ARCH standards.
    """
    try:
        PRJ_NAME: str = "CURL"
        
        # Directory Mapping
        ROOT_DIR: Path = Path(__file__).resolve().parent.parent
        MODULES_DIR: Path = ROOT_DIR / "modules"
        BIN_DIR: Path = ROOT_DIR / "bin"
        
        CURL_MODULE: Path = MODULES_DIR / "curl"
        CURL_BIN: Path = BIN_DIR / "curl"
        
        BUILDS_DIR: Path = Path(__file__).resolve().parent
        
        # --- 1. Dependency & Hash Validation (Ref: CC-DEP, CC-VAL-HASH) ---
        utils.update_submodule(CURL_MODULE)
        
        sources: List[Path] = [CURL_MODULE, Path(__file__), BUILDS_DIR / "build_utils.py"]
        token_dir: Path = CURL_BIN / ".tokens"
        token_file: Path = token_dir / ".valid"
        
        if not utils.check_build_needed(sources, token_file):
            utils.Logger.success(f"{PRJ_NAME} is already up to date.")
            return

        utils.Logger.info(f"Starting Build: {PRJ_NAME} (Content change detected)")
        
        # Initialize Visual Studio Environment
        env_manager = utils.BuildEnv()
        cmake_gen: str = env_manager.get_cmake_generator()
        utils.Logger.detail(f"Using CMake Generator: {cmake_gen}")
        
        # --- 2. Build Matrix (Ref: CC-ARCH-MATRIX) ---
        ARCH_MAP: Dict[str, str] = {
            "x86": "Win32",
            "x64": "x64"
        }
        # CURL usually builds both Debug and Release for each arch
        CONFIGS: List[str] = ["Release", "Debug"]
        
        # Common CMake Arguments (Ref: CC-FLAGS)
        # Enforce Standard: Static Runtime, No RTTI
        COMMON_ARGS: List[str] = [
            "-DBUILD_SHARED_LIBS=OFF",
            "-DCURL_USE_SCHANNEL=ON",
            "-DCURL_USE_OPENSSL=OFF",
            "-DENABLE_UNICODE=ON",
            "-DENABLE_IPV6=ON",
            "-DCURL_WINDOWS_SSPI=ON",
            "-DBUILD_CURL_EXE=OFF",
            "-DBUILD_TESTING=OFF",
            "-DCURL_STATIC_CRT=ON",
            "-DCURL_USE_LIBPSL=OFF",
            "-DCURL_use_LIBSSH2=OFF",
            "-DCURL_USE_LIBIDN2=OFF",
            "-DCURL_BROTLI=OFF",
            "-DCURL_ZSTD=OFF",
            "-DUSE_NGHTTP2=OFF",
            "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF",
            "-DCMAKE_CXX_FLAGS=/GR- /EHsc /MP",
            "-DCMAKE_C_FLAGS=/GR- /MP"
        ]
        
        for arch_name, cmake_arch in ARCH_MAP.items():
            # Capture environment for this architecture (Ref: CC-ENV-ISOLATION)
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
                build_temp: Path = CURL_MODULE / "build" / arch_name / config.lower()
                utils.clean_dir(build_temp)
                
                # 1. Configure
                configure_cmd: List[str] = [
                    cmake_exe, str(CURL_MODULE),
                    "-B", str(build_temp),
                    "-G", cmake_gen,
                    "-A", cmake_arch
                ] + COMMON_ARGS
                
                utils.Logger.detail(f"Configuring {arch_name} ({config})...")
                utils.run_process(configure_cmd, cwd=CURL_MODULE, env=vs_env)
                
                # 2. Build
                cpu_count = utils.get_cpu_limit()
                build_cmd: List[str] = [
                    cmake_exe, "--build", str(build_temp),
                    "--config", config,
                    "--target", "libcurl_static", 
                    "--parallel", str(cpu_count)
                ]
                
                utils.Logger.detail(f"Building {arch_name} ({config})...")
                utils.run_process(build_cmd, cwd=CURL_MODULE, env=vs_env)
                
                # 3. Deploy Artifacts (Ref: CC-FIO-ORG)
                artifact_dst: Path = CURL_BIN / "lib" / arch_name / config.lower()
                utils.ensure_dir(artifact_dst)
                
                # Heuristic search for libcurl*.lib in the 'lib' subfolder of build
                lib_found = False
                search_dir = build_temp / "lib" / config
                if search_dir.exists():
                    for root, _, files in os.walk(search_dir):
                        for name in files:
                            if name.endswith(".lib") and "libcurl" in name.lower():
                                shutil.copy2(Path(root) / name, artifact_dst / "libcurl.lib")
                                lib_found = True
                                
                            if name.endswith(".pdb") and "libcurl" in name.lower():
                                shutil.copy2(Path(root) / name, artifact_dst / "libcurl.pdb")
                
                if lib_found:
                    utils.Logger.success(f"Deployed: {arch_name}/{config} library")
                else:
                    utils.Logger.error(f"Failed to find libcurl library in {build_temp}")

        # --- 3. Export Headers (Ref: CC-SDK-EXPORT) ---
        utils.Logger.detail("Exporting headers...")

        header_src: Path = CURL_MODULE / "include" / "curl"
        header_dst: Path = CURL_BIN / "include" / "curl"
        
        utils.clean_dir(header_dst)
        utils.copy_files(header_src, header_dst, "*.h")
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
