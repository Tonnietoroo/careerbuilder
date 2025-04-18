from django.utils import timezone
from .models import InterviewQuestion
from interviews.models import Industry

def get_interview_questions(job_category, job_title):
    """Generate or retrieve interview questions based on job category and title."""
    
    # First try to get existing questions for this industry
    existing_questions = InterviewQuestion.objects.filter(industry=job_category)
    
    # If there are existing questions, return them all (up to 10)
    if existing_questions.exists():
        return existing_questions[:10]
    
    # Create default questions if none exist
    default_questions = [
        {
            'question': f'What motivated you to apply for this {job_title} position at our company?',
            'answer': 'Focus on: \n- Your research about the company\n- Alignment with company values\n- Specific aspects of the role that excite you\n- How this fits your career goals',
            'type': 'general'
        },
        {
            'question': f'What are your most relevant accomplishments for this {job_title} role?',
            'answer': 'Structure your answer using the STAR method:\n- Situation: Set the context\n- Task: Describe the challenge\n- Action: Explain what you did\n- Result: Share quantifiable outcomes',
            'type': 'behavioral'
        },
        {
            'question': 'How do you handle tight deadlines and pressure?',
            'answer': 'Discuss:\n- Your prioritization method\n- Time management techniques\n- Stress management strategies\n- Specific example of meeting a challenging deadline\n- How you maintain work quality under pressure',
            'type': 'behavioral'
        },
        {
            'question': f'What do you consider the biggest challenges in the {job_category} industry today?',
            'answer': 'Demonstrate:\n- Industry knowledge\n- Current trends awareness\n- Understanding of market challenges\n- Potential solutions or adaptations\n- How you stay informed about industry developments',
            'type': 'technical'
        },
        {
            'question': 'Describe a situation where you had to resolve a conflict at work.',
            'answer': 'Include:\n- The nature of the conflict\n- Your role in the situation\n- Communication methods used\n- Steps taken to resolve\n- Lessons learned\n- Positive outcome achieved',
            'type': 'behavioral'
        },
        {
            'question': 'Where do you see yourself in five years?',
            'answer': 'Address:\n- Professional development goals\n- Skills you want to acquire\n- Leadership aspirations\n- How the role and company align with these goals\n- Realistic progression within the organization',
            'type': 'general'
        },
        {
            'question': f'What unique skills would you bring to this {job_title} position?',
            'answer': 'Highlight:\n- Technical skills relevant to the role\n- Soft skills that set you apart\n- Unique experiences or perspectives\n- How these skills benefit the company\n- Examples of applying these skills successfully',
            'type': 'general'
        },
        {
            'question': 'Tell me about a time you failed and what you learned from it.',
            'answer': 'Structure:\n- Specific situation and challenge\n- Your approach and why it didn\'t work\n- What you learned from the experience\n- How you\'ve applied these lessons since\n- Changes in your approach as a result',
            'type': 'behavioral'
        },
        {
            'question': 'How do you stay updated with industry trends and developments?',
            'answer': 'Mention:\n- Professional associations\n- Industry publications\n- Online resources and platforms\n- Networking activities\n- Continuous learning initiatives\n- Relevant certifications or training',
            'type': 'general'
        },
        {
            'question': 'What questions do you have for us?',
            'answer': 'Prepare questions about:\n- Company culture and values\n- Team structure and dynamics\n- Growth opportunities\n- Current challenges and priorities\n- Success metrics for the role\n- Next steps in the process',
            'type': 'general'
        }
    ]
    
    # Create all questions at once using bulk_create
    questions = [
        InterviewQuestion(
            question=q['question'],
            answer=q['answer'],
            question_type=q['type'],
            industry=job_category
        ) for q in default_questions
    ]
    
    return InterviewQuestion.objects.bulk_create(questions)

# Create some default industries if they don't exist
default_industries = [
    {"name": "Technology", "description": "Software, IT, and tech companies"},
    {"name": "Healthcare", "description": "Medical, healthcare, and pharmaceutical"},
    {"name": "Finance", "description": "Banking, investment, and financial services"},
    {"name": "Education", "description": "Schools, universities, and educational services"},
    {"name": "Retail", "description": "Retail stores and e-commerce"}
]

# Create industries if they don't exist
for industry in default_industries:
    Industry.objects.get_or_create(
        name=industry["name"],
        defaults={"description": industry["description"]}
    ) 