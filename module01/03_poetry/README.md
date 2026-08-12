# 03 — Poetry

**Той самий `statusboard`, що і в [`../02_pipenv/`](../02_pipenv/).** Код не змінився жодним рядком:
ті самі `app.py`, `checks.py`, `services.py`, `incidents.py`, ті самі шаблони й той самий CSS.

Змінився **лише спосіб опису залежностей**:

|                                   | 02 — pip            | 03 — Poetry (ця папка)                |
| --------------------------------- | -------------------- | --------------------------------------------- |
| Маніфест                  | `requirements.txt` | `pyproject.toml`                            |
| Lock-файл                     | немає           | `poetry.lock`                               |
| Групи залежностей | немає           | є (`dev`, і будь-які власні) |
| Хеші пакетів           | немає           | є                                            |
| Створення venv           | вручну         | автоматично                        |

Якщо хочете зрозуміти **сам застосунок** — Flask, шаблони, API Cloudflare — читайте README у
[`../02_pipenv/`](../02_pipenv/README.md). Тут тільки про Poetry.

---

## Встановлення Poetry

Poetry не ставлять через `pip install` у проєкт — це окремий інструмент, а не залежність:

```bash
uv tool install poetry
# або: pipx install poetry
# або: curl -sSL https://install.python-poetry.org | python3 -

poetry --version
```

---

## Запуск

```bash
cd module01/03_poetry

poetry install
poetry run flask --app app run --debug
```

