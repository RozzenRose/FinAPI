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
