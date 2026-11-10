# План переноса провайдера HBase в апстрим (apache/airflow)

Целевое расположение: `providers/apache/hbase/` (не `providers/arenadata/hbase/`).

---

## 1. Структура директорий

Создать `providers/apache/hbase/` по структуре апстрима:

✅ **Структура создана.** Текущее состояние:

```
providers/apache/hbase/
├── pyproject.toml
├── provider.yaml
├── CHANGELOG.rst
├── README.rst
├── LICENSE
├── NOTICE
├── ruff.toml
├── src/airflow/providers/apache/hbase/
│   ├── hooks/          (hbase.py, hbase_cli.py, hbase_strategy.py)
│   ├── operators/      (hbase.py)
│   ├── sensors/        (hbase.py)
│   ├── client/         (thrift2_client.py)
│   ├── datasets/       (hbase.py)
│   ├── utils/          (data_conversion.py)
│   ├── hbase_thrift2_generated/   (вендоринг, см. п. 6b)
│   ├── example_dags/   (оставлены в src, см. п. 6e)
│   ├── connection_config.py
│   ├── thrift2_pool.py
│   ├── thrift2_ssl.py
│   ├── version_compat.py
│   └── get_provider_info.py
├── tests/
│   ├── unit/apache/hbase/
│   │   ├── hooks/
│   │   ├── operators/
│   │   ├── sensors/
│   │   └── utils/
│   └── integration/apache/hbase/  (будут удалены, см. п. 6d)
└── docs/
    ├── index.rst
    ├── commits.rst
    ├── connections.rst
    ├── hooks.rst
    ├── operators.rst
    ├── sensors.rst
    ├── security.rst
    ├── changelog.rst
    ├── example-dags.rst
    └── installing-providers-from-sources.rst
```

---

## 2. Массовый рефакторинг импортов ✅

Все вхождения `airflow.providers.arenadata.hbase` → `airflow.providers.apache.hbase` заменены во всех `.py` файлах.

---

## 3. Метаданные пакета ✅

`provider.yaml`, `pyproject.toml`, `get_provider_info.py` обновлены: все пути `arenadata` → `apache`, `package-name` = `apache-airflow-providers-apache-hbase`, `versions` сброшены до `1.0.0`, `state: not-ready`.

---

## 4. Тесты ✅

`tests/unit/apache/hbase/` — переструктурировано, 136 unit-тестов проходят. Интеграционные тесты в `tests/integration/` будут удалены перед финальным PR (см. п. 6d).

---

## 5. Документация ✅

Все RST-файлы созданы с правильными путями `apache-airflow-providers-apache-hbase`. RST-синтаксис проверен (docutils). Полная сборка через `breeze build-docs apache.hbase` временно недоступна из-за конфликта пакетов в базовом Docker-образе (`dhi.io` зеркало Debian) — upstream-проблема, не связанная с нашим кодом.

---

## 6. Специфика апстрима — требует отдельных решений

### a) `version_compat.py` ✅

**Решение принято**: оставить совместимость с Airflow 2.11+.

Файл использует прямые импорты из стабильных путей (`airflow.hooks.base`, `airflow.models.*`, `airflow.sensors.base`, `airflow.utils.context`), которые работают на всех версиях от 2.11.2 до 3.3.2. Импорты из `airflow.sdk` (появились в `common-compat>=1.12.0`) не используются — это намеренно, чтобы не ломать совместимость со старыми образами.

**Проверено**: тесты прошли на образах `hbase-test` для Airflow 2.11.2, 3.0.6, 3.1.8, 3.2.2, 3.3.2 со всеми поддерживаемыми Python (3.10–3.14).

**Важно из документации апстрима**: `version_compat.py` нельзя импортировать из другого провайдера или из тестового кода — это проверяется prek-хуком `check-imports-in-providers`. Файл должен быть скопирован целиком в корень пакета провайдера и использоваться только внутри него.

### b) `hbase_thrift2_generated/`
Сгенерированный Thrift-код (`THBaseService.py`, `ttypes.py`) — вендоринг. Пока **исключён из ruff** (`ruff.toml`). Вопрос будет поднят в code review апстрима.

Варианты для обсуждения:
- **Обосновать в PR** — добавить комментарий с источником `.thrift`-схемы и командой генерации; HBase Thrift2 API стабилен, перегенерация не нужна
- **Вынести в отдельный пакет** — если апстрим настаивает

### c) `sasl` зависимость ✅
`sasl` не используется в коде провайдера и не объявлен ни в `pyproject.toml`, ни в `provider.yaml`. Проблема снята.

### d) Тесты — system tests
`tests/integration/` будут **удалены** перед финальным PR. System tests в формате апстрима (`SystemTestContextBuilder`) — задача на будущее, после принятия провайдера в incubation.

### e) `example_dags/`
**Решение принято**: оставить в `src/.../example_dags/`. Перенос в `tests/system/` — задача на будущее. Апстрим принимает example DAGs в `src/` для новых провайдеров на стадии incubation.

### f) pylint → ruff ✅
`ruff.toml` добавлен, `# pylint: disable=...` убраны или заменены на `# noqa:`. `hbase_thrift2_generated/` исключён из ruff.

### g) `CHANGELOG.rst` ✅
Первоначальный changelog написан вручную в формате апстрима.

### h) `VERSIONING.md` ✅
Файл отсутствует (не переносился из arenadata).

---

## 7. Процесс принятия в апстрим (Accepting New Community Providers)

Перед открытием PR нужно пройти официальный процесс принятия нового провайдера.

### Предварительные требования

