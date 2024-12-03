import subprocess
import os
from pathlib import Path
from typing import Union, List, Any
from types import SimpleNamespace
from ..environment_manager.exceptions import PipInstallationError
import venv


class VirtualEnvironmentManager:
    """A class to manage Python virtual environments.

    This class provides methods to create, set up, and manage virtual
    environments, including installing and checking dependencies.

    Attributes:
        env_name (Path): The name of the virtual environment.
        base_dir (Path): The base directory where the virtual environment is created.
        env_path (Path): The full path to the virtual environment.
        _executor_venv (SimpleNamespace): The created virtual environment instance.
    """

    def __init__(
        self, env_name: Union[Path, str], base_dir: Union[Path, str], timeout: int = 60
    ) -> None:
        """Initializes the VirtualEnvironmentManager.

        Args:
            env_name (Union[Path, str]): The name of the virtual environment.
            base_dir (Union[Path, str]): The base directory for the virtual environment.
            timeout (int): The timeout for subprocess calls (default is 60 seconds).

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

        self._executor_venv = self._setup_environment()

    def _setup_environment(self) -> SimpleNamespace:
        """Sets up the virtual environment.

        Creates a new virtual environment if it does not exist, or ensures
        the directories exist if it does.

        Returns:
            SimpleNamespace: An object containing the environment executable path.
        """
        env_args = {"with_pip": True}
        env_builder = venv.EnvBuilder(**env_args)

        if self.env_path.exists():
            return env_builder.ensure_directories(self.env_path)
        else:
            env_builder.create(self.env_path)
            return env_builder.ensure_directories(self.env_path)

    def install_additional_dependencies(self, deps: List[str]):
        """Installs additional dependencies using pip.

        Args:
            deps (List[str]): A list of package names to install.

        Raises:
            TimeoutError: If the pip install command times out.
            PipInstallationError: If there is an error during installation.
        """
        cmd = [self._executor_venv.env_exe, "-m", "pip", "install"] + deps
        try:
            result = subprocess.run(
                cmd,
                check=True,
                cwd=self.base_dir,
                timeout=60,
                capture_output=True,
                encoding="utf-8",
            )
        except subprocess.TimeoutExpired:
            raise TimeoutError("pip install timed out")

        if result.returncode != 0:
            raise PipInstallationError(err=result.stderr, out=result.stdout)

    def get_pyexecutor(self) -> str:
        """Returns the path to the Python executable in the virtual environment.

        Returns:
            str: The path to the Python executable.
        """
        return self._executor_venv.env_exe

    def check_additional_dependencies(self, deps: List[str]) -> List[Any]:
        """Checks if additional dependencies are installed.

        Args:
            deps (List[str]): A list of package names to check.

        Returns:
            List[Any]: A list of uninstalled dependencies.

        Raises:
            TimeoutError: If the pip show command times out.
            PipInstallationError: If there is an error during the check.
        """
        uninstalled_deps = []
        try:
            cmd = [self._executor_venv.env_exe, "-m", "pip", "show"] + deps

            result = subprocess.run(
                cmd,
                check=True,
                cwd=self.base_dir,
                timeout=60,
                capture_output=True,
                encoding="utf-8",
            )

            if len(result.stderr) > 0:
                pkgs = result.stderr.split(":")[-1].split(",")
                pkgs = [ele.strip().replace("\n", "") for ele in pkgs]
                uninstalled_deps.extend(pkgs)
        except subprocess.TimeoutExpired:
            raise TimeoutError("pip install timed out")
        if result.returncode != 0:
            raise PipInstallationError(err=result.stderr, out=result.stdout)
        return uninstalled_deps
