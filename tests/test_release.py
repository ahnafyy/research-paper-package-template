from __future__ import annotations

from pathlib import Path

from paperkit.release import _files_under, _write_arxiv_tar, _write_zip


def test_release_archives_are_byte_identical(tmp_path: Path) -> None:
    project = tmp_path / "project"
    paper = project / "paper"
    sections = paper / "sections"
    sections.mkdir(parents=True)
    (paper / "main.tex").write_text("\\input{sections/result}\n", encoding="utf-8")
    (sections / "result.tex").write_text("Verified.\n", encoding="utf-8")
    (project / "project.yml").write_text("schema_version: 1\n", encoding="utf-8")

    first_tar = tmp_path / "first.tar.gz"
    second_tar = tmp_path / "second.tar.gz"
    _write_arxiv_tar(first_tar, paper)
    _write_arxiv_tar(second_tar, paper)
    assert first_tar.read_bytes() == second_tar.read_bytes()

    files = _files_under(project, ("paper", "project.yml"))
    first_zip = tmp_path / "first.zip"
    second_zip = tmp_path / "second.zip"
    _write_zip(first_zip, files)
    _write_zip(second_zip, files)
    assert first_zip.read_bytes() == second_zip.read_bytes()