poetry --version

# новий проект як пакет
poetry new facebook

# новий проект без вкладень
poetry new --flat auth-services

poetry install 

poetry env info
poetry env list


cd 03_poetry
poetry show
poetry show --only main
poetry show --only dev
poetry check

poetry add httpx
poetry show --tree
poetry show --tree --why urllib3

poetry remove httpx


poetry self add poetry-plugin-export
poetry export -f requirements.txt
poetry export -f requirements.txt --without-hashes

poetry run pip install httpx
poetry sync

poetry add --group docs mkdocs
poetry remove --group docs mkdocs


poetry run pytest -vv
poetry run mypy
poetry run mypy mypy_demo/broken.py
poetry run pre-commit run --all-files

deactivate
poetry env remove statusboard-8SkKN7Wn-py3.12
time poetry install

cd ../ && mkdir uv_test
cp ../03_poetry/pyproject.toml
time uv sync

cd ../04_uv

## uv

uv --version                                  # uv 0.11.4 — один бінарник, без Python-залежностей

# --- новий проєкт -----------------------------------------------------------
uv init facebook                              # новий проєкт (аналог poetry new --flat)
uv init --package auth-services               # як пакет: src/-розкладка + [build-system]
uv init --lib billing-client                  # бібліотека (--app = застосунок, типове)
uv init --bare                                # тільки pyproject.toml, без README і .python-version
uv add -r requirements.txt


uv run flask--app app run --debug

# --- оточення ---------------------------------------------------------------
uv venv                                       # створити venv вручну (sync робить це сам)
uv venv --clear                               # перестворити з нуля
uv sync                                       # привести venv у стан lock (аналог poetry sync)
uv sync --no-dev                              # без dev — так деплоять
uv sync --only-dev                            # тільки dev
uv sync --group docs                          # окрема група
uv sync --frozen                              # не чіпати lock; впасти, якщо застарів — для CI
uv sync --reinstall                           # перевстановити все, не видаляючи venv
                                              # .venv лежить У ТЕЦІ проєкту, не в кеші — на відміну від Poetry

# --- залежності -------------------------------------------------------------
uv add httpx                                  # додати + оновити lock + поставити у venv, одним кроком
uv add --dev ruff                             # dev-залежність (у Poetry: --group dev)
uv add --group docs mkdocs   
uv remove mkdocs --group docs                 # довільна група
uv add "flask>=3.1.0,<4.0.0"                  # з обмеженням версії
uv remove httpx                               # прибрати: маніфест + lock + venv, одним кроком
uv remove --dev ruff                          # прибрати з dev-групи
uv remove --optional charts plotly            # прибрати з extras
uv remove --no-sync httpx                     # прибрати з маніфесту й lock, venv не чіпати
uv add --no-sync httpx                        # оновити маніфест і lock, але НЕ ставити у venv
uv add --frozen httpx                         # дописати в маніфест, не перераховуючи lock

# --- що встановлено ---------------------------------------------------------
uv tree                                       # дерево залежностей (аналог poetry show --tree)
uv tree --depth 1                             # тільки прямі
uv tree --invert --package urllib3            # ХТО притягнув пакет (у Poetry: show --tree --why)
uv pip list                                   # плаский список, pip-сумісний
uv pip show flask                             # деталі по одному пакету

# --- lock -------------------------------------------------------------------
uv lock                                       # перерахувати uv.lock, нічого не встановлюючи
uv lock --check                               # чи lock актуальний (аналог poetry check --lock) — у CI
uv lock --upgrade                             # оновити все в межах обмежень
uv lock --upgrade-package flask               # оновити один пакет
                                              # uv.lock — власний формат, НЕ сумісний з poetry.lock

# --- запуск -----------------------------------------------------------------
uv run flask --app app run --debug            # сам синхронізує venv ПЕРЕД запуском — у Poetry так не буває
uv run pytest -vv
uv run mypy
uv run mypy mypy_demo/broken.py               # явний файл, бо exclude діє лише на обхід тек
uv run python -c "import flask; print(flask.__version__)"

# --- керування версіями Python (чого Poetry не вміє взагалі) ----------------
uv python list                                # які версії є і які доступні
uv python list --only-installed               # тільки те, що вже стоїть

# --- яка версія Python зараз використовується -------------------------------
uv python pin                                 # БЕЗ аргументу — показати пін теки (.python-version)
uv python find                                # БЕЗ аргументу — шлях до інтерпретатора, який буде взято
uv run python --version                       # версія в ОТОЧЕННІ проєкту — найнадійніша відповідь
uv run python -VV                             # те саме + як саме зібрано

uv python install 3.13                        # завантажити інтерпретатор — без pyenv
uv python pin 3.13                            # записати .python-version у теці
uv python pin --rm                            # зняти пін
uv python find 3.12                           # шлях до конкретної версії
uv python uninstall 3.11
uv venv --python 3.13                         # venv на конкретній версії

# --- глобальні утиліти (аналог pipx) ---------------------------------------
uv tool install ruff                          # поставити утиліту глобально
uv tool list
uvx ruff check .                              # запустити БЕЗ встановлення, у тимчасовому оточенні
uvx --from bandit bandit -r bandit_demo/      # коли ім'я команди != ім'я пакета

# --- export / міграція ------------------------------------------------------
uv export -o requirements.txt                 # з хешами; плагін не потрібен, на відміну від Poetry
uv export -o requirements.txt --no-hashes     # у Poetry цей прапорець зветься --without-hashes
uv export --no-dev -o requirements.txt
uv add -r requirements.txt                    # ЗВОРОТНИЙ шлях: імпорт з requirements.txt одною командою
                                              # у Poetry готової команди немає — там poetry add $(grep -v '^#' ...)

# --- конфлікт залежностей ---------------------------------------------------
uv lock --project conflict                    # той самий нерозв'язний набір, що в Poetry
                                              # той самий алгоритм PubGrub → те саме доведення, код 1
                                              # і той самий відступ до Flask 2.3.1, коли пін прибрати

# --- нове в 0.11 (у README 04_uv цього ще немає) ---------------------------
uv format                                     # вбудований форматер, ruff не потрібен
uv audit                                      # перевірка залежностей на CVE (аналог pip-audit)

# --- обслуговування ---------------------------------------------------------
uv self update                                # оновити сам uv

# --- заміри для порівняння --------------------------------------------------
time poetry --version                         # ~0,55 с — старт самого Poetry, на КОЖЕН poetry run
time uv --version                             # одиниці мілісекунд

