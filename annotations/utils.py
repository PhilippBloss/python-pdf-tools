from PyPDF2.generic._data_structures import ArrayObject, Destination, DictionaryObject, NameObject, NumberObject
from PyPDF2.generic._rectangle import RectangleObject
from PyPDF2.generic._fit import Fit
from PyPDF2 import PdfWriter

# pdf structure
ACTION = "/A"
ACTION_TYPE = "/Action"
ANNOTATIONS = "/Annots"
DESTINATION = "/Dest"
DESTINATION_OBJECT = 0
RECTANGLE = "/Rect"

def formatObj(obj: DictionaryObject) -> dict :
    return {"obj": obj, "rect": obj[RECTANGLE], "strings": []};

def checktext(array):
    def inner(text, transformMatrix, textMatrix, fontDict, fontSize):
        (x, y) = (textMatrix[4], textMatrix[5])
        for annot in array:
            rect = annot['rect']
            if inside(rect, x, y):
                annot['strings'].append({"text": text, "x": x, "y": y})
    return inner

def inside(rect, x: float, y: float) -> bool:
    return x > rect[0] and x < rect[2] and y > rect[1] and y < rect[3]

def buildInternalLink(rect: list, target_page_index: int, left: int, top: int, zoom: int):
    annotation = DictionaryObject({})
    annotation[NameObject('/Subtype')] = NameObject('/Link')
    annotation[NameObject('/Rect')] = RectangleObject(rect)
    annotation[NameObject('/BS')] = DictionaryObject({NameObject('/W'): NumberObject(0)})
    annotation[NameObject('/F')] = NumberObject(4)
    dest = Destination(
        NameObject("/LinkName"),
        NumberObject(target_page_index),
        Fit(
            fit_type='/XYZ', fit_args=(round(left), round(top), zoom)
        ),
    )
    annotation[NameObject("/Dest")] = dest.dest_array
    return annotation


def add_annotation(writer: PdfWriter, page_number: int, annotation):
    page = writer.pages[page_number]
    if page.annotations is None:
        page[NameObject("/Annots")] = ArrayObject()

    ind_obj = writer._add_object(annotation)

    page.annotations.append(ind_obj)