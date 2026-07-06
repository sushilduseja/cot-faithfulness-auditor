"""Thin entry point — delegates to src.experiments.corruption."""
import sys; sys.path.insert(0, ".")
from src.experiments.corruption import main
if __name__ == "__main__":
    main()
