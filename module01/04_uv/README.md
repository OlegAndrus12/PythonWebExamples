# 04 — uv

**Той самий `statusboard`.** Код не змінився ні тут, ні в [`../03_poetry/`](../03_poetry/) — ті самі
`app.py`, `checks.py`, `services.py`, `incidents.py`, ті самі шаблони й CSS.

Більше того: `[project]` у `pyproject.toml` **той самий**, що й у Poetry. Це PEP 621 — стандарт, а не
формат конкретного інструменту. Відрізняються лише lock-файл і команди.

|                                         | 02 — pip            | 03 — Poetry              | 04 — uv (ця)                                  |
| --------------------------------------- | -------------------- | ------------------------- | ------------------------------------------------ |
| Маніфест                        | `requirements.txt` | `pyproject.toml`        | `pyproject.toml` (**той самий**) |
| Lock                                    | —                   | `poetry.lock`           | `uv.lock`                                      |
| Групи                              | —                   | `[tool.poetry.group.*]` | `[dependency-groups]` (PEP 735)                |
| `lock` на цьому проєкті | —                   | **2620 мс**       | **93 мс**                                |
| Ставить сам Python            | ні                 | ні                      | **так**                                 |
| Написаний на                 | Python               | Python                    | Rust                                             |

---

## Встановлення uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# або: brew install uv
# або: pipx install uv

uv --version
```

---

## Запуск

```bash
cd module01/04_uv

uv run flask --app app run --debug
```

І все. Одна команда.

`uv run` перед запуском сам робить усе потрібне: знаходить (або **завантажує**) відповідний Python,
створює `.venv/`, читає `uv.lock`, доставляє те, чого бракує, і аж тоді запускає команду. Окремий
`uv sync` викликати не обов’язково — але можна:

```bash
uv sync              # привести .venv точно у стан uv.lock
uv sync --no-dev     # без dev-групи, для продакшну
```

> **`uv sync` синхронізує, а не доповнює.** Пакет, який ви поставили руками й немає в lock, буде
> **видалено**. Це поведінка `poetry sync`, а не `pip install -r`.

Venv створюється в `.venv/` у теці проєкту — на відміну від Poetry, який за замовчуванням ховає його
в кеш.

---

## `pyproject.toml`

```toml
[project]
name = "statusboard"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "flask>=3.1.0,<4.0.0",
    "requests>=2.32.3,<3.0.0",
]

[dependency-groups]
dev = ["ruff>=0.14.0"]
```

Порівняйте з `03_poetry/pyproject.toml`. Блок `[project]` ідентичний. Різниця тільки в тому, як
описані dev-залежності:

- Poetry: `[tool.poetry.group.dev.dependencies]` — секція під конкретний інструмент;
- uv: `[dependency-groups]` — **PEP 735**, стандарт, який уже підтримують і uv, і Poetry (2.x), і pip.

Секції `[build-system]` немає. Саме її відсутність означає «це застосунок, а не пакет»: uv керує
середовищем і не намагається нічого зібрати. Аналог `package-mode = false` у Poetry.

### Розширений приклад

У цій теці лежить [`pyproject.reference.toml`](pyproject.reference.toml) — пара до
[`../03_poetry/pyproject.reference.toml`](../03_poetry/pyproject.reference.toml). Блок `[project]` там
і тут ідентичний, тож у цьому файлі він скорочений, а вся увага на тому, **що в Poetry живе під
`[tool.poetry]`, а в uv називається інакше**: `[dependency-groups]`, `[tool.uv.sources]`,
`[[tool.uv.index]]`, `[tool.uv.workspace]`, `environments`, `conflicts`, `constraint-dependencies`.

Файл робочий — перевіряється так:

```bash
mkdir -p /tmp/uref && cp pyproject.reference.toml /tmp/uref/pyproject.toml
cd /tmp/uref && uv lock && uv tree --depth 1
```

### Чи сумісний синтаксис Poetry з uv

Частково. Перевірено:

| Запис                                             | uv                                                                                              |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| `"flask (>=3.1.0,<4.0.0)"` — Poetry у дужках | **працює** — це валідний PEP 508                                         |
| `"flask^3.1.0"` — caret                             | **падає**: `` `project.dependencies[0]` must be pep508 ``                            |
| `[tool.poetry.group.dev.dependencies]`               | **мовчки ігнорується** — пакети не встановлюються |

Останній рядок найнебезпечніший: помилки немає, `uv sync` відпрацьовує успішно, просто dev-залежності
тихо зникають. Тому при переході з Poetry групи треба переписати в `[dependency-groups]` руками.

Відповідники caret, якщо переносите вручну:

```
^1.2.3   →   >=1.2.3,<2.0.0
^0.2.3   →   >=0.2.3,<0.3.0
~1.2.3   →   ~=1.2.3
```

---

## Як створити `pyproject.toml` з нуля

```bash
uv init statusboard          # застосунок (за замовчуванням)
uv init --lib statusboard    # бібліотека: src/-розкладка + [build-system]
uv init --bare statusboard   # тільки pyproject.toml, без жодних зайвих файлів
uv init                      # у поточній теці
```

`uv init --app` створює:

```
statusboard/
├── .gitignore
├── .
python-version      ← якої версії Python вимагає проєкт
├── README.md
├── main.py
└── pyproject.toml
```

```toml
[project]
name = "statusboard"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []
```

Дві відмінності від `poetry new`, які видно одразу:

- **немає `[build-system]`** — це застосунок, збирати нічого не треба;
- **є `.python-version`** — файл, який фіксує інтерпретатор. `uv run` прочитає його і, якщо такої
  версії немає в системі, **завантажить її сам**. Poetry так не вміє.

`--bare` дає лише `pyproject.toml` без `main.py`, `README.md` і `.gitignore` — саме те, що потрібно,
коли код у теці вже є.

---

## Як перейти з `requirements.txt`

На відміну від Poetry, у uv це **вбудована команда**:

```bash
uv init --bare --name statusboard
uv add -r requirements.txt
```

Усе. Перевірено на нашому файлі — з

```
Flask==3.1.0
requests==2.32.3
```

виходить

```toml
dependencies = [
    "flask==3.1.0",
    "requests==2.32.3",
]
```

плюс `uv.lock` з 14 пакетами й готовий `.venv/`. Коментарі й порожні рядки uv розбирає сам — ніяких
`grep` і `tr`, як довелося робити для Poetry.

Dev-залежності:

```bash
uv add --dev -r requirements-dev.txt
```

### Та сама пастка, що і в Poetry

`==` переноситься дослівно. У `requirements.txt` це було правильно, у `pyproject.toml` — ні:

| Файл           | Що містить                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| `pyproject.toml` | **діапазони** — межі, у яких ви згодні оновлюватися |
| `uv.lock`        | **точні версії** — те, що реально встановлено            |

Подвійна фіксація означає, що `uv lock --upgrade` не зможе підняти навіть патч безпеки. Тому після
міграції межі розслаблюють:

```bash
uv add "flask>=3.1.0,<4.0.0" "requests>=2.32.3,<3.0.0"
```

### Зворотний шлях

```bash
uv export -o requirements.txt                    # з хешами
uv export --no-hashes --no-dev -o requirements.txt
uv pip compile pyproject.toml -o requirements.txt
```

`uv export` — вбудований, без плагінів (Poetry для цього потребує `poetry-plugin-export`).

---

## Як додати пакет у конкретну групу

```bash
uv add requests                  # у [project] dependencies — робоча залежність
uv add --dev pytest              # у групу dev (скорочення для --group dev)
uv add --group docs mkdocs       # у довільну групу; створиться, якщо її немає
uv add --group typing mypy

