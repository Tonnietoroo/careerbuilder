from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from .models import CV, CoverLetter, InterviewPrep, InterviewQuestion, JobCategory, DocumentFolder, Document
from .forms import CVForm, CoverLetterForm, InterviewPrepForm
from .utils import generate_pdf, generate_docx, generate_cover_letter, get_interview_questions, generate_cover_letter_pdf, generate_cover_letter_docx
import json
import openai
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def cv_list(request):
    cvs = CV.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'documents/cv_list.html', {'cvs': cvs})

@login_required
def cv_create(request):
    if request.method == 'POST':
        form = CVForm(request.POST)
        if form.is_valid():
            cv = form.save(commit=False)
            cv.user = request.user
            
            # Debug print
            print("POST Data:", request.POST)
            
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
                    'date_of_birth': form.cleaned_data['date_of_birth'].isoformat(),
                    'nationality': form.cleaned_data['nationality'],
                },
                'personal_profile': form.cleaned_data['personal_profile'],
                'work_experience': [],
                'education': [],
                'skills': [],
                'certifications': [],
                'languages': [],
                'hobbies': []
            }

            # Debug prints for dynamic data
            print("Work Experience Data:", list(zip(
                request.POST.getlist('job_title[]'),
                request.POST.getlist('company_name[]'),
                request.POST.getlist('work_location[]'),
                request.POST.getlist('work_start_date[]'),
                request.POST.getlist('work_end_date[]'),
                request.POST.getlist('work_responsibilities[]')
            )))

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

            # Debug print final CV data
            print("Final CV Data:", cv_data)

            cv.content = cv_data
            cv.save()

            messages.success(request, 'CV created successfully!')
            return redirect('documents:cv_preview', cv_id=cv.id)
        else:
            messages.error(request, 'Please correct the errors below.')
            print("Form Errors:", form.errors)
    else:
        form = CVForm()

    return render(request, 'documents/cv_create.html', {
        'form': form
    })

@login_required
def cv_preview(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id, user=request.user)
    context = {
        'cv': cv,
        'personal_info': cv.content.get('personal_info', {}),
        'bio_data': cv.content.get('bio_data', {}),
        'personal_profile': cv.content.get('personal_profile', ''),
        'work_experience': cv.content.get('work_experience', []),
        'education': cv.content.get('education', []),
        'skills': cv.content.get('skills', []),
        'certifications': cv.content.get('certifications', []),
        'languages': cv.content.get('languages', []),
        'hobbies': cv.content.get('hobbies', [])
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
                    'date_of_birth': form.cleaned_data['date_of_birth'].isoformat(),
                    'nationality': form.cleaned_data['nationality'],
                },
                'personal_profile': form.cleaned_data['personal_profile'],
                'work_experience': [],
                'education': [],
                'skills': [],
                'certifications': [],
                'languages': [],
                'hobbies': []
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

            cv.content = cv_data
            cv.save()
            messages.success(request, 'CV updated successfully!')
            return redirect('documents:cv_preview', cv_id=cv.id)
    else:
        # Pre-populate form with existing data
        initial_data = {
            'title': cv.title,
            'full_name': cv.content['personal_info']['full_name'],
            'email': cv.content['personal_info']['email'],
            'phone_number': cv.content['personal_info']['phone_number'],
            'address': cv.content['personal_info']['address'],
            'gender': cv.content['bio_data']['gender'],
            'date_of_birth': cv.content['bio_data']['date_of_birth'].split('T')[0],  # Get date part only
            'nationality': cv.content['bio_data']['nationality'],
            'personal_profile': cv.content['personal_profile'],
        }
        form = CVForm(initial=initial_data)

    return render(request, 'documents/cv_edit.html', {
        'form': form,
        'cv': cv,
        'work_experience': cv.content.get('work_experience', []),
        'education': cv.content.get('education', []),
        'skills': cv.content.get('skills', []),
        'certifications': cv.content.get('certifications', []),
        'languages': cv.content.get('languages', []),
        'hobbies': cv.content.get('hobbies', [])
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
    format = request.GET.get('format', 'pdf')
    
    if format == 'pdf':
        buffer = generate_pdf(cv)
        return FileResponse(
            buffer, 
            as_attachment=True, 
            filename=f'{cv.title}.pdf'
        )
    elif format == 'docx':
        buffer = generate_docx(cv)
        return FileResponse(
            buffer, 
            as_attachment=True, 
            filename=f'{cv.title}.docx'
        )
    
    return HttpResponse('Invalid format specified')

@login_required
def cover_letter_create(request):
    if request.method == 'POST':
        form = CoverLetterForm(request.user, request.POST)
        if form.is_valid():
            cover_letter = form.save(commit=False)
            cover_letter.user = request.user
            
            # Generate the cover letter content
            content = generate_cover_letter(
                cv=form.cleaned_data['cv'],
                job_title=form.cleaned_data['job_title'],
                company_name=form.cleaned_data['company_name']
            )
            
            cover_letter.content = content
            cover_letter.save()
            
            messages.success(request, 'Cover letter created successfully!')
            return redirect('documents:cover_letter_preview', cover_letter_id=cover_letter.id)
    else:
        form = CoverLetterForm(request.user)
    
    return render(request, 'documents/cover_letter_create.html', {'form': form})

@login_required
def cover_letter_preview(request, cover_letter_id):
    cover_letter = get_object_or_404(CoverLetter, id=cover_letter_id, user=request.user)
    return render(request, 'documents/cover_letter_preview.html', {'cover_letter': cover_letter})

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
    folders = DocumentFolder.objects.filter(user=request.user)
    current_folder = None
    doc_type = request.GET.get('type')
    sort = request.GET.get('sort', 'date')
    
    # Get current folder if specified
    folder_id = request.GET.get('folder')
    if folder_id:
        current_folder = get_object_or_404(DocumentFolder, id=folder_id, user=request.user)
    
    # Build document query
    documents = Document.objects.filter(user=request.user)
    if current_folder:
        documents = documents.filter(folder=current_folder)
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    # Apply sorting
    if sort == 'name':
        documents = documents.order_by('title')
    elif sort == 'type':
        documents = documents.order_by('document_type', '-created_at')
    else:  # date
        documents = documents.order_by('-created_at')
    
    # Add search functionality
    search_query = request.GET.get('search')
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__contains=search_query)
        )
    
    # Add pagination
    paginator = Paginator(documents, 12)  # Show 12 documents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'folders': folders,
        'current_folder': current_folder,
        'documents': page_obj,
        'doc_type': doc_type,
        'search_query': search_query,
        'page_obj': page_obj,
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
        try:
            document = Document(user=request.user)
            document.title = request.POST.get('title')
            document.document_type = request.POST.get('document_type')
            document.description = request.POST.get('description')
            
            # Handle file upload
            document.file = request.FILES['file']
            
            # Handle tags
            tags = request.POST.get('tags', '').split(',')
            document.tags = [tag.strip() for tag in tags if tag.strip()]
            
            # Handle folder
            folder_id = request.POST.get('folder')
            if folder_id:
                document.folder = get_object_or_404(DocumentFolder, id=folder_id, user=request.user)
            
            document.save()
            messages.success(request, 'Document uploaded successfully!')
        except Exception as e:
            messages.error(request, f'Error uploading document: {str(e)}')
    
    return redirect('documents:document_manager')

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
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    if request.method == 'POST':
        try:
            document.delete()
            messages.success(request, 'Document deleted successfully!')
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