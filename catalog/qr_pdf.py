"""Printable chapter QR sheets with a vector QR at its configured physical size."""

from io import BytesIO

import qrcode
from reportlab.lib.pagesizes import A2, A3, A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def page_size_for_marker(width_cm):
    if width_cm <= 17:
        return A4
    if width_cm <= 25:
        return A3
    return A2


def _fitted_text(value, max_width, font_size=12):
    from reportlab.pdfbase.pdfmetrics import stringWidth

    value = ' '.join(str(value).split())
    shortened = False
    while value and stringWidth(value, 'Helvetica', font_size) > max_width:
        value = value[:-1]
        shortened = True
    if shortened:
        while value and stringWidth(value + '...', 'Helvetica', font_size) > max_width:
            value = value[:-1]
    return value.rstrip() + ('...' if shortened else '')


def build_scene_qr_pdf(scene):
    """Return a one-page PDF; the entire QR, including quiet zone, has the saved width."""
    width_cm = float(scene.ar_marker_width_cm)
    if not 2 <= width_cm <= 30:
        raise ValueError('El ancho del QR debe estar entre 2 y 30 cm.')

    page_width, page_height = page_size_for_marker(width_cm)
    marker_width = width_cm * cm
    qr = qrcode.QRCode(border=4)
    qr.add_data(scene.qr_code)
    qr.make(fit=True)
    modules = qr.get_matrix()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(page_width, page_height), pageCompression=0)
    pdf.setTitle(f'QR para imprimir - {scene.title or "Capítulo"}')
    pdf.setAuthor('BibliotecaAR')

    margin = 48
    pdf.setFont('Helvetica-Bold', 18)
    pdf.drawString(margin, page_height - 56, 'QR del capítulo')
    pdf.setFont('Helvetica', 12)
    pdf.drawString(margin, page_height - 82, _fitted_text(scene.book.title, page_width - 2 * margin))
    pdf.drawString(
        margin,
        page_height - 102,
        _fitted_text(scene.title or f'Capítulo {scene.order}', page_width - 2 * margin),
    )

    qr_x = (page_width - marker_width) / 2
    qr_y = page_height - 170 - marker_width
    pdf.setFillColorRGB(1, 1, 1)
    pdf.rect(qr_x, qr_y, marker_width, marker_width, stroke=0, fill=1)
    pdf.setFillColorRGB(0, 0, 0)
    module_width = marker_width / len(modules)
    for row_index, row in enumerate(modules):
        for column_index, is_dark in enumerate(row):
            if is_dark:
                pdf.rect(
                    qr_x + column_index * module_width,
                    qr_y + (len(modules) - row_index - 1) * module_width,
                    module_width,
                    module_width,
                    stroke=0,
                    fill=1,
                )

    width_label = f'{width_cm:g} x {width_cm:g} cm (QR completo)'
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawCentredString(page_width / 2, qr_y - 24, width_label)

    ruler_y = qr_y - 61
    ruler_x = (page_width - 5 * cm) / 2
    pdf.setStrokeColorRGB(0.15, 0.23, 0.32)
    pdf.setLineWidth(1)
    pdf.line(ruler_x, ruler_y, ruler_x + 5 * cm, ruler_y)
    pdf.line(ruler_x, ruler_y - 4, ruler_x, ruler_y + 4)
    pdf.line(ruler_x + 5 * cm, ruler_y - 4, ruler_x + 5 * cm, ruler_y + 4)
    pdf.setFont('Helvetica', 9)
    pdf.drawCentredString(page_width / 2, ruler_y - 16, 'Comprobación: esta línea debe medir 5 cm')

    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawCentredString(page_width / 2, 59, 'Imprime al 100 % / tamaño real.')
    pdf.setFont('Helvetica', 9)
    pdf.drawCentredString(page_width / 2, 43, 'Desactiva "ajustar a página" y comprueba la línea de 5 cm.')
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
