import openai
from django.conf import settings
from .models import InterviewQuestion

openai.api_key = settings.OPENAI_API_KEY

def generate_cover_letter(cv, job_title, company_name):
    # Extract relevant information from CV
    full_name = cv.content['personal_info']['full_name']
    experience = cv.content['work_experience']
    skills = cv.content['skills']
    
    # Create prompt for GPT
    prompt = f"""
    Write a professional cover letter for {full_name} applying for the {job_title} position at {company_name}.
    
    Key experience:
    {format_experience(experience)}
    
    Key skills:
    {format_skills(skills)}
    
    The cover letter should be professional, enthusiastic, and highlight relevant experience and skills.
    Keep it concise and focused on the value the candidate can bring to the role.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional cover letter writer."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def get_interview_questions(job_category, job_title):
    # First check if we have pre-existing questions in our database
    existing_questions = InterviewQuestion.objects.filter(category=job_category)
    
    if existing_questions.exists():
        return existing_questions[:10]  # Return top 10 questions
    
    # If no existing questions, generate new ones using GPT
    prompt = f"""
    Generate 10 interview questions for a {job_title} position in the {job_category.name} industry.
    Include a mix of technical, behavioral, and general questions.
    For each question, also provide a suggested answer.
    Format: Question: [question] Answer: [answer]
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert interviewer."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Parse response and create questions
    questions = []
    content = response.choices[0].message.content
    qa_pairs = content.split('\n\n')
    
    for pair in qa_pairs:
        if 'Question:' in pair and 'Answer:' in pair:
            q, a = pair.split('Answer:')
            q = q.replace('Question:', '').strip()
            a = a.strip()
            
            question = InterviewQuestion.objects.create(
                category=job_category,
                question_type='general',  # You might want to detect the type
                question=q,
                answer=a
            )
            questions.append(question)
    
    return questions

def format_experience(experience):
    formatted = []
    for exp in experience:
        formatted.append(f"- {exp['job_title']} at {exp['company_name']}")
        for resp in exp['responsibilities'][:2]:  # Include top 2 responsibilities
            formatted.append(f"  • {resp}")
    return "\n".join(formatted)

def format_skills(skills):
    return "\n".join([f"- {skill['name']}" for skill in skills]) 