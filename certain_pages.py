from PyPDF2 import PdfWriter
import sys

def parseIntSet(tokens=[]):#https://stackoverflow.com/questions/712460/interpreting-number-ranges-in-python/712483#712483
    selection = []
    for i in tokens:
        if len(i) > 0:
            if i[:1] == "<":
                i = "1-%s"%(i[1:])
        try:
            selection.append(int(i))
        except:
            token = [int(k.strip()) for k in i.split('-')]
            if len(token) > 1:
                token.sort()
                first = token[0]
                last = token[len(token)-1]
                for x in range(first, last+1):
                    selection.append(x)
    return selection

args = sys.argv
args.pop(0)

args = parseIntSet(args)
for i in range(len(args)):
    args[i] = args[i]-1

writer = PdfWriter()
writer.append('pages.pdf', pages=args)

with open("result-cp.pdf", "wb") as out:
    writer.write(out)