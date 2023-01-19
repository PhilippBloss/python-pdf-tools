from PyPDF2 import PdfWriter, PdfReader
import sys
import annotations.fixActionsIntoDest as fad
import annotations.fixSourceReferences as fsr

"""
cli methods
"""

args = sys.argv
args.pop(0)

# prepare writer
writer = PdfWriter()
writer.append('pages.pdf')
writer._info = PdfReader('pages.pdf').metadata

if args[0] == '-fa':
    fad.fixWordActionsIntoDest(writer, True)
elif args[0] == '-fs':
    skip_input = False
    if args[1] == '-y':
        skip_input = True
        args.pop(1)
    fsr.fixWordSourceReferences(writer, skip_input, int(args[1])-1)
elif args[0] == '-f':
    fad.fixWordActionsIntoDest(writer, False)
    print()
    skip_input = True
    if args[1] == '-n':
        skip_input = False
        args.pop(1)

    fsr.fixWordSourceReferences(writer, skip_input, int(args[1])-1)