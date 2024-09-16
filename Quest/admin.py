from django.contrib import admin
from .models import Problem, TestCase, Submission, Tag

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'function_name', 'function_args')
    search_fields = ('title', 'function_name')

admin.site.register(Problem, ProblemAdmin)
admin.site.register(TestCase)
admin.site.register(Submission)
admin.site.register(Tag)
