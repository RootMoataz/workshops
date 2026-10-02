"""Build backend/lambda.zip for Lambda (Python 3.12, x86_64). Usage: python build.py (from backend/)."""
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE / "_build"
OUT = HERE / "lambda.zip"

shutil.rmtree(BUILD, ignore_errors=True)
BUILD.mkdir()
subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--target", str(BUILD),
                "--platform", "manylinux2014_x86_64", "--python-version", "3.12",
                "--implementation", "cp", "--only-binary=:all:", "-r", str(HERE / "requirements.txt")], check=True)
shutil.copy(HERE / "lambda_function.py", BUILD)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(BUILD.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            archive.write(path, path.relative_to(BUILD))
shutil.rmtree(BUILD)
print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KiB)")
