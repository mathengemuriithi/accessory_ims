from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io


def generate_sales_pdf(sales, store_name, date):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=4,
        alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#666666'),
        spaceAfter=20,
        alignment=TA_CENTER
    )

    story.append(Paragraph(store_name, title_style))
    story.append(Paragraph(f'Daily Sales Report — {date.strftime("%d %B %Y")}', subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a1a2e')))
    story.append(Spacer(1, 0.4*cm))

    if not sales:
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph('No sales recorded for this date.', styles['Normal']))
    else:
        # Summary stats
        total_revenue = sum(s.total for s in sales)
        total_profit = sum(s.profit for s in sales)
        total_items = sum(s.quantity for s in sales)

        summary_data = [
            ['Total Sales', 'Total Revenue', 'Total Profit'],
            [str(total_items) + ' items', f'KES {total_revenue:,.2f}', f'KES {total_profit:,.2f}'],
        ]
        summary_table = Table(summary_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f0f4ff')),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#1a1a2e'), colors.HexColor('#f0f4ff')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.6*cm))

        # Sales table
        story.append(Paragraph('Sales Breakdown', ParagraphStyle('SectionHead', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1a1a2e'), spaceBefore=6, spaceAfter=6)))

        header = ['Time', 'Product', 'Qty', 'Unit Price (KES)', 'Revenue (KES)', 'Profit (KES)', 'Attendant']
        table_data = [header]

        for sale in sales:
            attendant_name = sale.attendant.get_full_name() or sale.attendant.username if sale.attendant else 'N/A'
            table_data.append([
                sale.timestamp.strftime('%H:%M'),
                sale.product_name,
                str(sale.quantity),
                f'{sale.selling_price:,.2f}',
                f'{sale.total:,.2f}',
                f'{sale.profit:,.2f}',
                attendant_name,
            ])

        col_widths = [1.5*cm, 4.5*cm, 1.2*cm, 3*cm, 3*cm, 3*cm, 3*cm]
        sales_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        sales_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(sales_table)

        # Totals row
        story.append(Spacer(1, 0.3*cm))
        totals_data = [['', 'TOTALS', str(total_items), '', f'KES {total_revenue:,.2f}', f'KES {total_profit:,.2f}', '']]
        totals_table = Table(totals_data, colWidths=col_widths)
        totals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f4fd')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ]))
        story.append(totals_table)

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
    story.append(Paragraph(f'Generated by {store_name} IMS', ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER, spaceBefore=6)))

    doc.build(story)
    buffer.seek(0)
    return buffer
