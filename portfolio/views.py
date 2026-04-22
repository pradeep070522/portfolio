from django.shortcuts import render
from .models import Profile, Skill, SkillCategory, Project, Certificate, ProfilePhoto


def index(request):
    profile = Profile.objects.first()

    # Two separate photos for hero and about sections
    hero_photo  = None
    about_photo = None
    if profile:
        try:
            hero_photo  = profile.photos.get(slot='hero')
        except ProfilePhoto.DoesNotExist:
            pass
        try:
            about_photo = profile.photos.get(slot='about')
        except ProfilePhoto.DoesNotExist:
            pass

    skill_categories    = SkillCategory.objects.prefetch_related('skills').all()
    uncategorised_skills= Skill.objects.filter(category__isnull=True, is_featured=True)
    projects            = Project.objects.filter(is_featured=True)
    certificates        = (
        Certificate.objects.filter(is_featured=True)
        if profile and profile.show_certificates
        else Certificate.objects.none()
    )

    return render(request, 'portfolio/index.html', {
        'profile':              profile,
        'hero_photo':           hero_photo,
        'about_photo':          about_photo,
        'skill_categories':     skill_categories,
        'uncategorised_skills': uncategorised_skills,
        'projects':             projects,
        'certificates':         certificates,
    })
