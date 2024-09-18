from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from Quest.models import Problem, TestCase, Submission
from .serializers import ProblemSerializer, SubmissionSerializer
import requests
import json

JUDGE0_API_URL = "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true"

RAPIDAPI_HEADERS = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "cb713ba37cmsh56be9d7d92a3161p167cefjsn100249c5b326",
    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
}


class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer


    @action(detail=True, methods=['POST'])
    def submit_solution(self, request, pk=None):
        problem = self.get_object()
        solution_code = request.data.get('solution', "")
        testcases = problem.testcases.all()
        function_name = problem.function_name
        function_args = problem.function_args

        passed_all_testcases = True
        results = []

        for testcase in testcases:
            full_code = self.generate_full_code(solution_code, function_name, testcase.input_data)

            actual_output, error, judge0_response = self.run_solution_with_judge0(full_code)

            if error:
                # Return the error response immediately if there's an issue
                return Response([{"error": error, "judge0_response": judge0_response}, {"all_correct": False}], status=status.HTTP_200_OK)

            is_correct = (actual_output.strip() == str(testcase.expected_output_data).strip())
            if not is_correct:
                passed_all_testcases = False

            results.append({
                'input': testcase.input_data_to_display,
                'expected_output': testcase.expected_output_data,
                'actual_output': actual_output,
                'correct': is_correct,
                'judge0_response': judge0_response
            })

        self.add_submission(request.user, problem, solution_code, passed_all_testcases)

        all_correct = {"all_correct": passed_all_testcases}
        return Response([*results, all_correct], status=status.HTTP_200_OK)


    def generate_full_code(self, solution_code, function_name, input_data):
        """
        Generate the full Python code for execution including the solution function 
        and input data.
        """
        solution_code = solution_code.replace('\t', '    ')
        return f"""
{solution_code}

if __name__ == "__main__":
    soln = Solution()
    input_args = {input_data}
    print(soln.{function_name}(*input_args))
        """

    def run_solution_with_judge0(self, full_code):
        """
        Send the full solution code to the Judge0 API and handle the response.
        """
        payload = {
            "source_code": full_code,
            "language_id": 71, # Language ID for Python
            "stdin": "",
            "cpu_time_limit": "5",
            "memory_limit": "10240", # 10 MB
        }

        try:
            response = requests.post(JUDGE0_API_URL, data=json.dumps(payload), headers=RAPIDAPI_HEADERS)
            response_data = response.json()

            if response.status_code != 200:
                return None, f"Error: {response_data.get('message', 'Unknown error')}", response_data

            status_id = response_data.get('status', {}).get('id')
            if status_id == 6:  # Compilation error
                return None, f"Compilation Error: {response_data.get('compile_output', 'Unknown compilation error')}", response_data
            elif status_id == 5:  # Time Limit Exceeded
                return None, f"Time Limit Exceeded", response_data
            elif status_id == 7:  # Runtime Error
                return None, f"Runtime Error: {response_data.get('stderr', 'Unknown runtime error')}", response_data
            elif status_id == 3:  # Accepted (successful run)
                return response_data.get('stdout', '').strip(), None, response_data
            else:
                return None, "Unknown Status", response_data

        except Exception as e:
            return None, str(e), None

    def add_submission(self, user, problem, code, correct):
        """
        Store the user's submission result in the database.
        """
        Submission.objects.create(user=user, problem=problem, code=code, correct=correct)


class ProblemSubmissionsView(generics.ListAPIView):
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        problem_id = self.kwargs['pk']
        user = self.kwargs['user']
        return Submission.objects.filter(problem_id=problem_id, user=user).order_by('-submitted_at')
