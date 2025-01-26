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


def uv_init() -> None:
    subprocess.run(
        [
            "uv",
            "lock",
        ]
    )


def lint() -> None:
    subprocess.run(
        [
            "make",
            "lint",
        ]
    )


def make_env() -> None:
    subprocess.run(
        [
            "cp",
            ".env.example",
            ".env",
        ]
    )


if __name__ == "__main__":
    git_init()
    uv_init()
    make_env()
    lint()