uv add --optional postgres psycopg   # у extras, а не в групу — це різні речі

uv remove --group docs mkdocs    # прибрати саме з цієї групи
```

Результат у `pyproject.toml`:

```toml
[dependency-groups]
dev = ["bandit>=1.9.4", "pytest>=9.1.1", "ruff>=0.14.0"]
docs = ["mkdocs>=1.6.1"]
```

**Групи проти extras** — різниця, яку легко пропустити:

|                                                      | Кому потрібно                         | Чи їде у зібраний пакет |
| ---------------------------------------------------- | ------------------------------------------------- | ------------------------------------------ |
| `[dependency-groups]` (`--group`)                | вам, поки ви пишете код         | **ні**                             |
| `[project.optional-dependencies]` (`--optional`) | тому, хто ставить ваш пакет | **так**                           |

`pytest` — це група. «Підтримка Postgres» — це extra.

Встановлення й виключення:

```bash
uv sync                      # main + групи з default-groups (типово ["dev"])
uv sync --group docs         # додати ще одну
uv sync --no-dev             # без dev
uv sync --only-group docs    # тільки одна група, без робочих залежностей
uv sync --all-groups         # усі групи
```

Які групи ставляться без прапорців — керується маніфестом:

```toml
[tool.uv]
default-groups = ["dev", "typing"]
```

---

## Швидкість — і чому це не косметика

Реальні заміри на цьому проєкті (34 пакети), кеш прогрітий:

```
poetry lock   2620 мс        poetry install   2340 мс
uv lock         93 мс        uv sync           133 мс
```

Різниця приблизно у **28 разів** на резолюції й у **18** на встановленні. Перевірте самі:

```bash
rm uv.lock && time uv lock
```

Чому так:

- uv написаний на Rust, а не на Python;
- він має глобальний кеш пакетів і використовує **жорсткі посилання** замість копіювання файлів — тому
  другий venv з тими самими залежностями створюється майже миттєво й майже не займає диска;
- резолвер від початку проєктований під паралельні мережеві запити.

На проєкті з 34 пакетів це «приємно». На CI, де lock перевіряється на кожен push, або на монорепі з
двома сотнями залежностей — це різниця між секундами й хвилинами на кожному запуску: на наборі з
79 пакетів той самий розрив на резолюції росте до **48 разів**.

Ці цифри не з рекламного слайда — вони з [`../07_compare/`](../07_compare/), де лежить скрипт, який
їх зміряв, разом із описом того, що саме він робить і чого ці заміри **не** показують (наприклад,
на порожньому кеші uv не завжди найшвидший — там усі три чекають на мережу).

---

## uv замінює не тільки Poetry

Це головна ідея інструменту: один бінарник замість п’яти.

| Що робили раніше                     | Чим uv                              |
| -------------------------------------------------- | -------------------------------------- |
| `pyenv install 3.13`                             | `uv python install 3.13`             |
| `python -m venv .venv`                           | `uv venv`                            |
| `pip install -r requirements.txt`                | `uv pip install -r requirements.txt` |
| `pip-tools` / `pip-compile`                    | `uv lock`                            |
| `pipx install ruff`                              | `uv tool install ruff`               |
| `poetry install`                                 | `uv sync`                            |
| одноразовий запуск утиліти | `uvx ruff check .`                   |

### Python ставиться сам

```bash
uv python list
uv python install 3.13
uv run --python 3.13 python -V
```

Якщо в `requires-python` вказано версію, якої в системі немає, `uv run` **завантажить її сам**. Ні
Poetry, ні pip так не вміють — там потрібен `pyenv` окремо. Детальніше — у розділі
[«Керування версіями Python»](#керування-версіями-python) нижче.

### `uvx` — запустити, не встановлюючи

```bash
uvx ruff check .
```

Запускає `ruff`, не додаючи його до встановлених утиліт — у `uv tool list` він не з'явиться.

Але середовище **не видаляється**, а лишається в кеші й перевикористовується: перший запуск
повільний, наступні — миттєві. Керування кешем:

```bash
uv cache dir      # ~/.cache/uv
uv cache prune    # прибрати лише недосяжні об'єкти
uv cache clean    # очистити повністю
uvx --no-cache ruff check .
```

Те саме робить `pipx run` — детальніше в [`../05_other_tools/`](../05_other_tools/).

### Режим сумісності з pip

```bash
uv pip install flask
uv pip freeze
uv pip compile pyproject.toml -o requirements.txt
```

`uv pip` навмисно повторює інтерфейс pip. Це дозволяє прискорити наявний проєкт, не переписуючи його
під нову систему: замінили `pip` на `uv pip` — і все.

---

## Керування версіями Python

uv — єдиний з трьох інструментів, який сам **завантажує** інтерпретатори. Poetry і pipenv лише шукають
наявний, тому поруч з ними тримають `pyenv`. У uv це вбудовано, і версію можна задати на трьох
незалежних рівнях: одна команда → одна тека → уся машина.

### Що вже є на машині

```bash
uv python list                    # усе, що видно: і завантажене uv, і системне
uv python list --only-installed   # без варіантів, доступних до завантаження
uv python dir                     # ~/.local/share/uv/python
uv python find 3.12               # шлях до конкретного інтерпретатора
```

```
$ uv python list --only-installed
cpython-3.14.3-macos-x86_64-none   ~/.local/share/uv/python/cpython-3.14-.../bin/python3.14
cpython-3.13.13-macos-x86_64-none  /usr/local/bin/python3.13 -> ../Cellar/python@3.13/...
cpython-3.12.13-macos-x86_64-none  ~/.local/share/uv/python/cpython-3.12-.../bin/python3.12
```

Довгий ключ `cpython-3.12.13-macos-x86_64-none` — це `реалізація-версія-ОС-архітектура-ABI`. Його
можна передати цілком там, де очікується версія: це знадобиться, коли на машині є кілька збірок однієї
й тієї ж версії (як тут 3.13 від uv і 3.13 від Homebrew).

### Поставити і прибрати

```bash
uv python install 3.13            # одну
uv python install 3.11 3.12 3.13  # кілька за раз
uv python install 3.13t           # free-threaded, без GIL (PEP 703)
uv python install pypy@3.10       # інша реалізація, якщо є збірка
uv python upgrade 3.13            # до найновішого патчу в межах 3.13
uv python uninstall 3.11
```

Усе завантажене лежить у `~/.local/share/uv/python/` і системний Python **не** зачіпає. У
`~/.local/bin/` uv створює лише версійні симлінки (`python3.12`, `python3.13`) — голого `python3` там
немає, поки не попросите явно через `uv python install --default 3.13`.

### Три рівні вибору версії

| Рівень                      | Як задати                                      | Куди пише                | Область дії                       |
| --------------------------------- | ------------------------------------------------------ | -------------------------------- | ------------------------------------------- |
| одна команда           | `uv run --python 3.13 …`, `uv venv --python 3.13` | нікуди                     | один запуск                       |
| сесія shell                  | `export UV_PYTHON=3.13`                              | нікуди                     | поточний термінал           |
| тека (вибір)             | `uv python pin 3.13`                                 | `.python-version` у теці  | ця тека і всі підтеки      |
| проєкт (обмеження) | `requires-python`                                    | `pyproject.toml`               | усі, хто відкриє проєкт  |
| машина                      | `uv python pin --global 3.12`                        | `~/.config/uv/.python-version` | усе, де немає пінів вище |

Пріоритет — рівно в цьому порядку: `--python` → `UV_PYTHON` → `.python-version` (у поточній теці, далі
вгору по дереву) → `requires-python` → глобальний пін.

Різниця між двома проєктними рівнями принципова. `requires-python` — це **діапазон** сумісності, який
їде до споживачів пакета в метаданих. `.python-version` — це **вибір** однієї версії для роботи тут і
зараз, у метадані він не потрапляє. Тому в бібліотеці тримають широкий `requires-python = ">=3.12"`, а
`.python-version` — вужчий. Суперечність між ними uv не пропустить:

```
$ uv python pin 3.11
error: The requested Python version `3.11` is incompatible with the project `requires-python`
value of `>=3.12`.
```

Так само перевіряється й одноразовий `--python`:

```
$ uv run --python 3.11 python -V
error: The requested interpreter resolved to Python 3.11.15, which is incompatible with the
project's Python requirement: `>=3.12` (from `project.requires-python`)
```

### Пін у теці

```bash
uv python pin 3.13     # Pinned `.python-version` to `3.13`
uv python pin          # прочитати поточний, нічого не змінюючи
uv python pin --rm     # Removed Python version file at `.python-version`
```

`.python-version` **комітять**: тоді в усіх, хто клонував теку, `uv run` візьме ту саму версію
незалежно від їхніх машинних налаштувань. Файл діє й на підтеки, тому один пін у корені монорепи
накриває всі пакети всередині.

Прапорець `--resolved` записує не запит, а повний шлях до інтерпретатора — жорстко й не переносимо між
машинами, але однозначно, коли збірок однієї версії кілька:

```
$ uv python pin --resolved 3.13
Updated `.python-version` -> `/Users/…/uv/python/cpython-3.13-macos-x86_64-none/bin/python3.13`
```

### Пін на всю машину

```bash
uv python pin --global 3.12    # записати ~/.config/uv/.python-version
uv python pin --global         # прочитати
```

Це **резервне значення**, а не перемикач системи: діє лише там, де немає `.python-version` у теці або
вище, і лише на команди uv. Набраний у терміналі `python3` від нього не змінюється — shim-ів, як у
pyenv, у uv немає.

### Порівняння з pyenv

| pyenv                                                  | uv                                          |
| ------------------------------------------------------ | ------------------------------------------- |
| `pyenv install 3.13`                                 | `uv python install 3.13`                  |
| `pyenv versions`                                     | `uv python list`                          |
| `pyenv which python3.13`                             | `uv python find 3.13`                     |
| `pyenv local 3.13`                                   | `uv python pin 3.13`                      |
| `pyenv global 3.13`                                  | `uv python pin --global 3.13`             |
| `pyenv shell 3.13`                                   | `UV_PYTHON=3.13` або `--python 3.13` |
| `pyenv uninstall 3.11`                               | `uv python uninstall 3.11`                |
| компілює з джерел, хвилини       | готові збірки, секунди   |
| shim-и в`PATH` перехоплюють `python` | нічого не перехоплює      |

`.python-version` — це той самий файл, який читає pyenv, тому в простому випадку (`3.13`) вони
сумісні. Але розширений синтаксис uv — `3.13t`, `pypy@3.10`, повний ключ збірки — pyenv не зрозуміє.

### Перевести наявний проєкт на іншу версію

```bash
uv python pin 3.13
uv sync
```

`.venv` жорстко прив'язаний до одного інтерпретатора (шлях записаний у `pyvenv.cfg`), тому змінити
версію без перестворення оточення неможливо. Але робити це вручну не потрібно: `uv sync` бачить
розбіжність і перестворює сам.

```
$ uv python pin 3.13 && uv sync
Updated `.python-version` from `3.12` -> `3.13`
Using CPython 3.13.12
Removed virtual environment at: .venv
Creating virtual environment at: .venv
Installed 7 packages in 10ms
```

### Політика вибору інтерпретатора

```toml
[tool.uv]
python-preference = "only-managed"   # ігнорувати системні інтерпретатори
python-downloads = "manual"          # не тягнути молча, тільки явним uv python install
```

`python-preference` приймає `only-managed` | `managed` (типово) | `system` | `only-system`. Ті самі
налаштування доступні прапорцями (`--managed-python`, `--no-managed-python`,
`--no-python-downloads`) і змінними оточення (`UV_PYTHON_PREFERENCE`, `UV_PYTHON_DOWNLOADS`,
`UV_PYTHON_INSTALL_DIR`). Решта ключів — у [`pyproject.reference.toml`](pyproject.reference.toml).

`only-system` — це те, чим користуються в CI-образах і Docker, де інтерпретатор уже стоїть і
завантажувати другий немає сенсу.

### Чому це має значення саме тут

У [`pyproject.toml`](pyproject.toml) стоїть `requires-python = ">=3.12"` і **немає** `.python-version`.
Отже конкретну версію обирає машинний пін того, хто відкрив теку: у когось 3.12, у когось 3.14. Для
цього прикладу різниця невелика, але загалом від версії залежить результат розв'язання — залежності з
маркерами `python_version` (як `tomli` у довідковому файлі) з'являються або зникають, і `uv.lock`
виходить інший. Якщо приклад має відтворюватися однаково у всіх — додайте пін:

```bash
uv python pin 3.12
```

---

## `uv.lock`

```bash
head -40 uv.lock
grep -c "hash" uv.lock
```

Той самий принцип, що й у `poetry.lock`: точні версії всіх пакетів плюс хеші кожного архіву. Формат
свій (TOML), він **не сумісний** з `poetry.lock` — і його теж комітять у git.

Перевірити, що lock не застарів (аналог `poetry check --lock`):

```bash
uv lock --check
```

У CI використовують саме це, а також:

```bash
uv sync --frozen      # не переобчислювати lock; впасти, якщо він не збігається
uv sync --locked      # те саме, синонім
```

---

## Конфлікт залежностей

У теці [`conflict/`](conflict/) лежить **окремий міні-проєкт** з нерозв'язним набором версій —
окремий, щоб `pyproject.toml` і `uv.lock` самого `statusboard` не змінювалися. Усередині:

```toml
dependencies = [
    "flask==3.1.0",
    "werkzeug==2.3.0",
]
```

Flask 3.1.0 у метаданих оголошує `Werkzeug>=3.1`, а ми поруч вимагаємо рівно `2.3.0`. Такого набору
версій не існує. Націлюємо uv на цей проєкт ключем `--project`:

```bash
uv lock --project conflict
```

```
  × No solution found when resolving dependencies:
  ╰─▶ Because flask==3.1.0 depends on werkzeug>=3.1 and your project
      depends on flask==3.1.0, we can conclude that your project depends on
      werkzeug>=3.1.
      And because your project depends on werkzeug==2.3.0, we can conclude
      that your project's requirements are unsatisfiable.
