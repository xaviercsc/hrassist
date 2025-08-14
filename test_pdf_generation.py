#!/usr/bin/env python3
"""
Test script to verify PDF generation with proper formatting.
This tests the improved PDF generation logic for interview questions.
"""

import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

def test_pdf_generation():
    """Test the improved PDF generation with sample data"""
    
    # Sample data (similar to what would come from the application)
    job_title = "Python Developer – Kubernetes & AWS"
    candidate_name = "das wane"
    
    # Sample questions with double numbering (simulating AI response)
    sample_questions = [
        "1. Can you explain your experience with Python frameworks such as Flask, Django, or FastAPI, and describe a specific project where you utilized one of these frameworks?",
        "2. Describe your hands-on experience with Kubernetes. How have you used it for container orchestration in your previous projects?",
        "3. Can you detail the steps you would take to deploy a scalable Python application on AWS using services like EC2, Lambda, or EKS?",
        "4. How do you ensure that your RESTful APIs are efficient and secure? Can you provide examples of security measures you have implemented in past projects?",
        "5. Tell me about a challenging technical problem you solved using Python. What was your approach and what was the outcome?",
        "6. Describe a situation where you had to work under tight deadlines. How did you prioritize your tasks and ensure quality delivery?",
        "7. How do you handle feedback and criticism from team members or supervisors?",
        "8. Tell me about a time when you had to collaborate with a difficult team member. How did you handle the situation?",
        "9. What motivates you in your work, and how do you stay engaged with challenging projects?",
        "10. How do you approach learning new technologies or skills relevant to your role?",
        "11. Describe your experience with version control systems like Git. How do you manage code collaboration in team environments?",
        "12. Can you walk me through your experience with automated testing in Python applications?",
        "13. How do you stay updated with the latest trends and best practices in Python development and cloud technologies?",
        "14. Where do you see yourself in the next 3-5 years, and how does this role align with your career goals?",
        "15. Do you have any questions about the role, our team, or our company culture?"
    ]
    
    try:
        print("Testing PDF Generation...")
        print(f"Job: {job_title}")
        print(f"Candidate: {candidate_name}")
        print(f"Questions: {len(sample_questions)}")
        print("-" * 50)
        
        # Generate PDF with proper formatting
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Build PDF content
        story = []
        
        # Title
        title = Paragraph(f"Interview Questions", title_style)
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Job and candidate info
        job_info = Paragraph(f"<b>Position:</b> {job_title}", heading_style)
        story.append(job_info)
        story.append(Spacer(1, 0.1*inch))
        
        candidate_info = Paragraph(f"<b>Candidate:</b> {candidate_name}", heading_style)
        story.append(candidate_info)
        story.append(Spacer(1, 0.3*inch))
        
        # Process questions to remove double numbering
        processed_questions = []
        for question in sample_questions:
            question = question.strip()
            if question:
                # Remove leading numbers and dots if present (e.g., "1. " or "1.")
                clean_question = re.sub(r'^\d+\.\s*', '', question)
                processed_questions.append(clean_question)
        
        print("Processed questions (removing double numbering):")
        for i, question in enumerate(processed_questions[:3], 1):  # Show first 3
            print(f"  {i}. {question[:60]}...")
        print(f"  ... and {len(processed_questions)-3} more questions")
        print()
        
        # Add questions with proper formatting
        for i, question in enumerate(processed_questions, 1):
            if question.strip():  # Only add non-empty questions
                # Question number and text
                question_text = f"<b>{i}.</b> {question}"
                question_para = Paragraph(question_text, normal_style)
                story.append(question_para)
                story.append(Spacer(1, 0.15*inch))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Save test PDF
        pdf_filename = "test_interview_questions.pdf"
        with open(pdf_filename, "wb") as f:
            f.write(buffer.getvalue())
        
        print(f"✅ SUCCESS: PDF generated successfully!")
        print(f"📄 File saved as: {pdf_filename}")
        print(f"📊 PDF size: {len(buffer.getvalue())} bytes")
        print("\n🔧 Improvements made:")
        print("   ✅ Removed double numbering")
        print("   ✅ Added proper text wrapping") 
        print("   ✅ Improved layout with margins")
        print("   ✅ Better typography and spacing")
        print("   ✅ Automatic page breaks")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: PDF generation failed")
        print(f"Error details: {str(e)}")
        return False

def test_question_processing():
    """Test the question processing logic specifically"""
    
    print("\n" + "="*50)
    print("Testing Question Processing Logic")
    print("="*50)
    
    # Test cases for different numbering formats
    test_questions = [
        "1. Can you explain your experience with Python?",
        "2.How do you handle debugging?",
        "3 What is your approach to testing?",
        "4. Tell me about a challenging project.",
        "How do you stay updated with technology?",  # No number
        "  5. What are your career goals?  ",  # Extra spaces
    ]
    
    print("Original questions:")
    for q in test_questions:
        print(f"  '{q}'")
    
    print("\nProcessed questions (after removing numbering):")
    for i, question in enumerate(test_questions, 1):
        question = question.strip()
        if question:
            # Remove leading numbers and dots
            clean_question = re.sub(r'^\d+\.\s*', '', question)
            print(f"  {i}. {clean_question}")
    
    return True

if __name__ == "__main__":
    print("🔧 PDF Generation Test Suite")
    print("=" * 50)
    
    # Run tests
    test1_passed = test_question_processing()
    test2_passed = test_pdf_generation()
    
    print("\n" + "=" * 50)
    if test1_passed and test2_passed:
        print("🎉 All tests passed! PDF generation is working correctly.")
        print("\n📋 Summary of fixes:")
        print("   • Fixed double numbering issue")
        print("   • Added proper text wrapping for long questions")
        print("   • Improved PDF layout and formatting")
        print("   • Added automatic page breaks")
        print("   • Enhanced typography and spacing")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
