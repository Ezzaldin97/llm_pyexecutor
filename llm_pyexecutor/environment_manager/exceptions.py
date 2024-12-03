"""Module for Custom Exceptions

This module defines custom exceptions for handling errors related to 
python virtual environment mangement. 

"""


class PipInstallationError(Exception):
    """Exception raised for errors during pip package installation.

    Attributes:
        err (str): A string describing the error that occurred.
        out (str): A string containing the output from the pip command.

    Methods:
        __init__(self, err: str, out: str) -> None:
            Initializes the PipInstallationError with the specified error message
            and output.
    """

    def __init__(self, err: str, out: str) -> None:
        """Initializes the PipInstallationError with the given error message and output.

        Args:
            err (str): The error message describing the installation issue.
            out (str): The output from the pip command that provides context
                       for the error.

        Raises:
            Exception: Inherits from the base Exception class.
        """
        self.err = err
        self.out = out
        super().__init__(f"Error installing package: {err}\nOutput: {out}")
