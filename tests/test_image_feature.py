from docvert.models.document import Image, Document

def test_image_initialization()   -> None:
    img = Image(content="", alt_text="An image", extension=".png", image_bytes=b"fake")
    assert img.alt_text == "An image"
    assert img.extension == ".png"
    assert img.image_bytes == b"fake"
    assert img.filepath is None

def test_document_to_markdown_image()   -> None:
    img = Image(content="", alt_text="Test", filepath="assets/test.png")
    doc = Document(blocks=[img])
    assert doc.to_markdown() == "![Test](assets/test.png)\n"
