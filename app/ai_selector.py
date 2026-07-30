import json

from openai import OpenAI

from models import SubmittalSelection
from prompts import build_product_selection_prompt
from aliases import PRODUCT_ALIASES


def select_submittal_documents(
        client: OpenAI,
        material_file_id: str,
        scope_file_id: str,
        catalog_json: str,
        brand: str,
) -> SubmittalSelection:

    brand_aliases = PRODUCT_ALIASES.get(brand, {})
    aliases_json = json.dumps(brand_aliases)

    prompt = build_product_selection_prompt(
        catalog_json,
        aliases_json,
    )

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input= [
            {
                "role": "developer",
                "content": prompt,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "file_id": material_file_id,
                    },
                    {
                        "type":"input_file",
                        "file_id": scope_file_id,
                    },
                    {
                        "type": "input_text",
                        "text": (
                            "Identify the PDS documents needed for this roofing submittal. "
                            f"The selected manufacturer is {brand}."
                        ),
                    },
                ],
            },
        ],
        text_format=SubmittalSelection,
    )

    return response.output_parsed