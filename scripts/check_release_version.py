"""
Valida se a nova versao e maior que a atual (version.py) e que todas as tags no Git.
Uso: python scripts/check_release_version.py <nova_versao>
Exit: 0=OK, 1=nao leu version.py, 2=formato invalido, 3=nova <= atual, 4=nova <= tag existente
"""
import re
import subprocess
import sys
from pathlib import Path


def parse_version(s):
    """Converte '1.17.70' em lista de ints [1, 17, 70]."""
    try:
        return [int(x) for x in s.strip().lstrip("v").split(".")]
    except (ValueError, AttributeError):
        return None


def main():
    if len(sys.argv) < 2:
        sys.exit(2)
    new_ver_str = sys.argv[1].strip().lstrip("v")
    new_parts = parse_version(new_ver_str)
    if not new_parts:
        sys.exit(2)

    base_dir = Path(__file__).resolve().parent.parent
    version_file = base_dir / "core" / "version.py"
    if not version_file.exists():
        sys.exit(1)

    text = version_file.read_text(encoding="utf-8")
    m = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", text)
    if not m:
        sys.exit(1)

    cur_ver_str = m.group(1).strip()
    cur_parts = parse_version(cur_ver_str)
    if not cur_parts:
        sys.exit(2)
    if new_parts <= cur_parts:
        sys.exit(3)

    result = subprocess.run(
        ["git", "tag", "-l"],
        capture_output=True,
        text=True,
        cwd=base_dir,
        timeout=5,
    )
    tags = (result.stdout or "").strip().splitlines()
    for tag in tags:
        t = tag.strip().lstrip("v")
        tag_parts = parse_version(t)
        if tag_parts and new_parts <= tag_parts:
            sys.exit(4)

    sys.exit(0)


if __name__ == "__main__":
    main()
