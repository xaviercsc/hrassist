from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.http import HttpResponse
import io
from datetime import datetime


class PDFGenerator:
    @staticmethod
    def generate_interview_questions_pdf(job_application, questions):
        """Generate PDF with interview questions"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.darkblue
        )
        
        # Header
        story.append(Paragraph("Interview Questions", title_style))
        story.append(Spacer(1, 20))
        
        # Job and Candidate Information
        job_info = [
            ['Job Title:', job_application.job.title],
            ['Candidate:', f"{job_application.candidate.user.first_name} {job_application.candidate.user.last_name}"],
            ['Email:', job_application.candidate.user.email],
            ['Phone:', job_application.candidate.phone],
            ['AI Score:', f"{job_application.ai_score}/10" if job_application.ai_score else "Not calculated"],
            ['Generated On:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        info_table = Table(job_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Job Description Section
        story.append(Paragraph("Job Description", subtitle_style))
        story.append(Paragraph(job_application.job.description, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Required Skills Section
        story.append(Paragraph("Required Skills", subtitle_style))
        story.append(Paragraph(job_application.job.key_skills, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Interview Questions Section
        story.append(Paragraph("Interview Questions", subtitle_style))
        story.append(Spacer(1, 10))
        
        # Process questions
        question_lines = questions.split('\n')
        for line in question_lines:
            if line.strip():
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 15))
        
        # Scoring Section
        story.append(Spacer(1, 30))
        story.append(Paragraph("Evaluation Notes", subtitle_style))
        
        eval_table_data = [
            ['Question Type', 'Score (1-5)', 'Comments'],
            ['Technical Skills', '', ''],
            ['Experience Relevance', '', ''],
            ['Problem Solving', '', ''],
            ['Cultural Fit', '', ''],
            ['Overall Rating', '', '']
        ]
        
        eval_table = Table(eval_table_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        eval_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(eval_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    @staticmethod
    def create_pdf_response(buffer, filename):
        """Create HTTP response for PDF download"""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(buffer.getvalue())
        buffer.close()
        return response
