from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from pymongo import MongoClient

# uvicorn app:app --reload

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client['mydatabase']
collection = db['appointments']

def create_invoice(file_name, name, age, phone, date, time):
    pdf = SimpleDocTemplate(filename=file_name, pagesize=letter)

    content = []

    # logo_path = "path/to/your/company_logo.png"
    company_name = "Your Company Name"
    company_address = "123 Company Street, City, Country"

    # content.append(Image(logo_path, width=200, height=50))
    content.append(Paragraph(company_name, style=ParagraphStyle('Title')))
    content.append(Paragraph(company_address, style=getSampleStyleSheet()['BodyText']))

    content.append(Paragraph("", style=getSampleStyleSheet()['BodyText']))

    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

    content.append(Paragraph("Invoice", style_bold))
    content.append(Paragraph(f"Date: {date}", style_normal))
    content.append(Paragraph(f"Name: {name}", style_normal))
    content.append(Paragraph(f"Age: {age}", style_normal))
    content.append(Paragraph(f"Phone: {phone}", style_normal))
    content.append(Paragraph(f"Date: {date}", style_normal))
    content.append(Paragraph(f"Time: {time}", style_normal))
    
    data = [
        ["Description", "Details"],
        ["Name", name],
        ["Age", age],
        ["Phone", phone],
        ["Date", date],
        ["Time", time],
    ]
    
    table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                              ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                              ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                              ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                              ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                              ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                              ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    content.append(Table(data, style=table_style))

    pdf.build(content)

class AppointmentRequest(BaseModel):
    name: str
    outlet_name: str

@app.post("/book-appointment")
async def book_appointment(appointment_data: AppointmentRequest):
    try:
        
        result = await collection.insert_one(appointment_data.model_dump())
        appointment_id = str(result.inserted_id)

       
        pdf_name=f"appointment_1.pdf"
        pdf_path = f"/Users/rewatsachdeva/Desktop/web dev/clinic api-v2/{pdf_name}"
        create_invoice(pdf_path,
                       appointment_id,
                       appointment_data.name,
                       appointment_data.age,
                       appointment_data.phone,
                       appointment_data.date,
                       appointment_data.time)


        return JSONResponse(content="Booking successfull")
    
    except Exception as e:
        print(e)
        return JSONResponse(content="Booking failed", status_code=404)


class SlotRequest(BaseModel):
    appointment_date: str
