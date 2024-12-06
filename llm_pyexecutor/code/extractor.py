import re
import ast
from ..code.exceptions import NoCodeFoundError


class PythonCodeExtractor:
    """
    A class to extract and validate Python code from a given text input.
    """

    def __init__(self) -> None:
        """
        Initializes the PythonCodeExtractor instance.
        """
        pass

    @staticmethod
    def get_code(code: str) -> str:
        """
        Extracts Python code from a given string. It removes specific prefixes
        and markers that indicate the presence of Python code.

        Args:
            code (str): The input string that may contain Python code.

        Returns:
            str: The cleaned Python code without prefixes or markers.
        """
        if (
            code.startswith("python")
            or code.startswith("Python")
            or code.startswith("py")
        ):
            if re.match(r"^(python|py|Python)", code):
                code = re.sub(r"^(python|py|Python)", "", code)
            if re.match(r"^`(.*)`$", code):
                code = re.sub(r"^`(.*)`$", r"\1", code)
            if "<|python_tag|>" in code:
                code = code.replace("<|python_tag|>", "")
            code = code.strip()
            return code

    @staticmethod
    def is_python_code(text: str) -> bool:
        """
        Checks if the given text is valid Python code by attempting to parse it.

        Args:
            text (str): The input string to be validated as Python code.

        Returns:
            bool: True if the text is valid Python code, False otherwise.
        """
        try:
            ast.parse(text)
            return True
        except SyntaxError:
            return False

    @staticmethod
    def remove_repititive_lines(code: str) -> str:
        """
        Removes duplicate lines from the provided Python code.

        Args:
            code (str): The input Python code as a string.

        Returns:
            str: The Python code with duplicate lines removed.
        """
        code_lines = code.split("\n")
        unique_lines = []
        for line in code_lines:
            if line not in unique_lines:
                unique_lines.append(line)
        return "".join(line + "\n" for line in unique_lines)

    def extract_code(self, text: str, separator: str = "```") -> str:
        """
        Extracts Python code from a text input that is enclosed by a specified separator.
        It validates the extracted code to ensure it is valid Python code.

        Args:
            text (str): The input text containing Python code.
            separator (str): The separator used to identify code blocks (default is "```").

        Returns:
            str: The extracted and validated Python code.

        Raises:
            NoCodeError: If no valid Python code is found in the input text.
        """
        if separator in text and len(text.split(separator)) > 1:
            codes = text.split(separator)
        codes = [
            code
            for code in [PythonCodeExtractor.get_code(code) for code in codes]
            if code is not None
        ]
        clean_code = "".join(line + "\n" for line in codes)
        clean_code = PythonCodeExtractor.remove_repititive_lines(clean_code)
        try:
            PythonCodeExtractor.is_python_code(clean_code)
        except SyntaxError:
            raise NoCodeFoundError(sep=separator)
        return clean_code
