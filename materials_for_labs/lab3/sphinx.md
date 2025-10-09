# Sphinx

Относительно хорошая статья про сборку документации в python проекте:
https://habr.com/ru/articles/750968/

* это достаточно популярный инструмент для ведения автодокументации на проекте.
* рекрасен в комбинации GithubAction + GithubPages.
* удобен в настройке в проекте, сборка осуществляется в отдельной ветке в репозитории, документация описывается в *.rst формате.
* куча библиотек для связи с Pydantic, Numpy, Pandas и т.д. и т.п.

# Сборка и тест Sphinx

Для локальной сборки Sphinx и последующего теста следующая инструкция:

Вы в корневой папке проекта
```Bash
# Запуск виртуального окружения
python3 -m venv .venv
```

```Bash
# Активация виртуального окружения
source .venv/bin/activate
```

```Bash
# Установка того, что нужно для sphinx
pip install sphinx sphinx-autodoc-typehints pydantic sphinx_rtd_theme
```

```Bash
# Запуск создания окружения для sphinx
sphinx-quickstart docs_src
```

```Bash
# Запуск автосборки документации по docsting для sphinx
sphinx-apidoc -o docs_src/source students_folder
```

```Bash
# Сборка html
# Переходим в docs_src
cd docs_src
# Генерируем html странички
make html
```

```Bash
# Если все OK, то не забываме git add.
git add .
```

# Тест в существующем окружении Sphinx
Вы в корневой папке проекта
```Bash
# Запуск виртуального окружения
python3 -m venv .venv
```

```Bash
# Активация виртуального окружения
source .venv/bin/activate
```

```Bash
# Установка того, что нужно для sphinx
pip install sphinx sphinx-autodoc-typehints pydantic sphinx_rtd_theme
```

```Bash
# Сборка html
# Переходим в docs_src
cd docs_src
# Генерируем html странички
make html
```

```Bash
# Если все OK, то не забываме git add.
git add .
```
