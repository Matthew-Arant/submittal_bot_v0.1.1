from typing import Literal

from openai import OpenAI
from pydantic import BaseModel


class RoofingSystemSelection(BaseModel):
    roofing_system: Literal["TPO", "PVC", "EPDM"]


def identify_roofing_system(
    client: OpenAI,
    material_file_id: str,
    scope_file_id: str,
    brand: str,
) -> RoofingSystemSelection:

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": f"""
                You identify the roofing system for a commercial roofing project.

                Manufacturer:
                {brand}

                Return only the roofing system.

                Choose one of:
                - TPO
                - PVC
                - EPDM
                """,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "file_id": material_file_id,
                    },
                    {
                        "type": "input_file",
                        "file_id": scope_file_id,
                    },
                ],
            },
        ],
        text_format=RoofingSystemSelection,
    )

    return response.output_parsed