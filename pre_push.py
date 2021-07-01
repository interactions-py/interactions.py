#!/usr/bin/env python3
"""Run static analysis on the project."""

import sys
from os import path
from shutil import rmtree
from subprocess import CalledProcessError, check_call
from tempfile import mkdtemp

current_directory = path.abspath(path.join(__file__, ".."))


def do_process(args, shell=False):
    """Run program provided by args.

    Return True on success.

    Output failed message on non-zero exit and return False.

    Exit if command is not found.

    """
    print(f"Running: {' '.join(args)}")
    try:
        check_call(args, shell=shell)
    except CalledProcessError:
        print(f"\nFailed: {' '.join(args)}")
        return False
    except Exception as exc:
        sys.stderr.write(f"{str(exc)}\n")
        sys.exit(1)
    return True


def run_static():
    """Runs static tests.

    Returns a statuscode of 0 if everything ran correctly. Otherwise, it will return
    statuscode 1

    """
    success = True
    # Formatters
    success &= do_process(["black", "."])
    success &= do_process(["isort", "."])
    # Linters
    success &= do_process(["flake8", "--exclude=.eggs,build,docs,.venv*,env*"])

    tmp_dir = mkdtemp()
    try:
        success &= do_process(["sphinx-build", "-W", "--keep-going", "docs", tmp_dir])
    finally:
        rmtree(tmp_dir)

    return success


def main():
    success = True
    try:
        success &= run_static()
    except KeyboardInterrupt:
        return 1
    return int(not success)


if __name__ == "__main__":
    exit_code = main()
    print("\npre_push.py: Success!" if not exit_code else "\npre_push.py: Fail")
    sys.exit(exit_code)
