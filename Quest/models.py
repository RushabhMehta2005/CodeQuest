from django.db import models
from custom_auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Problem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.IntegerField(default=1) # 1, 2, 3 for easy, medium, hard
    function_name = models.CharField(max_length=255)
    function_args = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    editorial = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='problems')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title
    
class TestCase(models.Model):
    problem = models.ForeignKey(Problem, related_name='testcases', on_delete=models.CASCADE)
    input_data = models.TextField() # Store as JSON, for testcases
    input_data_to_display = models.TextField() # Human readable input
    explanation = models.TextField() # Explanation of input and expected output
    expected_output_data = models.TextField()

    def __str__(self):
        return f"Testcase {self.input_data} for {self.problem}."
    

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, related_name='submissions', on_delete=models.CASCADE)
    code = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    correct = models.BooleanField()

    def __str__(self):
        return f"{self.user} submitted {self.problem} on {self.submitted_at}."