```

Код повернення — **1**, `conflict/uv.lock` не створюється, ваш справжній `uv.lock` не змінюється
(перевірте: `uv lock --check` у корені теки далі проходить).

Це те саме доведення, що й у Poetry, — обидва спираються на алгоритм **PubGrub**, — але прочитайте
формулювання: uv веде вас за руку через кожен крок висновку («because… and…, we can conclude that…»)
і завершує тим, у чому саме суперечність. На двох залежностях різниця з Poetry косметична. На
справжньому графі з десятками пакетів саме цей текст вирішує, чи ви зрозумієте проблему за хвилину,
чи за годину.

### Той самий файл, але розв'язний

Заберіть версію у Flask — залиште `"flask"`:

```bash
uv lock --project conflict
grep -A1 '^name = "flask"' conflict/uv.lock
# name = "flask"
# version = "2.3.1"
```

(`^` тут не для краси: у `uv.lock` рядок `{ name = "flask" }` зустрічається ще й у списках
залежностей інших пакетів, тому без прив'язки до початку рядка grep покаже не те.)

uv **відступив назад** до найновішого Flask, який ще приймає Werkzeug 2.3.0. Це і є резолюція: не
«постав найновіше», а «знайди версії, за яких усі обмеження виконуються одночасно». pip
([`../02_pipenv/`](../02_pipenv/)) і Poetry ([`../03_poetry/`](../03_poetry/)) на цьому ж наборі
приходять до тієї самої `Flask 2.3.1` — відрізняються швидкість і текст помилки, а не відповідь.

Прибрати за собою:

```bash
rm -rf conflict/uv.lock conflict/.venv && git checkout -- conflict/pyproject.toml
```

### Чому в uv (як і в Poetry) не буває зламаного оточення

`uv add` не «доставляє пакет» — він перераховує граф, оновлює lock і **зводить оточення до нього**.
Якщо розв'язку немає, не змінюється нічого: ні `pyproject.toml`, ні `uv.lock`, ні `.venv`.

```bash
uv add --project conflict "flask==3.1.0"   # на розв'язному варіанті: впаде, нічого не змінить
```

uv навіть підказує вихід, якщо ви наполягаєте: `help: If you want to add the package regardless of the failed resolution, provide the --frozen flag`. Але й тоді ламається не оточення, а лише
`pyproject.toml`: `--frozen` пропускає і lock, і синхронізацію, тобто у `.venv` несумісні пакети так
і не потрапляють. Зверніть увагу, що `uv add` створює `conflict/.venv` — вона під `.gitignore`,
приберіть її разом з lock-файлом.

Порівняйте з pip, де послідовні `pip install flask==3.1.0` і `pip install werkzeug==2.3.0` лишають
несумісні пакети в одному venv **і повертають код 0** — детально це розібрано в
[`../02_pipenv/README.md`](../02_pipenv/README.md#конфлікт-залежностей).

|                                                                                  | pip                                     | Poetry             | uv                                     |
| -------------------------------------------------------------------------------- | --------------------------------------- | ------------------ | -------------------------------------- |
| Порахувати конфлікт наперед                             | `--dry-run`                           | `poetry lock`    | `uv lock`                            |
| Текст помилки                                                        | пара обмежень               | доведення | доведення, покроково |
| Відступити до старішої версії                          | так                                  | так             | так                                 |
| Може зламати готове оточення                            | **так, і повертає 0** | ні               | ні                                   |
| Скільки часу до відповіді «немає розв'язку» | ~0.7 с                                 | ~1.5 с            | ~0.08 с                               |

Останній рядок — заміряно на теплому кеші (`/usr/bin/time -p` на командах вище). Зверніть увагу, що
тут pip швидший за Poetry: граф із двох пакетів, суперечність видно одразу, і перевага резолвера uv
на такому розмірі — це вже не про алгоритм, а про те, що бінарник на Rust не витрачає час на старт
інтерпретатора. Як ця різниця виглядає на справжніх наборах залежностей — у
[`../07_compare/`](../07_compare/).

Є ще один випадок, якого немає ні в pip, ні в Poetry: коли конфлікт вам **потрібен**. Наприклад, дві
групи залежностей, які принципово не сумісні (torch під CPU і під CUDA). uv дозволяє оголосити це
явно через `[tool.uv] conflicts`, і тоді він тримає для кожної групи окремий набір версій замість
того, щоб падати. Це вже за межами цього заняття — але варто знати, що така опція існує.

---

## Тести

```bash
uv run pytest -q        # 5 тестів, ~0.05 с
uv run pytest -v
uv run pytest -k delete
```

Навмисно мінімальний набір — базовий CRUD через HTTP: read, create, create з порожнім полем, create з
дублем, delete. Два файли, `tests/conftest.py` і `tests/test_app.py`.

Тести **ідентичні** в усіх трьох теках — той самий набір, що і в
[`../02_pipenv/tests/`](../02_pipenv/tests/), де є й опис того, що саме перевіряється. Жоден тест не
виходить у мережу.

Уся конфігурація — в одному `pyproject.toml`, як і в Poetry, тільки група описана стандартом PEP 735:

```toml
[dependency-groups]
dev = ["bandit>=1.9.4", "pytest>=9.1.1", "ruff>=0.14.0"]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
addopts = "-ra"

