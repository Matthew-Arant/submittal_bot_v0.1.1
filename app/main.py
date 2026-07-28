import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from typing import Literal
from pydantic import BaseModel

from pathlib import Path
from product_catalog import load_catalog

import json

@st.cache_data
def get_catalog():
    return load_catalog("../product_library")

catalog = get_catalog()
catalog_json = json.dumps(catalog, indent=2)

Folder = Literal[
    "membrane",
    "accessories",
    "adhesives",
    "fasteners_and_plates",
    "insulation_and_coverboards",
]


class DocumentSelection(BaseModel):
    filename: str
    folder: Folder


class SubmittalSelection(BaseModel):
    manufacturer: str
    roofing_system: Literal["TPO", "PVC", "EPDM"]
    documents: list[DocumentSelection]


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
submit = form.form_submit_button("Submit")

if submit:

    if material is None or scope is None:
        st.error("Please upload both PDFs.")
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
                                "text": "Identify the PDS documents needed for this roofing submittal.",
                            },
                        ],
                    },
                ],
                text_format=SubmittalSelection,
            )
        result = response.output_parsed

        st.json(result.model_dump())
        st.write(response.output_text)