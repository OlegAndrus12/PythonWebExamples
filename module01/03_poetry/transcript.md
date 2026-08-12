# Transcript — 03 Poetry

Послідовність команд для живої демонстрації. Виконувати згори вниз.
Пояснення до кожної теми — у [`README.md`](README.md).

Кожен коментар `#` — це те, що очікувано з'явиться, або те, що варто сказати.
Кроки **1–7** нічого не змінюють у теці. Кроки **8–10** позначені як такі, що змінюють — там є відкат.

```bash
cd module01/03_poetry
poetry --version                              # Poetry (version 2.4.1)
```

---

## 1. Оточення створюється саме

```bash
poetry install                                # venv + пакети однією командою
poetry env info --path                         # ~/Library/Caches/pypoetry/virtualenvs/statusboard-8SkKN7Wn-py3.12
poetry env list                                # statusboard-8SkKN7Wn-py3.12 (Activated)

poetry run flask --app app run --debug         # → http://127.0.0.1:5000, потім Ctrl+C
```

`# ні python -m venv, ні activate, ні pip install -r. venv лежить у кеші, а не в проєкті.`
`# 8SkKN7Wn — хеш абсолютного шляху: перемістили теку → нове оточення.`
`# ПАСТКА: env info не тільки показує шлях, а й СТВОРЮЄ оточення, якщо його немає.`

---

## 2. Що встановлено і хто це притягнув

```bash
poetry show | wc -l                            # 39 пакетів усього
poetry show --only main | wc -l                # 12 робочих — а прямих у маніфесті лише 2
poetry show --only dev --top-level              # 6 dev-інструментів
poetry show --tree | head -20
poetry show --tree --why urllib3                # requests + types-requests обидва його тягнуть
```

`# --why БЕЗ --tree не працює: "cannot be used without --tree" (у README неточність).`

---

## 3. Маніфест

```bash
cat pyproject.toml
```

`# [project] — це PEP 621, стандарт. Той самий блок читають uv, pip, hatch → 04_uv/ бере цей самий файл.`
`# package-mode = false — застосунок, не бібліотека. Для бібліотеки був би [build-system] + poetry build/publish.`
`# [tool.poetry.group.dev.dependencies] — у requirements.txt цього не виразити ніяк.`
`# Чотири інструменти налаштовані тут же: [tool.ruff] [tool.pytest.ini_options] [tool.bandit] [tool.mypy].`

---

## 4. Lock-файл

```bash
grep -c '^\[\[package\]\]' poetry.lock         # 40 пакетів
grep -c 'sha256' poetry.lock                   # 524 хеші
head -30 poetry.lock                           # показати files=[...] і content-hash

poetry check                                   # All set!
poetry check --lock                            # All set!
```

`# маніфест = що я попросив (2 рядки). lock = що я отримав (40 пакетів, 524 хеші).`
`# Хеші — сенс lock-файлу: підмінений wheel призведе до падіння установки, а не до тихого запуску чужого коду.`
`# content-hash = відбиток pyproject.toml. Змінили маніфест без poetry lock → check --lock впаде. Це ставлять у CI.`
`# Lock комітять у git. Завжди.`

---

## 5. `sync` — те, чого в pip немає принципово

```bash
poetry run pip install httpx                   # ставлю пакет в обхід Poetry, руками
poetry sync                                    # 4 removals: httpx, httpcore, h11, anyio
```

`# sync прибрав не тільки httpx, а й усе, що він притягнув → оточення точно = lock.`
`# poetry install НІКОЛИ нічого не видаляє. У CI потрібен саме sync.`
`# install=з lock | lock=перерахувати, не ставити | sync=lock + видалити зайве | update=lock+install у межах обмежень`

---

## 6. Конфлікт залежностей — видно резолвер

```bash
cat conflict/pyproject.toml                    # flask (==3.1.0) + werkzeug (==2.3.0)
poetry -C conflict lock ; echo "exit=$?"       # exit=1, lock НЕ створився
```

Очікуваний вивід:

```
Because conflict-demo depends on flask (3.1.0) which depends on Werkzeug (>=3.1), werkzeug is required.
So, because conflict-demo depends on werkzeug (2.3.0), version solving failed.
```

```bash
poetry check --lock                            # All set! — мій справжній lock не зачепило
```

`# Це не "щось пішло не так", а доведення: flask 3.1.0 → Werkzeug>=3.1 → але просили 2.3.0 → розв'язку немає.`
`# Алгоритм PubGrub (той самий, що в uv) — тому названо саму пару обмежень.`
`# ГОЛОВНЕ: у pip послідовні install flask==3.1.0 + install werkzeug==2.3.0 лишають зламане оточення й код 0.`
`# У Poetry такого шляху немає: add спершу рахує весь граф і при конфлікті не змінює ні оточення, ні маніфест.`

---

## 7. Dev-інструменти — усі з однієї групи, усі з одного конфіга

```bash
poetry run pytest -q                           # 5 passed in 0.05s
poetry run ruff check .                        # All checks passed! (0,10 с)
poetry run bandit -c pyproject.toml -r .       # чисто
poetry run bandit -r bandit_demo/              # 33 знахідки: 8 high, 11 medium, 14 low
poetry run mypy                                # Success: no issues found in 6 source files (0,30 с з кешем)
poetry run mypy --strict                       # Found 15 errors in 6 files — вправа для студентів
poetry run mypy mypy_demo/broken.py            # Found 46 errors — і ЖОДНОЇ синтаксичної помилки
```

