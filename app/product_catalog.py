from pathlib import Path


def build_catalog(root: Path) -> list[dict[str, str]]:
    
    catalog: list[dict[str, str]] = []

    for pdf in root.rglob("*.pdf"):
        catalog.append(
            {
                "folder": pdf.parent.name,
                "filename": pdf.name,
                "path": str(pdf.relative_to(root)),
            }
        )

    return catalog


def load_catalog(root_path: Path) -> list[dict[str, str]]:
    if not root_path.exists():
        raise FileNotFoundError(f"Product library not found: {root_path.resolve()}")

    return build_catalog(root_path)