import argparse
import os
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def arguments():
    parser = argparse.ArgumentParser(description="Build the Popup Announcer add-on.")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "dist")
    return parser.parse_args()


def read_version():
    for line in (
        (PROJECT_ROOT / "manifest.ini").read_text(encoding="utf-8").splitlines()
    ):
        key, _, value = line.partition("=")
        if key.strip() == "version":
            return value.strip()
    raise SystemExit("version missing from manifest.ini")


def build_archive(output_directory):
    output_directory.mkdir(parents=True, exist_ok=True)
    archive_path = output_directory / f"popupAnnouncer-{read_version()}.nvda-addon"
    temporary_path = archive_path.with_suffix(".tmp")
    files = [
        PROJECT_ROOT / "manifest.ini",
        *sorted((PROJECT_ROOT / "globalPlugins").rglob("*.py")),
    ]
    with zipfile.ZipFile(temporary_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for source_path in files:
            archive.write(source_path, source_path.relative_to(PROJECT_ROOT))
    os.replace(temporary_path, archive_path)
    return archive_path


if __name__ == "__main__":
    print(build_archive(arguments().output_dir.resolve()))
