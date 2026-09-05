# Modelo de dados — PC Health Check

Base de dados relacional gerida por SQLAlchemy. Em desenvolvimento usa-se **SQLite**.

## Diagrama ER (textual)

```
┌──────────────────┐
│      users       │
├──────────────────┤
│ id PK            │
│ email UNIQUE     │
│ password_hash    │
│ company_name     │
│ technician_name  │
│ phone            │
│ plan             │  free | pro
│ logo_filename    │
│ brand_color      │
│ created_at       │
└────────┬─────────┘
         │ 1
         │
         │ *
┌────────▼─────────┐         ┌──────────────────┐
│    computers     │ 1────1  │    diagnoses     │
├──────────────────┤         ├──────────────────┤
│ id PK            │         │ id PK            │
│ user_id FK       │         │ computer_id FK U │
│ client_name      │         │ performance      │
│ brand            │         │ storage          │
│ model            │         │ operating_system │
│ processor        │         │ security         │
│ ram              │         │ updates          │
│ storage          │         │ overall          │
│ operating_system │         └──────────────────┘
│ analysis_date    │
│ notes            │         ┌──────────────────────┐
│ recommendations  │ 1────*  │ services_performed   │
│ score_performance│         ├──────────────────────┤
│ score_system     │         │ id PK                │
│ score_storage    │         │ computer_id FK       │
│ score_security   │         │ service_type         │
│ health_score     │         │ description          │
│ created_at       │         │ created_at           │
│ updated_at       │         └──────────────────────┘
└────────┬─────────┘
         │ 1
         │
         │ *
┌────────▼─────────┐
│     reports      │
├──────────────────┤
│ id PK            │
│ user_id FK       │
│ computer_id FK   │
│ health_score     │
│ created_at       │
└──────────────────┘
```

## Tabelas

### `users`

| Coluna | Tipo | Notas |
|--------|------|-------|
| `id` | Integer PK | |
| `email` | String(120) | único, indexado, lowercase no registo |
| `password_hash` | String(256) | `generate_password_hash` |
| `company_name` | String(150) | default `"Minha Empresa"` |
| `technician_name` | String(120) | obrigatório |
| `phone` | String(40) | opcional |
| `plan` | String(20) | `free` (default) ou `pro` |
| `logo_filename` | String(255) | ficheiro em `static/uploads/logos/` |
| `brand_color` | String(7) | hex, default `#2563eb` |
| `created_at` | DateTime | UTC |

Métodos úteis: `set_password`, `check_password`, `is_pro`, `logo_url()`.

### `computers`

| Coluna | Tipo | Notas |
|--------|------|-------|
| `id` | Integer PK | |
| `user_id` | Integer FK → users | indexado |
| `client_name` | String(150) | |
| `brand` | String(80) | |
| `model` | String(120) | |
| `processor` | String(150) | |
| `ram` | String(80) | texto livre (ex.: `16 GB DDR4`) |
| `storage` | String(120) | texto livre |
| `operating_system` | String(120) | |
| `analysis_date` | Date | |
| `notes` | Text | interno |
| `recommendations` | Text | no PDF |
| `score_performance` | Integer | 0–100 |
| `score_system` | Integer | 0–100 |
| `score_storage` | Integer | 0–100 |
| `score_security` | Integer | 0–100 |
| `health_score` | Integer | 0–100 |
| `created_at` / `updated_at` | DateTime | |

Cascade: eliminar computer elimina diagnosis, services e reports associados.

### `diagnoses`

Relação **1:1** com `computers` (`computer_id` unique).

Campos de rating (`String(30)`):

- `performance`, `storage`, `operating_system`, `security`, `updates`, `overall`

Valores permitidos: `excelente` | `bom` | `regular` | `necessita_atencao`.

### `services_performed`

| Coluna | Tipo | Notas |
|--------|------|-------|
| `id` | Integer PK | |
| `computer_id` | Integer FK | |
| `service_type` | String(40) | ver lista abaixo |
| `description` | String(255) | opcional |
| `created_at` | DateTime | |

Tipos: `diagnostico`, `atualizacao`, `configuracao`, `backup`, `instalacao_software`, `limpeza`, `outros`.

### `reports`

| Coluna | Tipo | Notas |
|--------|------|-------|
| `id` | Integer PK | |
| `user_id` | Integer FK | indexado |
| `computer_id` | Integer FK | |
| `health_score` | Integer | snapshot no momento da geração |
| `created_at` | DateTime | indexado; base do limite mensal |

## Constantes de domínio

Definidas em `app/models/computer.py`:

- `RATING_CHOICES` / `RATING_LABELS`
- `SERVICE_CHOICES` / `SERVICE_LABELS`

## Índices e constraints relevantes

- `users.email` UNIQUE  
- `diagnoses.computer_id` UNIQUE  
- Índices em `computers.user_id`, `reports.user_id`, `reports.created_at`  

## Evolução futura

Para produção recomenda-se:

1. Introduzir **Alembic** para migrações  
2. Migrar para **PostgreSQL**  
3. Tabela `subscriptions` / `payments` se houver billing real  
4. Soft-delete em computers/reports se necessário para auditoria  
