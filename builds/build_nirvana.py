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

        # 1. Update Submodule
        utils.update_submodule(NIRVANA_MODULE)
        
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
        utils.copy_files(NIRVANA_MODULE / "nirvana", dst_inc, "*.h", recursive=True)

        # 4. Finalize
        utils.write_build_token(token_dir, sources)
        utils.Logger.success(f"[{PRJ_NAME}] Successfully exported to {NIRVANA_BIN}")
        utils.Logger.info("=" * 60)

    except Exception as e:
        utils.Logger.fatal(f"[{PRJ_NAME}] Build Failed: {e}")

if __name__ == "__main__":
    main()