- **Working codebase** — рабочая реализация с тестами ✅
- **Stewardship commitment** — минимум 2 человека, готовых быть стюардами провайдера ⬜
- **Committer sponsorship** — минимум 1 существующий Airflow Committer, готовый спонсировать ⬜
- **Quality standards** — код, тесты, документация по [Contributing Guide](https://github.com/apache/airflow/blob/main/contributing-docs/README.rst) ⬜
- **System tests** — описать как будет валидироваться интеграция с живым HBase; апстрим поощряет публикацию результатов на публичном дашборде ⬜

### Процесс

1. Открыть `[DISCUSS]` тред на devlist (`dev@airflow.apache.org`) по шаблону ниже
2. Подождать 7 дней без возражений
3. После принятия — открывать PR

Формального голосования не требуется.

### Incubation stage — метрики за 6 месяцев

После принятия провайдер входит в **Incubation stage**. PMC проверяет метрики ежеквартально. Для graduation в Production нужно выполнить за 6 месяцев:

| Метрика | Порог |
|---------|-------|
| PR submitted | Минимум 10 PR за 6 месяцев |
| PR review time | PR рассматриваются в течение 14 дней |
| Issues reported | Минимум 15 уникальных issues за 6 месяцев |
| Contributors | Минимум 3 уникальных контрибьютора (код или документация) |
| Issue resolution rate | Минимум 50% issues закрыты в течение 90 дней |
| Security/release issues | Все security и release issues закрыты в течение 60 дней |
| Governance participation | Участие в квартальных governance updates на devlist |
| Quality standards | Соответствие Contributing Guide |

Эти метрики **аспирационные** — PMC пересмотрит их через 6 месяцев после первого квартального ревью.

### Шаблон письма на devlist

```
Subject: [DISCUSS] New Community Provider: Apache HBase

Hi Airflow community,

I'd like to propose adding a new community provider for Apache HBase.

Integration overview
--------------------
Apache HBase is a distributed, scalable, big data store built on top of HDFS.
This provider enables Airflow users to interact with HBase via the Thrift2 API,
offering hooks, operators, and sensors for common HBase operations.

System tests
------------
<описать как будут запускаться system tests и будет ли публичный дашборд>

Proposed stewards
-----------------
- <Name, GitHub handle, email>
- <Name, GitHub handle, email>

Sponsoring committer(s)
-----------------------
- <Name, GitHub handle>

Working implementation
----------------------
<ссылка на draft PR>

Incubation commitment
---------------------
We commit to:
- Maintaining the provider and responding to issues within a reasonable time
- Meeting the incubation health metrics within 6 months
- Participating in quarterly governance updates

Best regards,
<Your name>
```

---

## 8. Регистрация провайдера в монорепо

Апстрим использует **prek** (форк pre-commit, написанный на Rust) для статических проверок. Ряд хуков автоматически обновляет файлы монорепо при коммите.

**Что prek делает автоматически при коммите:**

- `update-pyproject-toml` — при изменении `provider.yaml` обновляет **корневой `pyproject.toml`** монорепо (регистрирует провайдер в рабочем пространстве)
- `sync-provider-readme` — синхронизирует `README.rst` провайдера с `pyproject.toml`
- `insert-license` — добавляет лицензионные заголовки во все файлы
- `ruff` + `ruff-format` — линтинг и форматирование
- `check-example-dag-tags` — проверяет наличие тега `"example"` в всех example DAGs
- `codespell` — проверяет орфографию; специфичные термины (`HBase`, `Thrift` и т.д.) нужно добавить в `docs/spelling_wordlist.txt`

**Установка и запуск:**

```bash
# Установить prek
uv tool install prek

# Зарегистрировать хуки в git
prek install

# Запустить все хуки на файлах провайдера перед PR
prek --all-files
```

После изменения зависимостей в `provider.yaml` — синхронизировать с `pyproject.toml`:

```bash
prek update-providers-dependencies --all-files
```

Локальная сборка провайдера для тестирования:

```bash
cd providers/apache/hbase
flit build
```

---

## Чеклист

| Задача | Сложность | Статус |
|--------|-----------|--------|
| Переименование путей (`arenadata` → `apache`) | Механическая, но объёмная | ✅ |
| Метаданные (`provider.yaml`, `pyproject.toml`, `get_provider_info.py`) | Простая | ✅ |
| Переструктурировать тесты (unit) | Простая | ✅ |
| Документация RST-файлы | Простая | ✅ |
| Убрать pylint, адаптировать под ruff | Простая | ✅ |
| Убрать `VERSIONING.md` | Простая | ✅ |
| Написать CHANGELOG в правильном формате | Простая | ✅ |
| Решение по `version_compat.py` (Airflow 2 vs 3) | Требует решения | ✅ |
| `on_kill` в операторах backup/restore | Средняя | ✅ |
| `max_workers` default выровнен в документации | Простая | ✅ |
| Kerberos/SASL — задокументировано как known limitation | Простая | ✅ |
| Удалить `tests/integration/` | Простая | ⬜ |
| Установить prek и запустить `prek --all-files` на файлах провайдера | Простая | ⬜ |
| Добавить HBase-специфичные термины в `docs/spelling_wordlist.txt` | Простая | ⬜ |
| `prek update-providers-dependencies --all-files` | Простая | ⬜ |
| Адаптация `sasl` зависимости | Средняя | ✅ (не используется) |
| Решение по `hbase_thrift2_generated/` (обсудить в PR) | Требует обсуждения с апстримом | ⬜ |
| Найти 2 стюарда и спонсора-коммиттера | Организационная | ⬜ |
| Описать план system tests для [DISCUSS] треда | Организационная | ⬜ |
| Отправить [DISCUSS] на devlist и дождаться одобрения | Организационная | ⬜ |
| System tests в формате апстрима (после incubation) | Средняя | ⬜ |
