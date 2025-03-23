from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Frame, PageTemplate, Image,Paragraph, Spacer
from datetime import datetime
from reportlab.lib.styles import getSampleStyleSheet
from .utils import home_tz, image_logo_path

def generate_report_pdf(title, data={}):
        try:
            if len(data) == 0:
                 return False, {
                    "message": "No data to generate report",
                    "status": 400
                }
            
            table_headers = data.get("headers", [])
            table_data = data.get("data", [])

            if (len(table_headers) == 0) or (len(table_data) == 0):
                return False, {
                    "message": "No data to generate report",
                    "status": 400
                }
            
            total = f"Total project(s): {str(data.get("total", 0))}"

            
            today_date = datetime.now(tz=home_tz).date()
            file_name = f"{title}_{today_date}_report.pdf"

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'

            pdf = SimpleDocTemplate(response, pagesize=A4, topMargin=30, bottomMargin=30)

            frame = Frame(40, 40, A4[0] - 80, A4[1] - 100, id='normal')

            # Define the page template with footer
            template = PageTemplate(id='test', frames=frame, onPage=create_pdf_header, onPageEnd=add_footer)
            pdf.addPageTemplates([template])

            elements = [Spacer(1, 60)]

            # Create Table
            styles = getSampleStyleSheet()
            title_style = styles["Title"]  # Using the default Title style
            title_style.fontSize = 12  # Adjust font size
            title_style.alignment = 1  # 1 = Centered

            total_style = styles["BodyText"]
            total_style.fontSize = 12

            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(total, total_style))
            elements.append(Spacer(1, 5))

            table = Table(table_headers+table_data, colWidths=[180, 100, 150, 150])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (1, 1), (-2, -2), 'TOP'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))

            elements.append(table)
            
            pdf.build(elements)

            return True, response
        except Exception as e:
            print(f"Error: {e}")
            return False, {
                "message": "Something went wrong",
                "status": 500
            }

def add_footer(canvas, doc):
    """
    Function to draw the footer on each page.
    """
    width, _ = letter  # Get page dimensions

    # Draw a horizontal line
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.line(40, 50, width - 40, 50)  # Line from left to right

    # Footer Text
    footer_text = "Projika - Project monitoring and evaluation management system"
    timestamp = f"Generated at: {datetime.now(tz=home_tz).strftime('%b %d, %Y at %I:%M %p')}"

    # Set font and size
    canvas.setFont("Helvetica", 8)

    # Position footer text and timestamp aligned to the right
    canvas.drawRightString(width - 40, 40, footer_text)
    canvas.drawRightString(width - 40, 30, timestamp)

def create_pdf_header(canvas, doc):
    """
    Creates a standard header for PROJIKA PDFs with an image, system name, and document title.
    """
    # Create Image object (adjust size as needed)
    img = Image(image_logo_path, width=60, height=60)  # Resize image appropriately

    # Define table structure
    title = [
        [img, "PROJIKA"],  # System title row
    ]

    # Create the table
    title_table = Table(title, colWidths=[200, 100], rowHeights=[50])

    # Apply styling
    title_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),  # Center all content
        # ('ALIGN', (1, 1), (1, 1), 'CENTER'),  
        # ('ALIGN', (2, 1), (2, 1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically center content
        ('FONTNAME', (1, 1), (-1, -1), 'Helvetica-Bold'),  # Bold text
        ('TEXTCOLOR', (1, 0), (-1, -1), colors.black),
        ('FONTSIZE', (1, 0), (-1, -1), 20),  # Font size
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),  # Space below each row
    ]))


    # Get current Y position and draw the table
    width, height = doc.pagesize
    title_table.wrapOn(canvas, width, height)
    title_table.drawOn(canvas, 100, height - 100)  # Adjust position as needed

    # Draw a line below the header
    line_y_position = height - 120  # Position the line slightly below the table
    canvas.setStrokeColor(colors.black)  # Line color
    canvas.setLineWidth(1)  # Line thickness
    canvas.line(50, line_y_position, width - 50, line_y_position)  # Draw line across the page
