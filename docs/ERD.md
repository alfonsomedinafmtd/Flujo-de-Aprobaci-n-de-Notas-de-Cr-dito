# Modelo relacional propuesto

```mermaid
erDiagram
    DEPARTMENT ||--o{ POSITION : contains
    POSITION }o--o{ BUSINESS_FUNCTION : includes
    POSITION ||--o{ EMPLOYEE : assigned_to
    EMPLOYEE ||--o| USER_ACCOUNT : authenticates_as
    USER_ACCOUNT ||--o{ AUTH_SESSION : owns
    DEPARTMENT ||--o{ CREDIT_NOTE : requests
    USER_ACCOUNT ||--o{ CREDIT_NOTE : creates
    STORE ||--o{ CREDIT_NOTE : receives
    COMPANY ||--o{ CREDIT_NOTE : issues
    CREDIT_NOTE ||--o{ CREDIT_NOTE_EVENT : records
    USER_ACCOUNT ||--o{ CREDIT_NOTE_EVENT : performs

    DEPARTMENT {
        int id PK
        string code UK
        string name UK
        boolean active
    }
    POSITION {
        int id PK
        int department_id FK
        string title
        string seniority
        boolean active
    }
    BUSINESS_FUNCTION {
        int id PK
        string code UK
        string name
    }
    EMPLOYEE {
        int id PK
        int position_id FK
        string first_name
        string last_name
        string country
        date hire_date
        string internal_email UK
        string status
    }
    USER_ACCOUNT {
        int id PK
        int employee_id FK,UK
        string username UK
        string password_hash
        string role
        boolean active
    }
    AUTH_SESSION {
        int id PK
        int user_id FK
        string token_hash UK
        string csrf_hash
        datetime expires_at
        datetime revoked_at
    }
    CREDIT_NOTE {
        int id PK
        decimal amount
        string currency
        string reason
        int requesting_department_id FK
        int created_by_user_id FK
        string requester_position_title
        int store_id FK
        int company_id FK
        string status
        int version
        datetime created_at
        datetime updated_at
    }
    CREDIT_NOTE_EVENT {
        int id PK
        int credit_note_id FK
        int actor_user_id FK
        string action
        string previous_status
        string new_status
        string comment
        datetime occurred_at
    }
```

El departamento del colaborador se obtiene por `employee → position → department`, evitando duplicarlo en varias tablas. La nota conserva su departamento solicitante y el título del cargo como instantáneas históricas; así, un cambio organizacional posterior no modifica retrospectivamente la analítica de la solicitud.
