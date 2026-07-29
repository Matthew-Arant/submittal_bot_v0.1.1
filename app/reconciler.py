from openai import OpenAI

from models import SubmittalSelection


def reconcile_invalid_paths(
        client: OpenAI,
        invalid_paths: list[str],
        catalog_json: str,
        material_file_id: str,
        scope_file_id: str,
) -> SubmittalSelection:

    response = client.responses.parse(
        model="gpt-5.6",
        input=[
            {
                "role": "developer",
                "content": f"""
                The previous selection contained invalid catalog paths.

                Invalid paths:
                {invalid_paths}

                Here is the complete catalog:

                {catalog_json}

                Your job is ONLY to replace the invalid paths.

                Rules:
                - Return ONLY exact paths from the catalog.
                - Do not modify any valid selections.
                - Do not invent filenames.
                - Return one replacement for each invalid path.""",
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_file", "file_id": material_file_id},
                    {"type": "input_file", "file_id": scope_file_id},
                ],
            },
        ],
        text_format=SubmittalSelection,
    )

    return response.output_parsed