"""
Check lint for code style in Python code.
"""
# pylint: disable=duplicate-code
import subprocess
from os import listdir
from pathlib import Path

from config.cli_unifier import _run_console_tool, choose_python_exe
from config.constants import PROJECT_CONFIG_PATH, PROJECT_ROOT
from config.lab_settings import LabSettings
from config.project_config import ProjectConfig
from config.stage_1_style_tests.common import check_result


def check_lint_on_paths(paths: list[Path], path_to_config: Path,
                        exit_zero: False = False) -> subprocess.CompletedProcess:
    """
    Run lint checks for the project.

    Args:
        paths (list[Path]): Paths to the projects.
        path_to_config (Path): Path to the config.
        exit_zero (False): Exit-zero lint argument.

    Returns:
        subprocess.CompletedProcess: Program execution values
    """
    lint_args = [
        "-m",
        "pylint",
        *map(str, paths)
        ,
        "--rcfile",
        str(path_to_config)
    ]
    if exit_zero:
        lint_args.append("--exit-zero")
    return _run_console_tool(str(choose_python_exe()), lint_args, debug=True)


def check_lint_level(lint_output: bytes, target_score: int) -> subprocess.CompletedProcess:
    """
    Run lint level check for the project.

    Args:
        lint_output (bytes): Pylint check output.
        target_score (int): Target score.

    Returns:
        subprocess.CompletedProcess: Program execution values
    """
    lint_level_args = [
        "-m",
        "config.stage_1_style_tests.lint_level",
        "--lint-output",
        str(lint_output),
        "--target-score",
        str(target_score)
    ]
    return _run_console_tool(str(choose_python_exe()), lint_level_args, debug=True)


def main() -> None:
    """
    Run lint checks for the project.
    """
    project_config = ProjectConfig(PROJECT_CONFIG_PATH)
    labs_list = project_config.get_labs_paths()

    pyproject_path = PROJECT_ROOT / "pyproject.toml"

    print("Running lint on config, seminars, admin_utils")
    completed_process = check_lint_on_paths(
        [
            PROJECT_ROOT / "config",
            PROJECT_ROOT / "seminars",
            PROJECT_ROOT / "admin_utils"
        ],
        pyproject_path, True)
    completed_process = check_lint_level(completed_process.stdout, 10)
    print(completed_process.stdout.decode("utf-8"))
    print(completed_process.stderr.decode("utf-8"))
    check_result(completed_process.returncode)

    if (PROJECT_ROOT / "core_utils").exists():
        print("core_utils exist")
        print("Running lint on core_utils")
        completed_process = check_lint_on_paths(
            [
                PROJECT_ROOT / "core_utils"
            ],
            pyproject_path)
        completed_process = check_lint_level(completed_process.stdout, 10)
        print(completed_process.stdout.decode("utf-8"))
        print(completed_process.stderr.decode("utf-8"))
        check_result(completed_process.returncode)

    for lab_name in labs_list:
        lab_path = PROJECT_ROOT / lab_name
        if "settings.json" in listdir(lab_path):
            target_score = LabSettings(PROJECT_ROOT / f"{lab_path}/settings.json").target_score

            print(f"Running lint for lab {lab_path}")
            completed_process = check_lint_on_paths(
                        [
                            lab_path
                        ],
                        pyproject_path)
            completed_process = check_lint_level(completed_process.stdout, target_score)
            print(completed_process.stdout.decode("utf-8"))
            print(completed_process.stderr.decode("utf-8"))
            check_result(completed_process.returncode)


if __name__ == "__main__":
    main()
