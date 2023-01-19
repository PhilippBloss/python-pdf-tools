from PyPDF2 import PdfMerger
import os

merger = PdfMerger()

files = os.listdir(os.getcwd())
files.sort()
for f in files:
    if os.path.isfile(os.path.join(os.getcwd(), f)) and f.endswith('.pdf'):
        merger.append(f)
      
merger.write("result-m.pdf")
merger.close()