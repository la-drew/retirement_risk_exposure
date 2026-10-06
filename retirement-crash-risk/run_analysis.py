from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from retirement_risk.analysis import run_project


if __name__ == "__main__":
    try:
        outputs = run_project(ROOT)
    except Exception as exc:
        print("\nAnalysis could not complete.")
        print(f"Reason: {exc}")
        print("\nTry these checks:")
        print("1. Make sure you are connected to the internet.")
        print("2. Run: pip install -r requirements.txt")
        print("3. Run the command again: python run_analysis.py")
        raise SystemExit(1)

    print("\nAnalysis complete. Generated:")
    for name, value in outputs.items():
        print(f"- {name}: {value}")