[tool.bandit]
exclude_dirs = [".venv", "tests"]
```

Для порівняння, у `02_pipenv` те саме потребувало трьох окремих файлів: `pytest.ini`,
`requirements-dev.txt` і `bandit.yaml`.

Запустити тести без dev-групи не вийде — і це правильно:

```bash
uv sync --no-dev && uv run pytest    # pytest не встановлено
uv sync                              # повернути dev-інструменти
```

---

## `bandit` — сканер безпеки

`ruff` шукає помилки стилю й логіки, `bandit` — **вразливості**: хардкоджені паролі, `shell=True`,
слабка криптографія, запити без таймауту.

```bash
uv run bandit -c pyproject.toml -r .          # перевірити проєкт
uv run bandit -c pyproject.toml -r . -ll      # лише severity >= medium
uv run bandit -c pyproject.toml -r . -f json  # для CI

uvx bandit -c pyproject.toml -r .             # без встановлення в проєкт
```

> Прапорець `-c pyproject.toml` **обов'язковий**. На відміну від ruff і pytest, bandit не читає
> `pyproject.toml` сам — без `-c` він просканує все, включно з `.venv`, і видасть сотні знахідок у
> чужому коді.

На цьому коді bandit не знаходить нічого. Ось що він повідомляє на навмисно поганому файлі:

```
[B602:subprocess_popen_with_shell_equals_true]  Severity: High
[B113:request_without_timeout]                  Severity: Medium
[B105:hardcoded_password_string]                Severity: Low
```

`B113` варто спробувати: приберіть `timeout` з `requests.get` у [`checks.py`](checks.py) — і bandit
почне лаятися. Запит без таймауту може висіти вічно й підвісити застосунок.

`exclude_dirs` виключає `tests`, бо `assert` там — це норма, а bandit позначає його як `B101`: в
оптимізованому байткоді `assert` зникає.

### Демонстрація: що bandit насправді ловить

У теці [`bandit_demo/`](bandit_demo/) лежить файл [`insecure.py`](bandit_demo/insecure.py), написаний
**щоб його сканували, а не запускали**. Він виключений з `exclude_dirs`, тому звичайна перевірка
проєкту лишається чистою. Наведіть bandit на нього окремо:

```bash
uv run bandit -r bandit_demo/
uv run bandit -r bandit_demo/ -ll       # тільки medium і high
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

