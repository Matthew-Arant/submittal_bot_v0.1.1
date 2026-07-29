from pathlib import Path
from pypdf import PdfReader, PdfWriter


CATEGORY_ORDER = {
    "membrane": 0,
    "insulation_and_coverboards": 1,
    "adhesives": 2,
    "accessories": 3,
    "fasteners_and_plates": 4,
}


def build_submittal(
    pdf_paths: list[Path],
    output_path: Path,
) -> None:

    submittal = PdfWriter()

    sorted_pdf_paths = sorted(
        pdf_paths,
        key=lambda path: next(
            (
                CATEGORY_ORDER[folder]
                for folder in path.parts
                if folder in CATEGORY_ORDER
            ),
            999,
        ),
    )

    for pdf_path in sorted_pdf_paths:
        reader = PdfReader(pdf_path)

        for page in reader.pages:
            submittal.add_page(page)

    with open(output_path, "wb") as output_file:
        submittal.write(output_file)