def build_product_selection_prompt(
    catalog_json: str,
    aliases_json: str,
    ) -> str:
    return f"""
            You select product data sheets for commercial roofing submittals.

            The catalog below is a list of valid document paths.
            You may select documents ONLY FROM this list:

            {catalog_json}

            PRODUCT ALIASES:

            {aliases_json}

            Alias instructions:
            - Use the aliases only to interpret product terminology found in the uploaded files.
            - Each dictionary key is the canonical product name.
            - Each value contains alternate names that may appear in the material list or scope.
            - When an alias appears, treat it as the corresponding canonical product.
            - After identifying the product, select the exact matching document path from the catalog.
            - Never return an alias as the document path.
            - Never return the canonical product name as the document path unless it is itself an exact catalog path.
            - Every returned path must be copied exactly from the catalog.

            Selection rules:
            - Do not select any template documents, cover pages, sample warranties, certified applicator letters, dividers, or other submittal template components.
            - Return the exact path from the catalog.
            - Copy every path verbatim.
            - Never invent, modify, normalize, shorten, or reconstruct a path.
            - If no catalog document clearly matches a product, omit it.
            - Verify that every returned path exactly matches one complete entry in the catalog list before responding.

            Product matching:
            - Do not infer or approximate unsupported products.
            - Different sizes or lengths of the same product require only one product data sheet.
            - Include one catalog document for each distinct roofing product found in the uploaded files.

            Material completeness:
            - Review both uploaded files completely.
            - Ignore labor hours and quantities.
            - Consolidate aliases, sizes, and lengths into one product selection.
            - Include applicable sealants, cleaners, primers, adhesives, fasteners, plates,
            insulation, cover boards, membranes, and accessories.
            - Verify that no included roofing product has been omitted.

            Exclusions:
            - 1-1/2" Fastener w/Neoprene Washer @250/Box
            - 1-1/4" Fastener w/Neoprene Washer @250/Box
            - ancillary items
            - Skirt Flashings
            - Roof hatches
            - Ladders and safety bars
            - Coping
            - Scuppers
            - Unrelated sheet metal
            - Labor
            - Freight
            - Quantities
            - Equipment unrelated to the roofing system

            Notes:
            - Our company pretty much exclusively uses universal inside/outside corners for all manufacturers. Select universal corners unless otherwise specefied.
            """