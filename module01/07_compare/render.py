#!/usr/bin/env python3
"""Turn results.json into bench.html — a self-contained page for the lecture.

    python3 render.py                 # reads results.json, writes bench.html

Standard library only, no CDN, no chart library: the page is one HTML file with
inline CSS, so it works from a USB stick in a room with no network. Every number
on the page comes out of results.json — nothing is typed in by hand.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Categorical slots 1-3 of the validated palette, light and dark steps. Fixed
# order, one hue per tool, never recoloured by rank.
SERIES = {
    "pip": {"label": "pip", "light": "#2a78d6", "dark": "#3987e5"},
    "poetry": {"label": "Poetry", "light": "#eb6834", "dark": "#d95926"},
    "uv": {"label": "uv", "light": "#1baf7a", "dark": "#199e70"},
}

SCENARIOS = {
    "lock": {
        "title": "Резолюція",
        "short": "резолюція",
        "blurb": "Перетворити діапазони з маніфесту на точні версії у lock-файлі.",
        "note": "У pip lock-файлів немає — у цьому рядку працює <code>pip-compile</code> "
        "з pip-tools, окремого проєкту. Це найближчий аналог, а не сам pip.",
    },
    "install-cold": {
        "title": "Встановлення, порожній кеш",
        "short": "порожній кеш",
        "blurb": "Перший раз на новій машині або в CI без кешу: створити venv і "
        "завантажити всі пакети.",
        "note": "Єдиний сценарій, який залежить від мережі, а не від інструмента: "
        "усі три чекають на ті самі wheel-и з PyPI. Тому саме тут різниця між "
        "двома запусками того самого інструмента може бути більшою, ніж різниця "
        "між інструментами — не робіть із цих цифр висновків про резолвери.",
    },
    "install-warm": {
        "title": "Встановлення, теплий кеш",
        "short": "теплий кеш",
        "blurb": "Друге оточення з тими самими залежностями — пакети вже в кеші, "
        "лишається розпакувати їх у venv.",
        "note": "Тут видно ціну копіювання файлів: uv кладе у venv жорсткі посилання "
        "на глобальний кеш замість копій, тому «встановлення» — це майже лише "
        "створення записів у теці. Це сценарій, який ви проходите щодня.",
    },
}

# The page is in Ukrainian; results.json keeps the English notes that live in
# bench.py next to the code. Falls back to the JSON note for an unknown set.
SET_NOTES = {
    "statusboard": "той самий застосунок, що у 02_pipenv / 03_poetry / 04_uv",
    "zoo_api": "рантайм-залежності zoo_api плюс звичайний dev-набір",
}

TOOL_NOTE = {
    "pip": "python -m venv + pip install -r",
    "poetry": "poetry install",
    "uv": "uv sync",
}


def fmt_seconds(value: float) -> str:
    if value < 1:
        return f"{value * 1000:.0f} мс"
    if value < 10:
        return f"{value:.2f} с"
    return f"{value:.1f} с"


def fmt_factor(value: float) -> str:
    return f"×{value:.0f}" if value >= 10 else f"×{value:.1f}"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def plural(count: int, one: str, few: str, many: str) -> str:
    """Ukrainian agreement: 1 пакет, 2 пакети, 5 пакетів."""
    tail, tens = count % 10, count % 100
    if tail == 1 and tens != 11:
        form = one
    elif 2 <= tail <= 4 and not 12 <= tens <= 14:
        form = few
    else:
        form = many
    return f"{count} {form}"


# --------------------------------------------------------------------------- #
# Chart pieces
# --------------------------------------------------------------------------- #


def bar_row(tool: str, cell: dict, scale: float, fastest: float) -> str:
    """One horizontal bar: mark, value at the tip, ×-factor against the fastest."""
    seconds = cell["seconds"]
    width = max(seconds / scale * 100, 0.6)  # a visible sliver rather than nothing
    factor = "" if seconds == fastest else fmt_factor(seconds / fastest)
    steps = " + ".join(" ".join(step["cmd"]) for step in cell["steps"])
    tip = f"{SERIES[tool]['label']} · {fmt_seconds(seconds)} · {steps}"
    return f"""        <div class="row">
          <div class="row-name">{esc(SERIES[tool]['label'])}</div>
          <div class="track" tabindex="0" data-tip="{esc(tip)}">
            <div class="bar" style="width:{width:.2f}%;background:var(--series-{tool})"></div>
            <div class="tip" role="tooltip">{esc(tip)}</div>
          </div>
          <div class="row-value">{fmt_seconds(seconds)}<span class="factor">{factor}</span></div>
        </div>"""


def panel(set_name: str, set_cfg: dict, cells: dict, scale: float) -> str:
    tools = [tool for tool in SERIES if tool in cells]
    fastest = min(cells[tool]["seconds"] for tool in tools)
    installed = next(
        (cells[tool].get("installed") for tool in tools if cells[tool].get("installed")), None
    )
    direct = plural(set_cfg["direct"], "пряма залежність", "прямі залежності", "прямих залежностей")
    packages = (
        f"{direct} → {plural(installed, 'пакет', 'пакети', 'пакетів')}" if installed else direct
    )
    rows = "\n".join(bar_row(tool, cells[tool], scale, fastest) for tool in tools)
    return f"""      <figure class="panel">
        <figcaption>
          <span class="panel-name">{esc(set_cfg['label'])}</span>
          <span class="panel-meta">{esc(packages)}</span>
        </figcaption>
{rows}
      </figure>"""


def section(name: str, meta: dict, results: dict, sets: dict) -> str:
    """One scenario: both dependency sets on one shared scale, so the growth shows."""
    cells = results[name]
    scale = max(cell["seconds"] for per_set in cells.values() for cell in per_set.values())
    panels = "\n".join(
        panel(set_name, sets[set_name], cells[set_name], scale)
        for set_name in sets
        if set_name in cells
    )
    # The note is fixed prose, but the winner is not assumed: if the measurement
    # disagrees with the expected ordering, the page says so instead of hiding it.
    note = meta["note"]
    losers = [
        set_name
        for set_name, per_set in cells.items()
        if min(per_set, key=lambda tool: per_set[tool]["seconds"]) != "uv"
    ]
    if losers:
        winners = {
            min(cells[s], key=lambda tool: cells[s][tool]["seconds"]) for s in losers
        }
        note += (
            " <strong>На цій машині uv тут не найшвидший</strong> — "
            f"перемагає {esc(', '.join(SERIES[w]['label'] for w in sorted(winners)))}."
        )
    return f"""    <section class="scenario">
      <div class="scenario-head">
        <h2>{esc(meta['title'])}</h2>
        <p class="blurb">{esc(meta['blurb'])}</p>
        <p class="axis">шкала обох панелей спільна, 0 – {fmt_seconds(scale)}</p>
      </div>
      <div class="panels">
{panels}
      </div>
      <p class="note">{note}</p>
    </section>"""


def table(results: dict, sets: dict) -> str:
    """Every cell in one grid: a tool per row, set × scenario across the top.

    The relief rule for the light-mode aqua step — every value is also here as
    text, so nothing on this page is carried by colour alone.
    """
    scenarios = [name for name in SCENARIOS if name in results]
    present = [name for name in sets if name in results[scenarios[0]]]

    set_head = "".join(
        f'<th class="num set-head" colspan="{len(scenarios)}">{esc(sets[name]["label"])}</th>'
        for name in present
    )
    scenario_head = "".join(
        f'<th class="num">{esc(SCENARIOS[scenario]["short"])}</th>'
        for _ in present
        for scenario in scenarios
    )

    rows = []
    for tool in SERIES:
        cells = []
        for set_name in present:
            for scenario in scenarios:
                cell = results[scenario].get(set_name, {}).get(tool)
                if cell is None:
                    cells.append('<td class="num muted">—</td>')
                    continue
                fastest = min(c["seconds"] for c in results[scenario][set_name].values())
                factor = (
                    ""
                    if cell["seconds"] == fastest
                    else f'<span class="factor">{fmt_factor(cell["seconds"] / fastest)}</span>'
                )
                cells.append(f'<td class="num strong">{fmt_seconds(cell["seconds"])}{factor}</td>')
        rows.append(
            f'<tr><th class="tool">'
            f'<span class="swatch" style="background:var(--series-{tool})"></span>'
            f"{esc(SERIES[tool]['label'])}</th>{''.join(cells)}</tr>"
        )

    return f"""    <section class="table-view">
      <h2>Усі цифри</h2>
      <p class="blurb">Один запуск на клітинку. ×-множник — до найшвидшого в колонці.</p>
      <div class="scroller">
        <table>
          <thead>
            <tr><th></th>{set_head}</tr>
            <tr><th></th>{scenario_head}</tr>
          </thead>
          <tbody>
{chr(10).join('            ' + row for row in rows)}
          </tbody>
        </table>
      </div>
    </section>"""


def hero(results: dict, sets: dict) -> str:
    """The one number the lecture leads with: warm install on the larger set."""
    scenario = "install-warm" if "install-warm" in results else next(iter(results))
    set_name = list(sets)[-1]
    if set_name not in results[scenario]:
        set_name = next(iter(results[scenario]))
    cells = results[scenario][set_name]
    fastest_tool = min(cells, key=lambda tool: cells[tool]["seconds"])
    slowest_tool = max(cells, key=lambda tool: cells[tool]["seconds"])
    factor = cells[slowest_tool]["seconds"] / cells[fastest_tool]["seconds"]
    return f"""      <div class="hero">
        <div class="hero-figure">{fmt_factor(factor)}</div>
        <p class="hero-text">
          різниця між <strong>{esc(SERIES[fastest_tool]['label'])}</strong>
          ({fmt_seconds(cells[fastest_tool]['seconds'])}) і
          <strong>{esc(SERIES[slowest_tool]['label'])}</strong>
          ({fmt_seconds(cells[slowest_tool]['seconds'])}) на сценарії
          «{esc(SCENARIOS[scenario]['title'].lower())}»,
          набір {esc(sets[set_name]['label'])}
        </p>
      </div>"""


def spec_strip(payload: dict) -> str:
    machine = payload["machine"]
    items = [
        ("машина", f"{machine['platform'].split('-')[0]} · {machine['machine']} · {machine['cpu_count']} CPU"),
        ("python", machine["python_version"].replace("Python ", "")),
        ("poetry", machine["tools"]["poetry"].replace("Poetry (version ", "").rstrip(")")),
        ("uv", machine["tools"]["uv"].split()[1]),
        ("заміри", "по одному запуску"),
    ]
    return "\n".join(
        f'        <div><dt>{esc(key)}</dt><dd>{esc(value)}</dd></div>' for key, value in items
    )


# --------------------------------------------------------------------------- #


def page(payload: dict) -> str:
    results = payload["results"]
    sets = payload["config"]["sets"]
    # results is keyed set -> scenario; the chart wants scenario -> set.
    by_scenario: dict[str, dict[str, dict]] = {}
    for set_name, scenarios in results.items():
        for scenario, cells in scenarios.items():
            by_scenario.setdefault(scenario, {})[set_name] = cells

    sections = "\n".join(
        section(name, meta, by_scenario, sets) for name, meta in SCENARIOS.items() if name in by_scenario
    )
    set_notes = "\n".join(
        f"        <li><strong>{esc(cfg['label'])}</strong> — {esc(SET_NOTES.get(name, cfg['note']))}: "
        f"{esc(plural(cfg['direct'], 'пряма залежність', 'прямі залежності', 'прямих залежностей'))}, "
        f"оголошених діапазонами, як ви написали б їх руками</li>"
        for name, cfg in sets.items()
    )

    return f"""<title>pip · Poetry · uv — заміри</title>
