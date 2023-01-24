from PyPDF2 import PdfWriter
from PyPDF2.generic import AnnotationBuilder, Fit
from PyPDF2._page import PageObject

from collections.abc import Callable
from typing import Any
from . import utils

# constant
maxTagLength = 6
opening_Bracket = '['
ending_Bracket = ']'

def visitorFor(array: list, page: int) -> Callable[[Any, Any, Any, Any, Any], None] :
    array.append({}) # local
    def visit(text, transformMatrix, textMatrix, fontDict, fontSize):
        if text.strip() == '':
            return
        text = text.strip()

        if text == opening_Bracket:
            array[0] = {'rec': [(textMatrix[4], textMatrix[5], fontDict, fontSize)], 'text': '', 'page': page}
        elif text.startswith(opening_Bracket):
            save = ending_Bracket in text
            if save:
                text = text[0:text.index(ending_Bracket)]
            if len(text) > maxTagLength+1: # Tag + [
                array[0] = {}
                return
            array[0] = {'rec': [(textMatrix[4], textMatrix[5], fontDict, fontSize)], 'text': text[1:len(text)], 'page': page}
            if save:
                array.append(array[0])
                array[0] = {}
        elif 'rec' in array[0]:
            if ending_Bracket in text:
                text = text[0:text.index(ending_Bracket)]
                if len(text) + len(array[0]['text']) > maxTagLength: # Not Tag
                    array[0] = {}
                    return
                array[0]['text'] += text
                array[0]['rec'].append((textMatrix[4], textMatrix[5], fontDict, fontSize))
                array.append(array[0])
                array[0] = {}
            else:
                if len(text) + len(array[0]['text']) > maxTagLength: # Not Tag
                    array[0] = {}
                    return
                array[0]['text'] += text
                array[0]['rec'].append((textMatrix[4], textMatrix[5], fontDict, fontSize))

    return visit

def anyInside(rects : list, rect) -> bool :
    for frect in rects:
        if utils.inside(rect, frect[0], frect[1]):
            return True
    return False

def filterAnnotated(page : PageObject, array : list) -> list :
    if utils.ANNOTATIONS in page:
        for annot in page[utils.ANNOTATIONS]:
            obj = annot.get_object()
            if utils.DESTINATION in obj:
                rect = obj[utils.RECTANGLE]
                array = list(filter(lambda source: not anyInside(source['rec'], rect), array))
    return array

def buildRec(source : dict):
    (fx, fy, fontDic, fontSize) = source['rec'][0]
    (lx, ly, fontDic, fontSize) = source['rec'][len(source['rec'])-1]

    lx += fontDic['/Widths'][ord(ending_Bracket)-fontDic['/FirstChar']]/100
    ly += fontSize

    fy -= fontDic['/FontDescriptor']['/CapHeight']/100

    source['rec'] = (fx, fy, lx, ly)

def fixWordSourceReferences(writer: PdfWriter, skip_input: bool, index_index: int):

    sources = []
    index_index = index_index if index_index < len(writer.pages) else len(writer.pages)-1

    for pageIndex in range(index_index):
        page = writer.pages[pageIndex]

        # extra array for visitor
        pageSources = []
        page.extract_text(visitor_text=visitorFor(pageSources, pageIndex))
        pageSources.pop(0)

        pageSources = filterAnnotated(page, pageSources)

        if len(pageSources) == 0:
            continue

        print('--' + str(pageIndex+1) + '--')
        for source in pageSources:
            print(source['text'])
            sources.append(source)

    if not skip_input and input('Wanna proceed fixing? (y/n) ') != 'y':
        return
    
    indexSources = []

    print('--Found--')

    for indexIndex in range(index_index, min(index_index+5, len(writer.pages))):# searching on index page and a max of 5 pages afterwards
        page = writer.pages[indexIndex]

        # extra array for visitor
        pageSources = []
        page.extract_text(visitor_text=visitorFor(pageSources, indexIndex))
        pageSources.pop(0)

        for source in pageSources:
            print(source['text'])
            indexSources.append(source)
    
    if not skip_input and input('Wanna proceed fixing? (y/n) ') != 'y':
        return

    for source in sources:
        indexSource = None
        for index in indexSources:
            if index['text'] == source['text']:
                indexSource = index
                break

        if indexSource == None:
            print('No index found for: ' + source['text'])
            continue
        
        buildRec(source)
        anno = AnnotationBuilder.link(
                    rect = source['rec'],
                    target_page_index = indexSource['page'],
                    fit=Fit.xyz(left = indexSource['rec'][0][0], top = indexSource['rec'][0][1]+indexSource['rec'][0][3]))

        writer.add_annotation(page_number=source['page'], annotation=anno)

    
    with open("result-an.pdf", "wb") as out:
        writer.write(out)