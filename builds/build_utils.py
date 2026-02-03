import os
import sys
import shutil
import subprocess
import hashlib
import io
from pathlib import Path
from typing import List, Dict, Optional, Union

# --- Common Paths ---
# C:/Users/Misaki/.sdk/base/builds/build_utils.py -> base/
BUILDS_DIR = Path(__file__).resolve().parent
ROOT_DIR = BUILDS_DIR.parent
MODULES_DIR = ROOT_DIR / "modules"
BIN_DIR = ROOT_DIR / "bin"
TOKENS_DIR = BUILDS_DIR / ".tokens"

class Config:
    """Centralized configuration for the build system."""
    ROOT_DIR = ROOT_DIR
    MODULES_DIR = MODULES_DIR
    BIN_DIR = BIN_DIR
    BUILDS_DIR = BUILDS_DIR
    TOKENS_DIR = TOKENS_DIR

import time

# Enable ANSI escape codes on Windows 10+
if os.name == 'nt':
    os.system('')

class Colors:
    """Design Tokens for CLI Feedback (Ref: UI-UX Standards)."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAY = '\033[90m'

import threading

import threading
import queue

import atexit

# Global process registry for graceful termination (Ref: CC-LOG-TERMINATE)
_active_processes = set()
_processes_lock = threading.Lock()

class Logger:
    _verbose = os.environ.get("BUILD_VERBOSE") == "1"
    _queue = queue.SimpleQueue()
    _thread = None
    _lock = threading.Lock() # Global lock for thread-safe initialization (Ref: CC-LOG-SYNC)
    _print_lock = threading.Lock() # Global lock for atomic console output (Ref: CC-LOG-PRINT-ATOMIC)

    @staticmethod
    def _worker():
        while True:
            msg = Logger._queue.get()
            if msg is None: break # Sentinel to stop
            with Logger._print_lock:
                # Use sys.stdout.write for atomic line output (Ref: CC-LOG-ATOMIC-SYSCALL)
                # Concatenating \n ensures the entire line is sent in one write operation
                sys.stdout.write(str(msg) + '\n')
                sys.stdout.flush() 


    @staticmethod
    def _sanitize(text: str) -> str:
        """
        Strips ANSI escape codes and ALL control characters except Tab/Newline.
        This prevents cursor-moving characters (like \b, \r) from distorting the console (Ref: CC-LOG-PURITY-GOD).
        """
        # 1. Strip ANSI escape sequences
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', text)
        
        # 2. Strip ALL control characters (ASCII 0-31, 127) except tab (\t = 9)
        # We handle \n and \r at the line-split level, so here we remove them to be safe.
        return "".join(c for c in text if ord(c) >= 32 or c == '\t')


    @staticmethod
    def start():
        # Silence background worker in child mode to prevent nested pipe contention (Ref: CC-LOG-BYPASS)
        if os.environ.get("BUILD_CHILD_MODE") == "1":
            return
        with Logger._lock:
            if Logger._thread is None:
                Logger._thread = threading.Thread(target=Logger._worker, daemon=True)
                Logger._thread.start()

    @staticmethod
    def stop():
        if os.environ.get("BUILD_CHILD_MODE") == "1":
            return
        with Logger._lock:
            if Logger._thread:
                Logger._queue.put(None)
                Logger._thread.join()
                Logger._thread = None # Reset for potential restart

    @staticmethod
    def set_verbose(enabled: bool):
        Logger._verbose = enabled

    @staticmethod
    def _print(msg: str):
        # Use global print lock and atomic write for output (Ref: CC-LOG-PRINT-ATOMIC)
        if os.environ.get("BUILD_CHILD_MODE") == "1":
            with Logger._print_lock:
                # Atomic write: single operation to prevent character-level interleaving
                sys.stdout.write(str(msg) + '\n')
                sys.stdout.flush()
            return


        # Ensure thread is running (lazy start)
        if Logger._thread is None:
            Logger.start()
        if Logger._thread: # Check again in case start() returned early
            Logger._queue.put(msg)
        else:
            # Fallback for parent process if start() was bypassed (shouldn't happen)
            print(msg)
            sys.stdout.flush()

    @staticmethod
    def info(msg: str):
        Logger._print(f"{Colors.OKCYAN}[INFO]{Colors.ENDC} {msg}")

    @staticmethod
    def verbose(msg: str):
        if Logger._verbose:
            Logger._print(f"{Colors.GRAY}[DEBUG]{Colors.ENDC} {msg}")

    @staticmethod
    def success(msg: str):
        Logger._print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {msg}")

    @staticmethod
    def detail(msg: str):
        if Logger._verbose:
            Logger._print(f"{Colors.OKBLUE}[DETAIL]{Colors.ENDC} {msg}")

    @staticmethod
    def warn(msg: str):
        Logger._print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {msg}")

    @staticmethod
    def error(msg: str):
        Logger._print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {msg}")

    @staticmethod
    def fatal(msg: str):
        Logger.error(msg)
        sys.exit(1)

# Register stop handler to ensure all processes flush their queue on exit (Ref: CC-LOG-ATEXIT)
atexit.register(Logger.stop)

def get_cpu_limit() -> int:
    """
    Returns the optimal number of threads per build job.
    Respects global limits to prevent system freeze during parallel project builds.
    (Ref: CC-RES-ALLOC)
    """
    try:
        # Check for dynamic limit set by build_all.py
        env_limit = os.environ.get("MAX_THREADS_PER_JOB")
        if env_limit:
            return int(env_limit)
        
        # Default to full system cores (safe for sequential runs)
        return os.cpu_count() or 4
    except:
        return 4

def run_process(cmd: List[str], cwd: Path = None, env: Dict[str, str] = None, check: bool = True, pipe_output: bool = False, prefix: str = None) -> subprocess.CompletedProcess:
    """
    Executes a subprocess with managed output visibility (Quiet by default).
    Captures and streams output via Logger to prevent console interleaving.
    """
    verbose = Logger._verbose
    
    # Always merge stderr into stdout for consistent linear output
    # Creation flags for Windows to support process groups (Ref: CC-PROC-TERMINATION-GROUP)
    creationflags = 0
    if os.name == 'nt':
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    # Isolate stdin to prevent tools from detecting interactive console (Ref: CC-LOG-ISOLATION-STDIN)
    # This stops Git/CMake from writing to CONOUT$ directly
    process = subprocess.Popen(
        cmd, 
        cwd=cwd, 
        env=env, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL, # Explicitly detach stdin
        text=False, # Binary mode for universal compatibility
        bufsize=0, # Unbuffered for real-time feedback
        creationflags=creationflags
    )
    
    # Register process for tracking
    with _processes_lock:
        _active_processes.add(process)
    
    # Stream output if verbose or explicitly requested (useful for parent-child piping)
    # Ref: CC-LOG-SYNC-GOD-TIER (Block-based binary capture with manual EOL handling)
    output_lines = []
    
    # Determine system encoding for decoding build logs
    import locale
    encoding = locale.getpreferredencoding()
    
    def process_line(b_line: bytearray):
        # Decode and handle carriage returns (\r)
        # Ref: CC-LOG-COLLAPSE (Collapse \r segments to the last one to prevent fragmentation)
        raw_text = b_line.decode(encoding, errors='replace')
        
        # If there are carriage returns, it's likely a progress bar. 
        # We take the last segment to avoid logging 100 partial lines.
        if '\r' in raw_text:
            segments = [s.strip() for s in raw_text.split('\r') if s.strip()]
            stripped = segments[-1] if segments else ""
        else:
            stripped = raw_text.strip()
        
        # Skip empty lines when prefix is present to prevent log noise (Ref: CC-LOG-QUIET-EMPTY)
        if prefix and not stripped:
            return

        # Sanitize child output: remove ANSI and ALL hidden control characters (Ref: CC-LOG-PURITY-GOD)
        if prefix:
            stripped = Logger._sanitize(stripped)

        output_lines.append(stripped)
        if verbose or pipe_output:
            msg = f"{prefix} {stripped}" if prefix else stripped
            Logger._print(msg)
    
    # Track partial lines across reads
    remnant = bytearray()
    
    def process_chunk(chunk: bytes):
        nonlocal remnant
        buffer = remnant + chunk
        
        # Search ONLY for line feed: \n (byte 10)
        # We handle \r (carriage return) inside process_line to collapse progress bars (Ref: CC-LOG-SYNC-GOD-V3)
        start = 0
        for i in range(len(buffer)):
            char = buffer[i]
            if char == 10: # \n (Line Feed)
                line_segment = buffer[start:i]
                # Even if empty, we might want it (unless prefixed)
                process_line(bytearray(line_segment))
                start = i + 1
        
        remnant = buffer[start:]

    try:
        # Use block-based reading for maximum robustness and performance (Ref: CC-LOG-SYNC-GOD-TIER)
        while True:
            # Read a chunk. 4096 is a good standard buffer size.
            chunk = process.stdout.read(4096)
            if not chunk:
                break
            process_chunk(chunk)
        
        # Process any remaining data at EOF
        if remnant:
            process_line(remnant)
        
        rc = process.wait() # Ensure process is fully closed
    except KeyboardInterrupt:
        terminate_all()
        # Re-raise for the top-level main() to handle if needed
        raise
    
    # Unregister process on completion
    with _processes_lock:
        if process in _active_processes:
            _active_processes.remove(process)
            
    full_output = "\n".join(output_lines)
    
    if check and rc != 0:
        # On failure in quiet mode, dump the captured output so the user sees what happened
        # Skip if we already piped the output to avoid redundancy
        if not verbose and not pipe_output:
            Logger.error(f"Command failed (RC={rc}): {' '.join(cmd)}")
            for line in output_lines:
                msg = f"{prefix} {line}" if prefix else line
                Logger._print(f"{Colors.GRAY}{msg}{Colors.ENDC}")
        else:
            Logger.error(f"Command failed (RC={rc})")
            
        raise subprocess.CalledProcessError(rc, cmd, output=full_output)
        
    return subprocess.CompletedProcess(cmd, rc, stdout=full_output)

class Timer:
    """High-precision timer for build performance metrics."""
    def __init__(self, name: str = None):
        self.name = name
        self.start_time = 0
        self.end_time = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        duration = self.end_time - self.start_time
        if self.name:
            # Timings are useful info, but keep at detail level to avoid noise (Ref: CC-LOG-UX)
            Logger.detail(f"[{self.name}] Time: {duration:.2f}s")

    
    @property
    def duration(self) -> float:
        return time.perf_counter() - self.start_time

class BuildError(Exception):
    """Custom exception for build-related failures."""
    pass

class BuildEnv:
    """Management of Build Environments (Visual Studio, MSBuild, etc.)."""
    def __init__(self):
        self.vs_path = self._locate_vs_path()
        if not self.vs_path:
            raise BuildError("Visual Studio installation not found via vswhere.")
        
        self.msbuild_path = self._locate_msbuild()
        if not self.msbuild_path:
            raise BuildError("MSBuild.exe not found in VS installation.")
        
        Logger.detail(f"VS Path: {self.vs_path}")
        Logger.detail(f"MSBuild: {self.msbuild_path}")

    def _locate_msbuild(self) -> Optional[Path]:
        """Finds MSBuild.exe within the VS installation path."""
        # Standard path for VS 2022+
        path = self.vs_path / "MSBuild/Current/Bin/MSBuild.exe"
        if not path.exists():
            # Fallback for older versions or different structures
            path = self.vs_path / "MSBuild/15.0/Bin/MSBuild.exe"
        return path
    
    def _locate_vs_path(self) -> Optional[Path]:
        """Internal helper to find VS installation using vswhere.exe."""
        vswhere = os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe")
        if not os.path.exists(vswhere):
            return None
            
        cmd = [
            vswhere, "-latest", "-products", "*", 
            "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
            "-property", "installationPath"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            path = result.stdout.strip()
            return Path(path) if path and os.path.exists(path) else None
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def get_env_vars(self, arch: str = 'x64') -> Dict[str, str]:
        """
        Captures Visual Studio environment variables for a specific architecture.
        (Ref: CC-ENV-ISOLATION)
        """
        script_map = {
            'x64': "VC/Auxiliary/Build/vcvars64.bat",
            'x86': "VC/Auxiliary/Build/vcvars32.bat",
            'win32': "VC/Auxiliary/Build/vcvars32.bat"
        }
        
        rel_path = script_map.get(arch.lower(), "Common7/Tools/VsDevCmd.bat")
        bat_path = self.vs_path / rel_path

        if not bat_path.exists():
            raise BuildError(f"Environment script not found: {bat_path}")

        # Capture environment by piping 'set' output from the batch execution
        cmd = f'"{bat_path}" >nul 2>&1 & set'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if not result.stdout:
            # Fallback to simple env if vcvars failed to produce stdout
            return dict(os.environ)

        env = dict(os.environ)
        for line in result.stdout.splitlines():
            if '=' in line:
                key, val = line.split('=', 1)
                # Normalize keys to uppercase for consistency (Ref: CC-ENV-NORM)
                env[key.upper()] = val
        return env

    def get_cmake_path(self, path_env: Optional[str]) -> str:
        """Finds cmake.exe in the VS environment or system path."""
        if not path_env:
            path_env = os.environ.get("PATH", "")
            
        for p in path_env.split(os.pathsep):
            cmake_exe = Path(p) / "cmake.exe"
            if cmake_exe.exists():
                return str(cmake_exe)
        return "cmake"

    def get_cmake_generator(self) -> str:
        """
        Dynamically determines the CMake generator string for the current VS installation.
        (Ref: CC-ENV-DYNAMIC)
        """
        vswhere = os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe")
        cmd = [vswhere, "-latest", "-property", "catalog_featureReleaseYear"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            year = result.stdout.strip()
            if year == "2022": return "Visual Studio 17 2022"
            if year == "2019": return "Visual Studio 16 2019"
            if year == "2026": return "Visual Studio 18 2026"
            return "Visual Studio 17 2022" # Default
        except:
            return "Visual Studio 17 2022"

def ensure_dir(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

def clean_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)
    ensure_dir(path)

def calculate_hash(sources: List[Union[str, Path]]) -> str:
    """Calculates cumulative MD5 hash for a list of files/directories."""
    hasher = hashlib.md5()
    for s in sorted(sources):
        p = Path(s)
        if p.is_file():
            hasher.update(p.read_bytes())
        elif p.is_dir():
            for f in sorted(p.rglob('*')):
                if f.is_file():
                    hasher.update(f.read_bytes())
        hasher.update(str(p).encode())
    return hasher.hexdigest()

def check_build_needed(sources: List[Union[str, Path]], token_file: Path, clean_on_rebuild_path: Optional[Path] = None) -> bool:
    if not token_file.exists():
        Logger.detail("Rebuild needed: Validation token missing (.valid)")
        return True
    
    current_hash = calculate_hash(sources)
    try:
        saved_hash = token_file.read_text().strip()
        if current_hash != saved_hash:
            Logger.detail(f"Rebuild needed: Content changes detected (Hash mismatch)")
            
            # Auto-Clean Logic (Ref: USR-REQ-AUTO-CLEAN)
            # If a previous build exists (indicated by token_file) but hash changed, 
            # we wipe the output directory to ensure no stale artifacts remain.
            if clean_on_rebuild_path and clean_on_rebuild_path.exists():
                Logger.info(f"Auto-cleaning output directory due to hash mismatch: {clean_on_rebuild_path}")
                clean_dir(clean_on_rebuild_path)
                
            return True
    except:
        return True
    return False

def write_build_token(target_dir: Path, sources: List[Union[str, Path]]):
    """Writes a validation token to mark a successful build."""
    ensure_dir(target_dir)
    token_file = target_dir / ".valid"
    current_hash = calculate_hash(sources)
    token_file.write_text(current_hash)
    Logger.detail(f"Build completion token recorded: .valid (Hash: {current_hash[:8]}...)")

def copy_files(src: Path, dst: Path, pattern: str, recursive: bool = False):
    """Robust file copy utility supporting patterns and recursion."""
    if not src.exists():
        return
    ensure_dir(dst)
    
    gen = src.rglob(pattern) if recursive else src.glob(pattern)
    for f in gen:
        if f.is_file():
            rel_path = f.relative_to(src)
            target = dst / rel_path
            ensure_dir(target.parent)
            shutil.copy2(f, target)

def update_submodule(path: Path):
    """Updates git submodule to its expected state."""
    Logger.detail(f"Updating submodule: {path}")
    # Use run_process to ensure output is captured and serialized (Ref: CC-LOG-SYNC-SUBMODULE)
    run_process(["git", "submodule", "update", "--init", "--recursive", str(path)], 
                cwd=ROOT_DIR)

def reset_submodule(path: Path, module_name: str):
    """
    Force resets a submodule by deleting its directory and re-initializing.
    (Ref: USR-REQ-RESET-SUBMODULE)
    """
    Logger.info(f"Resetting submodule '{module_name}' at {path}...")
    
    # Aggressively delete the module source folder if it exists
    if path.exists():
        Logger.detail(f"Deleting existing submodule directory: {path}")
        try:
            shutil.rmtree(path)
        except Exception as e:
            Logger.warn(f"Failed to delete submodule directory via rmtree: {e}. Trying via cmd...")
            # Still use captured run_process for cmd
            run_process(["cmd", "/c", "rd", "/s", "/q", str(path)])

    # Re-initialize submodule using run_process to prevent log interleaving
    Logger.detail(f"Re-initializing submodule '{module_name}'...")
    run_process(["git", "submodule", "update", "--init", "--recursive", module_name], 
                cwd=ROOT_DIR)


def apply_patch(repo_path: Path, patch_file: Path) -> bool:
    """Applies a .patch file using git apply (Ref: CC-PATCH-GIT)."""
    if not patch_file.exists():
        Logger.error(f"Patch file not found: {patch_file}")
        return False
    
    # Use git apply --check to see if the patch can be applied cleanly
    # Capture output via run_process to prevent interleaving
    try:
        run_process(["git", "apply", "--check", "--ignore-whitespace", str(patch_file)], cwd=repo_path)
        
        Logger.info(f"Applying patch: {patch_file.name}")
        run_process(["git", "apply", "--ignore-whitespace", str(patch_file)], cwd=repo_path)
        Logger.success(f"Successfully applied {patch_file.name}")
        return True
    except Exception as e:
        # Check if already applied via reverse check (also captured)
        try:
            run_process(["git", "apply", "--reverse", "--check", "--ignore-whitespace", str(patch_file)], cwd=repo_path)
            Logger.info(f"Patch {patch_file.name} already applied.")
            return True
        except:
            Logger.warn(f"Patch {patch_file.name} failed check or apply: {e}")
            return False

def run_nuget_restore(solution_path: Path):

    """Restores NuGet packages for a solution."""
    nuget_exe = BUILDS_DIR / "nuget.exe"
    if not nuget_exe.exists():
        Logger.warn("nuget.exe not found, skipping restore.")
        return
    
    Logger.info(f"Restoring NuGet packages for {solution_path.name}...")
    run_process([str(nuget_exe), "restore", str(solution_path)])

def terminate_all():
    """Kill all active subprocesses registered in the system."""
    with _processes_lock:
        if not _active_processes:
            return
            
        Logger.info(f"Terminating {_active_processes.__len__()} active processes and their descendants...")
        for p in _active_processes:
            try:
                # Kill process and its children on Windows (Ref: CC-PROC-TERMINATION-FORCE)
                if os.name == 'nt':
                    # /F = Force, /T = Tree (including children), /PID = Process ID
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(p.pid)], 
                                 capture_output=True, timeout=5)
                else:
                    p.terminate()
            except Exception:
                pass
        _active_processes.clear()
    
    # Also stop logger worker
    Logger.stop()
