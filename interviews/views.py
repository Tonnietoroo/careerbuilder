from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Industry, InterviewQuestion, InterviewPrep
from .forms import InterviewPrepForm, QuestionForm, IndustryForm
from .utils import get_interview_questions

@login_required
def interview_list(request):
    interviews = InterviewPrep.objects.filter(user=request.user).order_by('-interview_date')
    return render(request, 'interviews/interview_list.html', {'interviews': interviews})

@login_required
def interview_create(request):
    if request.method == 'POST':
        form = InterviewPrepForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.user = request.user
            interview.save()
            
            # Generate questions based on industry and job title
            questions = get_interview_questions(
                job_category=form.cleaned_data['industry'],
                job_title=form.cleaned_data['job_title']
            )
            
            # Add all generated questions to the interview prep
            if questions:
                interview.questions.add(*questions)
            
            messages.success(request, 'Interview preparation created successfully!')
            return redirect('interviews:interview_detail', interview_id=interview.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InterviewPrepForm()
    
    return render(request, 'interviews/interview_form.html', {
        'form': form,
        'industries': Industry.objects.all()
    })

@login_required
def interview_detail(request, interview_id):
    interview = get_object_or_404(InterviewPrep, id=interview_id, user=request.user)
    questions = interview.questions.all()  # Get all questions
    return render(request, 'interviews/interview_detail.html', {
        'interview': interview,
        'questions': questions
    })

@login_required
def interview_edit(request, interview_id):
    interview = get_object_or_404(InterviewPrep, id=interview_id, user=request.user)
    if request.method == 'POST':
        form = InterviewPrepForm(request.POST, instance=interview)
        if form.is_valid():
            form.save()  # Works correctly with DateTimeField now
            messages.success(request, 'Interview preparation updated successfully!')
            return redirect('interviews:interview_detail', interview_id=interview.id)
    else:
        form = InterviewPrepForm(instance=interview)
    return render(request, 'interviews/interview_form.html', {'form': form})

@login_required
def interview_delete(request, interview_id):
    interview = get_object_or_404(InterviewPrep, id=interview_id, user=request.user)
    if request.method == 'POST':
        interview.delete()
        messages.success(request, 'Interview preparation deleted successfully!')
        return redirect('interviews:interview_list')
    return render(request, 'interviews/interview_confirm_delete.html', {'interview': interview})

@login_required
def question_list(request):
    questions = InterviewQuestion.objects.all()
    return render(request, 'interviews/question_list.html', {'questions': questions})

@login_required
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question added successfully!')
            return redirect('interviews:question_list')
    else:
        form = QuestionForm()
    return render(request, 'interviews/question_form.html', {'form': form})

@login_required
def question_edit(request, question_id):
    question = get_object_or_404(InterviewQuestion, id=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('interviews:question_list')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'interviews/question_form.html', {'form': form})

@login_required
def question_delete(request, question_id):
    question = get_object_or_404(InterviewQuestion, id=question_id)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('interviews:question_list')
    return render(request, 'interviews/question_confirm_delete.html', {'question': question})

@login_required
def industry_list(request):
    industries = Industry.objects.all()
    return render(request, 'interviews/industry_list.html', {'industries': industries})

@login_required
def industry_create(request):
    if request.method == 'POST':
        form = IndustryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Industry added successfully!')
            return redirect('interviews:industry_list')
    else:
        form = IndustryForm()
    return render(request, 'interviews/industry_form.html', {'form': form})

@login_required
def industry_edit(request, industry_id):
    industry = get_object_or_404(Industry, id=industry_id)
    if request.method == 'POST':
        form = IndustryForm(request.POST, instance=industry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Industry updated successfully!')
            return redirect('interviews:industry_list')
    else:
        form = IndustryForm(instance=industry)
    return render(request, 'interviews/industry_form.html', {'form': form})

@login_required
def industry_delete(request, industry_id):
    industry = get_object_or_404(Industry, id=industry_id)
    if request.method == 'POST':
        industry.delete()
        messages.success(request, 'Industry deleted successfully!')
        return redirect('interviews:industry_list')
    return render(request, 'interviews/industry_confirm_delete.html', {'industry': industry})
