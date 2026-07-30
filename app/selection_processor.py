import streamlit as st

from validator import validate_paths
from reconciler import reconcile_invalid_paths


def deduplicate_paths(paths: list[str]) -> list[str]:

    return list(dict.fromkeys(paths))


def validate_and_reconcile_paths(
    *,
    client,
    selected_paths: list[str],
    catalog_paths: set[str],
    catalog_json: str,
    material_file_id: str,
    scope_file_id: str,
    max_reattempts: int = 3,
) -> tuple[list[str], list[str]]:

    valid_paths, invalid_paths = validate_paths(
        selected_paths,
        catalog_paths,
    )

    reattempts = 0

    while invalid_paths and reattempts < max_reattempts:
        reattempts += 1

        st.write("Retrying to validate selections...")

        paths_being_reconciled = invalid_paths.copy()

        corrected_result = reconcile_invalid_paths(
            client=client,
            invalid_paths=paths_being_reconciled,
            catalog_json=catalog_json,
            material_file_id=material_file_id,
            scope_file_id=scope_file_id,
        )

        corrected_paths = [
            document.path
            for document in corrected_result.documents
        ]

        if not corrected_paths:
            invalid_paths = paths_being_reconciled
            continue

        corrected_valid, corrected_invalid = validate_paths(
            corrected_paths,
            catalog_paths,
        )

        valid_paths.extend(corrected_valid)

        for path in corrected_valid:
            st.success(f"Reconciled and added: {path}")

        missing_replacement_count = (
            len(paths_being_reconciled)
            - len(corrected_paths)
        )

        if missing_replacement_count > 0:
            unresolved_paths = paths_being_reconciled[
                len(corrected_paths):
            ]

            corrected_invalid.extend(unresolved_paths)

        invalid_paths = corrected_invalid

    valid_paths = deduplicate_paths(valid_paths)

    if invalid_paths:
        st.error(
            "Some document selections could not be reconciled."
        )

        for path in invalid_paths:
            st.error(path)
    else:
        st.success(
            f"All {len(valid_paths)} selections are valid."
        )

    return valid_paths, invalid_paths