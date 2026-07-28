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


def load_catalog(root_path: str) -> list[dict[str, str]]:
    
    root = Path(root_path)

    if not root.exists():
        raise FileNotFoundError(f"Product library not found: {root.resolve()}")

    return build_catalog(root)