## Що таке `ruff` і навіщо він у dev-групі

`ruff` — лінтер і форматер для Python від Astral, тих самих авторів, що й uv, і теж на Rust. Він
замінює одразу цілий набір інструментів: `flake8` (+ десятки його плагінів), `isort`, `black`,
`pyupgrade`, `pydocstyle`, `autoflake`. Приблизно **1060 правил** в одному бінарнику.

Дві половини, які легко переплутати:

- **`ruff check`** — шукає *проблеми*: невикористані імпорти, неможливий код, підозрілі конструкції;
- **`ruff format`** — переписує *оформлення*: лапки, довжину рядків, відступи. Сумісний з `black`.

```bash
uv run ruff check .              # знайти проблеми
uv run ruff check --fix .        # виправити те, що можна, автоматично
uv run ruff check --statistics . # скільки чого
uv run ruff check --watch .      # стежити за файлами й перевіряти на льоту
uv run ruff rule F541            # пояснити конкретне правило

uv run ruff format .             # відформатувати
uv run ruff format --diff .      # показати зміни, нічого не чіпаючи
uv run ruff format --check .     # для CI: впасти, якщо код не відформатовано

uvx ruff check .                 # взагалі без встановлення в проєкт
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
`[*]` означає, що `--fix` виправить це сам.

Швидкість — **49 мс** на весь проєкт. Саме тому `ruff` ставлять у pre-commit hook: він встигає
відпрацювати раніше, ніж ви помітите паузу.

Налаштування живуть у тому ж `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]
```

> Детально про лінтери й форматери — окрема тема в [`../06_formatting/`](../06_formatting/). Тут ruff
> потрібен лише як приклад dev-залежності: інструмент, без якого код працює, і який **не має** їхати
> в продакшн.

---

## pre-commit — запускати ruff і bandit автоматично

`pre-commit` вішає перевірки на git-хук: вони спрацьовують на `git commit` і **лише для тих файлів,
що ви застейджили**. Конфігурація — [`.pre-commit-config.yaml`](.pre-commit-config.yaml).

```bash
uv run pre-commit install          # вписати хук у .git/hooks (один раз)
uv run pre-commit run --all-files  # прогнати зараз по всьому
uv run pre-commit autoupdate       # підняти версії в rev:
uv run pre-commit run ruff-check   # тільки один хук
```

Три хуки: `ruff-check` (шукає проблеми й виправляє), `ruff-format` (форматує), `bandit` (безпека).

### Три деталі, які варто знати

**1. Хуки ставляться на весь git-репозиторій, а не на теку.** У цьому репозиторії лежить кілька
проєктів, тому `.pre-commit-config.yaml` тут містить фільтр:

```yaml
files: ^module01/04_uv/
exclude: ^module01/04_uv/(bandit_demo|\.venv)/
```

Без нього хуки з цієї теки перевіряли б і дві інші копії того самого застосунку. З кореня репозиторію
конфіг треба вказувати явно:

```bash
pre-commit run --config module01/04_uv/.pre-commit-config.yaml --all-files
```

**2. `--exit-non-zero-on-fix` — не косметика.** З простим `--fix` ruff виправляє файл і завершується
кодом 0. Хук рапортує `Passed`, коміт проходить, а ваш код мовчки переписали. Перевірено: з голим
`--fix` зламаний файл давав `Passed`, з прапорцем — `Failed`.

**3. `--all-files` означає «усі файли, які знає git».** Поки тека не додана в git, хуки покажуть
`(no files to check) Skipped`. Це не поломка конфігурації — просто `git add` ще не робили.

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

`bandit_demo/` виключено з хуків навмисно: `ruff --fix` полагодив би саме те, що там має лишатися
зламаним.

---

## Перестворити оточення

Тут найпростіше з трьох інструментів, і причина архітектурна: uv **завжди** тримає оточення в
`.venv/` у корені проєкту. Немає ні каталогу кешованих venv, ні хешів у назвах, ні питання «а яке
саме оточення зараз активне» — воно одне, і воно лежить поруч із `pyproject.toml`.

```bash
rm -rf .venv && uv sync
```

Це і є весь рецепт. На цьому проєкті — **близько 0.1–0.3 секунди** на 33 пакети:

```
$ rm -rf .venv && time uv sync
Using CPython 3.12.13
Creating virtual environment at: .venv
Resolved 35 packages in 1ms
Installed 33 packages in 40ms
 + bandit==1.9.4
 + blinker==1.9.0
 ...
