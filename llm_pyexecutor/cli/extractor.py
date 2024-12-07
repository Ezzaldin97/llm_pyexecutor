import re
from typing import List


class PipCommandsExtrator:
    """
    A class to extract pip install commands and package names from given code snippets.
    """

    def __init__(self) -> None:
        """
        Initializes the PipCommandsExtrator instance.
        """
        pass

    @staticmethod
    def get_pip_install_command(code: str) -> str:
        """
        Extracts the pip install command from a given code string.

        Args:
            code (str): The input code string that may contain a pip install command.

        Returns:
            str: The pip install command if found, otherwise None.
        """
        if (
            code.startswith("shell")
            or code.startswith("sh")
            or code.startswith("bash")
            or code.startswith("powershell")
            or code.startswith("ps1")
            or code.startswith("pwsh")
        ):
            # Remove the shell command prefix
            if re.match(r"^(shell|sh|bash|powershell|ps1|pwsh)", code):
                code = re.sub(r"^(shell|sh|bash|powershell|ps1|pwsh)", "", code)
            # Remove backticks if present
            if re.match(r"^`(.*)`$", code):
                code = re.sub(r"^`(.*)`$", r"\1", code)
            code = code.strip()
        if code.startswith("pip install"):
            return code

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

    @staticmethod
    def get_packages(commands: str) -> List[str]:
        """
        Extracts package names from pip install commands in the provided string.

        Args:
            commands (str): A string containing pip install commands.

        Returns:
            List[str]: A list of package names extracted from the commands.
        """
        lines = commands.split("\n")
        pkgs = []
        for line in lines:
            if line.startswith("pip install"):
                pkg = line.split("pip install")[-1].strip()
                pkgs.append(pkg)
        clean_pkgs = []
        for ele in pkgs:
            if re.search(",", ele):
                clean_pkgs.extend(ele.split(","))
        return [pkg.strip() for pkg in clean_pkgs]

    def extract_packages(self, text: str, separator: str = "```") -> str:
        """
        Extracts package names from pip install commands found in a given text.

        Args:
            text (str): The input text containing code snippets.
            separator (str): The separator used to identify code blocks (default is "```").

        Returns:
            List[str]: A list of package names extracted from the pip install commands.
        """
        if separator in text and len(text.split(separator)) > 1:
            codes = text.split(separator)
        codes = [PipCommandsExtrator.get_pip_install_command(code) for code in codes]
        codes = [code for code in codes if code is not None]
        clean_code = "".join(line + "\n" for line in codes)
        clean_code = PipCommandsExtrator.remove_repititive_lines(clean_code)
        pkgs = PipCommandsExtrator.get_packages(clean_code)
        return pkgs
