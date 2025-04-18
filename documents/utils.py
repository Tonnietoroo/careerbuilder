from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Cm
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

def generate_pdf(cv, output):
    """Generate a PDF version of the CV"""
    doc = SimpleDocTemplate(output, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#2c3e50')
    )

    # Add name as title
    elements.append(Paragraph(cv.content['personal_info']['full_name'], title_style))
    
    # Contact information
    contact_info = [
        [cv.content['personal_info']['email']],
        [cv.content['personal_info']['phone_number']],
        [cv.content['personal_info']['address']]
    ]
    contact_table = Table(contact_info, colWidths=[400])
    contact_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#666666')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(contact_table)
    elements.append(Spacer(1, 20))

    # Professional Profile
    elements.append(Paragraph('Professional Profile', heading_style))
    elements.append(Paragraph(cv.content['personal_profile'], styles['Normal']))
    elements.append(Spacer(1, 20))

    # Work Experience
    elements.append(Paragraph('Work Experience', heading_style))
    for exp in cv.content['work_experience']:
        elements.append(Paragraph(
            f"<b>{exp['job_title']}</b> at <b>{exp['company_name']}</b>",
            styles['Normal']
        ))
        elements.append(Paragraph(
            f"<i>{exp['start_date']} - {exp['end_date'] or 'Present'}</i>",
            styles['Normal']
        ))
        for resp in exp['responsibilities']:
            elements.append(Paragraph(f"• {resp}", styles['Normal']))
        elements.append(Spacer(1, 12))

    # Education
    elements.append(Paragraph('Education', heading_style))
    for edu in cv.content['education']:
        elements.append(Paragraph(
            f"<b>{edu['degree']}</b> - {edu['institution']}",
            styles['Normal']
        ))
        elements.append(Paragraph(
            f"<i>{edu['start_date']} - {edu['end_date'] or 'Present'}</i>",
            styles['Normal']
        ))
        if edu['grade']:
            elements.append(Paragraph(f"Grade: {edu['grade']}", styles['Normal']))
        elements.append(Spacer(1, 12))

    # Skills
    if cv.content['skills']:
        elements.append(Paragraph('Skills', heading_style))
        skill_text = ' • '.join(skill['name'] for skill in cv.content['skills'])
        elements.append(Paragraph(skill_text, styles['Normal']))

    # Build the PDF
    doc.build(elements)

