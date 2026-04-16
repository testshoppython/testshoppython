from fpdf import FPDF
import io
from .. import models

class InvoicePDF(FPDF):
    def header(self):
        # Logo / Brand
        self.set_font('helvetica', 'B', 20)
        self.cell(0, 10, 'OWRE', 0, 1, 'L')
        self.set_font('helvetica', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'Premium Storage Solutions', 0, 1, 'L')
        self.cell(0, 6, 'Musterstraße 1, 10115 Berlin', 0, 1, 'L')
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'VIELEN DANK FÜR IHREN EINKAUF BEI OWRE.', 0, 1, 'C')
        self.cell(0, 5, f'Seite {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_invoice_pdf(order: models.Order, items) -> bytes:
    pdf = InvoicePDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Invoice Data
    pdf.set_font('helvetica', 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'RECHNUNG', 0, 1, 'R')
    
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 6, f'Rechnungsnummer: RE-{order.order_number}', 0, 1, 'R')
    pdf.cell(0, 6, f'Datum: {order.created_at.strftime("%d.%m.%Y")}', 0, 1, 'R')
    pdf.ln(10)
    
    # Customer Info
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 8, 'Rechnungsadresse:', 0, 1, 'L')
    pdf.set_font('helvetica', '', 11)
    # Assuming user relations
    name = f"{order.user.firstname} {order.user.lastname}" if order.user else "Kunde"
    email = order.user.email if order.user else ""
    pdf.cell(0, 6, name, 0, 1, 'L')
    pdf.cell(0, 6, email, 0, 1, 'L')
    pdf.ln(15)
    
    # Table Header
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(90, 10, ' Artikel', 'B', 0, 'L', 1)
    pdf.cell(30, 10, 'Menge', 'B', 0, 'C', 1)
    pdf.cell(35, 10, 'Einzelpreis', 'B', 0, 'R', 1)
    pdf.cell(35, 10, 'Gesamt', 'B', 1, 'R', 1)
    
    # Table Items
    pdf.set_font('helvetica', '', 11)
    for item in items:
        # Very simple drawing
        pdf.cell(90, 10, f' {item.product.name}', 'B', 0, 'L')
        pdf.cell(30, 10, str(item.quantity), 'B', 0, 'C')
        pdf.cell(35, 10, f'{item.price:.2f} EUR', 'B', 0, 'R')
        pdf.cell(35, 10, f'{(item.price * item.quantity):.2f} EUR', 'B', 1, 'R')
        
    # Totals
    pdf.ln(10)
    pdf.set_font('helvetica', 'B', 12)
    
    # If shipping is needed (assuming < 50 has 4.99)
    subtotal = sum(i.price * i.quantity for i in items)
    shipping = 4.99 if subtotal < 50 else 0.00
    
    if shipping > 0:
        pdf.cell(155, 8, 'Zwischensumme:', 0, 0, 'R')
        pdf.cell(35, 8, f'{subtotal:.2f} EUR', 0, 1, 'R')
        pdf.cell(155, 8, 'Versandkosten:', 0, 0, 'R')
        pdf.cell(35, 8, f'{shipping:.2f} EUR', 0, 1, 'R')
        
    pdf.set_fill_color(250, 245, 235)
    pdf.cell(155, 12, 'GESAMTBETRAG:', 0, 0, 'R', 1)
    pdf.cell(35, 12, f'{order.total_price:.2f} EUR', 0, 1, 'R', 1)
    
    pdf.ln(20)
    pdf.set_font('helvetica', '', 10)
    pdf.multi_cell(0, 6, "Der Rechnungsbetrag wurde per gewählter Zahlungsmethode beglichen. Gemäß Kleinunternehmerregelung § 19 UStG wird keine Umsatzsteuer ausgewiesen.")
    
    # Generate bytes
    return pdf.output(dest='S')
