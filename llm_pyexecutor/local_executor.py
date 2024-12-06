from llm_pyexecutor.code import (
    PythonCodeExtractor,
    PythonCodeExecutor,
    extract_dependecies,
    is_standard_package,
)
from llm_pyexecutor.logger import ExecutorLogger
from llm_pyexecutor.constants import STANDARD_PKG_SCRIPT
from llm_pyexecutor.environment_manager import VirtualEnvironmentManager
from pathlib import Path
from typing import Optional
import traceback
import os


class LLMPythonCodeExecutor:
    def __init__(
        self,
        name: Optional[str] = "local_executor",
        executor_dir_path: Optional[str] = ".",
        write_logs: Optional[bool] = True,
        venv_name: str = ".venv",
    ) -> None:
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
        self._executor_venv = VirtualEnvironmentManager(
            env_name=self.venv_name, base_dir=str(self.path), logger=self._logger
        )

    def __str__(self) -> str:
        pass

    def _intialize_executor_environment(self) -> None:
        if not self.path.exists():
            self.path.mkdir()
            (self.path / "logs").mkdir()
            (self.path / "scripts").mkdir()
            with open(
                (self.path / "scripts" / "is_standard_pkg.py"), "w", encoding="utf-8"
            ) as file:
                file.write(STANDARD_PKG_SCRIPT)

    def execute(self, text: str) -> None:
        if isinstance(text, str):
            try:
                self._logger.info("LLM Generated Text: \n" f"{text}")
                code = self._code_extractor.extract_code(text)
                self._logger.info("Extracted Python Code: \n" f"{code}")
                code_deps = extract_dependecies(code)
                self._logger.info("Python Code Dependencies: \n" f"{code_deps}")
                venv_executor = self._executor_venv.get_pyexecutor()
                standard_deps = is_standard_package(
                    venv_executor,
                    str((self.path / "scripts" / "is_standard_pkg.py")),
                    str(self.executor_dir_path),
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
                            additional_pkgs
                        )
                    )
                    if len(uninstalled_deps) > 0:
                        self._logger.info(
                            f"Found Extra Dependecies: {uninstalled_deps}"
                        )
                        self._logger.info("Installing Dependencies in Progress!!!")
                        self._executor_venv.install_additional_dependencies(
                            uninstalled_deps,
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