`# bandit: -c pyproject.toml ОБОВ'ЯЗКОВИЙ, сам він конфіг не читає (ruff/pytest/mypy — читають).`
`# mypy_demo: усе це коректний Python, який інтерпретатор без вагань виконає.`
`# --strict тут ловить 3 речі: no-untyped-def (в'юхи не анотовані), type-arg (-> dict "чого?"), no-any-return (json.loads → Any).`

---

## 8. pre-commit ⚠ потрібен `git add`

Хуки бачать **лише файли, які знає git**, а ця тека ще не в git — без цього кроку всі чотири
хуки дадуть `(no files to check) Skipped`.

```bash
# УВІМКНУТИ (intent-to-add: реєструє файли в індексі, вміст не стейджить)
cd ../.. && git add -N module01/03_poetry/*.py && cd module01/03_poetry

poetry run pre-commit run --all-files          # ruff check / ruff format / bandit / mypy — усі Passed

# ВІДКАТ
cd ../.. && git reset -q -- module01/03_poetry && cd module01/03_poetry
```

`# Хуки ставляться на весь РЕПОЗИТОРІЙ, не на теку → у конфізі є files: ^module01/03_poetry/`
`# --exit-non-zero-on-fix не косметика: з голим --fix ruff перепише файл і вийде з кодом 0 → коміт пройде.`
`# Хук mypy має ВЛАСНИЙ virtualenv і не бачить пакетів Poetry → сторонні залежності перелічені`
`#   руками в additional_dependencies, і цей список розходиться з маніфестом. Тому mypy частіше в CI.`

---

## 9. Створити проєкт з нуля ⚠ у `/tmp`, щоб не смітити

```bash
cd /tmp && rm -rf pnew pdemo

poetry new pnew && find pnew -type f | sort
# pnew/README.md
# pnew/pyproject.toml
# pnew/src/pnew/__init__.py        ← src/-розкладка вже типова у 2.x (--src застарів, пласка = --flat)
# pnew/tests/__init__.py

mkdir pdemo && cd pdemo
poetry init -n --name pdemo --python ">=3.12" --dependency flask --dev-dependency ruff
cat pyproject.toml                             # init НЕ створює ні src/, ні tests/, ні lock

poetry add --group docs mkdocs                 # нова група → у [dependency-groups] (PEP 735), не в [tool.poetry.group.*]
cat pyproject.toml | tail -5

cd /tmp && rm -rf pnew pdemo
cd ~/Projects/sandbox/PythonWebExamples/module01/03_poetry
```

`# poetry new = структура з нуля. poetry init = тека, де код уже є (наш випадок).`
`# Ім'я й пошту автора Poetry бере з git config user.name / user.email.`

---

## 10. Групи, оновлення, експорт — показати, не виконувати

```bash
poetry install --only main                     # так деплоять: без dev, лінтер в образ не потрапляє
poetry install --without dev
poetry install --with docs                     # додати optional-групу

poetry update                                  # оновити все в межах обмежень
poetry update flask                            # один пакет
poetry lock --regenerate                       # перерахувати lock з нуля
poetry env use python3.13                      # інша версія Python
poetry env remove --all                        # видалити оточення (далі poetry install)

poetry self add poetry-plugin-export           # у 2.x export — окремий плагін
poetry export -f requirements.txt -o requirements.txt --without-hashes
```

`# Міграція з requirements.txt: команди poetry import НЕ існує. Два кроки:`
`#   poetry init -n --name statusboard --python ">=3.12"`
`#   poetry add $(grep -v '^#' requirements.txt)        # без grep кожне слово коментаря = "пакет"`
`# ПАСТКА міграції: піни == переносяться як є. У маніфесті потрібні ДІАПАЗОНИ, точні версії — в lock.`
`#   Інакше подвійна фіксація: poetry update не підніме навіть патч безпеки. Далі: poetry add "flask@^3.1.0"`

---

## Мостик до `04_uv/`

```bash
time poetry --version                          # ~0,55 с — стільки коштує СТАРТ Poetry, і це на кожен poetry run
```

`# poetry lock тут ~2 с; на реальному проєкті — десятки секунд.`
`# Керування версіями Python Poetry не дає взагалі — для цього потрібен pyenv.`
`# 04_uv/ — той самий застосунок і ТОЙ САМИЙ pyproject.toml, але резолвер за 93 мс замість 2,5 с. Заміри — 07_compare/.`

---

## Перевірка, що після заняття все на місці

```bash
poetry check --lock                            # All set!
poetry run pytest -q                           # 5 passed
poetry run ruff check .                        # All checks passed!
poetry run mypy                                # Success: no issues found in 6 source files
ls conflict/                                   # тільки poetry.toml і pyproject.toml, без poetry.lock
git status --short module01/03_poetry           # ?? module01/03_poetry/  (нічого не в індексі)
```

> ⚠ `git checkout` у цій теці **не працює** — вона ще не в git. Якщо ламали файли навмисно
> (напр. правили `pyproject.toml`, щоб показати `check --lock`), відкат тільки з копії:
> `cp pyproject.toml /tmp/ ` **до** правки.
