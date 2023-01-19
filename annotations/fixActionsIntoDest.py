from PyPDF2 import PdfWriter
from PyPDF2.generic import AnnotationBuilder, Fit, NameObject
from PyPDF2.generic._data_structures import ArrayObject

from operator import itemgetter
from collections.abc import Callable
from typing import Any
from . import utils

def generateVisitorFor(annot: list) -> Callable[[Any, Any, Any, Any, Any], None] :
    annot.pop('runLabel', None)
    annot.pop('runRec', None)
    def visit(text, transformMatrix, textMatrix, fontDict, fontSize):
        if text.strip() == '':
            return
        text = text.strip()
            
        # in process
        if 'runLabel' in annot:
            if annot['runLabel'] == '': # already found
                return
            elif annot['runLabel'].startswith(text):
                label = annot['runLabel'] # text is just part of the label
                annot['runLabel'] = label[len(text):len(label)].strip()
            elif text.startswith(annot['runLabel']): # text more then needed by label
                annot['runLabel'] = ''
            else: # reset
                annot.pop('runLabel', None)
                annot.pop('runRec', None)
        elif annot['label'].startswith(text): # first potential found
            annot['runLabel'] = annot['label'].replace(text, '').strip()
            annot['runRec'] = textMatrix
            annot['runRec'][5] += fontSize-1

    return visit

def concatStrings(annotations : list):
    for annot in annotations:
        text = ""
        for string in sorted(annot['strings'], key=itemgetter("x", "y")):
            text += string['text']
        annot['text'] = text

def fixWordActionsIntoDest(writer: PdfWriter, save: bool):
    annotations = []

    # load annotations
    for pageIndex in range(len(writer.pages)):
        page = writer.pages[pageIndex]
        if(utils.ANNOTATIONS not in page):
            continue
        # extra array for visitor
        pageActions = []
        annos = []
        for annot in page[utils.ANNOTATIONS]:
            obj = annot.get_object()
            if utils.DESTINATION not in obj and utils.ACTION in obj and obj[utils.ACTION]['/Type'] == utils.ACTION_TYPE:
                formatted = utils.formatObj(obj)
                formatted['page'] = pageIndex
                pageActions.append(formatted)
            else:
                annos.append(annot)

        page[NameObject(utils.ANNOTATIONS)] = ArrayObject(annos)
        if len(pageActions) == 0:
            continue

        annotations.extend(pageActions)
        page.extract_text(visitor_text=utils.checktext(pageActions))
    
    # putting text together
    concatStrings(annotations)

    # dont need to search on early pages because e.g. table 3 will be on a later page then table 2
    next = 0
    lastPage = 0
    for annot in annotations:
        # find label
        if 'text' not in annot:
            continue

        text = annot['text']
        annot['label'] = text[:text.index(':')+1].replace('\r', '').replace('\n', '')
        print(annot['label'])

        if lastPage != annot['page']:
            next = 0

        # find correct destination
        for index in range(next, len(writer.pages)):
            search = writer.pages[index]
            if index == annot['page']:
                continue
            search.extract_text(visitor_text=generateVisitorFor(annot))
            if 'runRec' in annot:
                # found label on page 'search'
                print(index+1)
                rec = annot['runRec']

                annotation = AnnotationBuilder.link(
                    rect = annot['obj'][utils.RECTANGLE],
                    target_page_index = index,
                    fit=Fit.xyz(left = rec[4], top = rec[5]))
                
                # save for later if multiple were found
                if 'builded' in annot:
                    annot['builded'][index] = annotation
                else:
                    annot['builded'] = {index: annotation}
                break
        
        lastPage = annot['page']

        if 'builded' in annot:
            builded = annot['builded']
            if len(builded) == 0:
                # nothing found
                continue
            elif len(builded) == 1:
                # write single found
                page, ann = builded.popitem()
                writer.add_annotation(page_number=annot['page'], annotation=ann)
                next = page
            else:
                # wait for valid input
                while True:
                    print("Choose page: ")
                    input = int(input())
                    if input in builded:
                        page, anno = builded[input]
                        writer.add_annotation(page_number=annot['page'], annotation=anno)
                        next = page
                        break
                    else:
                        print('Invalid')
    
    if save:
        with open("result-an.pdf", "wb") as out:
            writer.write(out)