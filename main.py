"""
Main entry point for Sheldon Cooper - Autonomous Research Scientist.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    from src.main import main
    sys.exit(main())
