#!/usr/bin/env python3
"""
Validation script for EPIC-1: Project Foundation.
Runs all checks to verify the foundation is correctly set up.
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """
    Run a command and return success status.
    
    Args:
        cmd: Command to run as list of strings
        description: Description for logging
        
    Returns:
        True if command succeeded, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"VALIDATION: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("="*60)
    
    result = subprocess.run(cmd, capture_output=False)
    success = result.returncode == 0
    
    print(f"Result: {'PASS' if success else 'FAIL'}")
    return success


def validate_structure() -> bool:
    """
    Validate project structure exists.
    
    Checks that all required files and directories are in place.
    
    Returns:
        True if all required files exist, False otherwise
    """
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/exceptions.py",
        "app/core/constants.py",
        "app/core/logging.py",
        "app/api/__init__.py",
        "app/api/routes/__init__.py",
        "app/api/routes/health.py",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/unit/__init__.py",
        "tests/unit/test_config.py",
        "tests/unit/test_exceptions.py",
        "tests/unit/test_main.py",
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        ".env.example",
        "pytest.ini",
    ]
    
    backend_dir = Path(__file__).parent.parent
    
    print("\n" + "="*60)
    print("VALIDATION: Project Structure")
    print("="*60)
    
    all_exist = True
    for file in required_files:
        path = backend_dir / file
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if not exists:
            all_exist = False
    
    print(f"\nResult: {'PASS' if all_exist else 'FAIL'}")
    return all_exist


def main() -> int:
    """
    Run all validations.
    
    Executes structure validation, syntax checks, import tests,
    unit tests, and code quality checks.
    
    Returns:
        0 if all validations pass, 1 otherwise
    """
    print("\n" + "#"*60)
    print("# EPIC-1 VALIDATION: Project Foundation")
    print("#"*60)
    
    results = []
    
    # 1. Structure validation
    results.append(validate_structure())
    
    # 2. Python syntax check
    results.append(run_command(
        ["python", "-m", "py_compile", "app/main.py"],
        "Python Syntax Check (main.py)"
    ))
    
    # 3. Python syntax check for config
    results.append(run_command(
        ["python", "-m", "py_compile", "app/core/config.py"],
        "Python Syntax Check (config.py)"
    ))
    
    # 4. Import validation
    results.append(run_command(
        ["python", "-c", "from app.core.config import get_settings; s = get_settings(); print(f'Settings loaded: env={s.environment}')"],
        "Config Import Check"
    ))
    
    # 5. Run unit tests
    results.append(run_command(
        ["pytest", "tests/unit/", "-v", "--tb=short"],
        "Unit Tests"
    ))
    
    # Summary
    print("\n" + "#"*60)
    print("# VALIDATION SUMMARY")
    print("#"*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if all(results):
        print("\n✓ EPIC-1 VALIDATION PASSED")
        return 0
    else:
        print("\n✗ EPIC-1 VALIDATION FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
