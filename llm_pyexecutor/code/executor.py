import ast
import astor
import subprocess
from ..code.exceptions import CodeExecutionError


class PythonCodeExecutor:
    """A class to execute Python code in a controlled environment.

    This class provides functionality to clean and execute Python code
    using a specified virtual environment executor.

    Attributes
    ----------
    None
    """

    def __init__(self) -> None:
        """Initializes the PythonCodeExecutor instance."""
        pass

    @staticmethod
    def _clean_code(code: str) -> str:
        """Cleans the provided Python code by parsing and converting it to source format.

        This method takes a string of Python code, parses it into an Abstract Syntax Tree (AST),
        and then converts it back into a clean source code string.

        Parameters
        ----------
        code : str
            The Python code to be cleaned.

        Returns
        -------
        str
            A cleaned version of the provided Python code.

        Raises
        ------
        TypeError
            If the provided code is not a string.
        """
        if isinstance(code, str):
            code_nodes = ast.parse(code)
            clean_code_lines = []
            for node in code_nodes.body:
                clean_code_lines.append(astor.to_source(node))
            return "".join(line for line in clean_code_lines)
        else:
            raise TypeError("Code must be a string.")

    def execute_code(self, venv_executor: str, code: str, wd: str) -> str:
        """Executes the provided Python code using a specified virtual environment executor.

        This method cleans the code and runs it in a subprocess, ensuring that it is executed
        in a separate environment. It handles timeouts and errors during execution.

        Parameters
        ----------
        venv_executor : str
            The path to the Python interpreter in the virtual environment.
        code : str
            The Python code to be executed.
        wd : str
            working directory.
        Returns
        -------
        str
            result or error of code execution

        Raises
        ------
        TimeoutError
            If the code execution exceeds the allowed time limit of 120 seconds.
        CodeExecutionError
            If there is an error in code execution.
        """
        clean_code = PythonCodeExecutor._clean_code(code)
        cmd = [venv_executor, "-c", clean_code]
        try:
            result = subprocess.run(
                cmd,
                cwd=wd,
                check=True,
                timeout=120,
                capture_output=True,
                encoding="utf-8",
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            raise TimeoutError("timeout, running code takes more than 120 seconds")
        if result.returncode != 0:
            raise CodeExecutionError(result.stderr)
