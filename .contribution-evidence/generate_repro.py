"""Generate a synthetic mixed-section DOCX using only the standard library."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def generate(output):
    body = []
    for index, (width, height, left, right) in enumerate([
        (12240, 15840, 1440, 1440),
        (15840, 12240, 720, 1080),
        (12240, 15840, 1800, 2160),
    ]):
        prose = f"Section {index + 1} keeps every word within its margins. " * 24
        paragraph = f"<w:p><w:r><w:t>{prose}</w:t></w:r></w:p>"
        body.append(paragraph)
        body.append(f'<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/></w:tblPr>'
                    f'<w:tblGrid><w:gridCol w:w="0"/></w:tblGrid>'
                    f'<w:tr><w:tc>{paragraph}</w:tc></w:tr></w:tbl>')
        body.append(paragraph * 5)
        sect = (f'<w:sectPr><w:pgSz w:w="{width}" w:h="{height}"/>'
                f'<w:pgMar w:top="1440" w:bottom="1440" '
                f'w:left="{left}" w:right="{right}"/></w:sectPr>')
        body.append(f'<w:p><w:pPr>{sect}</w:pPr></w:p>' if index < 2 else '<w:p/>' + sect)
    document = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                '<w:body>' + ''.join(body) + '</w:body></w:document>')
    with ZipFile(output, "w", ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                         '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                         '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        package.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        package.writestr("word/document.xml", document)


if __name__ == "__main__":
    generate(Path(__file__).with_name("mixed-sections.docx"))
