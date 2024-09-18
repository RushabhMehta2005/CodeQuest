from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import Problem, TestCase, Submission, Tag
from django.core.serializers import serialize
import json


@login_required(login_url="/auth/login")
def home(request):
    query = request.GET.get('query', '')
    selected_difficulty = request.GET.get('difficulty', '')
    selected_tags = request.GET.getlist('tags')
    
    problems = Problem.objects.all()

    if query:
        problems = (problems.filter(title__icontains=query) | problems.filter(description__icontains=query))

    if selected_difficulty:
        problems = problems.filter(difficulty=selected_difficulty)

    if selected_tags:
        for selected_tag in selected_tags:
            problems = problems.filter(tags__id=selected_tag)

    paginator = Paginator(problems, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'Quest/home.html', {
        'page_obj': page_obj,
        'query': query,
        'selected_difficulty': selected_difficulty,
        'all_tags': Tag.objects.all(),
        'selected_tags': selected_tags
    })


@login_required(login_url="/auth/login")
def problem_submit(request, id):
    try:
        problem = Problem.objects.get(pk=id)
    except Problem.DoesNotExist:
        messages.error(request, "Problem not found.")
        return redirect(reverse('Quest:home'))

    initial_code = f"""
class Solution:
    def {problem.function_name}(self, {problem.function_args}):
        # Write your code here
        pass
"""
    submissions = Submission.objects.filter(problem=problem, user=request.user)
    submissions_data = [
        {
            'user': submission.user.username,
            'problem': submission.problem.title,
            'code': submission.code,
            'submitted_at': submission.submitted_at.strftime("%Y-%m-%d%H:%M:%S"),
            'correct': submission.correct,
        }
        for submission in submissions
    ]
    return render(request, "Quest/submit.html", {
        "problem": problem,
        "initial_code": initial_code,
        "submissions_json": json.dumps(submissions_data),
    })


@login_required(login_url="/auth/login")
def problem_by_tag(request, id):
    tag = get_object_or_404(Tag, id=id)

    problems = Problem.objects.filter(tags=tag)

    total_easy = problems.filter(difficulty=1).count()  # Easy
    total_medium = problems.filter(difficulty=2).count()  # Medium
    total_hard = problems.filter(difficulty=3).count()  # Hard

    solved_easy = problems.filter(difficulty=1, submissions__user=request.user, submissions__correct=True).distinct().count()
    solved_medium = problems.filter(difficulty=2, submissions__user=request.user, submissions__correct=True).distinct().count()
    solved_hard = problems.filter(difficulty=3, submissions__user=request.user, submissions__correct=True).distinct().count()

    easy_percentage = (solved_easy / total_easy * 100) if total_easy > 0 else 0
    medium_percentage = (solved_medium / total_medium * 100) if total_medium > 0 else 0
    hard_percentage = (solved_hard / total_hard * 100) if total_hard > 0 else 0

    context = {
        'tag': tag,
        'problems': problems,
        'solved_easy': solved_easy,
        'total_easy': total_easy,
        'easy_percentage': easy_percentage,
        'solved_medium': solved_medium,
        'total_medium': total_medium,
        'medium_percentage': medium_percentage,
        'solved_hard': solved_hard,
        'total_hard': total_hard,
        'hard_percentage': hard_percentage,
    }
    return render(request, 'Quest/tags.html', context)
