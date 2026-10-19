from __future__ import annotations

import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from app.gui.main import main

if __name__ == "__main__":
    raise SystemExit(main())
