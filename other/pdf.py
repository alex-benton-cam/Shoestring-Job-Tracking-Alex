from PyPDF2 import PdfFileMerger
from fpdf import FPDF
import barcode
from barcode.writer import ImageWriter
from barcode.writer import SVGWriter
from io import StringIO
from PIL import Image
"""
code39 = barcode.get_barcode_class('code39')
barcodeImg = code39('W/26413', writer=ImageWriter())
"""

barcodes = ['W/26413',
            'W/27436',
            'W/29238',
            'W/11307',
            'W/7215',
            'W/7544',
            'W/15053',
            'W/20206',
            'W/17783',
            'W/10635',
            'W/2667']



A4Width = 210
A4Height = 297
xmargin = 8
ymargin = 15
xgap = 3
ygap = 0
cols = 3
rows = 7

colHeight = A4Height - 2* ymargin
cellw = (A4Width -2*xmargin - (cols-1)*xgap)/cols
cellh = (A4Height -2*ymargin - (rows-1)*ygap)/rows
colw = cellw + xgap
colh = cellh + ygap
print(colh, colw)

pdf = FPDF('P', 'mm', 'A4')    
pdf.add_page()
pdf.set_font('Arial', 'B', 16)

for i in range(rows):
    for j in range(cols):
        index = i*cols+j
        try:
            x = xmargin+j*colw+2
            y = ymargin+i*colh+2
            pdf.code128(barcodes[index], x, y, w=1.4, h=colh/2)
            pdf.text(x, y+colh/2+8, barcodes[index])
        except:
            pass

pdf.output('tuto1.pdf', 'F')