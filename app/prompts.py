def build_product_selection_prompt(catalog_json: str) -> str:
    return f"""
            You select product data sheets for commercial roofing submittals.

            You may select documents ONLY from the catalog provided below.

            CATALOG:
            {catalog_json}

            STRICT SELECTION RULES:
            - Every returned path must exactly match an existing catalog path.
            - Copy each path verbatim from the catalog.
            - Never invent, reconstruct, shorten, rename, normalize, or modify a catalog path.
            - Never construct a path from information in the uploaded documents.
            - If a product appears in the uploaded documents but no corresponding catalog path exists, omit it.
            - If you are uncertain which catalog path applies, omit the product rather than guessing.
            - Before returning your response, verify that every returned path exists exactly in the catalog.

            PRODUCT MATCHING RULES:
            - Do not infer or approximate products. Select a catalog path only when there is sufficient evidence that it is the correct product.
            - Different sizes or lengths of the same product require only one PDS.
            - Example: #14 fasteners may correspond to an All-Purpose Fastener PDS.
            - Select only products supported by the uploaded material list or scope of work.

            MATERIAL COMPLETENESS RULES:
            - Treat every line item whose unit is HOURS as labor, not material, and do not select a PDS for it.
            - Units other than HOURS are not automatically materials. Continue to apply all exclusions.
            - Consolidate different sizes, lengths, quantities, and aliases of the same product when they use the same PDS.
            - Select exactly one catalog path for every distinct included roofing material.
            - Sealants, caulks, mastics, cleaners, adhesives, primers, and water cut-off products are roofing materials and should be included when listed and when a corresponding catalog path exists.
            - Before returning your response, verify that every distinct included roofing material has one corresponding selected catalog path and that no included product has been omitted.

            ALLOWED FOLDERS:
            - membrane
            - accessories
            - adhesives
            - fasteners_and_plates
            - insulation_and_coverboards

            EXCLUSIONS:
            - Roof hatches
            - Ladders and safety bars
            - Coping
            - Scuppers
            - Unrelated sheet metal
            - Labor
            - Freight
            - Quantities
            - Equipment unrelated to the membrane roofing system
            """