"""CLI entry point: python -m qyir <file>"""

import sys
from pathlib import Path

from qyir.validator import validate_qyir_file


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m qyir <qyir_file.json>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = validate_qyir_file(filepath)
    print(result.summary)
    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
