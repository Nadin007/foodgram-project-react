import io
import os

from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class PDFDownload:
    def download(self, downloadlist, header):
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'fonts', 'OpenSans-Regular.ttf')
        pdfmetrics.registerFont(TTFont('sans', font_path))
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        h = p.beginText(100, 750)
        h.setFont('sans', 20)
        h.setFillColorRGB(0, 0, 1)
        h.textLine(header)
        p.drawText(h)

        t = p.beginText(100, 700)
        t.setFillColorRGB(0, 0, 0)
        t.setFont('sans', 15)
        for s in downloadlist:
            t.textLine(f'* {s}')
        p.drawText(t)
        p.showPage()
        p.save()
        buffer.seek(0)
        result = FileResponse(
            buffer, as_attachment=True, filename='dowload.pdf')
        result.headers['Content-Type'] = 'application/pdf'
        return result
