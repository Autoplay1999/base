import os
import sys
from pathlib import Path
import build_utils as utils

def main():
    PRJ_NAME = "Nirvana"
    try:
        # Directory Mapping
        ROOT_DIR = Path(__file__).resolve().parent.parent
        MODULES_DIR = ROOT_DIR / "modules"
        BIN_DIR = ROOT_DIR / "bin"
        
        NIRVANA_MODULE = MODULES_DIR / "nirvana"
        NIRVANA_BIN = BIN_DIR / "nirvana"
        
        utils.Logger.info("=" * 60)
        utils.Logger.info(f"  {PRJ_NAME} Build System")
        utils.Logger.info("=" * 60)

        # 1. Update/Clone Repository (Manual Management)
        REPO_URL = "https://github.com/Autoplay1999/nirvana.git"
        if not NIRVANA_MODULE.exists():
            utils.Logger.info(f"[{PRJ_NAME}] Cloning repository...")
            utils.run_process(["git", "clone", REPO_URL, str(NIRVANA_MODULE)], cwd=MODULES_DIR)
        else:
             # Verify it's a git repo before pulling
            if (NIRVANA_MODULE / ".git").exists():
                utils.Logger.info(f"[{PRJ_NAME}] Updating repository...")
                # Fix detached HEAD: Fetch -> Checkout main -> Pull
                utils.run_process(["git", "fetch", "origin"], cwd=NIRVANA_MODULE)
                utils.run_process(["git", "checkout", "main"], cwd=NIRVANA_MODULE)
                utils.run_process(["git", "pull", "origin", "main"], cwd=NIRVANA_MODULE)
            else:
                 utils.Logger.warn(f"[{PRJ_NAME}] Directory exists but is not a git repo. Skipping update.")
        
        # 2. Check rebuild
        sources = [NIRVANA_MODULE, Path(__file__)]
        token_dir = NIRVANA_BIN / ".tokens"
        if not utils.check_build_needed(sources, token_dir / ".valid", clean_on_rebuild_path=NIRVANA_BIN):
            utils.Logger.success(f"[{PRJ_NAME}] Already up to date.")
            return

        # 3. Export Headers
        dst_inc = NIRVANA_BIN / "include" / "nirvana"
        utils.Logger.info(f"[{PRJ_NAME}] Exporting headers to {dst_inc}...")
        
        utils.ensure_dir(dst_inc)
        utils.clean_dir(dst_inc)
        utils.copy_files(NIRVANA_MODULE, dst_inc, "*.h", recursive=True)

        # 4. Finalize
        utils.write_build_token(token_dir, sources)
        utils.Logger.success(f"[{PRJ_NAME}] Successfully exported to {NIRVANA_BIN}")
        utils.Logger.info("=" * 60)

    except Exception as e:
        utils.Logger.fatal(f"[{PRJ_NAME}] Build Failed: {e}")

if __name__ == "__main__":
    main()
