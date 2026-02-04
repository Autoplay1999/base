import subprocess
import sys
import os
import argparse
from pathlib import Path
import build_utils as utils

# --- Configuration ---
BUILD_DIR = Path(__file__).parent.absolute()
LOG_DIR = BUILD_DIR.parent / "logs"

# The Unified Module List (100% Pythonized)
MODULES = [
    # Core Libraries (Individual Scripts)
    ("Zlib", "build_zlib.py"),
    ("TinyCC", "build_tinycc.py"),
    ("AsmJit", "build_asmjit.py"),
    ("CURL", "build_curl.py"),
    ("LuaJIT", "build_luajit.py"),
    ("Zydis", "build_zydis.py"),
    
    # Fast-Track Migration Scripts
    ("Headers-Only Libs", "build_headers_libs.py"), # Handles JSON, PHNT, NDK, LazyImporter, etc.
    ("CMake Libs", "build_cmake_libs.py"),
    
    # Complex Migration Scripts
    ("ImGui", "build_imgui.py"),
    ("KNSoft", "build_knsoft.py"),
]

import concurrent.futures
import time

def build_wrapper(module_info):
    name, script = module_info
    
    # Use per-module prefix for clean parallel output (Ref: CC-LOG-SYNC)
    prefix = f"{utils.Colors.GRAY}[{name}]{utils.Colors.ENDC}"
    
    timer = utils.Timer(name)
    try:
        with timer:
            # Propagate child mode to bypass internal logging threads in subprocesses
            child_env = dict(os.environ)
            child_env["BUILD_CHILD_MODE"] = "1"
            
            # Run Python script using unified run_process to ensure thread-safe output piping
            result = utils.run_process([sys.executable, script], cwd=BUILD_DIR, env=child_env, pipe_output=True, prefix=prefix)
        
        if result.returncode == 0:
            utils.Logger.success(f"[{name}] Completed.")
            return True, name, timer.duration

        else:
            utils.Logger.error(f"[{name}] FAILED (Code: {result.returncode})")
            return False, name, timer.duration
    except Exception as e:
        utils.Logger.error(f"[{name}] Unexpected Error: {e}")
        return False, name, 0.0

def run_build():
    parser = argparse.ArgumentParser(description="Unified Build System")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    # Mode selection (Ref: USR-REQ-MODES-GRANULAR)
    # sequential: 1 worker
    # lite:       25% cores
    # balanced:   50% cores (Default)
    # aggressive: 75% cores
    # full:       100% cores
    modes = ["sequential", "lite", "balanced", "aggressive", "full"]
    parser.add_argument("--mode", choices=modes, default="balanced", 
                      help="Build Mode: sequential (1), lite (25%%), balanced (50%%), aggressive (75%%), full (100%%)")
    parser.add_argument("--workers", type=int, help="Manual override for worker count")
    
    args = parser.parse_args()

    total_cores = os.cpu_count() or 4

    # Calculate Workers based on Mode
    if args.workers:
        workers = args.workers
        mode_name = f"Custom ({workers})"
    elif args.mode == "sequential":
        workers = 1
        mode_name = "Sequential (1)"
    elif args.mode == "lite":
        workers = max(1, int(total_cores * 0.25))
        mode_name = f"Lite (25% Cores: {workers} workers)"
    elif args.mode == "balanced":
        workers = max(1, int(total_cores * 0.50))
        mode_name = f"Balanced (50% Cores: {workers} workers)"
    elif args.mode == "aggressive":
        workers = max(1, int(total_cores * 0.75))
        mode_name = f"Aggressive (75% Cores: {workers} workers)"
    else: # full
        workers = total_cores
        mode_name = f"Full Power (100% Cores: {workers} workers)"

    # Calculate optimal threads per job to prevent over-subscription
    threads_per_job = max(1, total_cores // workers)
    os.environ["MAX_THREADS_PER_JOB"] = str(threads_per_job)
    
    utils.Logger.detail(f"Build Configuration: Mode={mode_name} | Workers={workers} | Threads/Job={threads_per_job} (System Cores: {total_cores})")
    utils.Logger.info(f"  UNIFIED BUILD SYSTEM (Mode: {mode_name})")

    # Propagate verbose setting via environment variable (Ref: CC-ENV-PROPAGATION)
    if args.verbose:
        os.environ["BUILD_VERBOSE"] = "1"
        utils.Logger.set_verbose(True)
    else:
        # Force disable if not requested (overrides external env vars)
        os.environ["BUILD_VERBOSE"] = "0"
        utils.Logger.set_verbose(False)

    utils.Logger.info("=" * 60)

    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Dependency Stages
    # Stage 1: Independent Modules (Can run in parallel)
    STAGE_1 = [
        ("Zlib", "build_zlib.py"), # Critical dependency for Curl
        ("TinyCC", "build_tinycc.py"),
        ("AsmJit", "build_asmjit.py"),
        ("LuaJIT", "build_luajit.py"),
        ("Zydis", "build_zydis.py"),
        ("Headers-Only Libs", "build_headers_libs.py"),
        ("CMake Libs", "build_cmake_libs.py"),
        ("ImGui", "build_imgui.py"),
        ("KNSoft", "build_knsoft.py"),
        ("VMP", "build_vmp.py"),
    ]

    # Stage 2: Dependent Modules (Must wait for Stage 1)
    STAGE_2 = [
        ("CURL", "build_curl.py"), # Depends on Zlib
    ]

    success_count = 0
    fail_count = 0
    total_timer = utils.Timer("Total Build")

    try:
        with total_timer:
            # Execute Stage 1
            utils.Logger.info(f"--- Stage 1: Independent Build Matrix ({len(STAGE_1)} modules) ---")
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(build_wrapper, mod): mod for mod in STAGE_1}
                for future in concurrent.futures.as_completed(futures):
                    success, name, _ = future.result()
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
            
            if fail_count > 0:
                utils.Logger.error("Stage 1 failures detected. Aborting Stage 2.")
                sys.exit(1)

            # Execute Stage 2
            utils.Logger.info(f"--- Stage 2: Dependent Build Matrix ({len(STAGE_2)} modules) ---")
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(build_wrapper, mod): mod for mod in STAGE_2}
                for future in concurrent.futures.as_completed(futures):
                    success, name, _ = future.result()
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
    except KeyboardInterrupt:
        utils.Logger.warning("\n[INTERRUPT] Build cancelled by user. Cleaning up...")
        utils.terminate_all()
        sys.exit(1)

    utils.Logger.info("-" * 60)
    utils.Logger.info("  FINAL BUILD SUMMARY")
    utils.Logger.info("-" * 60)
    utils.Logger.success(f"  Successful : {success_count}")
    if fail_count > 0:
        utils.Logger.error(f"  Failed     : {fail_count}")
        sys.exit(1)
    else:
        utils.Logger.success(f"  Failed     : 0")
    
    utils.Logger.info(f"  Total Time : {total_timer.duration:.2f}s")
    utils.Logger.info("=" * 60)
    
    # Flush logs
    utils.Logger.stop()

if __name__ == "__main__":
    run_build()
