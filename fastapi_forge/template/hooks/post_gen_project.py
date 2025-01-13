import subprocess


def git_init() -> None:
    subprocess.run(
        [
            "git",
            "init",
        ]
    )

    subprocess.run(
        [
            "git",
            "add",
            ".",
        ]
    )


def uv_run() -> None:
    subprocess.run(
        [
            "uv",
            "run",
            "src/app.py",
        ]
    )


if __name__ == "__main__":
    git_init()
    # uv_run()
