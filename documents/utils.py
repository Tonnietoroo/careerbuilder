from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import openai
from django.conf import settings
from interviews.models import InterviewQuestion
from io import BytesIO
from openai import OpenAI

def format_experience(experience):
    """Format work experience for the prompt"""
    formatted = []
    for job in experience:
        formatted.append(f"- {job['job_title']} at {job['company_name']}")
        for resp in job.get('responsibilities', []):
            formatted.append(f"  • {resp}")
    return "\n".join(formatted)

def format_skills(skills):
    """Format skills for the prompt"""
    hard_skills = [skill['name'] for skill in skills if skill['type'] == 'hard']
    soft_skills = [skill['name'] for skill in skills if skill['type'] == 'soft']
    
    formatted = []
    if hard_skills:
        formatted.append("Hard Skills:")
        formatted.extend([f"• {skill}" for skill in hard_skills])
    if soft_skills:
        formatted.append("\nSoft Skills:")
        formatted.extend([f"• {skill}" for skill in soft_skills])
    return "\n".join(formatted)

def generate_cover_letter(cv, job_title, company_name):
    """Generate a professional cover letter using OpenAI's GPT model"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )
    
    # Extract relevant information from CV
    personal_info = cv.content.get('personal_info', {})
    full_name = personal_info.get('full_name', '')
    email = personal_info.get('email', '')
    phone = personal_info.get('phone_number', '')
    address = personal_info.get('address', '')
    experience = cv.content.get('work_experience', [])
    skills = cv.content.get('skills', [])
    personal_profile = cv.content.get('personal_profile', '')
    
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Create professional template with proper spacing and formatting
    template = f"""
{full_name}
{address}
{phone}
{email}

{current_date}

Hiring Manager
{company_name}
[Company Address]

Dear Hiring Manager,

[CONTENT]

