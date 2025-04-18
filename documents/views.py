from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from .models import CV, CoverLetter, DocumentFolder, Document, CVTemplate
from .forms import CVForm, CoverLetterForm, InterviewPrepForm
from .utils import (
    generate_pdf, 
    generate_docx, 
    generate_cover_letter, 
    get_interview_questions, 
    generate_cover_letter_pdf, 
    generate_cover_letter_docx,
    generate_cover_letter_body
)
import json
import openai
from django.core.paginator import Paginator
from django.db.models import Q
from interviews.models import InterviewPrep, InterviewQuestion
from django.utils import timezone
from django.core.files.storage import default_storage
import docx2txt
import PyPDF2
import re

@login_required
def cv_list(request):
    cvs = CV.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'documents/cv_list.html', {'cvs': cvs})

@login_required
def cv_template_select(request):
    templates = CVTemplate.objects.filter(is_active=True)
    return render(request, 'documents/cv_template_select.html', {
        'templates': templates
    })

@login_required
def cv_create(request):
    # Get template_id from either GET (initial) or POST (form submission)
    template_id = request.GET.get('template') or request.POST.get('template')
    
    if not template_id:
        messages.error(request, 'Please select a template')
        return redirect('documents:cv_template_select')
    
    template = get_object_or_404(CVTemplate, id=template_id)
    
    if request.method == 'POST':
        form = CVForm(request.POST)
        if form.is_valid():
            cv = form.save(commit=False)
            cv.user = request.user
            cv.template = template
            
            # Create CV data dictionary
            cv_data = {
                'personal_info': {
                    'full_name': form.cleaned_data['full_name'],
                    'email': form.cleaned_data['email'],
                    'phone_number': form.cleaned_data['phone_number'],
                    'address': form.cleaned_data['address'],
                },
                'bio_data': {
                    'gender': form.cleaned_data['gender'],
                    'date_of_birth': form.cleaned_data['date_of_birth'].isoformat(),
                    'nationality': form.cleaned_data['nationality'],
                },
                'personal_profile': form.cleaned_data['personal_profile'],
                'work_experience': [],
                'education': [],
                'skills': [],
                'certifications': [],
                'languages': [],
                'hobbies': [],
                'referees': []
            }

            # Process work experience
            job_titles = request.POST.getlist('job_title[]')
            companies = request.POST.getlist('company_name[]')
            locations = request.POST.getlist('work_location[]')
            start_dates = request.POST.getlist('work_start_date[]')
            end_dates = request.POST.getlist('work_end_date[]')
            responsibilities = request.POST.getlist('work_responsibilities[]')

            for i in range(len(job_titles)):
                if job_titles[i] and companies[i]:
                    cv_data['work_experience'].append({
                        'job_title': job_titles[i],
                        'company_name': companies[i],
                        'location': locations[i],
                        'start_date': start_dates[i],
                        'end_date': end_dates[i] if end_dates[i] else None,
                        'responsibilities': responsibilities[i].split('\n') if responsibilities[i] else []
                    })

            # Process education
            degrees = request.POST.getlist('degree[]')
            institutions = request.POST.getlist('institution[]')
            edu_locations = request.POST.getlist('education_location[]')
            edu_start_dates = request.POST.getlist('education_start_date[]')
            edu_end_dates = request.POST.getlist('education_end_date[]')
            grades = request.POST.getlist('grade[]')

            for i in range(len(degrees)):
                if degrees[i] and institutions[i]:
                    cv_data['education'].append({
                        'degree': degrees[i],
                        'institution': institutions[i],
                        'location': edu_locations[i],
                        'start_date': edu_start_dates[i],
                        'end_date': edu_end_dates[i] if edu_end_dates[i] else None,
                        'grade': grades[i]
                    })

            # Process skills
            skill_names = request.POST.getlist('skill_name[]')
            skill_types = request.POST.getlist('skill_type[]')

            for i in range(len(skill_names)):
                if skill_names[i]:
                    cv_data['skills'].append({
                        'name': skill_names[i],
                        'type': skill_types[i]
                    })

            # Process certifications
            cert_names = request.POST.getlist('certificate_name[]')
            issuers = request.POST.getlist('issuing_organization[]')
            cert_dates = request.POST.getlist('date_earned[]')

            for i in range(len(cert_names)):
                if cert_names[i]:
                    cv_data['certifications'].append({
                        'certificate_name': cert_names[i],
                        'issuing_organization': issuers[i],
                        'date_earned': cert_dates[i]
                    })

            # Process languages
            languages = request.POST.getlist('language[]')
            proficiencies = request.POST.getlist('proficiency[]')

            for i in range(len(languages)):
                if languages[i]:
                    cv_data['languages'].append({
                        'language': languages[i],
                        'proficiency': proficiencies[i]
                    })

            # Process hobbies
            hobbies = request.POST.getlist('hobby[]')
            cv_data['hobbies'] = [hobby for hobby in hobbies if hobby]

            # Process referees
            for name, job, email, phone in zip(
                request.POST.getlist('referee_name[]'),
                request.POST.getlist('referee_job[]'),
                request.POST.getlist('referee_email[]'),
                request.POST.getlist('referee_phone[]')
            ):
                if name and job:  # Only add if at least name and job are provided
                    cv_data['referees'].append({
                        'name': name,
                        'job': job,
                        'email': email,
                        'phone': phone
                    })

            cv.content = cv_data
            cv.save()

            messages.success(request, 'CV created successfully!')
            return redirect('documents:cv_preview', cv_id=cv.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CVForm()

    return render(request, 'documents/cv_create.html', {
        'form': form,
        'template': template,
        'template_id': template_id  # Pass template_id to the template
    })

@login_required
def cv_preview(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id, user=request.user)
    
    # Get template CSS
    template_css = ""
    if cv.template and cv.template.css_template:
        try:
            template_css = cv.template.css_template.read().decode('utf-8')
        except Exception as e:
            messages.warning(request, "Could not load template CSS. Using default styling.")
    
    # Get template name (lowercase)
    template_name = cv.template.name.lower() if cv.template else 'professional'
    
    context = {
        'cv': cv,
        'template_css': template_css,
        'template_name': template_name,
        'personal_info': cv.content['personal_info'],
        'bio_data': cv.content.get('bio_data', {}),
        'personal_profile': cv.content['personal_profile'],
        'work_experience': cv.content['work_experience'],
        'education': cv.content['education'],
        'skills': cv.content['skills'],
        'certifications': cv.content.get('certifications', []),
        'languages': cv.content.get('languages', []),
        'hobbies': cv.content.get('hobbies', []),
        'referees': cv.content.get('referees', [])
    }
    
    return render(request, 'documents/cv_preview.html', context)

@login_required
def cv_edit(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id, user=request.user)
    
    if request.method == 'POST':
        form = CVForm(request.POST, instance=cv)
        if form.is_valid():
            cv = form.save(commit=False)
            
            # Process the form data
            cv_data = {
                'personal_info': {
                    'full_name': form.cleaned_data['full_name'],
                    'email': form.cleaned_data['email'],
                    'phone_number': form.cleaned_data['phone_number'],
                    'address': form.cleaned_data['address'],
                },
                'bio_data': {
                    'gender': form.cleaned_data['gender'],
                    'date_of_birth': form.cleaned_data['date_of_birth'].isoformat() if form.cleaned_data['date_of_birth'] else None,
                    'nationality': form.cleaned_data['nationality'],
                },
                'personal_profile': form.cleaned_data['personal_profile'],
                'work_experience': [],
                'education': [],
                'skills': [],
                'certifications': [],
                'languages': [],
                'hobbies': [],
                'referees': []
            }

            # Process work experience
            for job_title, company, location, start, end, resp in zip(
                request.POST.getlist('job_title[]'),
                request.POST.getlist('company_name[]'),
                request.POST.getlist('work_location[]'),
                request.POST.getlist('work_start_date[]'),
                request.POST.getlist('work_end_date[]'),
                request.POST.getlist('work_responsibilities[]')
            ):
                if job_title and company:
                    cv_data['work_experience'].append({
                        'job_title': job_title,
                        'company_name': company,
                        'location': location,
                        'start_date': start,
                        'end_date': end if end else None,
                        'responsibilities': resp.split('\n') if resp else []
                    })

            # Process education
            for degree, institution, location, start, end, grade in zip(
                request.POST.getlist('degree[]'),
                request.POST.getlist('institution[]'),
                request.POST.getlist('education_location[]'),
                request.POST.getlist('education_start_date[]'),
                request.POST.getlist('education_end_date[]'),
                request.POST.getlist('grade[]')
            ):
                if degree and institution:
                    cv_data['education'].append({
                        'degree': degree,
                        'institution': institution,
                        'location': location,
                        'start_date': start,
                        'end_date': end if end else None,
                        'grade': grade
                    })

            # Process skills
            for name, skill_type in zip(
                request.POST.getlist('skill_name[]'),
                request.POST.getlist('skill_type[]')
            ):
                if name:
                    cv_data['skills'].append({
                        'name': name,
                        'type': skill_type
                    })

            # Process certifications
            for name, org, date in zip(
                request.POST.getlist('certificate_name[]'),
                request.POST.getlist('issuing_organization[]'),
                request.POST.getlist('date_earned[]')
            ):
                if name and org:
                    cv_data['certifications'].append({
                        'certificate_name': name,
                        'issuing_organization': org,
                        'date_earned': date
                    })

            # Process languages
            for lang, prof in zip(
                request.POST.getlist('language[]'),
                request.POST.getlist('proficiency[]')
            ):
                if lang:
                    cv_data['languages'].append({
                        'language': lang,
                        'proficiency': prof
                    })

            # Process hobbies
            cv_data['hobbies'] = [
                hobby for hobby in request.POST.getlist('hobby[]') if hobby
            ]

            # Process referees
            for name, job, email, phone in zip(
                request.POST.getlist('referee_name[]'),
                request.POST.getlist('referee_job[]'),
                request.POST.getlist('referee_email[]'),
                request.POST.getlist('referee_phone[]')
            ):
                if name and job:  # Only add if at least name and job are provided
                    cv_data['referees'].append({
                        'name': name,
                        'job': job,
                        'email': email,
                        'phone': phone
                    })

            cv.content = cv_data
            cv.save()
            messages.success(request, 'CV updated successfully!')
            return redirect('documents:cv_preview', cv_id=cv.id)
    else:
        # Initialize form with existing data
        initial_data = {}
        content = cv.content or {}
        personal_info = content.get('personal_info', {})
        bio_data = content.get('bio_data', {})
        
        # Set initial values from content, with fallbacks
        initial_data.update({
            'full_name': personal_info.get('full_name', ''),
            'email': personal_info.get('email', ''),
            'phone_number': personal_info.get('phone_number', ''),
            'address': personal_info.get('address', ''),
            'gender': bio_data.get('gender', ''),
            'nationality': bio_data.get('nationality', ''),
            'personal_profile': content.get('personal_profile', ''),
        })
        
        # Handle date of birth separately due to format conversion
        dob = bio_data.get('date_of_birth')
        if dob:
            try:
                from datetime import datetime
                initial_data['date_of_birth'] = datetime.fromisoformat(dob.replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                initial_data['date_of_birth'] = None
        
        form = CVForm(initial=initial_data, instance=cv)
    
    return render(request, 'documents/cv_create.html', {
        'form': form,
        'template': cv.template,
        'template_id': cv.template.id if cv.template else None,
        'edit_mode': True,
        'cv': cv,
        'work_experience': cv.content.get('work_experience', []),
        'education': cv.content.get('education', []),
        'skills': cv.content.get('skills', []),
        'certifications': cv.content.get('certifications', []),
        'languages': cv.content.get('languages', []),
        'hobbies': cv.content.get('hobbies', []),
        'referees': cv.content.get('referees', [])
    })

@login_required
def cv_delete(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id, user=request.user)
    if request.method == 'POST':
        cv.delete()
        messages.success(request, 'CV deleted successfully!')
    return redirect('documents:cv_list')

@login_required
def cv_download(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id, user=request.user)
    download_format = request.GET.get('format', 'pdf')
    
    if download_format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{cv.title}.pdf"'
        # Generate PDF using your existing generate_pdf function
        generate_pdf(cv, response)
        return response
    elif download_format == 'docx':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{cv.title}.docx"'
        # Generate Word document
        generate_docx(cv, response)
        return response
    else:
        messages.error(request, 'Invalid format specified')
        return redirect('documents:cv_preview', cv_id=cv.id)

@login_required
def cover_letter_create(request):
    if request.method == 'POST':
        form = CoverLetterForm(request.user, request.POST)
        if form.is_valid():
            cover_letter = form.save(commit=False)
            cover_letter.user = request.user
            
            try:
                # Get CV data for the selected CV
                cv = form.cleaned_data['cv']
                personal_info = cv.content.get('personal_info', {})
                
                # Format the current date
                current_date = timezone.now().strftime("%B %d, %Y")
                
                # Generate the cover letter body
                body = generate_cover_letter_body(
                    cv=cv,
                    job_title=form.cleaned_data['job_title'],
                    company_name=form.cleaned_data['company_name']
                )
                
                # Structure the cover letter content
                content = {
                    'company_name': form.cleaned_data['company_name'],
                    'job_title': form.cleaned_data['job_title'],
                    'personal_info': {
                        'full_name': personal_info.get('full_name', ''),
                        'address': personal_info.get('address', ''),
                        'phone': personal_info.get('phone_number', ''),
                        'email': personal_info.get('email', '')
                    },
                    'date': current_date,
                    'body': body
                }
                
                # Store content as JSON string
                cover_letter.content = json.dumps(content)
                cover_letter.save()
                
                messages.success(request, 'Cover letter created successfully!')
                return redirect('documents:cover_letter_preview', cover_letter_id=cover_letter.id)
                
            except Exception as e:
                messages.error(request, f'Error generating cover letter: {str(e)}')
                return redirect('documents:cover_letter_list')
    else:
        form = CoverLetterForm(request.user)
    
    return render(request, 'documents/cover_letter_create.html', {'form': form})

@login_required
def cover_letter_preview(request, cover_letter_id):
    cover_letter = get_object_or_404(CoverLetter, id=cover_letter_id, user=request.user)
    
    try:
        # Convert string content to dictionary if needed
        content = cover_letter.content
        if isinstance(content, str):
            content = json.loads(content)
            
        # Ensure all required content is present
        if not content.get('body'):
            messages.error(request, 'Error: Cover letter content is missing')
            return redirect('documents:cover_letter_list')
        
        # Update cover_letter object with parsed content
        cover_letter.content = content
        
    except (json.JSONDecodeError, AttributeError) as e:
        messages.error(request, 'Error: Invalid cover letter format')
        return redirect('documents:cover_letter_list')
    
    return render(request, 'documents/cover_letter_preview.html', {
        'cover_letter': cover_letter,
    })

@login_required
def cover_letter_list(request):
    cover_letters = CoverLetter.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'documents/cover_letter_list.html', {'cover_letters': cover_letters})

@login_required
def cover_letter_edit(request, cover_letter_id):
    cover_letter = get_object_or_404(CoverLetter, id=cover_letter_id, user=request.user)
    
    if request.method == 'POST':
        form = CoverLetterForm(request.user, request.POST, instance=cover_letter)
        if form.is_valid():
            cover_letter = form.save(commit=False)
            
            # Regenerate content if any field changed
            if (form.cleaned_data['cv'] != cover_letter.cv or 
                form.cleaned_data['job_title'] != cover_letter.job_title or
                form.cleaned_data['company_name'] != cover_letter.company_name or
                form.cleaned_data['company_address'] != cover_letter.company_address):
                
                try:
                    content = generate_cover_letter(
                        form.cleaned_data['cv'],
                        form.cleaned_data['job_title'],
                        form.cleaned_data['company_name']
                    )
                    cover_letter.content = content
                except Exception as e:
                    messages.error(request, 'Error regenerating cover letter content. Please try again.')
                    return render(request, 'documents/cover_letter_edit.html', {'form': form})
            
            cover_letter.save()
            messages.success(request, 'Cover letter updated successfully!')
            return redirect('documents:cover_letter_preview', cover_letter_id=cover_letter.id)
    else:
        form = CoverLetterForm(request.user, instance=cover_letter, initial={
            'cv': cover_letter.cv,
            'company_name': cover_letter.company_name,
            'company_address': cover_letter.company_address,
            'job_title': cover_letter.job_title
        })
    
    return render(request, 'documents/cover_letter_edit.html', {
        'form': form,
        'cover_letter': cover_letter
    })

@login_required
def interview_prep_create(request):
    if request.method == 'POST':
        form = InterviewPrepForm(request.POST)
        if form.is_valid():
            prep = form.save(commit=False)
            prep.user = request.user
            
            # Get interview questions using AI
            job_title = form.cleaned_data['job_title']
            company_name = form.cleaned_data['company_name']
            
            try:
                questions = get_interview_questions(job_title, company_name)
                prep.save()  # Save before adding many-to-many relationship
                prep.questions.set(questions)
                messages.success(request, 'Interview preparation created successfully!')
                return redirect('documents:interview_prep_detail', prep_id=prep.id)
            except Exception as e:
                messages.error(request, str(e))
                return render(request, 'documents/interview_prep.html', {'form': form})
    else:
        form = InterviewPrepForm()
    
    return render(request, 'documents/interview_prep.html', {'form': form})

@login_required
def interview_prep_detail(request, prep_id):
    prep = get_object_or_404(InterviewPrep, id=prep_id, user=request.user)
    questions = prep.questions.all()
    return render(request, 'documents/interview_prep_detail.html', {
        'prep': prep,
        'questions': questions
    })

@login_required
def interview_prep_list(request):
    preps = InterviewPrep.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'documents/interview_prep_list.html', {'preps': preps})

