from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Quest.models import *
from django.db.models import Count

@login_required(login_url="/auth/login")
def profile(request):
    user = request.user
    
    solved_problems_count = Submission.objects.filter(user=user, correct=True).values('problem').distinct().count()
    
    submissions_count = Submission.objects.filter(user=user).count()
    
    skilled_topics = Tag.objects.filter(
        problems__submissions__user=user, 
        problems__submissions__correct=True
    ).annotate(solved_count=Count('problems__submissions')).order_by('-solved_count')[:5]  # Top 5 tags
    
    recent_submissions = Submission.objects.filter(user=user).order_by('-submitted_at')[:5]

    
    return render(request, "user_profile/profile.html", {
                    'user': user,
                    'solved_problems_count': solved_problems_count,
                    'submissions_count': submissions_count,
                    'skilled_topics': skilled_topics,
                    'recent_submissions': recent_submissions,
                })