real 0.11
```

Порівняйте з Poetry, де те саме — це `poetry env remove --all && poetry install` і кілька секунд, і з
pip, де це `rm -rf .venv`, `python -m venv .venv`, активація й `pip install -r requirements.txt`.
Швидкість тут не косметика, а зміна звички: коли перестворення коштує чверть секунди, ви робите його
за першої підозри, замість гадати, що там всередині зламалося. Саме тому в uv є жорсткі посилання на
глобальний кеш — деталі й заміри у [`../07_compare/`](../07_compare/).

Той самий результат без `rm -rf` — прапорцем `--clear` (він же `-c`):

```bash
uv venv --clear && uv sync
```

### Коли перестворювати не потрібно

Майже завжди, бо `uv sync` **сам зводить оточення до lock-файлу**:

| Задача                                                            | Команда                                                                   |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Привести оточення точно до lock                  | `uv sync` — це поведінка **за замовчуванням** |
| Дозволити в оточенні сторонні пакети    | `uv sync --inexact`                                                            |
| Перевстановити пакети, не видаляючи venv | `uv sync --reinstall` (або `--reinstall-package flask`)                   |
| Перерахувати версії з нуля                       | `uv lock --upgrade && uv sync`                                                 |
| Перейти на іншу версію Python                        | `uv python pin 3.13 && uv sync` — venv перестворить сам        |
| Скинути кеш пакетів                                    | `uv cache clean` (або `uv cache prune` — лише недосяжне)    |
| У CI: впасти, якщо lock не збігається            | `uv sync --frozen`                                                             |

Найважливіший рядок — перший. У Poetry `install` нічого не видаляє (для цього є окрема `poetry sync`),
у pip не видаляє ніщо взагалі. `uv sync` — **точний за замовчуванням**: поставте в оточення сторонній
пакет, і наступний `uv sync` приберe і його, і все, що він притягнув:

```bash
uv pip install httpx
uv sync
```

```
Uninstalled 5 packages in 12ms
 - anyio==4.14.2
 - h11==0.16.0
 - httpcore==1.0.9
 - httpx==0.28.1
 - typing-extensions==4.16.0
