# Integração com Banco de Dados e Testes

## 1. O Modelo (`models.py`) — "A Planta da Casa"

```python
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    registry,
)

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
```

**Pra uma criança de 5 anos:**
Imagine que você quer guardar dados de pessoas em uma gaveta. Antes de guardar, você precisa desenhar a "planta" de como cada pessoa vai ser anotada: nome, email, senha, e quando ela foi cadastrada. O `User` é essa planta. O `__tablename__ = "users"` é o nome da gaveta. O `table_registry` é o "caderno de registro" que diz "essa planta aqui vai virar uma gaveta de verdade no banco".

### Detalhes técnicos

- **`registry()`** — É o objeto central do SQLAlchemy que coordena a criação de tabelas, a relação entre classes Python e tabelas SQL. Pense nele como o "cartório" que registra que a classe `User` vira a tabela `users`.
- **`@table_registry.mapped_as_dataclass`** — Decorator que faz DUAS coisas ao mesmo tempo:
  1. Torna a classe uma **dataclass** Python (ganha `__init__`, `__repr__`, `__eq__` automáticos)
  2. Mapeia a classe para uma **tabela SQL** (declarative mapping do SQLAlchemy)
- **`Mapped[tipo]`** — Anotação que diz "essa coluna existe e é desse tipo". O SQLAlchemy lê essas anotações pra criar as colunas.
- **`mapped_column(init=False, primary_key=True)`** — Configura a coluna:
  - `init=False` → não pede no construtor (o banco gera automaticamente)
  - `primary_key=True` → chave primária (identificador único)
  - `unique=True` → não permite valores repetidos
  - `server_default=func.now()` → valor padrão é a data/hora atual do banco
- **`func.now()`** — Não é executado no Python! Vira o SQL `now()` no banco. Quem define o valor é o banco de dados no momento do INSERT.

---

## 2. A Infraestrutura de Teste (`conftest.py`) — "O Playground"

O `conftest.py` é um arquivo especial que o `pytest` lê automaticamente. Tudo que é definido aqui como fixture fica disponível pra qualquer teste na mesma pasta (e subpastas).

### Fixture `session` — "Cria uma gaveta de mentirinha"

```python
@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()
```

**Pra criança de 5 anos:**
Em vez de usar uma gaveta de verdade (um banco de dados PostgreSQL no servidor), você pega uma folha de papel e desenha uma gaveta falsa — o `sqlite:///:memory:`. É uma gaveta que só existe enquanto você brinca com ela. Quando termina, você amassa o papel e joga fora.

**Passo a passo:**

1. **`create_engine("sqlite:///:memory:")`** — Cria um banco SQLite que vive só na RAM. Não cria arquivo nenhum. É rápido e isolado.
2. **`table_registry.metadata.create_all(engine)`** — O registry tem um atributo `metadata` que é um catálogo de todas as tabelas registradas (no caso, só `users`). `create_all` executa o `CREATE TABLE` no banco. É aqui que a planta vira gaveta de verdade.
3. **`with Session(engine) as session: yield session`** — Cria uma sessão de conexão com o banco. O `yield` é o que faz uma fixture funcionar em dois tempos:
   - **Antes do teste**: cria o banco, cria as tabelas, entrega a `session`
   - **Depois do teste**: volta pra limpar
4. **`table_registry.metadata.drop_all(engine)`** — Executa `DROP TABLE` pra limpar.
5. **`engine.dispose()`** — Fecha a conexão.

### `_mock_db_time` — "O Relógio de Mentira"

```python
@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 1, 1)):

    def fake_time_hook(maper, connection, target):
        if hasattr(target, "created_at"):
            target.created_at = time

    event.listen(model, "before_insert", fake_time_hook)

    yield time

    event.remove(model, "before_insert", fake_time_hook)
```

**Pra criança de 5 anos:**
Imagine que você quer testar se o relógio do banco funciona, mas não quer esperar até 2026 pra ver se a data fica certa. Então você coloca um "adesivo" no banco que diz: "toda vez que for salvar, usa esse relógio de mentira aqui, não o relógio de verdade".

**Conceitos complexos explicados:**

- **`@contextmanager`** — Transforma uma função que tem `yield` em algo que você usa com `with`. É como um "intervalo": tudo antes do `yield` é a "preparação", tudo depois é a "limpeza".
- **`event.listen(model, "before_insert", fake_time_hook)`** — É um **hook** (gancho). O SQLAlchemy dispara eventos durante o ciclo de vida de uma operação. `before_insert` é disparado **antes** de inserir uma linha na tabela. A gente "escuta" esse evento e executa `fake_time_hook`.
- **`fake_time_hook`** — Recebe 3 parâmetros:
  - `maper` — o mapper (ignorado)
  - `connection` — a conexão (ignorado)
  - `target` — a **instância** do objeto que está sendo inserida

  Dentro do hook: se o objeto tiver o atributo `created_at`, substitui pelo valor mockado (`time`).
- **`event.remove(...)`** — Remove o hook depois que o teste acaba. Senão, hooks acumulados podem vazar entre testes.

### Fixture `mock_db_time`

```python
@pytest.fixture
def mock_db_time():
    return _mock_db_time
```

**Pra criança de 5 anos:**
É só um "apelido" pra função `_mock_db_time`. Como o `pytest` só enxerga fixtures, a gente cria essa fixture que devolve a função. Aí os testes podem pedir `mock_db_time` como parâmetro.

---

## 3. O Teste (`test_db.py`) — "A Prova"

```python
from dataclasses import asdict

from sqlalchemy import select

from models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username="jady", password="secret", email="jady@teste.com"
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == "jady"))

    assert asdict(user) == {
        "id": 1,
        "username": "jady",
        "password": "secret",
        "email": "jady@teste.com",
        "created_at": time,
    }
```

