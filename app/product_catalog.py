from pathlib import PurePosixPath

from gcs_storage import build_library_prefix, list_product_blobs


def build_catalog(
    brand: str,
    roofing_system: str,
) -> list[dict[str, str]]:

    prefix = build_library_prefix(
        brand=brand,
        roofing_system=roofing_system,
    )

    blobs = list_product_blobs(
        brand=brand,
        roofing_system=roofing_system,
    )

    catalog: list[dict[str, str]] = []

    for blob in blobs:
        if not blob.name.lower().endswith(".pdf"):
            continue

        relative_path = blob.name.removeprefix(prefix)
        path = PurePosixPath(relative_path)

        catalog.append(
            {
                "folder": path.parent.name,
                "filename": path.name,
                "path": relative_path,
            }
        )

    return catalog


def load_catalog(
    brand: str,
    roofing_system: str,
) -> list[dict[str, str]]:

    catalog = build_catalog(
        brand=brand,
        roofing_system=roofing_system,
    )

    if not catalog:
        raise FileNotFoundError(
            "No product PDFs found in GCS for "
            f"{brand}/{roofing_system}."
        )

    return catalog