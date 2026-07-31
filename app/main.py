import json
import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from subprocess import check_output

from product_catalog import load_catalog
from selection_processor import validate_and_reconcile_paths
from builder import build_submittal
from ai_selector import select_submittal_documents
from roofing_system import identify_roofing_system

app_directory = Path(__file__).resolve().parent
product_library_root = app_directory.parent / "product_library"
templates_root = app_directory.parent / "templates"


load_dotenv()

def get_version():
    try:
        return check_output(
            ["git", "describe", "--tags", "--always"],
            text=True,
        ).strip()
    except Exception:
        return "Development"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

APP_VERSION = get_version()
st.caption(f"App version: {APP_VERSION}")

st.title("Roofing Submittal Builder")

form = st.form(
    "submittal_form",
    clear_on_submit=True,
)

material = form.file_uploader("Material List")
scope = form.file_uploader("Scope of Work")

brand = form.selectbox(
    "Manufacturer",
    ["JM", "Carlisle", "Elevate", "GAF"],
    index=None,
    placeholder="Select a manufacturer...",
)

submittal_name = form.text_input(
    "Submittal Filename",
    value = "Roofing Submittal",
)

submit = form.form_submit_button("Submit")

if submit:

    if material is None or scope is None or brand is None:
        st.error("Please upload both PDFs and select a manufacturer.")
    else:
        with st.spinner("Reading documents..."):


            material_file = client.files.create(
                file=(material.name, material.getvalue(), "application/pdf"),
                purpose="user_data",
            )

            scope_file = client.files.create(
                file=(scope.name, scope.getvalue(), "application/pdf"),
                purpose="user_data",
            )

            roofing_system = identify_roofing_system(
                client=client,
                material_file_id=material_file.id,
                scope_file_id=scope_file.id,
                brand=brand,
            )

            catalog = load_catalog(
                product_library_root 
                / brand.lower() 
                / roofing_system.roofing_system.lower()
            )

            catalog_path_list = [
                item["path"]
                for item in catalog
            ]

            catalog_json = json.dumps(
                catalog_path_list, 
                indent=2,
            )

            result = select_submittal_documents(
                client=client,
                material_file_id=material_file.id,
                scope_file_id=scope_file.id,
                catalog_json=catalog_json,
                brand=brand,
            )

        # st.json(result.model_dump()) - for test
        catalog_paths = set(catalog_path_list)
        selected_paths = [document.path for document in result.documents]

        pdf_paths = []

        validation_spinner = st.empty()

        with st.spinner("Validating selections..."):


            valid_paths, invalid_paths = validate_and_reconcile_paths(
                client=client,
                selected_paths=selected_paths,
                catalog_paths=catalog_paths,
                catalog_json=catalog_json,
                material_file_id=material_file.id,
                scope_file_id=scope_file.id,
            )

        validation_spinner.empty()

        library_root = (
            product_library_root 
            / brand.lower() 
            / roofing_system.roofing_system.lower()
        )

        for path in valid_paths:
            pdf_path = library_root / path

            if pdf_path.is_file():
                pdf_paths.append(pdf_path)
            else:
                st.error(f"Missing file: {pdf_path}")

        if not submittal_name.strip():
            submittal_name = "Roofing Submittal"

        if not submittal_name.lower().endswith(".pdf"):
            submittal_name += ".pdf"

        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        output_path = Path(temp_file.name)
        temp_file.close()

        with st.spinner("Building submittal..."):


            template_path = (
                templates_root 
                / brand.lower()
                / "submittal_template.pdf"
            )

            if not template_path.is_file():
                st.error(f"Missing template: {template_path}")
                st.stop()

            build_submittal(
                pdf_paths=pdf_paths,
                template_path=template_path,
                output_path=output_path,
            )

        with open(output_path, "rb") as finished_pdf:
            pdf_data = finished_pdf.read()

        output_path.unlink()

        st.success("Submittal created successfully!")

        st.download_button(
            label="Download Submittal",
            data=pdf_data,
            file_name=submittal_name,
            mime="application/pdf",
        )