@login_required
def interview_prep_delete(request, prep_id):
    prep = get_object_or_404(InterviewPrep, id=prep_id, user=request.user)
    
    if request.method == 'POST':
        # Delete associated questions first
        prep.questions.all().delete()
        prep.delete()
        messages.success(request, 'Interview preparation deleted successfully!')
    
    return redirect('documents:interview_prep_list')

@login_required
def interview_prep_edit(request, prep_id):
    prep = get_object_or_404(InterviewPrep, id=prep_id, user=request.user)
    
    if request.method == 'POST':
        form = InterviewPrepForm(request.POST, instance=prep)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interview preparation updated successfully!')
            return redirect('documents:interview_prep_detail', prep_id=prep.id)
    else:
        form = InterviewPrepForm(instance=prep)
    
    return render(request, 'documents/interview_prep.html', {'form': form, 'edit_mode': True})

@login_required
def document_manager(request):
    # Get all folders for the user
    folders = DocumentFolder.objects.filter(user=request.user)
    
    # Get all documents for the user, ordered by upload date
    documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')
    
    context = {
        'folders': folders,
        'documents': documents,
        'current_folder': None
    }
    
    return render(request, 'documents/document_manager.html', context)

@login_required
def folder_view(request, folder_id):
    # Get the current folder
    folder = get_object_or_404(DocumentFolder, id=folder_id, user=request.user)
    
    # Get all folders for the sidebar
    folders = DocumentFolder.objects.filter(user=request.user)
    
    # Get documents in this folder
    documents = Document.objects.filter(
        user=request.user,
        folder=folder
    ).order_by('-uploaded_at')
    
    context = {
        'folders': folders,
        'documents': documents,
        'current_folder': folder
    }
    
    return render(request, 'documents/document_manager.html', context)

