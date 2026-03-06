### Архитектура
Архитектура разделена на слои:

- `API` слой  
Принимает `http` запросы. Зависят от `usecases`
`account router`: `POST /api/accounts` `GET /api/accounts` `GET /api/accounts/{id}`

`transaction router`: `POST /api/transaction` `GET /api/transactions/{id}` `GET /api/accounts/{id}/transactions`

- `Service` слой
Роуты вызывают `usecases`. Они собирают данные в `Entitys`, выполняют дополнительную валидацию, собирают данные необходимые для выполнения логики. Зависят от `repository`

- `Domain` слой
Слой, который хранит логику. `entities` `services`. Ни от чего не зависит

- `Repository` слой
Слой, который хранит `repositories`, классы для хранения методов обращения к хранилищам данных. 
<img width="1696" height="447" alt="image" src="https://github.com/user-attachments/assets/b19802a2-15d1-4bdd-82d9-3e0243beff1d" />

### Запуск
Для запуска нужно просто зайти в директорию и выполнить `docekr compose up -d`.
Миграции будут применены автоматически. `uvicorn` так же запустится автоматически. После запуска переходим в браузере `http://127.0.0.1:8000/docs#/`, там `Swagger` уже нарисовал минимальный интерфейс для работы с API.

Файл `.env` на гите не по ошибке, а для того, что бы упростить жизнь клонерам.

### Запуск тестов
API тесты: 
`python -m pytest tests/api_tests.py`

Domain тесты:
`python -m pytest tests/domain_tests.py`

Тест SQLAlchemy моделей: 
`python -m pytest tests/models_tests.py`

Тест Pydantic моделей:
`python -m pytest tests/pydantic_models_tests/account_schemas_tests.py`
`python -m pytest tests/pydantic_models_tests/transaction_schemas_tests.py`

Usecases тест: 
`python -m pytest tests/usecases_tests/account_usecases_tests.py`
`python -m pytest tests/usecases_tests/transaction_usecases_tests.py`

Repositories тест:
`python -m pytest tests/repositories_tests/account_repository_tests.py`
`python -m pytest tests/repositories_tests/transaction_repository_tests.py`

Интеграционные тесты:
`python -m pytest tests/integration_account_tests.py`
`python -m pytest tests/integration_transaction_tests.py`