```

Візьміть для перевірки саме пакет, якого немає в `uv.lock` (`grep 'name = "httpx"' uv.lock` — нічого).
З `rich` дослід не вийде: він у цьому проєкті **є** в оточенні законно, як залежність `bandit`, і
`uv sync` його не торкнеться.

Це саме те, чого не вміє `pip install -r requirements.txt`, і причина, чому оточення під uv не
«накопичує» пакети з часом.

### Активація

Активовувати нічого не потрібно: `uv run python app.py`, `uv run pytest`, `uv run flask --app app run`
самі беруть `.venv`. Але `.venv` — звичайний venv, тому працює і звичний шлях:

```bash
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

Різниця з Poetry: там venv лежить у кеші й шлях треба питати командою (`poetry env info -p`), тут він
завжди `.venv` у теці проєкту.

---

## Довідник команд

| Команда                      | Що робить                                                                 |
| ----------------------------------- | --------------------------------------------------------------------------------- |
| `uv init` / `uv init --app`     | створити новий проєкт                                          |
| `uv add flask`                    | додати залежність, оновити lock і venv                    |
| `uv add --dev ruff`               | додати dev-залежність                                             |
| `uv remove flask`                 | прибрати залежність                                             |
| `uv sync`                         | привести venv у стан lock                                            |
| `uv sync --no-dev`                | без dev-групи                                                             |
| `uv sync --frozen`                | не чіпати lock; впасти, якщо застарів                   |
| `uv lock`                         | перерахувати lock                                                     |
| `uv lock --check`                 | перевірити актуальність lock                                |
| `uv lock --upgrade`               | оновити все в межах обмежень                              |
| `uv lock --upgrade-package flask` | оновити один пакет                                                |
| `uv run <cmd>`                    | виконати команду (сам синхронізує перед цим) |
| `uv tree`                         | дерево залежностей                                               |
| `uv export -o requirements.txt`   | згенерувати`requirements.txt`                                        |
| `uv venv`                         | створити venv вручну                                                |
| `uv venv --clear`                 | перестворити venv з нуля                                         |
| `uv sync --reinstall`             | перевстановити всі пакети, не видаляючи venv    |
| `uv cache clean`                  | очистити кеш пакетів                                            |
| `uv python install 3.13`          | завантажити інтерпретатор                                 |
| `uv python list`                  | які версії є і які доступні                                 |
| `uv python pin 3.13`              | записати`.python-version` у теці                                   |
| `uv python pin --global 3.12`     | версія за замовчуванням для всієї машини       |
| `uv python pin --rm`              | зняти пін теки                                                        |
| `uv python find 3.12`             | шлях до інтерпретатора                                        |
| `uv python upgrade 3.13`          | оновити патч-версію                                              |
| `uv python uninstall 3.11`        | прибрати інтерпретатор                                       |
| `uv tool install ruff`            | поставити утиліту глобально                              |
| `uvx ruff check .`                | запустити утиліту без встановлення                 |
| `uv build`                        | зібрати wheel і sdist (потрібен`[build-system]`)                |
| `uv publish`                      | залити на PyPI                                                            |
| `uv cache clean`                  | очистити кеш                                                           |

