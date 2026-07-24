from __future__ import annotations

import gzip
import hashlib
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path

import yaml

from paperkit.config import load_yaml
from paperkit.paper import PaperBuildError, build_paper
from paperkit.pipeline import build
from paperkit.validation import validate_project

ARCHIVE_TIME = (1980, 1, 1, 0, 0, 0)
REPRODUCIBILITY_PATHS = (
    "README.md",
    "Makefile",
    "project.yml",
    "pyproject.toml",
    "research",
    "scripts",
    "src",
    "tests",
    "artifacts",
)
ARXIV_EXCLUDED_SUFFIXES = {
    ".aux",
    ".bbl",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".pdf",
}


class ReleaseError(RuntimeError):
    """Raised when release validation or packaging fails."""


def _files_under(root: Path, relatives: tuple[str, ...]) -> list[tuple[Path, Path]]:
    files: list[tuple[Path, Path]] = []
    for relative in relatives:
        source = root / relative
        candidates = source.rglob("*") if source.is_dir() else [source]
        files.extend(
            (candidate, candidate.relative_to(root))
            for candidate in candidates
            if candidate.is_file()
        )
    return sorted(files, key=lambda item: item[1].as_posix())


def _write_zip(path: Path, files: list[tuple[Path, Path]]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source, relative in files:
            info = zipfile.ZipInfo(relative.as_posix(), ARCHIVE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())


def _write_arxiv_tar(path: Path, paper_dir: Path) -> None:
    files = [
        candidate
        for candidate in sorted(paper_dir.rglob("*"))
        if candidate.is_file()
        and candidate.name != ".gitkeep"
        and candidate.suffix.lower() not in ARXIV_EXCLUDED_SUFFIXES
    ]
    with (
        path.open("wb") as raw,
        gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed,
        tarfile.open(fileobj=compressed, mode="w") as archive,
    ):
        for source in files:
            relative = source.relative_to(paper_dir)
            info = archive.gettarinfo(str(source), arcname=relative.as_posix())
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mode = 0o644
            with source.open("rb") as handle:
                archive.addfile(info, handle)


def _write_citation(path: Path, root: Path) -> None:
    project = load_yaml(root / "project.yml")
    authors = []
    for author in project["authors"]:
        rendered = {"family-names": author["name"]}
        if author.get("orcid"):
            rendered["orcid"] = f"https://orcid.org/{author['orcid']}"
        authors.append(rendered)
    citation = {
        "cff-version": "1.2.0",
        "message": "If you use this research package, please cite it using this metadata.",
        "title": project["project"]["title"],
        "type": "article",
        "authors": authors,
        "repository-code": project["links"]["repository"],
        "url": project["links"]["site"],
        "license": project["licenses"]["content"],
    }
    path.write_text(yaml.safe_dump(citation, sort_keys=False), encoding="utf-8")


def _write_checksums(directory: Path) -> None:
    lines = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            lines.append(f"{digest}  {path.relative_to(directory).as_posix()}")
    (directory / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="ascii")


def release(root: Path, *, dry_run: bool = False) -> Path:
    root = root.resolve()
    build(root)
    report = validate_project(root, release=True)
    if not report.ok:
        raise ReleaseError("Release blocked:\n- " + "\n- ".join(report.errors))
    if dry_run:
        return root / "dist"

    try:
        pdf = build_paper(root)
    except PaperBuildError as error:
        raise ReleaseError(str(error)) from error

    site = root / "site"
    for command in (["npm", "ci"], ["npm", "run", "build"]):
        completed = subprocess.run(command, cwd=site, check=False)
        if completed.returncode != 0:
            raise ReleaseError(
                f"Site command {' '.join(command)} failed with exit code {completed.returncode}."
            )

    staging = Path(tempfile.mkdtemp(prefix="paperkit-release-", dir=root))
    try:
        shutil.copyfile(pdf, staging / "paper.pdf")
        shutil.copytree(site / "dist", staging / "site")
        _write_arxiv_tar(staging / "arxiv-source.tar.gz", root / "paper")
        _write_zip(
            staging / "reproducibility.zip",
            _files_under(root, REPRODUCIBILITY_PATHS),
        )
        _write_citation(staging / "CITATION.cff", root)
        _write_checksums(staging)

        destination = root / "dist"
        backup = root / ".dist.previous"
        if backup.exists():
            shutil.rmtree(backup)
        if destination.exists():
            destination.replace(backup)
        staging.replace(destination)
        if backup.exists():
            shutil.rmtree(backup)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return root / "dist"
