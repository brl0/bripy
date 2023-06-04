from pathlib import Path

import nox
import yaml

nox.options.sessions = ["black", "isort", "lint", "test"]
nox.options.default_venv_backend = "mamba"
nox.options.stop_on_first_error = True
nox.options.reuse_existing_virtualenvs = True


ENV_FILE = "environment.yaml"
_DEFAULT_PY = "3.10"
PYTEST_OPTS = ""
PROJECT_PATH = "src/bripy"


def read_env_nox(path=ENV_FILE):
    yml = Path(path).read_text()
    data = yaml.safe_load(yml)
    _channels = data.get("channels")
    channels = []
    for _ in _channels:
        channels.extend(["-c", _])
    deps = data.get("dependencies")
    pip = None
    for i in reversed(range(len(deps))):
        if isinstance(deps[i], dict):
            pip = deps.pop(i).get("pip")
            break
    deps = [*channels, *deps]
    return deps, pip


def install_pkgs(session, conda=None, pip=None):
    if conda is None and pip is None:
        conda, pip = read_env_nox()
    session.conda_install(*conda)
    if pip:
        session.install(*pip)


@nox.session(venv_backend=None)
def develop(session):
    session.install("flit")
    session.run(*"flit install -s".split(), *session.posargs)


@nox.session(tags=["lint", "fix"])
def black(session):
    session.install("black")
    session.run(*"black ./".split(), *session.posargs)


@nox.session(tags=["lint", "fix"])
def isort(session):
    session.install("isort")
    session.run(*"isort ./".split(), *session.posargs)


@nox.session(tags=["lint"])
def lint(session):
    session.install("flake8")
    session.run(*"flake8 ./".split(), *session.posargs)


@nox.session(venv_backend=None)
def install(session):
    session.install("-e", ".[test]")


@nox.session(python=_DEFAULT_PY)
def install_list_env(session):
    install_pkgs(session)
    session.install("-e", ".[test]")
    session.run(*"conda list".split(), *session.posargs)


@nox.session(
    python=["3.10", "3.7", "3.8", "3.9"],
    # python=["3.10", "3.11", "3.7", "3.8", "3.9"],
    # python=["3.10", "3.11", "3.7"],
)
def test(session):
    install_pkgs(session)
    session.install("-e", ".[test]")
    session.run("pytest", *PYTEST_OPTS.split(), *session.posargs)


# @nox.session(python=_DEFAULT_PY)
@nox.session(venv_backend=None)
def debug(session):
    # install_pkgs(session)
    # session.install("-e", ".[test]")
    cmds = [
        "pytest",
        *PYTEST_OPTS.split(),
        "--log-level=DEBUG",
        "-vvv",
        "-p",
        "pytest_print",
        "--print-relative-time",
        "--showlocals",
        "--print",
        "--exitfirst",
        "--last-failed-no-failures=all",
        "--last-failed",
        "--new-first",
        *session.posargs,
    ]
    session.run(*cmds)


@nox.session(python="3.11")
def debug311(session):
    install_pkgs(session)
    session.install("-e", ".[test]")
    cmds = [
        "pytest",
        *PYTEST_OPTS.split(),
        "--log-level=DEBUG",
        "-vvv",
        "-p",
        "pytest_print",
        "--print-relative-time",
        "--showlocals",
        "--print",
        "--exitfirst",
        "--last-failed-no-failures=all",
        "--last-failed",
        "--new-first",
        *session.posargs,
    ]
    session.run(*cmds)


@nox.session(python=_DEFAULT_PY)
def coverage(session):
    install_pkgs(session)
    session.install("-e", ".[test]")
    cmds = [
        "pytest",
        *PYTEST_OPTS.split(),
        "-p",
        "pytest_cov",
        f"--cov={PROJECT_PATH}",
        "--cov-report=term-missing",
        *session.posargs,
    ]
    session.run(*cmds)


@nox.session(python=_DEFAULT_PY)
def coverage_html(session):
    install_pkgs(session)
    session.install("-e", ".[test]")
    cmds = [
        "pytest",
        *PYTEST_OPTS.split(),
        "-p pytest_cov",
        f"--cov={PROJECT_PATH}",
        "--cov-report=term-missing",
        "--cov-report=html",
        *session.posargs,
    ]
    session.run(*cmds)


@nox.session(tags=["build"])
def build(session):
    session.install("flit")
    session.run(*"flit build".split())


@nox.session(tags=["build"])
def rm_dirs(session):
    paths = ["build", "dist"]
    for path in paths:
        p = Path(path)
        if p.exists():
            session.run(*f"rm -rf {str(p)}".split())
