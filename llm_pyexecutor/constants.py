STANDARD_PKG_SCRIPT = """import sys

standard_packages = []
std_lib_modules = set(sys.builtin_module_names) | set(sys.modules.keys())
std_lib_modules.update(sys.stdlib_module_names)
for package in std_lib_modules:
    standard_packages.append(package)
print(standard_packages)
"""
