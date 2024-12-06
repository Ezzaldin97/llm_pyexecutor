import subprocess
import ast
from typing import Dict, List
from ..code.exceptions import CodeExecutionError


def extract_dependecies(code: str) -> List[Dict[str, str]]:
    """
    Extracts module dependencies from a given Python code string.

    This function parses the provided code and identifies all the import statements.
    It returns a list of dictionaries, each containing the module name, the imported
    name, and its alias (if any).

    Args:
        code (str): A string containing Python code.

    Returns:
        List[Dict[str, str]]: A list of dictionaries where each dictionary contains:
            - "module": The name of the module being imported.
            - "name": The name of the imported object.
            - "alias": The alias used for the imported object (or the name if no alias is used).
    """
    deps = []
    tree = ast.parse(code)
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = node.names[0].name if isinstance(node, ast.Import) else node.module
            for alias in node.names:
                deps.append(
                    {
                        "module": module.split(".")[0] if "." in module else module,
                        "name": alias.name,
                        "alias": alias.asname or alias.name,
                    }
                )
    return deps


def is_standard_package(venv_executor: str, script_path: str, wd: str) -> List[str]:
    """
    Checks if the specified packages are standard packages in a virtual environment.

    This function executes a script in the provided virtual environment to determine
    if the packages are standard. It uses subprocess to run the command.

    Args:
        venv_executor (str): The path to the Python interpreter in the virtual environment.
        script_path (str): The path to the script that will check for the standard packages.
        wd (str): working directory.

    Returns:
        List[str]: The output from the executed script, which may include information
        about the packages checked.

    Raises:
        TimeoutError: If the script execution exceeds 120 seconds.
        CodeExecutionError: If the script returns a non-zero exit code, indicating an error.
    """
    cmd = [venv_executor, script_path]
    try:
        result = subprocess.run(
            cmd,
            cwd=wd,
            check=True,
            timeout=120,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        res = (
            result.stdout.strip()
            .replace("\n", "")
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .split(",")
        )
        res = [ele.strip() for ele in res]
        return res
    except subprocess.TimeoutExpired:
        raise TimeoutError("timeout, running code takes more than 120 seconds")
    if result.returncode != 0:
        raise CodeExecutionError(result.stderr)
