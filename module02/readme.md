
# List of tools python uses for virtualenvs

1. virtualenv (third-party tool)
    1. Introduced in 2007.
    2. Created to solve the problem of dependency isolation across projects.
2. venv  (built in virtualenv)
    1. since python 3.3 (September 29, 2012)
    2. does not have a mechanism to solve conflicts
3. pipenv

| Command                        | Description                                              | Example                                 |
| ------------------------------ | -------------------------------------------------------- | --------------------------------------- |
| `pipenv install`               | Create venv & install all packages from `Pipfile`        | `pipenv install`                        |
| `pipenv install requests`      | Create venv if none exists, then install package         | `pipenv install requests`               |
| `pipenv install --dev black`   | Install a dev dependency                                 | `pipenv install --dev pytest`           |
| `pipenv install --python 3.11` | Create venv with specific Python version                 | `pipenv install --python 3.11`          |
| `pipenv uninstall requests`    | Remove a package                                         | `pipenv uninstall flask`                |
| `pipenv uninstall --all`       | Remove all packages                                      | `pipenv uninstall --all`                |
| `pipenv lock`                  | Generate `Pipfile.lock` with exact dependency versions   | `pipenv lock`                           |
| `pipenv update`                | Update all dependencies to latest allowed by `Pipfile`   | `pipenv update`                         |
| `pipenv update requests`       | Update a single package                                  | `pipenv update requests`                |
| `pipenv shell`                 | Activate the virtual environment                         | `pipenv shell`                          |
| `pipenv run python app.py`     | Run a command inside venv without activating             | `pipenv run python manage.py runserver` |
| `pipenv --venv`                | Show virtual environment path                            | `pipenv --venv`                         |
| `pipenv --py`                  | Show Python interpreter path                             | `pipenv --py`                           |
| `pipenv graph`                 | Show dependency tree                                     | `pipenv graph`                          |
| `pipenv check`                 | Check for security vulnerabilities in installed packages | `pipenv check`                          |
| `pipenv sync`                  | Sync venv exactly with `Pipfile.lock`                    | `pipenv sync`                           |
| `pipenv clean`                 | Remove unused packages                                   | `pipenv clean`                          |

| Section          | Purpose                    | Description                                                                                    | Example                           |
| ---------------- | -------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------- |
| `[[source]]`     | Package repository/source  | Defines where to fetch packages from (e.g., PyPI or private repo). Includes URL and SSL check. | `url = "https://pypi.org/simple"` |
| `[packages]`     | Main dependencies          | Lists project runtime packages with version specs. `"*"` means latest version allowed.         | `requests = "*"`                  |
| `[dev-packages]` | Development dependencies   | Packages only needed for development (testing, linting). Installed with `--dev` flag.          | `pytest = "*"`                    |
| `[requires]`     | Python version requirement | Specifies the Python version to use for the virtual environment.                               | `python_version = "3.11"`         |


4. pyenv
    1. just the tool to manage python version
    2. On Windows, pyenv is replaced by pyenv-win (a separate project).

| Command                     | Description                                                                   |
| --------------------------- | ----------------------------------------------------------------------------- |
| `pyenv install <version>`   | Install a specific Python version (e.g., 3.11.5)                              |
| `pyenv uninstall <version>` | Uninstall a specific Python version                                           |
| `pyenv versions`            | List all Python versions installed                                            |
| `pyenv global <version>`    | Set the global (default) Python version                                       |
| `pyenv local <version>`     | Set Python version for the current directory (creates `.python-version` file) |
| `pyenv shell <version>`     | Set Python version for the current shell session only                         |
| `pyenv rehash`              | Rebuild pyenv shims after installing/uninstalling packages                    |
| `pyenv which <command>`     | Show the full path to the executable for the current Python version           |
| `pyenv version`             | Show the current active Python version                                        |
| `pyenv help`                | Show help for pyenv commands                                                  |



5. pipx
    - https://pipx.pypa.io/stable/installation/
    - pipx install pipenv instead of pip3 install --user pipx
    - pipx install poetry
    - pipx list
    - pipx uninstall-all
    - pipx upgrade-all
    - pipx reinstall
    - pipx run -> Downloads and runs the tool in a temporary isolated env, then cleans up.
    - pipx run yt-dlp -f b "https://www.youtube.com/watch?v=O8n_BcXejH8"

