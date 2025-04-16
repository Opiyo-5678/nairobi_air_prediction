import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    Paragraph, 
    SimpleDocTemplate, 
    Spacer, 
    Table, 
    TableStyle,
    Image
)
from reportlab.lib.units import inch
from reportlab.lib import colors
import qrcode
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def generate_receipt_pdf(donation):
    """Generate a professional PDF receipt with enhanced styling and features"""
    buffer = BytesIO()
    
    # Document setup with proper margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    
    # ======================
    # Custom Style Definitions
    # ======================
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1,  # Center
        spaceAfter=0.2*inch,
        fontName='Helvetica-Bold'
    )
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.HexColor('#2980b9'),
        alignment=1,
        spaceAfter=0.4*inch,
        fontName='Helvetica-Bold'
    )
    
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=12,
        leading=14,
        spaceAfter=0.2*inch,
        fontName='Helvetica'
    )
    
    highlight_style = ParagraphStyle(
        'Highlight',
        parent=content_style,
        textColor=colors.HexColor('#27ae60'),
        fontSize=13,
        fontName='Helvetica-Bold'
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6c757d'),
        alignment=1,
        spaceBefore=0.5*inch,
        fontName='Helvetica'
    )
    
    watermark_style = ParagraphStyle(
        'Watermark',
        parent=styles['Normal'],
        fontSize=72,
        textColor=colors.HexColor('#f1f1f1'),
        alignment=1,
        leading=80,
        fontName='Helvetica-Bold'
    )
    
    # ======================
    # PDF Content Elements
    # ======================
    elements = []
    
    # 1. Organization Logo
    try:
        logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.jpeg')
        if os.path.exists(logo_path):
            elements.append(Image(logo_path, width=2*inch, height=1*inch, hAlign='CENTER'))
            elements.append(Spacer(1, 0.2*inch))
    except (ImproperlyConfigured, OSError):
        pass  # Skip logo if not available
    
    # 2. Watermark for confirmed donations
    if donation.status == 'confirmed':
        elements.append(Paragraph("PAID", watermark_style))
    
    # 3. Header Section
    elements.append(Paragraph("<b>CLEAN AIR INITIATIVE</b>", header_style))
    elements.append(Paragraph("<font color='#2980b9'>OFFICIAL DONATION RECEIPT</font>", title_style))
    
    # 4. Receipt Details Table
    data = [
        ["Receipt Number:", str(donation.id)],
        ["Date:", donation.date.strftime('%B %d, %Y')],
        ["Time:", donation.date.strftime('%I:%M %p')],
        ["Amount:", f"KES {donation.amount:,.2f}"],  
        ["Status:", donation.get_status_display()],
        ["Payment Method:", "M-Pesa"],
        ["Phone Number:", donation.phone_number],
        ["M-Pesa Receipt:", donation.mpesa_receipt if hasattr(donation, 'mpesa_receipt') and donation.mpesa_receipt else "Pending"],
    ]
    
    # Additional confirmation details if available
    if hasattr(donation, 'confirmation_date') and donation.confirmation_date:
        data.append(["<b>Confirmed On:</b>", donation.confirmation_date.strftime('%B %d, %Y %I:%M %p')])
    
    if hasattr(donation, 'confirmed_by') and donation.confirmed_by:
        data.append([
            "<b>Confirmed By:</b>", 
            donation.confirmed_by.get_full_name() if hasattr(donation.confirmed_by, 'get_full_name') 
            else str(donation.confirmed_by)
        ])
    
    # Create and style the table
    receipt_table = Table(data, colWidths=[2*inch, 4*inch], hAlign='LEFT')
    receipt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#343a40')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e9ecef')),
    ]))
    
    elements.append(receipt_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # 5. QR Code Verification Section (Fixed Implementation)
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        verification_url = f"https://cleanair.org/verify/{donation.id}"
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Image(qr_buffer, width=1.5*inch, height=1.5*inch, hAlign='CENTER'))
        elements.append(Paragraph(
            "<font size='9' color='#6c757d'><i>Scan to verify this receipt</i></font>", 
            ParagraphStyle(name='QRFooter', alignment=1, spaceBefore=0.1*inch)
        ))
        elements.append(Spacer(1, 0.3*inch))
    except Exception as e:
        print(f"QR code generation failed: {str(e)}")
        # Continue without QR code if generation fails
    
    # 6. Thank You Section
    elements.append(Paragraph(
        "<b>Thank you for your generous donation!</b>", 
        ParagraphStyle(
            name='ThankYou',
            alignment=1,
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=0.3*inch,
            spaceAfter=0.3*inch
        )
    ))
    
    elements.append(Paragraph(
        f"Your contribution of <font color='#27ae60'><b>KES {donation.amount:,.2f}</b></font> helps us "
        "improve air quality monitoring and awareness programs across our communities.", 
        ParagraphStyle(
            name='ThankYouContent',
            alignment=1,
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#495057'),
            spaceAfter=0.5*inch
        )
    ))
    
    # 7. Footer Section
    elements.append(Paragraph(
        "Clean Air Initiative • P.O. Box 12345, Nairobi • Tel: +254 700 000000<br/>"
        "Email: info@cleanair.org • Website: www.cleanair.org<br/>"
        "<font size='8'>This is an official tax-deductible receipt. Please retain for your records.</font>", 
        footer_style
    ))
    
    # ======================
    # PDF Generation
    # ======================
    doc.build(elements)
    buffer.seek(0)
    return buffer