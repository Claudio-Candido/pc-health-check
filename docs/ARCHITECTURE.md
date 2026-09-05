# Arquitetura — PC Health Check

## Visão geral

O PC Health Check segue o padrão **Application Factory** do Flask, com domínio separado em **Blueprints** e lógica de negócio em **Services**.

```
Pedido HTTP
    │
    ▼
create_app()  →  extensões (db, login, csrf)
    │
    ▼
Blueprint correspondente
    │
    ├── valida auth / ownership
    ├── lê/escreve Models (SQLAlchemy)
    └── chama Services (score, PDF, limites)
    │
    ▼
Template Jinja2  ou  ficheiro PDF (BytesIO)
```

## Application Factory

Ficheiro: `app/__init__.py`

Responsabilidades:

1. Carregar `Config`
2. Inicializar extensões (`db`, `login_manager`, `csrf`)
3. Registar blueprints
4. Definir `user_loader`
5. Redirecionar convidados de `/` para `/landing`
6. Criar tabelas (`db.create_all()`) no arranque

Entry point: `run.py` → `create_app()` → `app.run(host="0.0.0.0", port=5000)`.

## Extensões

| Extensão | Módulo | Função |
|----------|--------|--------|
| `SQLAlchemy` | `app.extensions.db` | ORM / sessão |
| `LoginManager` | `app.extensions.login_manager` | Sessões de utilizador |
| `CSRFProtect` | `app.extensions.csrf` | Tokens CSRF |

## Blueprints

| Blueprint | Prefixo | Responsabilidade |
|-----------|---------|------------------|
| `auth_bp` | `/auth` | Registo, login, logout |
| `dashboard_bp` | `/` | Métricas e resumos |
| `computers_bp` | `/computers` | CRUD equipamento + diagnóstico + serviços |
| `reports_bp` | `/reports` | Histórico, preview, gerar/descarregar PDF |
| `settings_bp` | `/settings` | Perfil, logo, billing |

Cada blueprint tem:

```
blueprints/<nome>/
  __init__.py   # Blueprint(...) + import routes
  routes.py     # views
```

## Camada de serviços

| Serviço | Função |
|---------|--------|
| `health_score.calculate_scores` | Converte ratings → scores por categoria + final |
| `health_score.score_label` / `score_color` | UI / PDF |
| `plan_limits.can_generate_report` | Enforce FREE vs PRO |
| `plan_limits.usage_summary` | Dashboard / billing |
| `pdf_generator.generate_report_pdf` | Bytes do PDF |

Os serviços **não** conhecem Flask request/response (exceto `plan_limits`, que lê `current_app.config` para o limite FREE).

## Fluxo: gerar relatório

```
POST /reports/generate/<computer_id>
        │
        ├─ ownership check
        ├─ diagnosis obrigatório
        ├─ can_generate_report(user)?
        │     ├─ NÃO → flash + redirect billing
        │     └─ SIM → cria Report + commit
        └─ redirect /reports/<id>/download
                │
                └─ generate_report_pdf(computer, user, logo_path)
                   → send_file(BytesIO, application/pdf)
```

## Frontend

- CSS único: `static/css/app.css` (design system: sidebar, cards, badges, formulários, landing)
- JS mínimo: `static/js/app.js` (menu mobile, data default, enable/disable descrições de serviços)
- Sem frameworks SPA — server-rendered Jinja2
- Layout autenticado vs páginas públicas (`layouts/base.html`)

## Persistência

- Dev: SQLite (`pc_health.db` na raiz)
- Produção recomendada: PostgreSQL via `DATABASE_URL`
- Sem migrações Alembic no MVP (`create_all` apenas)

## Decisões de desenho

1. **Score persistido no Computer** — evita recalcular em listagens; recalcula no create/edit.  
2. **Report como entidade separada** — permite histórico e contagem mensal do plano.  
3. **Upgrade PRO simulado** — foca o MVP no produto, não no billing.  
4. **Um Diagnosis por Computer** — modelo 1:1 simples para o fluxo atual.  
5. **Português (pt)** na UI — público-alvo de técnicos lusófonos.
