from PyPDF2 import PdfReader, PdfWriter
import json

writer = PdfWriter()
writer.append('pages.pdf')
writer._info = PdfReader('pages.pdf').metadata

def process(parent, arr, prefix):
    num = 1
    for bookmark in arr:
        if not "hide" in bookmark:
            # fonts = reader.getPage(bookmark['page']-1).getObject()['/Resources']['/Font']
            # https://github.com/py-pdf/PyPDF2/blob/main/PyPDF2/_page.py#L1259
            obj = writer.add_outline_item(prefix + str(num) + " " + bookmark['name'], bookmark['page']-1, parent=parent)
            if "sub" in bookmark:
                process(obj, bookmark['sub'], prefix + str(num) + ".")
        num += 1

with open("bookmarks.json", encoding="utf-8") as json_file:
    process(None, json.load(json_file), "")

with open("result-bm.pdf", "wb") as out:
    writer.write(out)