Best regards,
{full_name}"""

    # Create prompt for GPT with specific instructions for professional content
    prompt = f"""
    Generate three compelling paragraphs for a professional cover letter for a {job_title} position at {company_name}.
    
    Use these details strategically:
    - Skills: {format_skills(skills)}
    - Experience: {format_experience(experience)}
    - Profile: {personal_profile}

    Follow this structure:
    1. Opening Paragraph: 
       - Express genuine interest in the specific role
       - Demonstrate knowledge of {company_name}
       - Mention how your background aligns with the company's mission
       
    2. Core Value Paragraph:
       - Highlight 2-3 most relevant achievements
       - Connect your experience directly to the role's requirements
       - Use specific metrics or outcomes when possible
       
    3. Closing Paragraph:
       - Reinforce your enthusiasm
       - Summarize your value proposition
       - Express interest in further discussion
       
    Requirements:
    - Keep tone professional but engaging
    - Focus on value you'll bring to the role
    - Use active voice and confident language
    - Avoid clichés and generic statements
    - Keep paragraphs concise and impactful
    - Do not include any headers or contact information
    """
    
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": settings.SITE_URL,
                "X-Title": "CareerBuilder",
            },
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert cover letter writer who creates compelling, professional content that:
                    - Demonstrates genuine interest in the role and company
                    - Highlights relevant achievements and skills
                    - Uses confident, active language
                    - Maintains professional tone while showing personality
                    - Creates clear value propositions
                    Generate only the body paragraphs, no headers or signatures."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=800,
        )
        
        generated_content = completion.choices[0].message.content.strip()
        
        # Clean up any formatting issues
        content_lines = generated_content.split('\n')
        cleaned_lines = []
        for line in content_lines:
            # Skip any lines that might contain formatting markers or duplicated info
            if any(x in line.lower() for x in [
                'first paragraph:', 'second paragraph:', 'third paragraph:',
                'dear', 'sincerely', 'hiring manager', full_name.lower(), 
                email, phone, address, '[content]'
            ]):
                continue
            cleaned_lines.append(line)
        
        # Join lines and ensure proper spacing
        cleaned_content = '\n\n'.join(
            para.strip() 
            for para in ' '.join(cleaned_lines).split('\n\n') 
            if para.strip()
        )
        
        # Create the final letter with proper formatting
        final_letter = template.replace('[CONTENT]', cleaned_content)
        
        if len(final_letter) < 100:
            raise ValueError("Generated content too short")
            
        return final_letter
        
    except Exception as e:
        print(f"Error generating cover letter: {str(e)}")
        return template.replace('[CONTENT]', 
            f"I am writing to express my strong interest in the {job_title} position at {company_name}. "
            "With my background and skills, I believe I would be a valuable addition to your team.\n\n"
            "[Error: Could not generate custom content. Please try again.]"
        )

def generate_pdf(cv):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(cv.title, styles['Title']))
    elements.append(Spacer(1, 12))

    # Personal Information
    elements.append(Paragraph('Personal Information', styles['Heading1']))
    personal_info = cv.content.get('personal_info', {})
    info_data = [
        ['Full Name:', personal_info.get('full_name', '')],
        ['Email:', personal_info.get('email', '')],
        ['Phone:', personal_info.get('phone_number', '')],
        ['Address:', personal_info.get('address', '')]
    ]
    table = Table(info_data, colWidths=[100, 400])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Bio Data
    elements.append(Paragraph('Bio Data', styles['Heading1']))
    bio_data = cv.content.get('bio_data', {})
    bio_table = Table([
        ['Gender:', bio_data.get('gender', '')],
        ['Date of Birth:', bio_data.get('date_of_birth', '')],
        ['Nationality:', bio_data.get('nationality', '')]
    ], colWidths=[100, 400])
    bio_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(bio_table)
    elements.append(Spacer(1, 12))

    # Personal Profile
    elements.append(Paragraph('Personal Profile', styles['Heading1']))
    elements.append(Paragraph(cv.content.get('personal_profile', ''), styles['Normal']))
    elements.append(Spacer(1, 12))

    # Work Experience
    elements.append(Paragraph('Work Experience', styles['Heading1']))
    for work in cv.content.get('work_experience', []):
        elements.append(Paragraph(f"{work['job_title']} at {work['company_name']}", styles['Heading2']))
        elements.append(Paragraph(f"{work['location']} | {work['start_date']} - {work.get('end_date', 'Present')}", styles['Italic']))
        for resp in work.get('responsibilities', []):
            elements.append(Paragraph(f"• {resp}", styles['Normal']))
        elements.append(Spacer(1, 12))

    # Education
    elements.append(Paragraph('Education', styles['Heading1']))
    for edu in cv.content.get('education', []):
        elements.append(Paragraph(edu['degree'], styles['Heading2']))
        elements.append(Paragraph(f"{edu['institution']} - {edu['location']}", styles['Normal']))
        elements.append(Paragraph(f"{edu['start_date']} - {edu.get('end_date', 'Present')}", styles['Normal']))
        if edu.get('grade'):
            elements.append(Paragraph(f"Grade: {edu['grade']}", styles['Normal']))
        elements.append(Spacer(1, 12))

    # Skills
    elements.append(Paragraph('Skills', styles['Heading1']))
    hard_skills = [skill['name'] for skill in cv.content.get('skills', []) if skill['type'] == 'hard']
    soft_skills = [skill['name'] for skill in cv.content.get('skills', []) if skill['type'] == 'soft']
    if hard_skills:
        elements.append(Paragraph('Hard Skills:', styles['Heading2']))
        for skill in hard_skills:
            elements.append(Paragraph(f"• {skill}", styles['Normal']))
    if soft_skills:
        elements.append(Paragraph('Soft Skills:', styles['Heading2']))
        for skill in soft_skills:
            elements.append(Paragraph(f"• {skill}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Certifications
    elements.append(Paragraph('Certifications', styles['Heading1']))
    for cert in cv.content.get('certifications', []):
        elements.append(Paragraph(cert['certificate_name'], styles['Heading2']))
        elements.append(Paragraph(f"{cert['issuing_organization']} - {cert['date_earned']}", styles['Normal']))
        elements.append(Spacer(1, 12))

    # Languages
    elements.append(Paragraph('Languages', styles['Heading1']))
    for lang in cv.content.get('languages', []):
        elements.append(Paragraph(f"{lang['language']}: {lang['proficiency'].title()}", styles['Normal']))

    # Hobbies
    elements.append(Paragraph('Hobbies & Interests', styles['Heading1']))
    for hobby in cv.content.get('hobbies', []):
        elements.append(Paragraph(f"• {hobby}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_docx(cv):
    doc = Document()
    
    # Create italic style
    italic_style = doc.styles.add_style('Italic Style', 1)  # 1 is character style
    italic_style.font.italic = True
    
    # Title
    doc.add_heading(cv.title, 0)

    # Personal Information
    doc.add_heading('Personal Information', level=1)
    personal_info = cv.content.get('personal_info', {})
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    cells = [
        ('Full Name:', personal_info.get('full_name', '')),
        ('Email:', personal_info.get('email', '')),
        ('Phone:', personal_info.get('phone_number', '')),
        ('Address:', personal_info.get('address', ''))
    ]
    for i, (key, value) in enumerate(cells):
        table.cell(i, 0).text = key
        table.cell(i, 1).text = value

    # Bio Data
    doc.add_heading('Bio Data', level=1)
    bio_data = cv.content.get('bio_data', {})
    table = doc.add_table(rows=3, cols=2)
    table.style = 'Table Grid'
    cells = [
        ('Gender:', bio_data.get('gender', '')),
        ('Date of Birth:', bio_data.get('date_of_birth', '')),
        ('Nationality:', bio_data.get('nationality', ''))
    ]
    for i, (key, value) in enumerate(cells):
        table.cell(i, 0).text = key
        table.cell(i, 1).text = value

    # Personal Profile
    doc.add_heading('Personal Profile', level=1)
    doc.add_paragraph(cv.content.get('personal_profile', ''))

    # Work Experience
    doc.add_heading('Work Experience', level=1)
    for work in cv.content.get('work_experience', []):
        doc.add_heading(f"{work['job_title']} at {work['company_name']}", level=2)
        # Use italic style for date range
        p = doc.add_paragraph()
        p.add_run(f"{work['location']} | {work['start_date']} - {work.get('end_date', 'Present')}").italic = True
        for resp in work.get('responsibilities', []):
            doc.add_paragraph(f"• {resp}", style='List Bullet')

    # Education
    doc.add_heading('Education', level=1)
    for edu in cv.content.get('education', []):
        doc.add_heading(edu['degree'], level=2)
        doc.add_paragraph(f"{edu['institution']} - {edu['location']}")
        # Use italic style for date range
        p = doc.add_paragraph()
        p.add_run(f"{edu['start_date']} - {edu.get('end_date', 'Present')}").italic = True
        if edu.get('grade'):
            doc.add_paragraph(f"Grade: {edu['grade']}")

    # Skills
    doc.add_heading('Skills', level=1)
    hard_skills = [skill['name'] for skill in cv.content.get('skills', []) if skill['type'] == 'hard']
    soft_skills = [skill['name'] for skill in cv.content.get('skills', []) if skill['type'] == 'soft']
    if hard_skills:
        doc.add_heading('Hard Skills:', level=2)
        for skill in hard_skills:
            doc.add_paragraph(f"• {skill}", style='List Bullet')
    if soft_skills:
        doc.add_heading('Soft Skills:', level=2)
        for skill in soft_skills:
            doc.add_paragraph(f"• {skill}", style='List Bullet')

    # Certifications
    doc.add_heading('Certifications', level=1)
    for cert in cv.content.get('certifications', []):
        doc.add_heading(cert['certificate_name'], level=2)
        doc.add_paragraph(f"{cert['issuing_organization']} - {cert['date_earned']}")

    # Languages
    doc.add_heading('Languages', level=1)
    for lang in cv.content.get('languages', []):
        doc.add_paragraph(f"{lang['language']}: {lang['proficiency'].title()}")

    # Hobbies
    doc.add_heading('Hobbies & Interests', level=1)
    for hobby in cv.content.get('hobbies', []):
        doc.add_paragraph(f"• {hobby}", style='List Bullet')

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def get_interview_questions(job_title, company_name):
    """Generate interview questions and tips for a specific job"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )
    
    prompt = f"""
    Generate 10 interview questions and detailed answers for a {job_title} position at {company_name}.
    
    For each question, provide:
    1. A challenging but realistic question
    2. A detailed sample answer that demonstrates expertise
    3. Mix of technical, behavioral, and role-specific questions
    
    Format EXACTLY as follows for each question:
    Q: [The interview question]
    A: [The detailed answer]

    Make questions specific to the {job_title} role and {company_name}'s industry.
    Include questions about:
    - Technical skills required for the role
    - Past experience and achievements
    - Problem-solving abilities
    - Team collaboration
    - Role-specific scenarios
    """
    
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": settings.SITE_URL,
                "X-Title": "CareerBuilder",
            },
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert interviewer. Generate specific, detailed interview questions and answers. Format each Q&A pair exactly as requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = completion.choices[0].message.content.strip()
        
        # Parse and store the questions
        questions = []
        current_question = None
        current_answer = []
        
        # Split content into lines and process
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('Q:'):
                # If we have a previous question, save it
                if current_question is not None:
                    question_obj = InterviewQuestion.objects.create(
                        question=current_question,
                        answer='\n'.join(current_answer),
                        question_type='general'
                    )
                    questions.append(question_obj)
                
                # Start new question
                current_question = line[2:].strip()
                current_answer = []
            elif line.startswith('A:'):
                current_answer.append(line[2:].strip())
            elif current_answer:  # Continue adding to current answer
                current_answer.append(line)
        
        # Don't forget to save the last question
        if current_question is not None:
            question_obj = InterviewQuestion.objects.create(
                question=current_question,
                answer='\n'.join(current_answer),
                question_type='general'
            )
            questions.append(question_obj)
        
        if not questions:  # If no questions were parsed successfully
            raise ValueError("No questions were generated")
            
        return questions
        
    except Exception as e:
        print(f"Error generating interview questions: {str(e)}")
        # Return default questions if generation fails
        return [
            InterviewQuestion.objects.create(
                question_type='general',
                question=f"Tell me about your experience relevant to this {job_title} position.",
                answer=f"Focus on your most relevant experience for the {job_title} role. Highlight specific achievements and how they demonstrate your qualifications. Mention any similar roles or projects you've worked on, and explain how that experience would benefit {company_name}."
            ),
            InterviewQuestion.objects.create(
                question_type='general',
                question=f"Why are you interested in this position at {company_name}?",
                answer=f"Research {company_name}'s mission, values, and recent projects. Explain how your career goals align with the company's objectives. Discuss specific aspects of the role that interest you and how you can contribute to the company's success."
            ),
            InterviewQuestion.objects.create(
                question_type='general',
                question="What is your greatest professional achievement?",
                answer="Choose a significant achievement that demonstrates skills relevant to the role. Use the STAR method (Situation, Task, Action, Result) to structure your response. Quantify the results when possible and explain how this experience has prepared you for this position."
            )
        ]

def generate_cover_letter_pdf(cover_letter):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Add company info
    elements.append(Paragraph(cover_letter.company_name, styles['Heading1']))
    elements.append(Paragraph(cover_letter.company_address, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Add date
    elements.append(Paragraph(cover_letter.created_at.strftime('%B %d, %Y'), styles['Normal']))
    elements.append(Spacer(1, 12))

    # Add content
    elements.append(Paragraph(cover_letter.content, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Add signature
    elements.append(Paragraph('Sincerely,', styles['Normal']))
    elements.append(Paragraph(cover_letter.cv.content['personal_info']['full_name'], styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_cover_letter_docx(cover_letter):
    doc = Document()
    
    # Add company info
    doc.add_heading(cover_letter.company_name, 0)
    doc.add_paragraph(cover_letter.company_address)
    doc.add_paragraph()  # blank line

    # Add date
    doc.add_paragraph(cover_letter.created_at.strftime('%B %d, %Y'))
    doc.add_paragraph()  # blank line

    # Add content
    doc.add_paragraph(cover_letter.content)
    doc.add_paragraph()  # blank line

    # Add signature
    doc.add_paragraph('Sincerely,')
    doc.add_paragraph(cover_letter.cv.content['personal_info']['full_name'])

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer 