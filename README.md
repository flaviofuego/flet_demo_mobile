# flet_demo_mobile

A Flet mobile application built with **Clean Architecture** principles.

## Architecture overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        main.py  (entry point + DI)               │
└────────────────────────────┬─────────────────────────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │         Presentation Layer           │
          │  pages/  │  components/  │ viewmodels│
          └──────────────────┬──────────────────-┘
                             │  (calls use cases)
          ┌──────────────────▼──────────────────┐
          │           Domain Layer               │
          │  entities/  │  usecases/  │ repos/   │
          └──────────────────┬──────────────────-┘
                             │  (implements contracts)
          ┌──────────────────▼──────────────────┐
          │            Data Layer                │
          │  models/  │  datasources/  │ repos/  │
          └─────────────────────────────────────-┘
                             │
          ┌──────────────────▼──────────────────┐
          │              Core                    │
          │  error/exceptions  │  utils/result   │
          └─────────────────────────────────────-┘
```

### Layer responsibilities

| Layer            | Package                        | Responsibility                                          |
|------------------|--------------------------------|---------------------------------------------------------|
| **Core**         | `src/core/`                    | Cross-cutting concerns: exceptions, `Result` type       |
| **Domain**       | `src/domain/`                  | Business entities, repository contracts, use cases      |
| **Data**         | `src/data/`                    | DTOs, data sources, repository implementations          |
| **Presentation** | `src/presentation/`            | Flet pages, reusable components, view models            |

### Dependency rule

Dependencies only point **inward**:

```
Presentation → Domain ← Data
                 ↑
               Core
```

The domain layer has **zero** knowledge of Flet, databases, or any
infrastructure detail. Every concrete dependency is injected in `main.py`.

---

## Project structure

```
flet_demo_mobile/
├── main.py                                # Entry point + manual DI wiring
├── requirements.txt
├── pyproject.toml
├── src/
│   ├── core/
│   │   ├── error/
│   │   │   └── exceptions.py             # AppException hierarchy
│   │   └── utils/
│   │       └── result.py                 # Result[T] = Success | Failure
│   ├── domain/
│   │   ├── entities/
│   │   │   └── user.py                   # User entity (immutable dataclass)
│   │   ├── repositories/
│   │   │   └── user_repository.py        # Abstract repository contract
│   │   └── usecases/
│   │       └── get_users.py              # GetUsersUseCase
│   ├── data/
│   │   ├── models/
│   │   │   └── user_model.py             # UserModel DTO (JSON ↔ entity)
│   │   ├── datasources/
│   │   │   └── user_local_datasource.py  # In-memory data source
│   │   └── repositories/
│   │       └── user_repository_impl.py   # UserRepository implementation
│   └── presentation/
│       ├── pages/
│       │   └── home_page.py              # Home screen
│       ├── components/
│       │   └── user_card.py              # Reusable UserCard widget
│       └── viewmodels/
│           └── home_viewmodel.py         # State + commands for home page
└── tests/
    ├── domain/
    │   ├── test_user_entity.py
    │   └── test_get_users.py
    ├── data/
    │   ├── test_user_model.py
    │   └── test_user_repository_impl.py
    └── presentation/
        └── test_home_viewmodel.py
```

---

## Getting started

### Prerequisites

- Python 3.11+
- [Flet](https://flet.dev) (`pip install flet`)

### Run locally (desktop/browser)

```bash
pip install -r requirements.txt
python main.py
```

### Run tests

```bash
pip install pytest
pytest
```

### Package for mobile

Follow the official [Flet publish guide](https://flet.dev/docs/publish) to
build Android/iOS packages:

```bash
# Android
flet build apk

# iOS (macOS only)
flet build ipa
```

---

## Adding a new feature

1. **Entity** – add a new dataclass in `src/domain/entities/`.
2. **Repository contract** – define an abstract class in `src/domain/repositories/`.
3. **Use case(s)** – implement business logic in `src/domain/usecases/`.
4. **Model** – add a DTO in `src/data/models/` with `from_dict`/`to_dict`/`to_entity`.
5. **Data source** – implement the storage backend in `src/data/datasources/`.
6. **Repository impl** – implement the contract in `src/data/repositories/`.
7. **View model** – manage page state in `src/presentation/viewmodels/`.
8. **Page** – build the Flet UI in `src/presentation/pages/`.
9. **Wire up** – inject all dependencies in `main.py`.