from reportlab.pdfgen import canvas

def generate_receipt(filename):

    c = canvas.Canvas(filename)

    c.drawString(100, 750, "SmartPay Receipt")

    c.save()