"""Module for Custom Exceptions
This module defines custom exceptions that can be used in a code execution context. 
These exceptions are designed to handle specific error cases related to code responses 
and execution failures.
"""


class NoCodeFoundError(Exception):
    """Exception raised when no code is found in the response.

    This exception is used to indicate that a response does not contain any code
    in the expected format.

    Parameters
    ----------
    sep : str
        The separator that indicates the start and end of the code block in the response.

    Attributes
    ----------
    sep : str
        The separator used to identify the code block in the response.

    Methods
    -------
    __init__(sep: str) -> None
        Initializes the NoCodeFoundError with a message indicating that no code was found
        in the response.
    """

    def __init__(self, sep: str) -> None:
        self.sep = sep
        super().__init__(
            "No code found in response. Code must be in the following format:"
            f"{self.sep}python"
            " # code here"
            f"{self.sep}"
        )


class CodeExecutionError(Exception):
    """Exception raised when code execution fails.

    This exception is used to indicate that code execution has encountered an error.

    Parameters
    ----------
    msg : str
        A message describing the reason for the code execution failure.

    Attributes
    ----------
    msg : str
        The message that provides details about the execution failure.

    Methods
    -------
    __init__(msg: str) -> None
        Initializes the CodeExecutionError with a message describing the failure.
    """

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__("Code Execution Failed due to:" f"{self.msg}")