Відкрити [http://127.0.0.1:5000](http://127.0.0.1:5000).

Зверніть увагу: **ніякого `python -m venv` і ніякої активації.** Poetry сам створив віртуальне
середовище й сам поставив туди пакети. Де воно лежить:

```bash
poetry env info --path
```

За замовчуванням — у кеші (`~/Library/Caches/pypoetry/virtualenvs/`), а не в теці проєкту. Якщо
хочеться `.venv` поруч із кодом, як у попередній папці:

```bash
poetry config virtualenvs.in-project true
```

### `poetry run` і `poetry shell`

```bash
poetry run flask --app app run    # виконати одну команду в середовищі
poetry run python
poetry env activate               # надрукує команду активації (Poetry 2.x)
```

`poetry run` не активує середовище — він просто запускає команду всередині нього. У 99 % випадків цього
досить.

---

## `pyproject.toml`

```toml
[project]
name = "statusboard"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "flask (>=3.1.0,<4.0.0)",
    "requests (>=2.32.3,<3.0.0)",
]

[tool.poetry]
package-mode = false

[tool.poetry.group.dev.dependencies]
ruff = "^0.14.0"
```

Три речі, які варто розібрати.

**`[project]` — це стандарт, а не вигадка Poetry.** Це PEP 621. Той самий блок читають uv, pip, hatch,
setuptools. Раніше Poetry мав власний формат (`[tool.poetry.dependencies]`), і його ще багато де видно
в старих проєктах — але з Poetry 2.x правильний варіант саме цей.

**`package-mode = false`.** `statusboard` — застосунок, а не бібліотека: ніхто не буде ставити його
командою `pip install statusboard`. Цей рядок каже Poetry «керуй лише середовищем, збирати нічого не
треба». Без нього Poetry шукав би пакет `statusboard/` і вимагав би `src/`-розкладку та build-backend.

> Якщо ви **пишете бібліотеку**, все навпаки: `package-mode` не потрібен, з’являється секція
> `[build-system]`, і `poetry build` збирає `.whl` та `.tar.gz`, які можна залити на PyPI через
> `poetry publish`. Це і є головна відмінність Poetry від pip — він уміє **пакувати**, а не тільки
> встановлювати.

**Групи залежностей.** `ruff` потрібен для розробки й **не має потрапити в продакшн**:

```bash
poetry install --only main      # без dev — так деплоять
poetry install --with dev       # з dev (за замовчуванням і так ставиться)
poetry install --only dev
```

У `requirements.txt` цього не виразити ніяк. Там довелося б вести другий файл руками й вічно стежити,
щоб вони не розійшлися.

Групи можна створювати свої:

```toml
[tool.poetry.group.docs]
optional = true

[tool.poetry.group.docs.dependencies]
mkdocs = "^1.6"
```

### Як додати пакет у конкретну групу

```bash
poetry add requests                  # у [project] dependencies — робоча залежність
poetry add --group dev pytest        # у групу dev
poetry add --group docs mkdocs       # у групу docs (створиться, якщо її немає)
poetry add --group typing mypy

poetry remove --group docs mkdocs    # прибрати саме з цієї групи
```

Прапорець `--group` (скорочено `-G`) — це вся відповідь. Без нього пакет потрапляє в робочі
залежності й поїде в продакшн.

> **Увага, змінилася поведінка.** Poetry 2.x створює **нову** групу вже в стандартній секції
> `[dependency-groups]` (PEP 735), а не у своїй власній `[tool.poetry.group.*]`. Перевірено на
> Poetry 2.4.1: `poetry add --group docs mkdocs` у порожньому проєкті дав
>
> ```toml
> [dependency-groups]
> docs = [
>     "mkdocs (>=1.6.1,<2.0.0)"
> ]
> ```
>
> Але якщо секція `[tool.poetry.group.docs.dependencies]` вже існує, Poetry допише пакет **туди**.
> Тому в реальних проєктах трапляються обидва варіанти одночасно, і це нормально. Саме через це
> [`../04_uv/`](../04_uv/) читає ті самі групи без жодних змін.

Встановлення й виключення груп:

```bash
poetry install                # main + усі не-optional групи
poetry install --with docs    # додати optional-групу
poetry install --without dev  # усе, крім dev
poetry install --only main    # тільки робочі залежності — так деплоять
poetry install --only docs    # тільки одна група
```

Перевірено: `--with docs` бачить `mkdocs`, `--only main` — ні.

### Розширений приклад

У цій же теці лежить [`pyproject.reference.toml`](pyproject.reference.toml) — довідковий файл, у
якому зібрано майже все, що взагалі можна написати в `pyproject.toml`, з поясненнями українською:
`classifiers`, extras, маркери оточення, приватні індекси, точки розширення, консольні команди,
кілька груп залежностей, вибір build-backend, а також секції `[tool.ruff]`, `[tool.pytest.ini_options]`,
`[tool.mypy]` і `[tool.coverage]` та їхні відповідники в uv.

Це шпаргалка, а не шаблон: реальний маніфест майже ніколи не містить і чверті цього. Файл валідний —
перевіряється так:

```bash
mkdir -p /tmp/ref && cp pyproject.reference.toml /tmp/ref/pyproject.toml
cd /tmp/ref && touch README.md && poetry check
```

---

## Як створити `pyproject.toml` з нуля

### Варіант 1: `poetry new` — новий проєкт разом зі структурою тек

```bash
poetry new statusboard
```

Створює одразу все:

```
statusboard/
├── README.md
├── pyproject.toml
├── src/statusboard/__init__.py
└── tests/__init__.py
```

> У Poetry 2.x `--src` **уже є типовою поведінкою**, і сам прапорець позначено застарілим:
> `The --src option is now the default and will be removed in a future version.`
> Щоб отримати стару пласку розкладку без `src/`, потрібен `--flat`.

Згенерований файл:

```toml
[project]
name = "statusboard"
version = "0.1.0"
description = ""
authors = [{name = "Oleh Andrus", email = "..."}]
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[tool.poetry]
packages = [{include = "statusboard", from = "src"}]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```

Ім'я та пошту Poetry бере з `git config user.name` і `user.email`.

### Варіант 2: `poetry init` — у вже наявній теці

Це те, що потрібно, коли код уже написаний (як у нашому випадку):

```bash
cd module01/03_poetry
poetry init
```

Запуститься діалог: ім'я, версія, опис, автор, ліцензія, версія Python, а тоді два питання про
залежності — робочі й dev. На кожне можна відповісти порожнім рядком і додати їх потім через
`poetry add`.

**Неінтерактивно** (для скриптів і CI) — прапорець `-n` плюс параметри:

```bash
poetry init -n \
  --name statusboard \
  --description "Uptime board for public sites" \
  --author "Oleh <oleh@example.com>" \
  --python ">=3.12" \
  --dependency flask \
  --dependency requests \
  --dev-dependency ruff
```

Poetry сам знайде актуальні версії й підставить діапазони:

```
Using version ^3.1.3 for flask
Using version ^2.34.2 for requests
```

Зверніть увагу: `poetry init` **не створює** ні `src/`, ні `tests/`, ні lock-файл. Він пише лише
`pyproject.toml`. Залежності встановить наступний `poetry install`.

---

## Як перейти з `requirements.txt`

Готової команди `poetry import` **не існує** — на відміну від uv, де це вбудовано. Робиться у два
кроки.

```bash
# 1. створити маніфест
poetry init -n --name statusboard --python ">=3.12"

# 2. згодувати йому весь список
poetry add $(cat requirements.txt)
```

Якщо у файлі є коментарі — а вони бувають майже завжди — потрібен `grep`:

```bash
poetry add $(grep -v '^#' requirements.txt)
```

**Чому цього достатньо.** Непроквотована підстановка `$(...)` ділить вивід на слова по пробілах
**і по переносах рядків** — тож `tr '\n' ' '` не потрібен. Порожні рядки при цьому не дають жодного
аргументу, тож і відфільтровувати їх окремо не треба. Перевірити, що саме піде в команду, можна так:

```bash
printf '  [%s]\n' $(grep -v '^#' requirements.txt)
```

```
  [Flask==3.1.0]
  [requests==2.32.3]
```

Без `grep` той самий рядок дає `[#]`, `[web]`, `[framework]`, `[Flask==3.1.0]`… — кожне слово
коментаря стає окремою «назвою пакета», і `poetry add` падає.

Варіант через `xargs` робить те саме й комусь читається легше:

```bash
grep -v '^#' requirements.txt | xargs poetry add
```

> Обидва варіанти не впораються з коментарем **у кінці рядка** (`Flask==3.1.0  # web`). Якщо такі є,
> фільтр складніший: `sed 's/#.*//' requirements.txt`.

Перевірено на нашому файлі — з

```
Flask==3.1.0
requests==2.32.3
```

виходить

```toml
dependencies = [
    "flask (==3.1.0)",
    "requests (==2.32.3)"
]
```

плюс одразу згенерований `poetry.lock` з усіма 13 пакетами.

### Головна пастка міграції

Точні пінами `==` **переносяться як є**. Для `requirements.txt` це було правильно, а в
`pyproject.toml` — майже завжди ні.

Розподіл ролей у Poetry інший:

| Файл           | Що містить                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| `pyproject.toml` | **діапазони** — межі, у яких ви згодні оновлюватися |
| `poetry.lock`    | **точні версії** — те, що реально встановлено            |

Якщо залишити `==` у маніфесті, ви отримаєте подвійну фіксацію: `poetry update` не зможе підняти
навіть патч із виправленням безпеки, бо маніфест це забороняє. Тому після міграції діапазони
розслаблюють:

```bash
poetry add "flask@^3.1.0" "requests@^2.32.3"
```

Точні версії при цьому нікуди не дінуться — вони лишаться в `poetry.lock`, де їм і місце.

### Якщо є `requirements-dev.txt`

Він стає групою:

```bash
poetry add --group dev $(grep -v '^#' requirements-dev.txt)
```

### Зворотний шлях

Іноді потрібно віддати `requirements.txt` кудись, де Poetry немає — AWS Lambda, старі buildpack-и,
корпоративні системи збірки:

```bash
poetry self add poetry-plugin-export      # у Poetry 2.x це окремий плагін
poetry export -f requirements.txt -o requirements.txt --without-hashes
poetry export -f requirements.txt -o requirements-dev.txt --only dev
```

Без `--without-hashes` у файл потраплять хеші з lock — і це насправді краще, бо `pip install --require-hashes` тоді перевірить кожен архів.

---

## Синтаксис версій

| Запис         | Означає                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------- |
| `^1.2.3`         | `>=1.2.3, <2.0.0` — caret, «не ламай мажорну»                                  |
| `^0.2.3`         | `>=0.2.3, <0.3.0` — для `0.x` мажорною вважається друга цифра |
| `~1.2.3`         | `>=1.2.3, <1.3.0` — tilde, тільки патчі                                             |
| `>=3.1.0,<4.0.0` | те саме явно, PEP 508                                                                   |
| `*`              | будь-яка                                                                                   |

`^` — типовий вибір Poetry за замовчуванням. Він спирається на те, що всі дотримуються семантичного
версіонування; на практиці це не завжди так, і саме тому потрібен lock-файл.

---

## `poetry.lock` — головне на цьому занятті

`pyproject.toml` описує, **що ви попросили**. `poetry.lock` фіксує, **що ви отримали**:

```bash
head -30 poetry.lock
grep -c '^\[\[package\]\]' poetry.lock   # 40 пакетів: 13 робочих + dev-інструменти
grep -c "hash\|sha256" poetry.lock       # ~524 у цьому проєкті
```

У ньому:

- **точна версія кожного пакета** — не тільки ваших двох, а всіх тринадцяти разом із транзитивними
  (плюс усе, що притягнули `ruff`, `pytest`, `bandit`, `pre-commit` і `mypy` у групу `dev`);
- **SHA-256 кожного файлу**, який буде завантажено;
- `content-hash` — відбиток самого `pyproject.toml`.

Хеші — це і є сенс lock-файлу. При встановленні кожен завантажений архів звіряється з хешем. Якщо
PyPI зламають, дзеркало підмінить wheel або мейнтейнер перезапише реліз — установка **впаде**, а не
тихенько запустить чужий код.

`content-hash` дозволяє Poetry помітити, що `pyproject.toml` змінили, а `poetry.lock` — ні.

> **Lock-файл комітять у git. Завжди.**

### `install` проти `lock` проти `sync`

| Команда     | Читає                                                 | Що робить                                                                                                  |
| ------------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `poetry install` | lock (а якщо його немає — маніфест) | ставить рівно те, що в lock                                                                       |
| `poetry lock`    | `pyproject.toml`                                         | перераховує залежності й переписує lock, нічого не встановлюючи |
| `poetry sync`    | lock                                                       | ставить те, що в lock,**і видаляє все зайве**                                    |
| `poetry update`  | `pyproject.toml`                                         | `lock` + `install`: підтягує новіші версії в межах обмежень                  |

`poetry sync` — це те, чого принципово немає в pip: воно приводить середовище **точно** у стан
lock-файлу, прибираючи пакети, які ви колись поставили руками й забули.

### Вправа: зламати lock навмисно

```bash
# 1. У pyproject.toml змініть flask на (>=3.0.0,<4.0.0)
poetry check --lock
```

```
Error: pyproject.toml changed significantly since poetry.lock was last generated.
Run `poetry lock` to fix the lock file.
```

Саме цю перевірку ставлять у CI, щоб ніхто не задеплоїв версії, яких ніхто не переглядав. Повернути
як було:

```bash
git checkout -- pyproject.toml poetry.lock
```

---

## Конфлікт залежностей

Резолвер видно тоді, коли він не може розв'язати задачу. У теці [`conflict/`](conflict/) лежить
**окремий міні-проєкт** саме для цього — окремий, щоб `pyproject.toml` і `poetry.lock` самого
`statusboard` залишились недоторканими. Усередині:

```toml
dependencies = [
    "flask (==3.1.0)",
    "werkzeug (==2.3.0)",
]
```

Flask 3.1.0 у метаданих оголошує `Werkzeug>=3.1`, а ми поруч вимагаємо рівно `2.3.0`. Такого набору
версій не існує.

Poetry запускається з ключем `-C` (він же `--directory`) — це і є спосіб націлити його на інший
проєкт, не переходячи в теку:

```bash
poetry -C conflict lock
```

```
Skipping virtualenv creation, as specified in config file.
Updating dependencies
Resolving dependencies...

Because conflict-demo depends on flask (3.1.0) which depends on Werkzeug (>=3.1), werkzeug is required.
So, because conflict-demo depends on werkzeug (2.3.0), version solving failed.
```

Код повернення — **1**, `conflict/poetry.lock` не створюється, ваш справжній lock-файл не змінюється.
Перевірити можна відразу: `poetry check --lock` у корені теки, як і раніше, скаже `All set!`.

Прочитайте текст помилки уважно — це не «щось пішло не так», а **доведення**, вибудуване від вашого
проєкту до суперечності:

1. `conflict-demo` залежить від `flask (3.1.0)`;
2. той залежить від `Werkzeug (>=3.1)`;
3. отже, `werkzeug>=3.1` обов'язковий;
4. але `conflict-demo` вимагає `werkzeug (2.3.0)` → розв'язку немає.

Poetry (як і uv) використовує алгоритм **PubGrub**, і ця здатність назвати саму пару обмежень, а не
просто «конфлікт», — його прямий наслідок.

### Той самий файл, але розв'язний

Заберіть у `conflict/pyproject.toml` версію в Flask — залиште просто назву (це «будь-яка версія»;
`flask (*)` Poetry не приймає, він падає з `The requirement is invalid`):

```toml
dependencies = [
    "flask",
    "werkzeug (==2.3.0)",
]
```

```bash
poetry -C conflict lock
```

Тепер `poetry lock` спокійно проходить і пише `conflict/poetry.lock`, а в ньому — `Flask 2.3.1`:

```bash
grep -A1 'name = "flask"' conflict/poetry.lock
# name = "flask"
# version = "2.3.1"
```

Poetry **відступив назад** до найновішого Flask, який ще приймає Werkzeug 2.3.0. Це і є резолюція:
не «постав найновіше», а «знайди версії, за яких усі обмеження виконуються одночасно». pip у
[`../02_pipenv/`](../02_pipenv/) і uv у [`../04_uv/`](../04_uv/) на цьому ж наборі приходять до тієї
самої `Flask 2.3.1`.

Прибрати за собою:

```bash
rm -f conflict/poetry.lock && git checkout -- conflict/pyproject.toml
```

### Чим це відрізняється від pip

Головна відмінність — не текст помилки, а те, **чого тут не може статися**. У pip послідовні
`pip install flask==3.1.0` і `pip install werkzeug==2.3.0` лишають зламане оточення й повертають код
0 (детально — у [`../02_pipenv/README.md`](../02_pipenv/README.md#конфлікт-залежностей)). У Poetry
такого шляху просто немає: `poetry add` спершу перераховує **весь** граф, і якщо розв'язку немає —
не змінює ні оточення, ні `pyproject.toml`.

Перевірте на розв'язному варіанті з попереднього кроку (`flask` без версії + `werkzeug (==2.3.0)`) —
спробуйте додати конфліктний пін:

```bash
poetry -C conflict add "flask==3.1.0"
```

```
Because flask (3.1.0) depends on Werkzeug (>=3.1)
 and conflict-demo depends on werkzeug (2.3.0), flask is forbidden.
So, because conflict-demo depends on flask (3.1.0), version solving failed.
```

Код 1 — і `conflict/pyproject.toml` **не змінився**: рядка `flask==3.1.0` у ньому не з'явилося.
Порівняйте з pip, який у такій ситуації встановлює пакет і повідомляє про проблему постфактум.

|                                                             | pip                                     | Poetry                                                               |
| ----------------------------------------------------------- | --------------------------------------- | -------------------------------------------------------------------- |
| Порахувати конфлікт наперед        | `--dry-run`                           | так,`poetry lock`                                               |
| Назвати конкретну пару обмежень | так, коротко                  | так, як доведення                                      |
| Відступити до старішої версії     | так                                  | так                                                               |
| Може зламати готове оточення       | **так, і повертає 0** | ні                                                                 |
| Знайти вже зламане                          | `pip check`                           | не потрібно — стан описаний lock-файлом |

---

## Тести

```bash
poetry run pytest -q        # 5 тестів, ~0.05 с
poetry run pytest -v
poetry run pytest -k delete
```

Навмисно мінімальний набір — базовий CRUD через HTTP: read, create, create з порожнім полем, create з
дублем, delete. Два файли, `tests/conftest.py` і `tests/test_app.py`.

Тести **ідентичні** в усіх трьох теках — це той самий набір, що і в
[`../02_pipenv/tests/`](../02_pipenv/tests/), і опис того, що саме перевіряється, є там. Жоден тест не
виходить у мережу.

Різниця лише в тому, **де живе конфігурація**. У `02_pipenv` для цього довелося завести три окремі
файли — `pytest.ini`, `requirements-dev.txt` і `bandit.yaml`. Тут усі три стають секціями одного
`pyproject.toml`:

```toml
[tool.poetry.group.dev.dependencies]
ruff = "^0.14.0"
pytest = "^9.1.1"
bandit = "^1.9.4"
mypy = "^1.18.0"

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
addopts = "-ra"

[tool.bandit]
exclude_dirs = [".venv", "tests"]

[tool.mypy]
python_version = "3.12"
check_untyped_defs = true
```

Чотири інструменти, один файл. Саме тому `setup.cfg`, `.flake8`, `mypy.ini` і `pytest.ini` поступово
зникають з проєктів.

---

## `bandit` — сканер безпеки

`ruff` шукає помилки стилю й логіки, `bandit` — **вразливості**: хардкоджені паролі, `shell=True`,
слабка криптографія, запити без таймауту.

```bash
poetry run bandit -c pyproject.toml -r .          # перевірити проєкт
poetry run bandit -c pyproject.toml -r . -ll      # лише severity >= medium
poetry run bandit -c pyproject.toml -r . -f json  # для CI
```

> Прапорець `-c pyproject.toml` **обов'язковий**. На відміну від ruff і pytest, bandit не читає
> `pyproject.toml` сам — без `-c` він просто просканує все, включно з `.venv`, і видасть сотні
> знахідок у чужому коді.

На цьому коді bandit не знаходить нічого. Ось що він повідомляє на навмисно поганому файлі:

```
[B602:subprocess_popen_with_shell_equals_true]  Severity: High
[B113:request_without_timeout]                  Severity: Medium
[B105:hardcoded_password_string]                Severity: Low
```

`B113` варто спробувати: приберіть `timeout` з `requests.get` у [`checks.py`](checks.py) — і bandit
почне лаятися. Запит без таймауту може висіти вічно й підвісити застосунок.

`exclude_dirs` виключає `tests`, бо `assert` там — це норма, а bandit позначає його як `B101`: в
оптимізованому байткоді `assert` зникає, тож покладатися на нього в робочому коді не можна.

### Демонстрація: що bandit насправді ловить

У теці [`bandit_demo/`](bandit_demo/) лежить файл [`insecure.py`](bandit_demo/insecure.py), написаний
**щоб його сканували, а не запускали**. Він виключений з `exclude_dirs`, тому звичайна перевірка
проєкту лишається чистою. Наведіть bandit на нього окремо:

```bash
poetry run bandit -r bandit_demo/
poetry run bandit -r bandit_demo/ -ll       # тільки medium і high
```

Результат — **33 знахідки, 29 різних правил**: 8 high, 11 medium, 14 low.

| Severity       | Правило     | Про що                                                                                                    |
| -------------- | ------------------ | -------------------------------------------------------------------------------------------------------------- |
| **High** | `B602`           | `subprocess(..., shell=True)` з інтерпольованим рядком — ін'єкція команд |
| **High** | `B501`           | `requests.get(..., verify=False)` — TLS без перевірки сертифіката                    |
| **High** | `B201`           | `app.run(debug=True)` — консоль Werkzeug відкрита в інтернет                        |
| **High** | `B301`           | `pickle.loads()` чужих байтів — це виконання чужого коду                    |
| Medium         | `B113`           | `requests.get()` без `timeout` — запит може висіти вічно                           |
| Medium         | `B608`           | SQL, зібраний форматуванням рядка                                                    |
| Medium         | `B506`           | `yaml.load()` замість `yaml.safe_load()`                                                            |
| Medium         | `B310`           | `urlopen()` без перевірки схеми — приймає і `file://`                            |
| Medium         | `B701`           | Jinja2 з`autoescape=False` — XSS                                                                           |
| Medium         | `B324`           | MD5 там, де потрібен SHA-256                                                                      |
| Low            | `B105`–`B107` | паролі й токени в коді                                                                       |
| Low            | `B108`           | передбачуваний шлях у`/tmp`                                                               |
| Low            | `B311`           | `random` замість `secrets` для токенів                                                    |
| Low            | `B110`           | `except Exception: pass`                                                                                     |

Файл побудований парами: поруч із небезпечною функцією стоїть безпечний варіант — `fingerprint` і
`fingerprint_safely`, `find_user` і `find_user_safely`, `list_dir` і `list_dir_safely`. Так видно не
лише що зламано, а й як лагодити.

Дві деталі, які добре обговорити на занятті:

- **`B110` не спрацьовує на `except OSError: pass`** — лише на широкому `except Exception`. Ловити
  конкретну помилку, яку ви свідомо ігноруєте, — нормально; ховати всі підряд — ні.
- **Команди в демо нешкідливі** (`echo`, `ls`). Bandit позначає **патерн**, а не корисне
  навантаження, тож навчальному файлу не потрібна руйнівна команда, щоб продемонструвати проблему.

> ⚠ Цей файл не можна запускати й не можна нічого з нього копіювати. Він існує рівно для того, щоб
> показати звіт сканера.

---

## Що таке `ruff` і навіщо він у групі `dev`

`ruff` — лінтер і форматер для Python, написаний на Rust. Замінює одразу набір інструментів: `flake8`
(+ десятки плагінів), `isort`, `black`, `pyupgrade`, `pydocstyle`, `autoflake`. Приблизно **1060
правил** в одному бінарнику.

Дві половини, які легко переплутати:

- **`ruff check`** — шукає *проблеми*: невикористані імпорти, недосяжний код, підозрілі конструкції;
- **`ruff format`** — переписує *оформлення*: лапки, довжину рядків, відступи. Сумісний з `black`.

```bash
poetry run ruff check .              # знайти проблеми
poetry run ruff check --fix .        # виправити те, що можна, автоматично
poetry run ruff check --statistics . # скільки чого
poetry run ruff check --watch .      # стежити за файлами й перевіряти на льоту
poetry run ruff rule F541            # пояснити конкретне правило

poetry run ruff format .             # відформатувати
poetry run ruff format --diff .      # показати зміни, нічого не чіпаючи
poetry run ruff format --check .     # для CI: впасти, якщо код не відформатовано
```

На коді цієї теки `ruff check .` знаходить справжню помилку:

```
F541 [*] f-string without any placeholders
  --> app.py:32:19
   |
32 |         message = f"Could not reach the Cloudflare status API."
   |                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
help: Remove extraneous `f` prefix
```

Префікс `f` лишився після того, як з рядка прибрали підстановку. Код працює, але `f` тепер бреше.
`[*]` означає, що `--fix` виправить це сам. Уся перевірка займає **49 мс**.

Налаштування живуть у тому ж `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]
```

**Чому саме в групі `dev`, а не в `[project] dependencies`:** без `ruff` застосунок працює. Він
потрібен тому, хто пише код, а не тому, хто його запускає. Тому на деплої —
`poetry install --only main`, і лінтер в образ не потрапляє.

> Детально про лінтери й форматери — окрема тема в [`../06_formatting/`](../06_formatting/).

---

## `mypy` — статична перевірка типів

Третій інструмент у dev-групі, і він відповідає на питання, якого не ставлять ні `ruff`, ні `bandit`:
**чи узгоджені між собою типи**.

Анотації (`name: str`, `-> dict[str, str]`) інтерпретатор **не перевіряє**. Він кладе їх у
`__annotations__` і йде далі:

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

greet(42)          # Python це виконає без жодної скарги
```

`mypy` — це те, що робить анотації справжніми:

```
error: Argument 1 to "greet" has incompatible type "int"; expected "str"  [arg-type]
```

Ключове: він **не запускає** ваш код. Він читає його як текст, будує граф типів і шукає суперечності.
Тому він бачить гілку `if`, у яку ви жодного разу не заходили в тестах.

### Запуск

```bash
poetry run mypy                      # усе, що перелічено в [tool.mypy] files
poetry run mypy app.py               # один файл
poetry run mypy --strict             # найсуворіший режим
poetry run mypy --install-types      # доставити відсутні стаби
poetry run mypy --no-incremental     # ігнорувати кеш
```

На відміну від `bandit`, mypy **сам знаходить** `pyproject.toml` — прапорець `-c` не потрібен.

Скільки це коштує часу (та сама тека, ті самі 6 файлів):

| Команда                       | Час            |
| ------------------------------------ | ----------------- |
| `ruff check .`                     | **0,05 с** |
| `mypy` (перший запуск) | **5,1 с**  |
| `mypy` (з `.mypy_cache/`)       | **0,25 с** |

Різниця у 100 разів — не недбалість авторів. `ruff` дивиться на синтаксичне дерево одного файлу;
mypy розбирає типи **всього, що ви імпортуєте**, включно зі stdlib і сторонніми пакетами. Результат
він кешує в `.mypy_cache/` — цю теку додано в `.gitignore`.

### `types-requests` — і чому самого `mypy` мало

У dev-групі поруч із `mypy` з'явився ще один пакет:

```toml
mypy = "^1.18.0"
types-requests = "^2.33.0.20260712"
```

`requests` **не постачає інформації про типи**: у ньому немає файлу-маркера `py.typed`. Без стабів
mypy вважає, що `requests.get(...)` повертає `Any`, і вся перевірка нижче за цим рядком просто
зникає. Стаби для таких пакетів живуть окремо — у репозиторії **typeshed** — і ставляться як
`types-<назва>`:

```bash
poetry run mypy --install-types     # mypy сам скаже, чого бракує, і поставить
```

Це dev-залежність: на продакшні ніхто не імпортує `types-requests`.

> Сучасні пакети роблять інакше — кладуть `py.typed` усередину себе, і тоді нічого доставляти не
> треба. Так роблять `pydantic`, `fastapi`, `sqlalchemy` 2.x, `flask`. Тому для Flask стаби тут і не
> знадобилися, а для `requests` — знадобилися.

### Налаштування

```toml
[tool.mypy]
python_version = "3.12"
files = ["app.py", "checks.py", "services.py", "incidents.py", "tests"]
check_untyped_defs = true
warn_unused_ignores = true
warn_redundant_casts = true
exclude = ["mypy_demo/", "bandit_demo/", "conflict/", "test_env/"]
```

Два рядки варто розібрати.

**`check_untyped_defs` — найважливіший прапорець на старті.** За замовчуванням mypy **повністю
пропускає тіло функції, у якої немає жодної анотації**. Тобто на файлі без підказок він не знайде
нічого й радісно скаже `Success` — а новачок зробить висновок, що код ідеальний. Цей прапорець каже
«тіло все одно перевіряй, параметри вважай `Any`». Досить однієї анотації в сигнатурі, щоб функція
почала вважатися типізованою.

**`exclude` діє лише на обхід тек.** Файл, названий у командному рядку явно, перевіряється завжди —
саме тому `mypy mypy_demo/broken.py` працює, а звичайний `mypy` лишається чистим. Той самий принцип,
що і в `exclude_dirs` у bandit.

### Що знаходить `--strict` на цьому коді

Звичайний запуск чистий:

```bash
poetry run mypy
# Success: no issues found in 6 source files
```

`--strict` вмикає близько десятка прапорців одразу — і одразу ж знаходить 15 місць:

```
services.py:33:  Returning Any from function declared to return "dict[str, str]"  [no-any-return]
incidents.py:26: Missing type arguments for generic type "dict"                   [type-arg]
checks.py:28:    Missing type arguments for generic type "dict"                   [type-arg]
app.py:18:       Function is missing a return type annotation                     [no-untyped-def]
tests/conftest.py:26: Function is missing a type annotation                       [no-untyped-def]
Found 15 errors in 6 files (checked 6 source files)
```

Три різні претензії, і кожна справедлива:

- **`[no-untyped-def]`** — Flask-в'юхи й тести не анотовані взагалі;
- **`[type-arg]`** — `-> dict` і `-> list[dict]` у `checks.py` та `incidents.py`: «словник **чого**?»
  Саме той словник, форму якого docstring описує словами, а код — ніяк;
- **`[no-any-return]`** — `json.loads()` у `services.py` повертає `Any`, а функція обіцяла
  `dict[str, str]`. Ніхто цього не звіряє.

**Код навмисно не виправлений.** Він побайтово однаковий у
[`../02_pipenv/`](../02_pipenv/), тут і в [`../04_uv/`](../04_uv/) — усі три теки відрізняються лише
описом залежностей. Ці 15 помилок — не поломка, а вправа: спробуйте прибрати їх самі й подивіться,
скільки з них вимагають реального рішення (`TypedDict` для результату перевірки), а скільки
дописуються механічно.

### Демонстрація: `mypy_demo/broken.py`

У теці [`mypy_demo/`](mypy_demo/) лежить файл [`broken.py`](mypy_demo/broken.py) — рівно той самий
прийом, що і з [`bandit_demo/`](bandit_demo/): написаний, **щоб його перевіряли, а не запускали**.
Теку виключено в `[tool.mypy]`, `[tool.ruff]` і `[tool.bandit]`, тож звичайні перевірки лишаються
чистими. Наведіть mypy на нього окремо:

```bash
poetry run mypy mypy_demo/broken.py
```

Результат — **46 помилок, 33 різні коди**.

Головне, що варто сказати на занятті: **у файлі немає жодної синтаксичної помилки**. Усе це —
коректний Python, який інтерпретатор без вагань почне виконувати.

Перші два рядки файлу — це **inline-конфігурація**, окрема можливість mypy:

```python
# mypy: disallow-untyped-defs, disallow-any-generics, warn-return-any
# mypy: warn-unreachable, strict-equality
```

Так суворі перевірки вмикаються для одного файлу, незалежно від `[tool.mypy]`. У реальних проєктах
цим користуються навпаки — щоб **послабити** правила в одному важкому модулі, не чіпаючи весь проєкт.

| Група                         | Коди                                                                                         | Про що                                                                            |
| ---------------------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| **Найчастіші**     | `arg-type`, `return-value`, `assignment`                                                   | не той тип у виклику, у`return`, у присвоєнні            |
| **Найцінніший**   | `union-attr`                                                                                   | `.upper()` на значенні, яке може бути `None`                  |
| Атрибути й виклики | `attr-defined`, `call-arg`, `call-overload`, `override`, `abstract`                    | друкарські помилки, зміна API, зламаний контракт |
| Контейнери               | `index`, `list-item`, `dict-item`, `operator`, `type-var`                              | не той елемент, не той індекс, не той операнд       |
| Анотації                   | `no-untyped-def`, `type-arg`, `var-annotated`, `valid-type`                              | анотації немає, вона неповна або це не тип           |
| `Any` тече                   | `no-any-return`, `import-untyped`, `import-not-found`                                      | межа програми, за якою перевірки немає                 |
| Мертвий код              | `unreachable`, `return`, `comparison-overlap`, `truthy-function`, `func-returns-value` | гілка, яка ніколи не виконається                            |
| `TypedDict`                      | `typeddict-item`, `typeddict-unknown-key`, `literal-required`                              | словник із фіксованою формою                                  |
| Імена                         | `name-defined`, `no-redef`                                                                   | не існує / визначено двічі                                        |
| Решта                         | `misc`, `unused-ignore`, `unreachable`                                                     | `__init__ -> int`, забутий `# type: ignore`                                 |

Файл побудований парами, як і `bandit_demo/insecure.py`: поруч із помилковою функцією стоїть
виправлена — `show` і `show_safely`, `load_services` і `load_services_safely`, `seen` і `seen_ok`.

Три місця, які варто розібрати повільно:

**1. `[union-attr]` — те, заради чого все це.**

```python
def find_service(name: str, table: dict[str, str]) -> str | None:
    return table.get(name)

def show(name: str, table: dict[str, str]) -> str:
    url = find_service(name, table)
    return url.upper()          # error: Item "None" of "str | None" has no attribute "upper"
```

Функція чесно оголосила, що може повернути `None`. Тепер **кожен**, хто про це забув, отримує
помилку до запуску. Це і є той `AttributeError: 'NoneType' object has no attribute ...`, який ви
інакше побачите о третій ночі. Виправлення — звузити тип через `if url is None:`; mypy читає `if` і
замовкає.

**2. `[no-any-return]` — межа, за якою mypy сліпий.**

```python
def load_services(path: str) -> dict[str, str]:
    with open(path) as handle:
        return json.loads(handle.read())     # [no-any-return]
```

`json.loads` повертає `Any` — інакше й бути не може, у JSON немає типів. Anything, що прийшло з `Any`,
для mypy невидиме. Правильна відповідь не «поставити `# type: ignore`», а **перевірити форму даних
один раз, на вході** — саме те, за що відповідає `pydantic` у [`../../pydantic_ex/`](../../pydantic_ex/).

**3. `[unreachable]` і `[comparison-overlap]` — помилки, а не педантизм.**

```python
def is_ok(status: int) -> bool:
    return status == "200"      # завжди False; тести на це не спрацюють
```

Порівняння `int` із `str` не падає — воно **тихо повертає `False`**. Без mypy це знайдуть у продакшні.

### Чого mypy **не** ловить

Остання секція `broken.py` — навмисно протилежна: код, який проходить перевірку й падає на запуску.

```python
def crash_on_empty(rows: list[str]) -> str:
    return rows[0]                       # IndexError на []

def crash_on_zero(total: int, count: int) -> float:
    return total / count                 # ZeroDivisionError

def lie_with_cast(payload: object) -> str:
    return cast(str, payload).upper()    # cast — це обіцянка, а не перевірка
```

`list[str]` нічого не каже про **кількість** елементів, `int` — про його **значення**, а `cast()`
просто наказує mypy повірити вам на слово. Зелений `mypy` означає «анотації несуперечливі», а не
«програма працює». Тому mypy не замінює тести — він працює **разом** із ними.

### Як вводити в наявний проєкт

Ніхто не вмикає `--strict` на робочому коді в перший день — ви отримаєте тисячу помилок і вимкнете
інструмент назавжди. Правильний порядок:

1. `check_untyped_defs = true` — нічого не анотуючи, побачити реальні помилки в тілах функцій;
2. анотувати **сигнатури** — mypy сам виведе типи всередині; анотації потрібні на межах;
3. `disallow_untyped_defs = true` **на один модуль** через `[[tool.mypy.overrides]]`;
4. коли модуль чистий — розширювати список;
5. `strict = true`, коли чистий увесь проєкт.

Послаблення для окремого модуля виглядає так:

```toml
[[tool.mypy.overrides]]
module = ["legacy.*"]
disallow_untyped_defs = false
ignore_errors = true
```

### mypy проти інших перевіряльників

| Інструмент                  | Що це                                                                                                       |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **mypy**                        | еталонна реалізація, розвивається разом зі стандартом типів |
| **pyright** / **Pylance** | від Microsoft; це те, що підкреслює код у VS Code. Швидший                        |
| **ty**, **pyrefly**       | нові перевіряльники на Rust — швидкі, ще дозрівають                      |
| **pydantic**                    | не конкурент: він перевіряє**дані під час виконання**           |

Типова робоча схема — `pyright` у редакторі для миттєвого підсвічування плюс `mypy` у CI як умова
проходження.

> Про самі анотації — синтаксис, дженерики, протоколи — окрема тема в
> [`../07_typing/`](../07_typing/).

---

## pre-commit — запускати ruff, bandit і mypy автоматично

`pre-commit` вішає перевірки на git-хук: вони спрацьовують на `git commit` і **лише для тих файлів,
що ви застейджили**. Конфігурація — [`.pre-commit-config.yaml`](.pre-commit-config.yaml).

```bash
poetry run pre-commit install          # вписати хук у .git/hooks (один раз)
poetry run pre-commit run --all-files  # прогнати зараз по всьому
poetry run pre-commit autoupdate       # підняти версії в rev:
poetry run pre-commit run ruff-check   # тільки один хук
```

Чотири хуки: `ruff-check` (шукає проблеми й виправляє), `ruff-format` (форматує), `bandit` (безпека),
`mypy` (типи).

### Чотири деталі, які варто знати

**1. Хуки ставляться на весь git-репозиторій, а не на теку.** У цьому репозиторії лежить кілька
проєктів, тому `.pre-commit-config.yaml` тут містить фільтр:

```yaml
files: ^module01/03_poetry/
exclude: ^module01/03_poetry/(bandit_demo|mypy_demo|\.venv)/
```

Без нього хуки з цієї теки перевіряли б і дві інші копії того самого застосунку. З кореня репозиторію
конфіг треба вказувати явно:

```bash
pre-commit run --config module01/03_poetry/.pre-commit-config.yaml --all-files
```

**2. `--exit-non-zero-on-fix` — не косметика.** З простим `--fix` ruff виправляє файл і завершується
кодом 0. Хук рапортує `Passed`, коміт проходить, а ваш код мовчки переписали. Перевірено: з голим
`--fix` зламаний файл давав `Passed`, з прапорцем — `Failed`.

**3. `--all-files` означає «усі файли, які знає git».** Поки тека не додана в git, хуки покажуть
`(no files to check) Skipped`. Це не поломка конфігурації — просто `git add` ще не робили.

**4. Хук mypy живе у власному оточенні — і це найпоширеніша пастка.** pre-commit будує кожному хуку
**окремий virtualenv** і про Poetry нічого не знає. Той mypy не бачить ні `flask`, ні
`types-requests`, тому кожен `import flask` для нього нерозв'язний, а всі типи Flask перетворюються
на `Any`. Сторонні пакети доводиться перелічувати руками:

```yaml
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.20.2
    hooks:
      - id: mypy
        additional_dependencies: [flask==3.1.3, types-requests==2.33.0.20260712]
        args: [--config-file, module01/03_poetry/pyproject.toml]
```

Цей список **не синхронізується** з `pyproject.toml` автоматично й з часом розходиться з ним. Саме
тому багато команд не вішають mypy на git-хук узагалі, а запускають його в CI, де оточення справжнє:

```bash
poetry install && poetry run mypy
```

`--config-file` тут обов'язковий з тієї ж причини, що і в bandit: хук запускається з **кореня
репозиторію**, а не з теки проєкту. Шляхи до файлів pre-commit підставляє сам, тому список `files` з
`[tool.mypy]` у цьому режимі не використовується.

### Що хуки реально ловлять

Перевірено на навмисно зіпсованому коді:

```python
def broken():
    msg = f"no placeholders"          # ruff: F541
    return os.system("echo " + msg)   # bandit: B605
```

```
ruff check....................Failed
bandit........................Failed
>> Issue: [B605:start_process_with_a_shell] Starting a process with a shell
```

На чистому коді теки всі чотири проходять:

```
ruff check...............................................................Passed
ruff format..............................................................Passed
bandit...................................................................Passed
mypy.....................................................................Passed
```

`bandit_demo/` і `mypy_demo/` виключено з хуків навмисно: `ruff --fix` полагодив би саме те, що там
має лишатися зламаним, а `mypy` завалив би кожен коміт своїми 46 помилками.

---

## Перестворити оточення

У pip venv лежить там, де ви його створили: `.venv/` у теці проєкту, і видалити його — це `rm -rf`.
У Poetry venv — **не файл у проєкті, а керований об'єкт**, і його шлях залежить від конфігурації.
Тому перше питання завжди: «а яке саме оточення я зараз використовую?»

```bash
poetry env info          # повна інформація про поточне оточення
poetry env info -p       # тільки шлях (він же --path)
poetry env list          # усі оточення, які Poetry веде для цього проєкту
```

> **Пастка, на якій легко згубити півгодини.** `poetry env info` не просто повідомляє шлях — він
> **створює оточення**, якщо його ще немає. Так само робить `poetry env activate`. Тобто після
> `poetry env remove --all` достатньо запитати `poetry env info --path`, і оточення знову існує
> (порожнє, з одним `pip`). Перевірено на Poetry 2.4.1. Якщо ви розбираєтесь, «звідки взялося це
> оточення» — можливо, його створила ваша ж діагностична команда.

За замовчуванням (`virtualenvs.in-project` не виставлений) Poetry тримає оточення **не в проєкті**,
а у своєму каталозі, з іменем на кшталт `statusboard-8SkKN7Wn-py3.12`:

```
~/Library/Caches/pypoetry/virtualenvs/     # macOS
~/.cache/pypoetry/virtualenvs/             # Linux
```

Хеш у назві — від абсолютного шляху до проєкту. Практичний наслідок: **перемістили теку проєкту —
отримали нове оточення**, а старе лишилося висіти в кеші.

### Власне перестворення

```bash
poetry env remove --all     # видалити всі оточення цього проєкту
poetry install              # створити нове з poetry.lock
```

`--all` тут важливий: якщо в проєкту накопичилося кілька оточень (різні версії Python, зміна шляху),
`poetry install` може полагодити не те, на яке ви дивитесь. Видалити одне конкретне — за іменем зі
`poetry env list`:

```bash
poetry env remove statusboard-8SkKN7Wn-py3.12
```

### Коли перестворювати не потрібно

Здебільшого — не потрібно, і це головна перевага lock-файлу:

| Задача                                                                | Команда                                                                                          |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Привести оточення точно до lock                      | `poetry sync` — доставить, чого не було, **і видалить зайве** |
| Перевстановити залежності, не чіпаючи venv | `poetry install` (ідемпотентна, видаляти нічого не треба)            |
| Перерахувати версії з нуля                           | `poetry lock --regenerate && poetry install`                                                          |
| Перейти на іншу версію Python                            | `poetry env use python3.13 && poetry install`                                                         |
| Тримати venv у теці проєкту                              | `poetry config virtualenvs.in-project true` (далі `poetry install`)                             |
| Скинути завантажені артефакти                    | `poetry cache clear --all pypi`                                                                       |

Різниця між `poetry install` і `poetry sync` — та сама, про яку йшлося у
[`../02_pipenv/`](../02_pipenv/README.md): `install` **ніколи нічого не видаляє**. Прибрали пакет із
`pyproject.toml`, зробили `poetry install` — він залишиться в оточенні. У CI потрібен `poetry sync`:

```bash
poetry run pip install httpx     # сторонній пакет, якого немає в poetry.lock
poetry sync
```

```
  - Removing anyio (4.14.2)
  - Removing h11 (0.16.0)
  - Removing httpcore (1.0.9)
  - Removing httpx (0.28.1)
  - Removing typing-extensions (4.16.0)
```

Для перевірки беріть саме пакет, якого немає в lock-файлі. З `rich` дослід не вийде: він у цьому
проєкті присутній законно, як залежність `bandit` із dev-групи, і `poetry sync` його не торкнеться.

> `poetry install --sync` у Poetry 2.x **позначений застарілим** — тепер це окрема команда
> `poetry sync`.

### Активація

Оточення можна не активовувати взагалі: `poetry run python app.py` і `poetry run pytest` роблять це
самі. Якщо все ж потрібна активована оболонка:

```bash
eval $(poetry env activate)
```

`poetry env activate` **не активує** оточення (дочірній процес не може змінити ваш shell) — він
**друкує команду**, яку треба виконати; тому `eval`. І він створює оточення, якщо його ще немає.
Команди `poetry shell`, яка була у Poetry 1.x, у 2.x більше немає.

### Особливість цієї теки

`statusboard` оголошений як `package-mode = false`, тому `poetry install` керує лише залежностями й
не намагається збирати сам проєкт — ключ `--no-root` тут не потрібен. У проєкті, який справді є
пакетом (як `zoo_api/` у корені репозиторію), `poetry install` за замовчуванням встановлює і сам
проєкт теж.

---

## Довідник команд

| Команда                        | Що робить                                                                         |
| ------------------------------------- | ----------------------------------------------------------------------------------------- |
| `poetry new --src myproj`           | створити новий проєкт                                                  |
| `poetry init`                       | створити`pyproject.toml` у наявній теці                             |
| `poetry install`                    | створити venv (якщо треба) і поставити залежності    |
| `poetry install --only main`        | без dev-груп — для продакшну                                          |
| `poetry sync`                       | привести середовище точно до lock, видаливши зайве |
| `poetry add requests`               | додати залежність і оновити lock                                  |
| `poetry add --group dev pytest`     | додати dev-залежність                                                     |
| `poetry remove requests`            | прибрати залежність                                                     |
| `poetry lock`                       | перерахувати lock без встановлення                             |
| `poetry update`                     | оновити все в межах обмежень                                      |
| `poetry update flask`               | оновити один пакет                                                        |
| `poetry show`                       | список встановленого                                                   |
| `poetry show --tree`                | дерево залежностей                                                       |
| `poetry show --why urllib3`         | хто саме притягнув цей пакет                                      |
| `poetry check`                      | перевірити коректність`pyproject.toml`                             |
| `poetry check --lock`               | перевірити, чи lock не застарів                                     |
| `poetry run <cmd>`                  | виконати команду в середовищі                                   |
| `poetry env info` / `--path`      | де лежить venv (**створює його**, якщо немає)           |
| `poetry env list`                   | усі середовища цього проєкту                                     |
| `poetry env use python3.13`         | перейти на іншу версію Python                                          |
| `poetry env activate`               | надрукувати команду активації (`eval $(...)`)                |
| `poetry env remove --all`           | видалити середовища проєкту                                      |
| `poetry lock --regenerate`          | перерахувати lock з нуля                                                 |
| `poetry cache clear --all pypi`     | очистити кеш завантажених пакетів                           |
| `poetry export -f requirements.txt` | згенерувати`requirements.txt` (потрібен плагін)                |
| `poetry build`                      | зібрати wheel і sdist (лише якщо не`package-mode = false`)            |
| `poetry publish`                    | залити на PyPI                                                                    |

Найкорисніша тут — `poetry show --why urllib3`. Це та команда, яка потрібна о другій ночі, коли
сканер безпеки лається на пакет, про який ви вперше чуєте, і треба зрозуміти, хто його притягнув.

---

## Що Poetry дав порівняно з pip

1. **Lock-файл із хешами** — відтворюваність і захист від підміни пакета.
2. **Розділення прямих і транзитивних залежностей** — у `pyproject.toml` рівно два рядки, у
   `poetry.lock` — усі п’ятнадцять пакетів.
3. **Групи залежностей** — dev-інструменти не їдуть у продакшн.
4. **`poetry sync`** — середовище можна привести до опису, а не тільки доповнити.
5. **Збірка і публікація** — `poetry build`, `poetry publish` (для бібліотек).
6. **venv створюється сам.**

Чого Poetry **не** дає:

- **швидкості.** `poetry lock` на цьому крихітному проєкті — близько **1,9 секунди** з прогрітим кешем.
  На реальному проєкті з десятками залежностей це десятки секунд, іноді хвилини;
- керування версіями самого Python (для цього досі потрібні `pyenv` або `uv python`).

Обидва пункти закриває наступна папка.

---

Далі: [`../04_uv/`](../04_uv/) — той самий застосунок і **той самий `pyproject.toml`**, але резолвер,
який робить ту саму роботу за 93 мілісекунди замість 2,6 секунди. Заміри й скрипт, який їх робить, —
у [`../07_compare/`](../07_compare/).
