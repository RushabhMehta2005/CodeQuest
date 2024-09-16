from rest_framework import serializers
from Quest.models import Problem, TestCase, Submission


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = '__all__'

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'

class ProblemSerializer(serializers.ModelSerializer):
    testcases = TestCaseSerializer(many=True, read_only=True)
    submissions = SubmissionSerializer(many=True, read_only=True)

    class Meta:
        model = Problem
        fields = '__all__'