@login_required
def folder_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        parent_id = request.POST.get('parent')
        
        try:
            folder = DocumentFolder(
                user=request.user,
                name=name,
                description=description
            )
            if parent_id:
                folder.parent = get_object_or_404(DocumentFolder, id=parent_id, user=request.user)
            folder.save()
            messages.success(request, 'Folder created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating folder: {str(e)}')
    
    return redirect('documents:document_manager')

@login_required
def document_upload(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        document_type = request.POST.get('document_type')
        uploaded_file = request.FILES.get('document')
        
        if not all([title, document_type, uploaded_file]):
            messages.error(request, 'Please fill all required fields')
            return redirect('documents:document_manager')
        
        # Create document
        document = Document.objects.create(
            user=request.user,
            title=title,
            document_type=document_type,
            file=uploaded_file
        )
        
        try:
            # Extract content based on file type
            content = extract_document_content(document)
            if content:
                document.content = content
                document.is_parsed = True
                document.save()
                messages.success(request, 'Document uploaded and parsed successfully!')
            else:
                messages.warning(request, 'Document uploaded but content could not be parsed')
        except Exception as e:
            messages.error(request, f'Error parsing document: {str(e)}')
        
        return redirect('documents:document_manager')
    
    return redirect('documents:document_manager')

def extract_document_content(document):
    """Extract content from uploaded document."""
    file_path = document.file.path
    content = {}
    
    if file_path.endswith('.docx'):
        text = docx2txt.process(file_path)
    elif file_path.endswith('.pdf'):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
    else:
        return None
    
    # Parse content based on document type
    if document.document_type == 'cv':
        content = parse_cv_content(text)
    elif document.document_type == 'cover_letter':
        content = parse_cover_letter_content(text)
    
    return content

def parse_cv_content(text):
    """Parse CV content into structured format."""
    content = {
        'personal_info': {},
        'work_experience': [],
        'education': [],
        'skills': [],
        'languages': [],
        'referees': []
    }
    
    # Extract personal info (example patterns)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b(?:\+\d{1,3}[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b'
    
    # Find email
    email_match = re.search(email_pattern, text)
    if email_match:
        content['personal_info']['email'] = email_match.group()
    
    # Find phone number
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        content['personal_info']['phone_number'] = phone_match.group()
    
    # Add more parsing logic for other sections
    # This is a basic example - you might want to use more sophisticated parsing
    
    return content

@login_required
def convert_to_template(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    if request.method == 'POST':
        template_id = request.POST.get('template')
        if not template_id:
            messages.error(request, 'Please select a template')
            return redirect('documents:document_detail', document_id=document_id)
        
        template = get_object_or_404(CVTemplate, id=template_id)
        
        try:
            # Ensure proper content structure
            content = document.content or {}
            if not isinstance(content, dict):
                content = {}
            
            # Create basic CV structure if missing
            cv_content = {
                'personal_info': content.get('personal_info', {}),
                'bio_data': content.get('bio_data', {}),
                'personal_profile': content.get('personal_profile', ''),
                'work_experience': content.get('work_experience', []),
                'education': content.get('education', []),
                'skills': content.get('skills', []),
                'certifications': content.get('certifications', []),
                'languages': content.get('languages', []),
                'hobbies': content.get('hobbies', []),
                'referees': content.get('referees', [])
            }
            
            # Create new CV from uploaded document
            cv = CV.objects.create(
                user=request.user,
                title=f"{document.title} (Converted)",
                template=template,
                content=cv_content
            )
            
            messages.success(request, 'Document converted to CV successfully!')
            return redirect('documents:cv_edit', cv_id=cv.id)
            
        except Exception as e:
            messages.error(request, f'Error converting document: {str(e)}')
            return redirect('documents:document_detail', document_id=document_id)
    
    templates = CVTemplate.objects.filter(is_active=True)
    return render(request, 'documents/convert_to_template.html', {
        'document': document,
        'templates': templates
    })

@login_required
def document_move(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    if request.method == 'POST':
        folder_id = request.POST.get('folder')
        try:
            if folder_id:
                document.folder = get_object_or_404(DocumentFolder, id=folder_id, user=request.user)
            else:
                document.folder = None
            document.save()
            messages.success(request, 'Document moved successfully!')
        except Exception as e:
            messages.error(request, f'Error moving document: {str(e)}')
    
    return redirect('documents:document_manager')

@login_required
def document_delete(request, document_id):
    if request.method == 'POST':
        document = get_object_or_404(Document, id=document_id, user=request.user)
        try:
            # Delete the actual file
            if document.file:
                document.file.delete()
            # Delete the document record
            document.delete()
            messages.success(request, 'Document deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting document: {str(e)}')
    
    return redirect('documents:document_manager')

@login_required
def cover_letter_download(request, cover_letter_id):
    cover_letter = get_object_or_404(CoverLetter, id=cover_letter_id, user=request.user)
    format = request.GET.get('format', 'pdf')
    
    if format == 'pdf':
        buffer = generate_cover_letter_pdf(cover_letter)
        return FileResponse(
            buffer, 
            as_attachment=True, 
            filename=f'cover_letter_{cover_letter.company_name}.pdf'
        )
    elif format == 'docx':
        buffer = generate_cover_letter_docx(cover_letter)
        return FileResponse(
            buffer, 
            as_attachment=True, 
            filename=f'cover_letter_{cover_letter.company_name}.docx'
        )
    
    return HttpResponse('Invalid format specified')

@login_required
def cover_letter_delete(request, cover_letter_id):
    cover_letter = get_object_or_404(CoverLetter, id=cover_letter_id, user=request.user)
    
    if request.method == 'POST':
        cover_letter.delete()
        messages.success(request, 'Cover letter deleted successfully!')
    else:
        messages.error(request, 'Invalid request method.')
    
    return redirect('documents:cover_letter_list') 