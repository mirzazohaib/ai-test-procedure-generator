"""
PDF Renderer using ReportLab.
Converts Markdown-style text into a professional PDF document.
"""
import io
import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

class PDFRenderer:
    """Renders test procedures to PDF format"""
    
    def render(self, content: str, project_id: str) -> bytes:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=LETTER)
        width, height = LETTER
        
        # --- HEADER ---
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"Test Procedure: {project_id}")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.line(50, height - 80, width - 50, height - 80)
        
        # --- BODY CONTENT ---
        text_obj = c.beginText(50, height - 100)
        text_obj.setFont("Helvetica", 12)
        
        lines = content.split('\n')
        y = height - 100
        
        for line in lines:
            # Check for page break
            if y < 50:
                c.drawText(text_obj)
                c.showPage()
                # Reset for new page
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, height - 50, f"Test Procedure: {project_id} (Cont.)")
                c.line(50, height - 80, width - 50, height - 80)
                text_obj = c.beginText(50, height - 100)
                text_obj.setFont("Helvetica", 12)
                y = height - 100
            
            # Simple Formatting Logic
            if line.strip().startswith("## "):
                # H2 Header
                c.drawText(text_obj)  # Flush previous text
                y -= 20
                text_obj = c.beginText(50, y)
                text_obj.setFont("Helvetica-Bold", 14)
                text_obj.textLine(line.replace("## ", "").strip())
                text_obj.setFont("Helvetica", 12)
                y -= 20
            elif line.strip().startswith("**") and line.strip().endswith("**"):
                # Bold Line
                text_obj.setFont("Helvetica-Bold", 12)
                text_obj.textLine(line.replace("**", "").strip())
                text_obj.setFont("Helvetica", 12)
                y -= 14
            else:
                # Regular Text
                text_obj.textLine(line)
                y -= 14
            
        c.drawText(text_obj)
        c.save()
        
        buffer.seek(0)
        return buffer.getvalue()