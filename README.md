# Проект «Курсовая работа по написанию и контейнеризации бэкэнда» 
![Github actions](https://github.com/snigiden/foodgram-project-react/actions/workflows/workflow.yml/badge.svg)
___
## Используемые технологии:
- Python
- Django
- Django Rest Framework
- Docker
- PostgreSQL
- Telegram bot API
___
## Описание

Данный репозиторий содержит курсовую работу по написанию бэкэнда для фудблога, построенного на работе с эндпоинтами, указанными ниже, и последующем его CI/CD.
___
## Установка и запуск
* Клонировать репозиторий

* Установить docker на удалённый сервер под управлением debian based дистрибутива linux

* Настроить nginx и docker на удалённом сервере

* Создать .env файл

* Отредактировать цепочку секретов

* Импортировать базу ингредиентов:
  sudo docker-compose exec backend python manage.py load_ingredients
___
## Список эндпоинтов:

* /api/users
* /api/recipes
* /api/ingredients
* /api/tags

***
## Памятка .env
~~~
DB_ENGINE= СУБД
DB_NAME= имя базы данных
POSTGRES_USER= логин для подключения к базе данных
POSTGRES_PASSWORD= пароль для подключения к БД
DB_HOST= название сервиса (контейнера)
DB_PORT= порт для подключения к БД 
~~~
