import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_dummy_pdf():
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    test_data_dir = os.path.join(PROJECT_ROOT, "test_data")
    os.makedirs(test_data_dir, exist_ok=True)
    pdf_path = os.path.join(test_data_dir, "financial_report.pdf")
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Page 1: Text that the Search Agent can find
    c.drawString(100, 750, "OmniBrain Corp Financial Report 2023")
    c.drawString(100, 700, "Our Q3 revenue growth was unprecedented.")
    c.drawString(100, 680, "To understand the details, refer to the revenue growth chart on Page 2.")
    c.drawString(100, 660, "You can also query our historical structured database for precise figures.")
    c.showPage()
    
    # Page 2: A dummy chart (just text mimicking a chart/table)
    c.drawString(100, 750, "Chart: Q3 Revenue Growth by Region")
    c.drawString(100, 700, "North America: 25%")
    c.drawString(100, 680, "Europe: 15%")
    c.drawString(100, 660, "Asia Pacific: 40%")
    # Let's draw a literal rectangle to simulate a vector chart that PyMuPDF's get_images would miss
    c.rect(100, 500, 200, 100, stroke=1, fill=0)
    c.drawString(110, 550, "Vector Chart Box")
    c.showPage()
    
    c.save()
    print(f"Created dummy PDF at {pdf_path}")

if __name__ == "__main__":
    create_dummy_pdf()
