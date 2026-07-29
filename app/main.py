import json
import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from product_catalog import load_catalog
from validator import validate_paths
from reconciler import reconcile_invalid_paths
from models import SubmittalSelection
from selection_processor import validate_and_reconcile_paths
from builder import build_submittal

app_directory = Path(__file__).resolve().parent
product_library_root = app_directory.parent / "product_library"


@st.cache_data
def get_catalog():
    return load_catalog(product_library_root)


catalog = get_catalog()
catalog_json = json.dumps(catalog, indent=2)


load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

st.title("Roofing Submittal Builder")

form = st.form("submittal_form")

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

            response = client.responses.parse(
                model="gpt-5.6",
                input=[
                    {
                        "role": "developer",
                        "content": f"""

                        You select product data sheets for commercial roofing submittals.

                        You may select documents ONLY from this catalog:

                        {catalog_json}

                        Rules:
                        - Return the exact filename and folder from the catalog.
                        - Never invent, shorten, or modify a filename.
                        - Every selected document must come from one of these folders:
                        membrane, accessories, adhesives, fasteners_and_plates,
                        insulation_and_coverboards.
                        - Match aliases and descriptions from the uploaded documents to the closest
                        applicable product in the catalog.
                        - Different sizes or lengths of the same product require only one PDS.
                        - Example: #14 fasteners may correspond to an All-Purpose Fastener PDS.
                        - Exclude roof hatches, ladders and safety bars, coping, scuppers,
                        unrelated sheet metal, labor, freight, quantities, and equipment
                        unrelated to the membrane roofing system.
                        - Select only products supported by the uploaded material list or scope of work.
                        """,
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_file", "file_id": material_file.id},
                            {"type": "input_file", "file_id": scope_file.id},
                            {
                                "type": "input_text",
                                "text": (
                                    "Identify the PDS documents needed for this roofing submittal."
                                    f"Identify the selected manufacturer is {brand}."
                                ),
                            },
                        ],
                    },
                ],
                text_format=SubmittalSelection,
            )

        result = response.output_parsed
        # st.json(result.model_dump()) - for test
        catalog_paths = {item["path"] for item in catalog}
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

        for path in valid_paths:
            pdf_path = product_library_root / path

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
            build_submittal(
                pdf_paths=pdf_paths,
                output_path=output_path,
            )

        with open(output_path, "rb") as finished_pdf:
            pdf_data = finished_pdf.read()

        output_path.unlink()

        st.success(f"Submittal created: {output_path}")

        st.download_button(
            label="Download Submittal",
            data=pdf_data,
            file_name=submittal_name,
            mime="application/pdf",
        )
