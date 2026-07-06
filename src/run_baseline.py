"""Thin entry point — delegates to src.experiments.baseline."""
import sys; sys.path.insert(0, ".")
from src.experiments.baseline import main
if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(limit=limit)