**Passo a passo completo:**

1. **`def test_create_user(session, mock_db_time):`**
   O pytest vê que o teste precisa de `session` e `mock_db_time`. Ele procura as fixtures com esses nomes no `conftest.py` e **injeta** os valores automaticamente (isso se chama **dependency injection** — em vez de você criar os objetos, alguém te entrega eles prontos).

2. **`with mock_db_time(model=User) as time:`**
   Chama o context manager `_mock_db_time`. Antes de executar o bloco `with`, ele:
   - Instala o hook `before_insert` no modelo `User`
   - Define `time = datetime(2026, 1, 1)`
   - Retorna `time` no `as ... time`

3. **`new_user = User(...)`**
   Cria uma instância de `User`. Como é uma `@mapped_as_dataclass`, o construtor (`__init__`) foi gerado automaticamente com os campos: `username`, `password`, `email`.
   `id` e `created_at` têm `init=False`, então não aparecem no construtor.

4. **`session.add(new_user)`**
   Fala pra sessão: "vigia esse objeto". Ainda não foi pro banco.

5. **`session.commit()`**
   Aqui acontece a mágica:
   - O SQLAlchemy gera o SQL: `INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)`
   - Antes de executar, dispara o evento `before_insert`
   - Nosso hook pega o `target` (o `new_user`) e seta `target.created_at = time` (2026-01-01)
   - O SQL é executado
   - O banco retorna o `id` gerado (auto-increment)
   - O SQLAlchemy atualiza o objeto `new_user.id` com o valor retornado

6. **`session.scalar(select(User).where(User.username == "jady"))`**
   Faz uma consulta: `SELECT * FROM users WHERE username = 'jady'`.
   `scalar()` retorna um único resultado (ou `None`). O SQLAlchemy reconstrói um objeto `User` a partir da linha do banco.

7. **`asdict(user)`**
   Como `User` é uma dataclass, `asdict()` converte pra dicionário. Vai retornar:
   ```python
   {
       "id": 1,
       "username": "jady",
       "password": "secret",
       "email": "jady@teste.com",
       "created_at": datetime(2026, 1, 1, 0, 0)
   }
   ```

8. **`assert`**
   Compara o dicionário com o esperado. Se tudo bater, o teste passa.

---

## 4. Fluxo Visual Completo

```
models.py (planta)
    │
    ▼
conftest.py: session()
    ├── create_engine("sqlite:///:memory:")  → banco fake na RAM
    ├── create_all(engine)                   → CREATE TABLE users
    ├── yield session                        → entrega pro teste
    │
    ▼
test_db.py: test_create_user(session, mock_db_time)
    │
    ├── mock_db_time(model=User)
    │   └── hook: before_insert → sobrescreve created_at
    │
    ├── User(username="jady", ...)  → cria objeto
    ├── session.add(new_user)       → observa
    ├── session.commit()            → INSERT + dispara hook
    │
    ├── session.scalar(select(...)) → SELECT
    │
    └── assert asdict(user) == {...}  → verifica
    │
    ▼
conftest.py: session() (volta do yield)
    ├── drop_all(engine)  → DROP TABLE
    └── dispose()         → fecha conexão
```

---

## 5. Resumo dos Conceitos (versão 5 anos)

| Conceito | Explicação |
|----------|-----------|
| **ORM** | É um tradutor: você escreve `User()` em Python, ele vira `INSERT INTO users` em SQL |
| **Registry** | Um caderno que guarda a lista de todas as plantas de gaveta que você desenhou |
| **Fixture** | Um "ajudante" que prepara tudo que o teste precisa e limpa depois |
| **Session** | Um bloco de notas onde você rabisca as mudanças (add). Só quando você `commit`, passa a limpo pro banco |
| **`yield` em fixture** | "Pausa" a fixture: prepara as coisas → entrega pro teste → volta pra limpar |
| **Event hook** | Um "aviso" que o SQLAlchemy dá: "ei, estou prestes a inserir algo! Alguém quer mexer antes?" |
| **SQLite :memory:** | Banco de dados que mora na RAM — quando o programa termina, ele simplesmente desaparece |
| **Dependency Injection** | O pytest pergunta pro teste "você precisa de quê?" e entrega na mão — você não precisa criar nada |

---

# Configuração do Banco + Alembic

## 1. Criar `fast_zero/settings.py`

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str = Field(init=False)
```

## 2. Criar `.env` na raiz do projeto

```
DATABASE_URL="sqlite:///database.db"
```

## 3. Adicionar `database.db` ao `.gitignore`

```bash
echo 'database.db' >> .gitignore
```

## 4. Instalar Alembic

```bash
poetry add alembic
```

## 5. Iniciar Alembic

```bash
alembic init migrations
```

Cria o diretório `migrations/` e o arquivo `alembic.ini`.

## 6. Configurar `migrations/env.py`

Adicionar os imports e configurar a URL do banco e os metadados:

```python
from fast_zero.models import table_registry
from fast_zero.settings import Settings

config = context.config
config.set_main_option('sqlalchemy.url', Settings().DATABASE_URL)
target_metadata = table_registry.metadata
```

## 7. Criar migração automática

```bash
alembic revision --autogenerate -m "create users table"
```

Gera um arquivo em `migrations/versions/` com `upgrade()` e `downgrade()`.

## 8. Aplicar a migração

```bash
alembic upgrade head
```

## 9. Verificar o banco (opcional)

```bash
sqlite3 database.db
.tables
.schema
select version_num from alembic_version;
.quit
```
