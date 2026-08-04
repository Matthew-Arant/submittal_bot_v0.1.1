from pathlib import Path

import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
from google.api_core.exceptions import NotFound


BUCKET_NAME = "product_library"


def get_storage_client() -> storage.Client:
    credentials_info = dict(st.secrets["gcp_service_account"])

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info
    )

    return storage.Client(
        project=credentials.project_id,
        credentials=credentials,
    )


def build_library_prefix(
    brand: str,
    roofing_system: str,
) -> str:
    return f"{brand.lower()}/{roofing_system.lower()}/"


def list_product_blobs(
    brand: str,
    roofing_system: str,
) -> list[storage.Blob]:
    client = get_storage_client()

    prefix = build_library_prefix(
        brand=brand,
        roofing_system=roofing_system,
    )

    return list(
        client.list_blobs(
            BUCKET_NAME,
            prefix=prefix,
        )
    )

def download_product_pdfs(
    brand: str,
    roofing_system: str,
    selected_paths: list[str],
    destination_root: Path,
) -> list[Path]:

    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)

    prefix = build_library_prefix(
        brand=brand,
        roofing_system=roofing_system,
    )

    downloaded_paths: list[Path] = []

    for selected_path in selected_paths:
        blob_name = f"{prefix}{selected_path}"
        blob = bucket.blob(blob_name)

        local_path = destination_root / selected_path
        local_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            local_path.write_bytes(blob.download_as_bytes())
        except NotFound as error:
            raise FileNotFoundError(
                f"GCS product PDF not found: {blob_name}"
            ) from error

        downloaded_paths.append(local_path)

    return downloaded_paths