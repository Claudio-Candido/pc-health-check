# Catálogo de rotas — PC Health Check

Aplicação **server-rendered** (não é API REST JSON). Todas as rotas abaixo devolvem HTML, redirects ou PDF, salvo indicação em contrário.

CSRF: formulários POST incluem `csrf_token`. Pedidos sem token válido são rejeitados (400).

---

## Públicas

### `GET /landing`

Landing page de marketing (features + planos).  
Se o utilizador já estiver autenticado → redirect para `/`.

### `GET /auth/register` · `POST /auth/register`

Cria conta FREE.

**POST fields:** `email`, `password` (≥6), `technician_name`, `company_name` (opcional).

Sucesso → login automático + redirect dashboard.

### `GET /auth/login` · `POST /auth/login`

**POST fields:** `email`, `password`, `remember` (opcional).

Query `?next=` suportada após login.

### `GET /auth/logout`

Termina sessão → `/auth/login`.

---

## Dashboard

### `GET /`

Requer login. Mostra estatísticas, computadores e relatórios recentes, utilização do plano.

Convidados são redirecionados para `/landing` (hook `before_request`).

---

## Computadores

### `GET /computers/`

Lista equipamentos do utilizador.  
Query: `?q=` pesquisa em cliente / marca / modelo (`ilike`).

### `GET /computers/new` · `POST /computers/new`

Formulário completo: equipamento + diagnóstico + serviços + notas.

**POST fields principais:**

- Equipamento: `client_name`, `brand`, `model`, `processor`, `ram`, `storage`, `operating_system`, `analysis_date`
- Diagnóstico: `diag_performance`, `diag_storage`, `diag_operating_system`, `diag_security`, `diag_updates`, `diag_overall`
- Serviços: `services` (lista), `svc_desc_<tipo>`
- Texto: `recommendations`, `notes`

Sucesso → `/computers/<id>`.

### `GET /computers/<id>`

Detalhe com score, diagnóstico, serviços.  
403 se não pertencer ao utilizador.

### `GET /computers/<id>/edit` · `POST /computers/<id>/edit`

Atualiza dados, recalcula score, substitui lista de serviços.

### `POST /computers/<id>/delete`

Elimina computer (cascade diagnosis/services/reports).

---

## Relatórios

### `GET /reports/`

Histórico de PDFs gerados + resumo de utilização.

### `GET /reports/preview/<computer_id>`

Pré-visualização HTML do conteúdo do relatório (sem consumir limite).

### `POST /reports/generate/<computer_id>`

1. Valida ownership e existência de diagnosis  
2. Verifica limite do plano  
3. Cria registo `Report`  
4. Redirect para download  

Se limite FREE atingido → flash + redirect `/settings/billing`.

### `GET /reports/<id>/download`

Gera PDF on-the-fly e devolve `application/pdf` (attachment).  
Nome sugerido: `pc-health-<cliente>-<id>.pdf`.

---

## Definições

### `GET /settings/` · `POST /settings/`

Perfil da empresa.

**POST fields:** `technician_name`, `company_name`, `phone`, `brand_color` (PRO), `logo` (ficheiro, PRO).

### `GET /settings/billing` · `POST /settings/billing`

**POST `action`:**

- `upgrade` → `plan = pro`  
- `downgrade` → `plan = free`  

Simulação MVP — sem pagamento.

---

## Estáticos

| Rota | Conteúdo |
|------|----------|
| `/static/css/app.css` | Estilos |
| `/static/js/app.js` | Comportamento UI |
| `/static/uploads/logos/<file>` | Logotipos PRO |

---

## Códigos de resposta comuns

| Código | Situação |
|--------|----------|
| 200 | Página / PDF OK |
| 302/303 | Redirect pós-ação |
| 400 | CSRF inválido |
| 401/302 | Não autenticado → login |
| 403 | Recurso de outro utilizador |
| 404 | ID inexistente |
