import os
import shutil
import subprocess
from pathlib import Path
import build_utils as utils

# --- Configuration ---
ROOT_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = ROOT_DIR / "modules"
BIN_DIR = ROOT_DIR / "bin"
BUILDS_DIR = ROOT_DIR / "builds"

# (Name, RelPath, ProjectFile, HeaderExportPath, SolutionFile, HeaderPattern)
KNSOFT_MODULES = [
    ("NDK", "KNSoft.NDK/Source/KNSoft.NDK", "KNSoft.NDK.vcxproj", "KNSoft.NDK/Source/Include/KNSoft/NDK", "KNSoft.NDK.sln", "*"),
    ("SlimDetours", "KNSoft.SlimDetours/Source/KNSoft.SlimDetours", "KNSoft.SlimDetours.vcxproj", None, "KNSoft.SlimDetours.sln", None),
    ("Syscall", "KNSoft.Syscall/Source/KNSoft.Syscall", "KNSoft.Syscall.vcxproj", "KNSoft.Syscall/Source/KNSoft.Syscall", "KNSoft.Syscall.sln", "*.h;*.inc;*.inl"),
    ("FirmwareSpec", "KNSoft.FirmwareSpec/VSProject", "SmbiosDecode.vcxproj", "KNSoft.FirmwareSpec", "KNSoft.FirmwareSpec.sln", "*.h;*.inl"),
    ("MakeLifeEasier", "KNSoft.MakeLifeEasier/Source/KNSoft.MakeLifeEasier", "KNSoft.MakeLifeEasier.vcxproj", "KNSoft.MakeLifeEasier/Source/KNSoft.MakeLifeEasier", "KNSoft.MakeLifeEasier.sln", "*.h;*.inl")
]

def build_module(name: str, rel_path: str, project_file: str, header_pkg: str = None, solution_file: str = None, header_pattern: str = "*"):
    try:
        mod_dir = MODULES_DIR / rel_path
        project_path = mod_dir / project_file
        
        if not project_path.exists():
            utils.Logger.error(f"[{name}] Project not found at {project_path}")
            return

        utils.Logger.detail(f"[{name}] Starting MSBuild execution (Original Way)...")
        
        # Rebuild check (Basic)
        token_dir = BIN_DIR / "KNSoft" / ".tokens" / name.lower()
        if not utils.check_build_needed([mod_dir, project_path], token_dir / ".valid"):
            utils.Logger.success(f"[{name}] Already up to date.")
            return

        # 1. Update Submodule
        utils.update_submodule(MODULES_DIR / rel_path.split('/')[0])

        # 1.1 Apply Patch (Ref: CC-PATCH-AUTO)
        if name == "FirmwareSpec":
            patch_file = BUILDS_DIR / "firmwarespec.patch"
            utils.apply_patch(MODULES_DIR / "KNSoft.FirmwareSpec", patch_file)

        # Special handling for FirmwareSpec: Build TypeInfoGenerator
        if name == "FirmwareSpec":
            type_info_gen_path = mod_dir.parent / "TypeInfoGenerator" / "TypeInfoGenerator.csproj"
            if type_info_gen_path.exists():
                utils.Logger.detail(f"[{name}] Building dependency TypeInfoGenerator...")
                for config in ["Release", "Debug"]:
                     utils.run_process(["dotnet", "build", str(type_info_gen_path), "-c", config])

        # 2. Restore NuGet (if solution exists)
        if solution_file:
             sln_path = mod_dir.parent / solution_file
             if sln_path.exists():
                   utils.run_nuget_restore(sln_path)

        # 3. Environment & MSBuild
        env_manager = utils.BuildEnv()
        PLATFORM_MAP = {"x86": "Win32", "x64": "x64"}

        success = True
        for arch_name, msbuild_platform in PLATFORM_MAP.items():
            for config in ["Release", "Debug"]:
                try:
                    utils.Logger.detail(f"[{name}] Building {arch_name}|{config}...")
                    env = env_manager.get_env_vars(arch_name)
                    # Build command
                    # Note: NDK only supports Release (x86/x64)
                    if name == "NDK" and config == "Debug":
                        utils.Logger.detail(f"[{name}] Skipping {arch_name}|{config} (Unsupported)")
                        continue

                    cmd = [
                        str(env_manager.msbuild_path), str(project_path),
                        f"/p:Configuration={config}",
                        f"/p:Platform={arch_name if arch_name != 'x86' else 'Win32'}",
                        f"/m:{utils.get_cpu_limit()}", "/v:m"
                    ]
                    
                    utils.run_process(cmd, env=env)
                        
                    # Copy Artifacts
                    out_dir = mod_dir / "OutDir" / arch_name / config
                    lib_dst = BIN_DIR / "KNSoft" / "lib" / arch_name / config.lower()
                    utils.ensure_dir(lib_dst)
                    
                    # Copy .lib and .pdb
                    found = False
                    if out_dir.exists():
                        for f in out_dir.glob("*"):
                            if f.suffix.lower() in [".lib", ".pdb"]:
                                shutil.copy2(f, lib_dst / f.name)
                                found = True
                    
                    if not found:
                        utils.Logger.warn(f"[{name}] No artifacts found in {out_dir}")
                    
                except Exception as e:
                    utils.Logger.error(f"[{name}] Build failed for {arch_name}|{config}: {e}")
                    success = False
        
        # Header Export
        if header_pkg:
            header_src = MODULES_DIR / header_pkg
            # 4. Export Headers (Unified)
            dst_inc = BIN_DIR / "KNSoft" / "include" / "KNSoft" / name
            utils.Logger.detail(f"[{name}] Exporting headers from {header_src} to {dst_inc}...")
            
            patterns = header_pattern.split(';')
            for pat in patterns:
                 pat = pat.strip()
                 if pat:
                      utils.copy_files(header_src, dst_inc, pat, recursive=True)

        if success:
            # 5. Finalize
            utils.write_build_token(token_dir, [mod_dir, project_path])
            utils.Logger.success(f"[{name}] Build Complete.")
        else:
            utils.Logger.error(f"[{name}] Build Failed. Check logs.")
            
    except Exception as e:
        utils.Logger.error(f"[{name}] Failed: {e}")

def main():
    utils.Logger.detail("=" * 60)
    utils.Logger.detail("  KNSoft Modules Build System (MSBuild Reversion)")
    utils.Logger.detail("=" * 60)

    
    if not BIN_DIR.exists():
        BIN_DIR.mkdir(parents=True, exist_ok=True)
    
    for name, path, proj, header_pkg, sln, pattern in KNSOFT_MODULES:
        build_module(name, path, proj, header_pkg, sln, pattern)
        
    utils.Logger.info("=" * 60)

if __name__ == "__main__":
    main()
