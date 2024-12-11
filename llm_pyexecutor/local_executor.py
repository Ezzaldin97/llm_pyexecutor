import os
import traceback
from pathlib import Path
from typing import Optional

from llm_pyexecutor.cli import PipCommandsExtrator
from llm_pyexecutor.code import (
    PythonCodeExecutor,
    PythonCodeExtractor,
    extract_dependecies,
    is_standard_package,
)
from llm_pyexecutor.constants import STANDARD_PKG_SCRIPT
from llm_pyexecutor.environment_manager import VirtualEnvironmentManager
from llm_pyexecutor.logger import ExecutorLogger


class LLMPythonCodeExecutor:
    """A class to extract code, install dependencies and execute code
    from a given test
    """

    def __init__(
        self,
        name: Optional[str] = "local_executor",
        executor_dir_path: Optional[str] = ".",
        write_logs: Optional[bool] = True,
        venv_name: str = ".venv",
    ) -> None:
        """
        A class to execute Python code generated by a language model (LLM) in a controlled environment.

        Attributes:
            name (str): The name of the executor.
            executor_dir_path (Path): The directory path where the executor will operate.
            venv_name (str): The name of the virtual environment to be created.
            _logger (ExecutorLogger): Logger for logging execution details.
            _code_extractor (PythonCodeExtractor): Extractor for extracting Python code from text.
            _code_executor (PythonCodeExecutor): Executor for executing the extracted Python code.
            _pip_extractor (PipCommandsExtrator): Extractor for extracting pip commands from text.
            _executor_venv (VirtualEnvironmentManager): Manages the virtual environment for code execution.
        """
        self.name = name
        if Path(executor_dir_path).exists():
            self.executor_dir_path = Path(executor_dir_path)
        else:
            raise ValueError(f"{executor_dir_path} doesn't Exist on your system")
        self.path = self.executor_dir_path / self.name
        self.venv_name = venv_name
        self._intialize_executor_environment()
        if write_logs:
            self._logger = ExecutorLogger(
                logs_path=os.path.join(self.executor_dir_path, self.name, "logs")
            )
        else:
            self._logger = ExecutorLogger()
        self._logger.info("starting code execution tool")
        self._code_extractor = PythonCodeExtractor()
        self._code_executor = PythonCodeExecutor()
        self._pip_extractor = PipCommandsExtrator()
        self._executor_venv = VirtualEnvironmentManager(
            env_name=self.venv_name, base_dir=str(self.path), logger=self._logger
        )

    def __str__(self) -> str:
        """
        Returns a string representation of the LLMPythonCodeExecutor instance.

        Returns:
            str: A string representation of the executor.
        """
        pass

    def _intialize_executor_environment(self) -> None:
        """
        Initializes the executor environment by creating necessary directories and files.
        This includes creating a logs directory, a scripts directory, and a standard package script.
        """
        if not self.path.exists():
            self.path.mkdir()
            (self.path / "logs").mkdir()
            (self.path / "scripts").mkdir()
            with open(
                (self.path / "scripts" / "is_standard_pkg.py"), "w", encoding="utf-8"
            ) as file:
                file.write(STANDARD_PKG_SCRIPT)

    def execute(self, text: str) -> str:
        """
        Executes the provided text as Python code after extracting it from the input string.

        Parameters:
            text (str): The input text containing Python code to be executed.

        Returns:
            str: Returns the result of the code execution or an error message if an exception occurs.

        Raises:
            TypeError: If the provided text argument is not a string.
        """
        if isinstance(text, str):
            try:
                self._logger.info("LLM Generated Text: \n" f"{text}")
                self._logger.info("Searching for Packages to install from text")
                extracted_pkgs = self._pip_extractor.extract_packages(text)
                code = self._code_extractor.extract_code(text)
                self._logger.info("Extracted Python Code: \n" f"{code}")
                if len(extracted_pkgs) == 0:
                    code_deps = extract_dependecies(code)
                    self._logger.info("Python Code Dependencies: \n" f"{code_deps}")
                    venv_executor = self._executor_venv.get_pyexecutor()
                    standard_deps = is_standard_package(
                        venv_executor,
                        str((self.path / "scripts" / "is_standard_pkg.py")),
                        ".",
                    )
                    additional_pkgs = list(
                        {
                            deps["module"]
                            for deps in code_deps
                            if deps["module"] not in standard_deps
                        }
                    )
                    if len(additional_pkgs) == 0:
                        self._logger.info("No installation Needed")
                    else:
                        self._logger.info("Check if packages are installed")
                        uninstalled_deps = (
                            self._executor_venv.check_additional_dependencies(
                                additional_pkgs, str(self.executor_dir_path)
                            )
                        )
                        if len(uninstalled_deps) > 0:
                            self._logger.info(
                                f"Found Extra Dependecies: {uninstalled_deps}"
                            )
                            self._logger.info("Installing Dependencies in Progress!!!")
                            self._executor_venv.install_additional_dependencies(
                                uninstalled_deps, str(self.executor_dir_path)
                            )
                            self._logger.info("Installation Successfully Completed!!")
                else:
                    self._logger.info(
                        "Found Packages to install from text: " f"{extracted_pkgs}"
                    )
                    venv_executor = self._executor_venv.get_pyexecutor()
                    uninstalled_deps = (
                        self._executor_venv.check_additional_dependencies(
                            extracted_pkgs, str(self.executor_dir_path)
                        )
                    )
                    if len(uninstalled_deps) > 0:
                        self._logger.info(
                            f"Found Extra Dependecies: {uninstalled_deps}"
                        )
                        self._logger.info("Installing Dependencies in Progress!!!")
                        self._executor_venv.install_additional_dependencies(
                            uninstalled_deps, str(self.executor_dir_path)
                        )
                        self._logger.info("Installation Successfully Completed!!")
                code_result = self._code_executor.execute_code(
                    venv_executor,
                    code,
                    str(self.executor_dir_path),
                )
                self._logger.info("Code Execution Result: \n" f"{code_result}")
                return code_result
            except Exception:
                self._logger.error(
                    "Error Occured During Code Execution: \n"
                    f"{traceback.format_exc()}"
                )
                return (
                    "Error Occured During Code Execution: \n"
                    f"{traceback.format_exc()}"
                )
        else:
            self._logger.error("Expected text argument to be string")
            raise TypeError("Expected text argument to be string")
