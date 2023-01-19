from PyPDF2.generic._data_structures import DictionaryObject

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