def generate_docx(cv, output):
    """Generate a Word document version of the CV"""
    doc = Document()
    
    # Add custom styles
    styles = doc.styles
    
    # Heading style
    heading_style = styles.add_style('CustomHeading', WD_STYLE_TYPE.PARAGRAPH)
    heading_style.font.size = Pt(16)
    heading_style.font.bold = True
    heading_style.font.color.rgb = RGBColor(44, 62, 80)  # #2c3e50
    heading_style.paragraph_format.space_before = Pt(20)
    heading_style.paragraph_format.space_after = Pt(12)
    
    # Name and title
    title = doc.add_heading(cv.content['personal_info']['full_name'], 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Contact information
    contact_info = doc.add_paragraph()
    contact_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact_info.add_run(cv.content['personal_info']['email']).italic = True
    contact_info.add_run(' | ')
    contact_info.add_run(cv.content['personal_info']['phone_number']).italic = True
    contact_info.add_run(' | ')
    contact_info.add_run(cv.content['personal_info']['address']).italic = True
    
    # Professional Profile
    doc.add_heading('Professional Profile', level=1).style = heading_style
    doc.add_paragraph(cv.content['personal_profile'])
    
    # Work Experience
    doc.add_heading('Work Experience', level=1).style = heading_style
    for exp in cv.content['work_experience']:
        p = doc.add_paragraph()
        p.add_run(f"{exp['job_title']} at {exp['company_name']}").bold = True
        p.add_run(f"\n{exp['start_date']} - {exp['end_date'] or 'Present'}").italic = True
        
        if exp['responsibilities']:
            for resp in exp['responsibilities']:
                bullet_p = doc.add_paragraph(style='List Bullet')
                bullet_p.add_run(resp)
    
    # Education
    doc.add_heading('Education', level=1).style = heading_style
    for edu in cv.content['education']:
        p = doc.add_paragraph()
        p.add_run(f"{edu['degree']} - {edu['institution']}").bold = True
        p.add_run(f"\n{edu['start_date']} - {edu['end_date'] or 'Present'}").italic = True
        if edu['grade']:
            p.add_run(f"\nGrade: {edu['grade']}")
    
    # Skills
    if cv.content['skills']:
        doc.add_heading('Skills', level=1).style = heading_style
        skills_para = doc.add_paragraph()
        for i, skill in enumerate(cv.content['skills']):
            skills_para.add_run(skill['name'])
            if i < len(cv.content['skills']) - 1:
                skills_para.add_run(' • ')
    
    # Set margins for better layout
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
    
    # Save the document
    doc.save(output)

def get_interview_questions(job_title, company_name):
    """Generate interview questions and tips for a specific job"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
        default_headers=settings.OPENROUTER_HEADERS
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
        
        return questions
        
    except Exception as e:
        print(f"Error generating interview questions: {str(e)}")
        # Return default questions if generation fails
        return [
            InterviewQuestion.objects.create(
                question_type='general',
                question=f"Tell me about your experience relevant to this {job_title} position.",
                answer=f"Focus on your most relevant experience for the {job_title} role. Highlight specific achievements and how they demonstrate your qualifications."
            ),
            InterviewQuestion.objects.create(
                question_type='general',
                question=f"Why are you interested in working at {company_name}?",
                answer=f"Research {company_name}'s mission and values. Explain how your career goals align with the company's objectives."
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

def generate_cover_letter_body(cv, job_title, company_name):
    """
    Generate the body content for a cover letter using CV data and job details.
    """
    try:
        # Get relevant information from CV
        work_experience = cv.content.get('work_experience', [])
        skills = cv.content.get('skills', [])
        education = cv.content.get('education', [])
        
        # Create an introduction paragraph
        intro = (f"I am writing to express my keen interest in the {job_title} position at {company_name}. "
                "As a motivated professional with a strong background in technology and a passion for innovation, "
                "I am confident in my ability to contribute effectively to your team.")

        # Create a skills and experience paragraph
        skill_names = [skill['name'] for skill in skills[:3]]  # Get top 3 skills
        if skill_names:
            skills_text = ", ".join(skill_names[:-1]) + f" and {skill_names[-1]}" if len(skill_names) > 1 else skill_names[0]
            experience_para = f"\n\nMy expertise in {skills_text} aligns perfectly with the requirements of this role. "
        else:
            experience_para = "\n\nThroughout my career, I have developed a diverse set of technical skills. "

        # Add work experience
        if work_experience:
            latest_job = work_experience[0]  # Get most recent experience
            experience_para += (f"In my current role as {latest_job.get('job_title')} at {latest_job.get('company_name')}, "
                              "I have successfully:")
            
            # Add bullet points from responsibilities
            responsibilities = latest_job.get('responsibilities', [])
            if responsibilities:
                experience_para += "\n"
                for resp in responsibilities[:3]:  # Include top 3 responsibilities
                    experience_para += f"\n• {resp}"

        # Add education if available
        if education:
            latest_edu = education[0]  # Get most recent education
            edu_para = f"\n\nI hold a {latest_edu.get('degree')} from {latest_edu.get('institution')}"
            if latest_edu.get('grade'):
                edu_para += f" with a grade of {latest_edu.get('grade')}"
            edu_para += ". "
            experience_para += edu_para

        # Create a closing paragraph
        closing = ("\n\nI am particularly drawn to your company's reputation for innovation and excellence in the industry. "
                  "I am excited about the possibility of bringing my expertise and enthusiasm to your team. "
                  "I would welcome the opportunity to discuss how my skills and experience align with your needs in more detail.")

        # Combine all paragraphs
        body = intro + experience_para + closing

        return body

    except Exception as e:
        # Fallback content in case of any error
        return (f"I am writing to express my strong interest in the {job_title} position at {company_name}.\n\n"
                "Throughout my career, I have developed a strong skill set that aligns well with this role. "
                "I have consistently demonstrated my ability to deliver results and work effectively in team environments. "
                "My technical expertise and problem-solving abilities have enabled me to make significant contributions "
                "in my previous roles.\n\n"
                "I am excited about the opportunity to bring my skills and experience to your organization. "
                "I would welcome the chance to discuss how I can contribute to your team in more detail.") 