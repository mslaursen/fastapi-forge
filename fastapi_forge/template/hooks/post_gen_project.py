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


if __name__ == "__main__":
    git_init()
    uv_init()