---

## Підсумок трьох папок

|                                         | pip                          | Poetry             | uv                    |
| --------------------------------------- | ---------------------------- | ------------------ | --------------------- |
| Lock-файл                           | ні                         | так             | так                |
| Хеші пакетів                 | ні (лише вручну) | так             | так                |
| Прямі vs транзитивні    | не розрізняє      | розрізняє | розрізняє    |
| Групи залежностей       | ні                         | так             | так (PEP 735)      |
| Видаляє зайве               | ні                         | `poetry sync`    | `uv sync`           |
| Створює venv                     | ні                         | так             | так                |
| Ставить Python                   | ні                         | ні               | так                |
| Збирає пакет                 | ні                         | так             | так                |
| Швидкість                      | —                           | повільно   | дуже швидко |
| Стандартний маніфест | ні                         | PEP 621            | PEP 621               |

**Що з цього обирати у 2026 році:**

- **pip** — треба знати завжди. Він є всюди, він усередині Docker-образів, CI та легасі-проєктів.
  Розуміти venv і `requirements.txt` обов’язково.
- **Poetry** — дуже поширений, ви точно натрапите на нього в наявних проєктах. Зрілий, стабільний,
  добре документований.
- **uv** — для нових проєктів. Швидкий, покриває весь цикл, спирається на стандарти замість власних
  форматів. Обмеження: молодий (перший реліз — 2024), тому екосистема плагінів і корпоративні
  інтеграції ще наздоганяють.

Практична порада: **не змішуйте їх в одному проєкті.** Два lock-файли, які нічого не знають один про
одного, — це гарантований конфлікт версій, який виявиться на продакшні.

Рядок «Швидкість» у таблиці вище — єдиний, який можна зміряти замість обговорювати. Скрипт, який це
робить, і графік із результатами — у [`../07_compare/`](../07_compare/).
