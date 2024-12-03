import subprocess
import os
from pathlib import Path
from typing import Union, List, Any
from types import SimpleNamespace
from ..environment_manager.exceptions import PipInstallationError
import venv


class VirtualEnvironmentManager:
    """
    A class to manage a Python virtual environment, including creating the environment,
    installing dependencies, and checking for installed packages.

    Attributes:
        env_name (Path): The name of the virtual environment.
        base_dir (Path): The base directory where the virtual environment will be created.
        env_path (Path): The full path to the virtual environment.
        timeout (int): The maximum time to wait for subprocess calls.
        logger: A logging object for logging messages.
        _executor_venv (SimpleNamespace): An object representing the virtual environment.
    """

    def __init__(
        self,
        env_name: Union[Path, str],
        base_dir: Union[Path, str],
        logger,
        timeout: int = 60,
    ) -> None:
        """
        Initializes the VirtualEnvironmentManager with the specified environment name and base directory.

        Args:
            env_name (Union[Path, str]): The name of the virtual environment.
            base_dir (Union[Path, str]): The base directory for the virtual environment.
            timeout (int): The timeout for subprocess calls (default is 60 seconds).
            logger: A logger object for logging messages.

        Raises:
            ValueError: If env_name or base_dir is not a string or Path object.
            ValueError: If timeout is less than 1.
        """
        if isinstance(env_name, str):
            self.env_name = Path(env_name)
        elif isinstance(env_name, Path):
            self.env_name = env_name
        else:
            raise ValueError("env_name must be a string or a Path object")

        if isinstance(base_dir, str):
            self.base_dir = Path(base_dir)
        elif isinstance(base_dir, Path):
            self.base_dir = base_dir
        else:
            raise ValueError("base_dir must be a string or a Path object")

        self.env_path = self.base_dir / self.env_name

        if timeout < 1:
            raise ValueError("Timeout must be greater than 0")
        self.timeout = timeout
        self.logger = logger

        self._executor_venv = self._setup_environment()

    def _setup_environment(self) -> SimpleNamespace:
        """
        Sets up the virtual environment by creating it if it does not exist.

        Returns:
            SimpleNamespace: An object containing the environment executable path.

        Logs messages about the creation of the environment and whether it already exists.
        """
        self.logger.info("Creating Executor Virtual Environment")
        env_args = {"with_pip": True}
        env_builder = venv.EnvBuilder(**env_args)

        if self.env_path.exists():
            self.logger.info("Found Existing Environment")
            return env_builder.ensure_directories(self.env_path)
        else:
            env_builder.create(self.env_path)
            return env_builder.ensure_directories(self.env_path)

    def install_additional_dependencies(self, deps: List[str]):
        """
        Installs additional dependencies using pip in the virtual environment.

        Args:
            deps (List[str]): A list of dependency names to install.

        Raises:
            TimeoutError: If the pip install command times out.
            PipInstallationError: If the installation fails for any reason.
        """
        self.logger.info(f"install additional dependencies {deps} using pip")
        cmd = [self._executor_venv.env_exe, "-m", "pip", "install"] + deps
        try:
            result = subprocess.run(
                cmd,
                check=True,
                cwd=self.base_dir,
                timeout=self.timeout,
                capture_output=True,
                encoding="utf-8",
            )
            self.logger.info("dependencies successfully installed!!")
        except subprocess.TimeoutExpired:
            self.logger.error("pip install timed out")
            raise TimeoutError("pip install timed out")
        if result.returncode != 0:
            self.logger.error(
                "Error Occurred during installation due to:" f"{result.stderr}"
            )
            raise PipInstallationError(err=result.stderr, out=result.stdout)

    def get_pyexecutor(self) -> str:
        """
        Returns the path to the Python executable in the virtual environment.

        Returns:
            str: The path to the Python executable.
        """
        return self._executor_venv.env_exe

    def check_additional_dependencies(self, deps: List[str]) -> List[Any]:
        """
        Checks if additional dependencies are installed in the virtual environment.

        Args:
            deps (List[str]): A list of dependency names to check.

        Returns:
            List[Any]: A list of uninstalled dependencies.

        Raises:
            TimeoutError: If the pip show command times out
            PipInstallationError: If the checking fails for any reason.
        """
        self.logger.info(f"Checking additional dependencies: {deps}")
        uninstalled_deps = []
        try:
            cmd = [self._executor_venv.env_exe, "-m", "pip", "show"] + deps
            result = subprocess.run(
                cmd,
                check=True,
                cwd=self.base_dir,
                timeout=self.timeout,
                capture_output=True,
                encoding="utf-8",
            )
            if len(result.stderr) > 0:
                pkgs = result.stderr.split(":")[-1].split(",")
                pkgs = [ele.strip().replace("\n", "") for ele in pkgs]
                uninstalled_deps.extend(pkgs)
                self.logger.info(f"Found Uninstalled dependencies: {uninstalled_deps}")
        except subprocess.TimeoutExpired:
            self.logger.error("pip install timed out")
            raise TimeoutError("pip install timed out")
        if result.returncode != 0:
            self.logger.error(
                "Error Occurred during checking due to:" f"{result.stderr}"
            )
            raise PipInstallationError(err=result.stderr, out=result.stdout)
        return uninstalled_deps
