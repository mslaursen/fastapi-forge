import subprocess
import yaml
import os
import shutil
from fastapi_forge.logger import logger


def run_command(command: list[str]) -> None:
    subprocess.run(command, check=True)


def uv_init() -> None:
    run_command(["uv", "lock"])


def lint() -> None:
    run_command(["make", "lint"])


def make_env() -> None:
    run_command(["cp", ".env.example", ".env"])


def _process_paths(paths: list[str], cwd: str) -> tuple[list[str], list[str]]:
    files = []
    folders = []
    for path in paths:
        if not path:
            continue
        full_path = os.path.join(cwd, path)
        if path.endswith((".py", ".yaml")):
            files.append(full_path)
        else:
            folders.append(full_path)
    return files, folders


def _get_delete_flagged() -> tuple[list[str], list[str]]:
    files = []
    folders = []
    cwd = os.getcwd()

    try:
        with open("forge-config.yaml") as stream:
            config = yaml.safe_load(stream) or {}
            paths_config = config.get("paths", {})

            for item in paths_config.values():
                if "enabled" in item and not item["enabled"]:
                    new_files, new_folders = _process_paths(item.get("paths", []), cwd)
                    files.extend(new_files)
                    folders.extend(new_folders)

                if "requires_all" in item:
                    conditions_met = all(
                        paths_config.get(req, {}).get("enabled", False) is False
                        for req in item["requires_all"]
                    )
                    if conditions_met:
                        new_files, new_folders = _process_paths(
                            item.get("paths", []), cwd
                        )
                        files.extend(new_files)
                        folders.extend(new_folders)

    except Exception as e:
        logger.error(f"Error reading config file: {e}")

    return files, folders


def _is_empty_init(dirpath: str) -> bool:
    init_file = os.path.join(dirpath, "__init__.py")
    try:
        with open(init_file, "r") as f:
            return not any(
                line.strip() and not line.strip().startswith("#")
                for line in f.read().splitlines()
            )
    except OSError:
        return False


def delete_empty_init_folders(root_dir: str = "{{cookiecutter.project_name}}") -> None:
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if dirpath != root_dir and set(filenames) == {"__init__.py"} and not dirnames:
            if _is_empty_init(dirpath):
                os.remove(os.path.join(dirpath, "__init__.py"))
                os.rmdir(dirpath)
                logger.info(f"Deleted empty package: {dirpath}")


def cleanup() -> None:
    files, folders = _get_delete_flagged()

    for path in files:
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Deleted file: {path}")
        except OSError as exc:
            logger.error(f"Error deleting file {path}: {exc}")

    for path in folders:
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                logger.info(f"Deleted folder: {path}")
        except OSError as exc:
            logger.error(f"Error deleting folder {path}: {exc}")

    delete_empty_init_folders()


if __name__ == "__main__":
    cleanup()
    uv_init()
    make_env()
    lint()
