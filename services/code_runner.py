import ast
import os
import sys
import tempfile
import time
import subprocess

FORBIDDEN_MODULES = {
    'os', 'sys', 'subprocess', 'shutil', 'socket', 'requests', 'urllib',
    'builtins', 'posix', 'nt', 'pty', 'pathlib', 'ctypes', 'fcntl',
    'winreg', 'msvcrt', 'multiprocessing', 'threading', 'asyncio'
}

FORBIDDEN_CALLS = {'exec', 'eval', 'compile', 'open', '__import__'}

class SecurityValidator(ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_Import(self, node):
        for alias in node.names:
            base_module = alias.name.split('.')[0]
            if base_module in FORBIDDEN_MODULES:
                self.errors.append(f"Importing '{base_module}' is restricted for security.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            base_module = node.module.split('.')[0]
            if base_module in FORBIDDEN_MODULES:
                self.errors.append(f"Importing from '{base_module}' is restricted for security.")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
            self.errors.append(f"Call to '{node.func.id}()' is restricted for security.")
        self.generic_visit(node)

def validate_code_safety(code_str: str):
    """Parses code AST to ensure no dangerous operations or imports."""
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return False, f"Syntax Error: {e.msg} on line {e.lineno}"

    validator = SecurityValidator()
    validator.visit(tree)

    if validator.errors:
        return False, "; ".join(validator.errors)

    return True, None

def run_test_case_subprocess(code: str, test_input: str, timeout_sec: float = 2.5):
    """
    Executes Python code in an isolated subprocess with stdin and timeout.
    Returns: (stdout, stderr, exit_code, runtime_ms, error_msg)
    """
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        temp_filepath = f.name

    start_time = time.time()
    try:
        # Run using current python interpreter in isolated mode (-I -S -u)
        # -I: isolate python, ignore environment variables and user site
        # -u: unbuffered binary stdout/stderr
        proc = subprocess.run(
            [sys.executable, '-u', temp_filepath],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        runtime_ms = round((time.time() - start_time) * 1000, 2)
        return proc.stdout, proc.stderr, proc.returncode, runtime_ms, None
    except subprocess.TimeoutExpired:
        runtime_ms = round(timeout_sec * 1000, 2)
        return "", "", -1, runtime_ms, f"Time Limit Exceeded ({timeout_sec}s)"
    except Exception as e:
        runtime_ms = round((time.time() - start_time) * 1000, 2)
        return "", "", 1, runtime_ms, str(e)
    finally:
        try:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
        except OSError:
            pass

def execute_coding_submission(code: str, test_cases: list, timeout_sec: float = 2.5):
    """
    Validates code safety and executes against each test case.
    test_cases: [{'input': '...', 'expected': '...', 'is_hidden': bool}, ...]
    Returns dict:
      {
         'result_status': 'Accepted' | 'Wrong Answer' | 'Time Limit Exceeded' | 'Runtime Error' | 'Security Error',
         'test_cases_passed': int,
         'test_cases_total': int,
         'runtime_ms': float,
         'error_message': str,
         'test_results': [ ... ]
      }
    """
    # 1. Security Check
    is_safe, sec_err = validate_code_safety(code)
    if not is_safe:
        return {
            'result_status': 'Security Error',
            'test_cases_passed': 0,
            'test_cases_total': len(test_cases),
            'runtime_ms': 0.0,
            'error_message': sec_err,
            'test_results': []
        }

    passed_count = 0
    total_count = len(test_cases)
    total_runtime = 0.0
    detailed_results = []
    overall_status = 'Accepted'
    first_error = None

    for idx, tc in enumerate(test_cases):
        test_in = str(tc.get('input', ''))
        expected_out = str(tc.get('expected', '')).strip()
        is_hidden = tc.get('is_hidden', False)

        stdout, stderr, code_ret, tc_runtime, err_msg = run_test_case_subprocess(
            code, test_in, timeout_sec=timeout_sec
        )
        total_runtime += tc_runtime

        actual_out = stdout.strip()

        if err_msg and "Time Limit Exceeded" in err_msg:
            passed = False
            tc_status = 'Time Limit Exceeded'
            if overall_status == 'Accepted':
                overall_status = 'Time Limit Exceeded'
                first_error = f"Test Case {idx + 1}: Execution exceeded time limit."
        elif code_ret != 0 or stderr:
            passed = False
            tc_status = 'Runtime Error'
            if overall_status == 'Accepted':
                overall_status = 'Runtime Error'
                clean_err = stderr.splitlines()[-1] if stderr.splitlines() else "Runtime Error"
                first_error = f"Test Case {idx + 1}: {clean_err}"
        elif actual_out == expected_out:
            passed = True
            passed_count += 1
            tc_status = 'Passed'
        else:
            passed = False
            tc_status = 'Wrong Answer'
            if overall_status == 'Accepted':
                overall_status = 'Wrong Answer'
                first_error = f"Test Case {idx + 1}: Expected '{expected_out}' but got '{actual_out}'"

        detailed_results.append({
            'test_case_number': idx + 1,
            'status': tc_status,
            'passed': passed,
            'input': test_in if not is_hidden else "[Hidden Test Case]",
            'expected': expected_out if not is_hidden else "[Hidden Test Case]",
            'actual': actual_out if not is_hidden else ("[Matches Expected]" if passed else "[Incorrect Output]"),
            'runtime_ms': tc_runtime,
            'is_hidden': is_hidden
        })

    avg_runtime = round(total_runtime / max(1, total_count), 2)

    return {
        'result_status': overall_status,
        'test_cases_passed': passed_count,
        'test_cases_total': total_count,
        'runtime_ms': avg_runtime,
        'error_message': first_error,
        'test_results': detailed_results
    }