<style>
  :root {{
    color-scheme: light;
    --plane:          #f4f4f1;
    --surface:        #fcfcfb;
    --ink:            #0b0b0b;
    --ink-2:          #52514e;
    --muted:          #898781;
    --grid:           #e1e0d9;
    --hairline:       rgba(11, 11, 11, 0.10);
    --series-pip:     {SERIES['pip']['light']};
    --series-poetry:  {SERIES['poetry']['light']};
    --series-uv:      {SERIES['uv']['light']};
    /* Named families before system-ui: a bare system-ui can resolve to a serif
       when the renderer has no desktop font config, and the page must not
       silently change voice depending on where it is opened. */
    --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, system-ui, sans-serif;
    --mono: SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", ui-monospace, monospace;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      color-scheme: dark;
      --plane:         #0d0d0d;
      --surface:       #1a1a19;
      --ink:           #ffffff;
      --ink-2:         #c3c2b7;
      --muted:         #898781;
      --grid:          #2c2c2a;
      --hairline:      rgba(255, 255, 255, 0.10);
      --series-pip:    {SERIES['pip']['dark']};
      --series-poetry: {SERIES['poetry']['dark']};
      --series-uv:     {SERIES['uv']['dark']};
    }}
  }}
  :root[data-theme="dark"] {{
    color-scheme: dark;
    --plane:         #0d0d0d;
    --surface:       #1a1a19;
    --ink:           #ffffff;
    --ink-2:         #c3c2b7;
    --muted:         #898781;
    --grid:          #2c2c2a;
    --hairline:      rgba(255, 255, 255, 0.10);
    --series-pip:    {SERIES['pip']['dark']};
    --series-poetry: {SERIES['poetry']['dark']};
    --series-uv:     {SERIES['uv']['dark']};
  }}

  body {{
    margin: 0;
    background: var(--plane);
    color: var(--ink);
    font-family: var(--sans);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}
  .wrap {{
    max-width: 1040px;
    margin: 0 auto;
    padding: 48px 24px 96px;
    display: flex;
    flex-direction: column;
    gap: 40px;
  }}
  h1, h2, h3 {{ text-wrap: balance; margin: 0; }}
  h1 {{ font-size: clamp(28px, 4.4vw, 44px); letter-spacing: -0.02em; line-height: 1.1; }}
  h2 {{ font-size: 21px; letter-spacing: -0.01em; }}
  p {{ margin: 0; }}
  code {{ font-family: var(--mono); font-size: 0.92em; }}

  header {{ display: flex; flex-direction: column; gap: 24px; }}
  .eyebrow {{
    font-family: var(--mono);
    font-size: 12px;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: var(--muted);
  }}
  .lede {{ max-width: 62ch; color: var(--ink-2); font-size: 17px; }}

  .hero {{ display: flex; align-items: baseline; gap: 20px; flex-wrap: wrap; }}
  .hero-figure {{
    font-size: clamp(56px, 9vw, 92px);
    font-weight: 600;
    letter-spacing: -0.04em;
    line-height: 0.9;
    color: var(--series-uv);
  }}
  .hero-text {{ max-width: 34ch; color: var(--ink-2); font-size: 15px; }}
  .hero-text strong {{ color: var(--ink); font-weight: 600; }}

  dl.spec {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px 32px;
    margin: 0;
    padding: 16px 20px;
    background: var(--surface);
    border: 1px solid var(--hairline);
    border-radius: 3px;
  }}
  dl.spec dt {{
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
  }}
  dl.spec dd {{ margin: 0; font-family: var(--mono); font-size: 13px; color: var(--ink-2); }}

  .legend {{ display: flex; gap: 24px; flex-wrap: wrap; align-items: center; }}
  .legend span {{ display: inline-flex; align-items: center; gap: 8px; font-size: 14px; color: var(--ink); }}
  .legend code {{ color: var(--muted); }}
  .swatch {{ width: 10px; height: 10px; border-radius: 2px; flex: none; }}

  .scenario {{
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 28px;
    background: var(--surface);
    border: 1px solid var(--hairline);
    border-radius: 3px;
  }}
  .scenario-head {{ display: flex; flex-direction: column; gap: 6px; }}
  .blurb {{ color: var(--ink-2); font-size: 15px; max-width: 68ch; }}
  .axis {{
    font-family: var(--mono);
    font-size: 12px;
    color: var(--muted);
    font-variant-numeric: tabular-nums;
  }}
  .note {{
    font-size: 13.5px;
    color: var(--ink-2);
    max-width: 72ch;
    padding-left: 12px;
    border-left: 2px solid var(--grid);
  }}

  .panels {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 28px; }}
  .panel {{ margin: 0; display: flex; flex-direction: column; gap: 10px; min-width: 0; }}
  figcaption {{ display: flex; flex-direction: column; gap: 1px; }}
  .panel-name {{ font-size: 14px; font-weight: 600; }}
  .panel-meta {{ font-family: var(--mono); font-size: 11.5px; color: var(--muted); }}

  .row {{ display: grid; grid-template-columns: 62px 1fr auto; align-items: center; gap: 10px; }}
  .row-name {{ font-size: 13px; color: var(--ink-2); }}
  .track {{
    position: relative;
    height: 18px;
    min-width: 0;
    background: linear-gradient(to right, var(--grid) 1px, transparent 1px) repeat-x;
    background-size: 25% 100%;
    border-radius: 0 2px 2px 0;
    outline-offset: 3px;
  }}
  .bar {{
    height: 100%;
    border-radius: 0 4px 4px 0;
    min-width: 3px;
  }}
  .row-value {{
    font-family: var(--mono);
    font-size: 13px;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
    color: var(--ink);
  }}
  .factor {{ color: var(--muted); margin-left: 8px; }}

  .tip {{
    position: absolute;
    left: 0;
    bottom: calc(100% + 8px);
    z-index: 5;
    width: max-content;
    max-width: 300px;
    padding: 8px 10px;
    background: var(--ink);
    color: var(--surface);
    font-size: 12px;
    line-height: 1.35;
    border-radius: 3px;
    opacity: 0;
    visibility: hidden;
    transition: opacity 120ms ease;
  }}
  .track:hover .tip, .track:focus-visible .tip {{ opacity: 1; visibility: visible; }}
  @media (prefers-reduced-motion: reduce) {{ .tip {{ transition: none; }} }}

  .scroller {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
  th, td {{ text-align: left; padding: 7px 12px; border-bottom: 1px solid var(--grid); white-space: nowrap; }}
  thead th {{
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 500;
  }}
  td.num, th.num {{ text-align: right; font-family: var(--mono); font-variant-numeric: tabular-nums; }}
  td.strong {{ color: var(--ink); }}
  td.muted {{ color: var(--muted); }}
  th.set-head {{
    border-left: 1px solid var(--grid);
    color: var(--ink);
    font-size: 12px;
    text-align: center;
  }}
  th.tool {{ font-weight: 400; color: var(--ink-2); }}
  th.tool .swatch {{ display: inline-block; margin-right: 8px; vertical-align: middle; }}

  .method {{ display: flex; flex-direction: column; gap: 12px; }}
  .method ul {{ margin: 0; padding-left: 20px; display: flex; flex-direction: column; gap: 8px; }}
  .method li {{ color: var(--ink-2); font-size: 14.5px; max-width: 76ch; }}
  .method strong {{ color: var(--ink); font-weight: 600; }}
  pre {{
    margin: 0;
    padding: 14px 16px;
    background: var(--surface);
    border: 1px solid var(--hairline);
    border-radius: 3px;
    overflow-x: auto;
    font-family: var(--mono);
    font-size: 13px;
    color: var(--ink-2);
  }}
  footer {{ color: var(--muted); font-size: 13px; border-top: 1px solid var(--grid); padding-top: 20px; }}
</style>

<div class="wrap">
  <header>
    <p class="eyebrow">module 01 · пакетні менеджери</p>
    <h1>pip, Poetry і uv на тих самих залежностях</h1>
    <p class="lede">
      Той самий набір пакетів, той самий інтерпретатор, той самий кеш — і три операції,
      які ви робите щодня. Усі цифри отримані скриптом <code>bench.py</code> із цієї теки;
      запустіть його й отримаєте свої.
    </p>
{hero(by_scenario, sets)}
    <dl class="spec">
{spec_strip(payload)}
    </dl>
    <div class="legend">
      <span><i class="swatch" style="background:var(--series-pip)"></i>pip <code>· python -m venv + pip install</code></span>
      <span><i class="swatch" style="background:var(--series-poetry)"></i>Poetry <code>· poetry install</code></span>
      <span><i class="swatch" style="background:var(--series-uv)"></i>uv <code>· uv sync</code></span>
    </div>
  </header>

{sections}

{table(by_scenario, sets)}

  <section class="method">
    <h2>Як це міряли</h2>
    <ul>
      <li><strong>Кеші перенаправлені, а не почищені.</strong> Кожен процес отримує
        <code>PIP_CACHE_DIR</code>, <code>POETRY_CACHE_DIR</code>, <code>UV_CACHE_DIR</code>
        у тимчасовій теці. «Порожній кеш» — це новий порожній кеш, а не
        <code>uv cache clean</code>: ваш справжній кеш не чіпають.</li>
      <li><strong>Один інтерпретатор на всі три інструменти</strong>, знайдений через
        <code>uv python find</code>. Жодному з них не дозволено завантажувати Python,
        інакше ми міряли б швидкість мережі, а не резолвер.</li>
      <li><strong>venv створюється всередині заміру.</strong> <code>poetry install</code> і
        <code>uv sync</code> роблять оточення самі, тому pip міряється разом із
        <code>python -m venv</code> — інакше pip виглядав би швидшим, ніж він є.</li>
      <li><strong>Міряється лише команда під тестом.</strong> Lock-файл, з якого встановлюють,
        і прогрів кешу — це підготовка, вона поза таймером.</li>
      <li><strong>pip встановлює з приколотих версій.</strong> У рядку «резолюція» він
        справді резолвить (через <code>pip-compile</code>), а в рядках встановлення читає
        готовий <code>requirements.txt</code> — так само, як Poetry й uv читають свої
        lock-файли. Реальний <code>requirements.txt</code> теж приколотий, тому pip там
        швидший саме тому, що робить менше.</li>
      <li><strong>Один запуск на клітинку</strong> — це заміри, а не статистика. Для
        «резолюції» й «теплого кешу» різниця між запусками — одиниці відсотків; для
        «порожнього кешу» вона велика. Кожна команда, її тривалість і код повернення —
        у <code>results.json</code>.</li>
    </ul>
  </section>

  <section class="method">
    <h2>Набори залежностей</h2>
    <ul>
{set_notes}
    </ul>
    <pre>cd module01/07_compare
python3 bench.py --quick     # лише малий набір, ~1 хвилина
python3 bench.py             # уся матриця → results.json
python3 render.py            # results.json → bench.html</pre>
  </section>

  <footer>
    Заміри на одній машині з домашньою мережею. Цифри для «порожнього кешу» залежать від
    каналу й дзеркала PyPI; «резолюція» і «теплий кеш» від мережі майже не залежать —
    саме на них варто дивитися.
  </footer>
</div>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--results", type=Path, default=HERE / "results.json")
    parser.add_argument("--out", type=Path, default=HERE / "bench.html")
    args = parser.parse_args()

    payload = json.loads(args.results.read_text())
    args.out.write_text(page(payload))
    print(f"written to {args.out}")


if __name__ == "__main__":
    main()