| Package Name     | Description                         | Typical Use Case                          |
| ---------------- | ----------------------------------- | ----------------------------------------- |
| **poetry**       | Dependency management and packaging | Manage Python project dependencies        |
| **black**        | Code formatter                      | Format Python code automatically          |
| **httpie**       | User-friendly HTTP client           | Test and interact with HTTP APIs          |
| **cookiecutter** | Project scaffolding                 | Generate project templates                |
| **flake8**       | Code style checker                  | Enforce Python style guidelines           |
| **mypy**         | Static type checker                 | Type checking for Python code             |
| **yt-dlp**       | Video downloader                    | Download videos from YouTube and others   |
| **pytest**       | Testing framework                   | Run Python tests                          |
| **tox**          | Automation testing                  | Automate testing in multiple environments |
| **awscli**       | AWS command-line tool               | Manage AWS services                       |
| **pre-commit**   | Git hooks manager                   | Manage pre-commit hooks                   |
| **bandit**       | Security linter                     | Check Python code for security issues     |
| **sphinx**       | Documentation generator             | Generate project docs                     |
| **invoke**       | Task execution tool                 | Run shell and Python tasks                |
| **pip-tools**    | Dependency management tools         | Compile requirem                          |


6. poetry
    - poetry add git+ssh://git@github.com/sdispater/pendulum.git

| Command                    | Description                                                  |
| -------------------------- | ------------------------------------------------------------ |
| `poetry init`              | Create a new `pyproject.toml` interactively                  |
| `poetry new <project>`     | Create a new project skeleton                                |
| `poetry install`           | Install dependencies from `pyproject.toml` and `poetry.lock` |
| `poetry add <package>`     | Add a dependency and update `pyproject.toml` and lock file   |
| `poetry remove <package>`  | Remove a dependency                                          |
| `poetry update`            | Update dependencies to latest allowed versions               |
| `poetry lock`              | Generate or update `poetry.lock` without installing          |
| `poetry run <command>`     | Run a command inside the virtual environment                 |
| `poetry shell`             | Spawn a shell within the virtual environment                 |
| `poetry show`              | List installed packages and their versions                   |
| `poetry show --tree`       | Show dependency graph/tree of installed packages             |
| `poetry version <version>` | Show or set the project version                              |
| `poetry config --list`     | List Poetry configuration settings                           |
| `poetry publish`           | Publish package to PyPI or other repository                  |
| `poetry check`             | Check for validity of the `pyproject.toml` and dependencies  |

| Section                          | Purpose                     | Description                                                                                 | Example                                                                            |
| -------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `[tool.poetry]`                  | Project metadata            | Basic info like project name, version, description, authors, license, repository, keywords  | `name = "myproject"`<br>`version = "0.1.0"`                                        |
| `[tool.poetry.dependencies]`     | Runtime dependencies        | Lists main packages required to run the project, with version constraints                   | `python = "^3.11"`<br>`requests = "^2.28.1"`                                       |
| `[tool.poetry.dev-dependencies]` | Development dependencies    | Packages needed only for development, testing, linting                                      | `pytest = "^7.3.1"`                                                                |
| `[build-system]`                 | Build system configuration  | Specifies the build backend and requirements, as per PEP 518                                | `requires = ["poetry-core>=1.0.0"]`<br>`build-backend = "poetry.core.masonry.api"` |
| `[tool.<tool-name>]`             | Tool-specific configuration | Config for other tools like formatters (`black`), linters (`isort`), type checkers (`mypy`) | `[tool.black]`<br>`line-length = 88`                                               |


7. versioning
    1. MAJOR.MINOR.PATCH
        - MAJOR version when you make incompatible API changes
        - MINOR version when you add functionality in a backward-compatible manner
        - PATCH version when you make backward-compatible bug fixes
    2. https://docs.djangoproject.com/en/5.2/releases/

| Sign | Meaning                                   | Example              | Effect                            |
| ---- | ----------------------------------------- | -------------------- | --------------------------------- |
| `==` | Exactly this version                      | `requests==2.28.1`   | Only version 2.28.1 is allowed    |
| `>=` | Greater than or equal to                  | `requests>=2.0`      | Any version 2.0 or higher         |
| `<=` | Less than or equal to                     | `requests<=2.28`     | Versions up to 2.28 (inclusive)   |
| `>`  | Greater than                              | `requests>2.0`       | Versions strictly above 2.0       |
| `<`  | Less than                                 | `requests<3.0`       | Versions strictly below 3.0       |
| `~=` | Compatible release (often called “tilde”) | `requests~=2.28.0`   | Equivalent to `>=2.28.0, <2.29.0` |
| `^`  | Compatible with (used in Poetry)          | `requests = "^2.28"` | Equivalent to `>=2.28.0, <3.0.0`  |


8. conflict
    - pipenv install "requests>=2.25"


| Package  | Version constraint   | Notes                                           |
| -------- | -------------------- | ----------------------------------------------- |
| requests | `2.28.1`             | Requires `urllib3` version `<2.0`               |
| urllib3  | `>=2.0.0` (explicit) | Conflicts with `requests` dependency constraint |

9. how to use requirements.txt
    1. poetry add $(cat requirements.txt)
    2. pipenv install -r requirements.txt
    