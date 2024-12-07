import pytest
import os
from llm_pyexecutor import LLMPythonCodeExecutor

text_with_no_dependencies = (
    "here's a code to get the current working directory using python\n"
    "```python\n"
    "import os\n"
    "print(os.getcwd())"
    "```\n"
)

text_with_dependencies = (
    "To calculate the dot product between two matrices in Python,"
    "you can use the `numpy` library, which provides a convenient function called `dot` for this purpose."
    "Here's a step-by-step guide on how to do it:\n\n1. Install `numpy` if you haven't already."
    "You can install it using pip:\n   ```bash\n   pip install numpy\n   ```\n\n2. Use the `numpy.dot`"
    "function to calculate the dot product of two matrices."
    "\n\nHere's an example:\n\n```python\nimport numpy as np\n\n#"
    "Define two matrices\nmatrix_a = np.array([[1, 2, 3],\n"
    "[4, 5, 6]])\n\nmatrix_b = np.array([[7, 8],\n"
    "[9, 10],\n                     [11, 12]])\n\n# Calculate the dot product"
    "\ndot_product = np.dot(matrix_a, matrix_b)\n\n# Alternatively,"
    "you can use the @ operator for matrix multiplication"
    '\n# dot_product = matrix_a @ matrix_b\n\nprint("Dot Product:")\n'
    "print(dot_product)\n```\n\nIn this example, `matrix_a` is a 2x3 matrix"
    " and `matrix_b` is a 3x2 matrix. The dot product of these two matrices will"
    " result in a 2x2 matrix.\n\nOutput:\n```\nDot Product:\n[[ 58  64]\n [139 154]]\n"
    "```\n\nMake sure that the number of columns in the first matrix (`matrix_a`) is"
    " equal to the number of rows in the second matrix (`matrix_b`) for the dot product to be defined."
)


@pytest.fixture
def local_executor_instance() -> LLMPythonCodeExecutor:
    return LLMPythonCodeExecutor(executor_dir_path="tests")


def test_if_local_executor_dir_exists(local_executor_instance) -> None:
    assert "local_executor" in os.listdir("tests/")


def test_local_executor_output_with_no_dependencies(local_executor_instance) -> None:
    real = (f"{os.path.join(os.getcwd(), 'tests')}""\n")
    output = local_executor_instance.execute(text_with_no_dependencies)
    assert output == real


def test_local_executor_output_with_dependencies(local_executor_instance) -> None:
    real = "Dot Product:\n[[ 58  64]\n [139 154]]\n"
    output = local_executor_instance.execute(text_with_dependencies)
    assert output == real
