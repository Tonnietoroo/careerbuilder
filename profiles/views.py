from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Skill, Education, WorkExperience
from .forms import ProfileForm, EducationForm, WorkExperienceForm
from django.http import JsonResponse

@login_required
def profile_view(request):
    profile = Profile.objects.get_or_create(user=request.user)[0]
    education = Education.objects.filter(profile=profile)
    experience = WorkExperience.objects.filter(profile=profile)
    
    context = {
        'profile': profile,
        'education': education,
        'experience': experience,
    }
    return render(request, 'profiles/profile_view.html', context)

@login_required
def profile_edit(request):
    profile = Profile.objects.get_or_create(user=request.user)[0]
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profiles:profile_view')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'profiles/profile_edit.html', {'form': form})

@login_required
def add_education(request):
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.profile = request.user.profile
            education.save()
            return redirect('profiles:profile_view')
    else:
        form = EducationForm()
    
    return render(request, 'profiles/education_form.html', {'form': form})

@login_required
def add_experience(request):
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.profile = request.user.profile
            experience.save()
            return redirect('profiles:profile_view')
    else:
        form = WorkExperienceForm()
    
    return render(request, 'profiles/experience_form.html', {'form': form})

@login_required
def endorse_skill(request, profile_id, skill_id):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, id=profile_id)
        skill = get_object_or_404(Skill, id=skill_id)
        
        # Check if already endorsed
        if not profile.skillendorsement_set.filter(endorsed_by=request.user, skill=skill).exists():
            profile.skillendorsement_set.create(
                skill=skill,
                endorsed_by=request.user
            )
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})
