from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Course, Enrollment, Question, Choice, Submission


def index(request):
    courses = Course.objects.all()
    return render(request, 'OnlineCourse/course_list_bootstrap.html', {'course_list': courses})


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'OnlineCourse/course_details_bootstrap.html', {'course': course})


def extract_answers(request):
    submitted_choices = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            submitted_choices.append(int(value))
    return submitted_choices


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)

    submitted_choice_ids = extract_answers(request)
    selected_choices = Choice.objects.filter(id__in=submitted_choice_ids)
    submission.choices.set(selected_choices)
    submission.save()

    return HttpResponseRedirect(
        reverse('OnlineCourse:show_exam_result', args=(course.id, submission.id))
    )


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    selected_choice_ids = submission.choices.values_list('id', flat=True)

    lessons = course.lessons.all()
    total_score = 0

    for lesson in lessons:
        questions = lesson.questions.all()
        for question in questions:
            if question.is_get_score(selected_choice_ids):
                total_score += question.question_grade

    context = {'course': course, 'grade': total_score}
    return render(request, 'OnlineCourse/exam_result_bootstrap.html', context)