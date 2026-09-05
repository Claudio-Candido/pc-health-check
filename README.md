# PC Health Check

**Plataforma SaaS para técnicos de informática gerarem relatórios profissionais de diagnóstico de computadores.**

Registe equipamentos, avalie desempenho / segurança / armazenamento, calcule o **PC Health Score (0–100)** e entregue PDFs com a marca da sua empresa.

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Índice

1. [Visão geral](#visão-geral)
2. [Funcionalidades](#funcionalidades)
3. [Planos SaaS](#planos-saas)
4. [Stack tecnológica](#stack-tecnológica)
5. [Arquitetura](#arquitetura)
6. [Modelo de dados](#modelo-de-dados)
7. [PC Health Score](#pc-health-score)
8. [Geração de PDF](#geração-de-pdf)
9. [Rotas da aplicação](#rotas-da-aplicação)
10. [Instalação e arranque](#instalação-e-arranque)
11. [Configuração](#configuração)
12. [Utilização (fluxo típico)](#utilização-fluxo-típico)
13. [Testes](#testes)
14. [Estrutura de pastas](#estrutura-de-pastas)
15. [Segurança](#segurança)
16. [Roadmap](#roadmap)
17. [Documentação adicional](#documentação-adicional)
18. [Licença](#licença)

---

## Visão geral

O **PC Health Check** é um MVP SaaS pensado para:

- Oficinas de informática
- Técnicos freelancers
- Empresas de suporte IT

O objetivo é transformar uma análise técnica num **relatório PDF profissional** em minutos, com pontuação objetiva e recomendações claras para o cliente final.

### Problema que resolve

| Antes | Com PC Health Check |
|-------|---------------------|
| Relatórios em Word/Excel inconsistentes | PDF padronizado e profissional |
| Avaliação subjetiva sem score | Score 0–100 com 4 categorias |
| Sem controlo de volume | Planos FREE / PRO com limites |
| Sem marca da empresa | Logo + cor (plano PRO) |

---

## Funcionalidades

### Cadastro de computador

Campos obrigatórios:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| Cliente | Nome do cliente final | Maria Silva |
| Marca | Fabricante | Dell |
| Modelo | Modelo do equipamento | Latitude 5520 |
| Processador | CPU | Intel i7-1185G7 |
| Memória RAM | Quantidade / tipo | 16 GB DDR4 |
| Armazenamento | Disco | 512 GB SSD NVMe |
| Sistema operativo | SO instalado | Windows 11 Pro |
| Data da análise | Data do diagnóstico | 2026-03-20 |

Campos opcionais: **notas técnicas** (internas) e **recomendações** (visíveis no PDF).

### Diagnóstico

Seis dimensões avaliadas:

1. Desempenho  
2. Armazenamento  
3. Sistema operativo  
4. Segurança  
5. Atualizações  
6. Estado geral  

Cada dimensão aceita um de quatro níveis:

| Código interno | Etiqueta |
|----------------|----------|
| `excelente` | Excelente |
| `bom` | Bom |
| `regular` | Regular |
| `necessita_atencao` | Necessita atenção |

### Serviços realizados

É possível marcar um ou mais serviços, com descrição opcional:

- Diagnóstico  
- Atualização  
- Configuração  
- Backup  
- Instalação de software legítimo  
- Limpeza  
- Outros  

### Dashboard

- Total de computadores  
- Total de relatórios  
- Score médio  
- Utilização do plano no mês corrente  
- Listas de computadores e relatórios recentes  

### Relatórios PDF

Incluem:

- Logotipo da empresa (PRO) ou nome da empresa  
- Dados do cliente e do equipamento  
- Tabela de diagnóstico  
- Pontuação por categoria + score final  
- Serviços realizados  
- Recomendações e notas  
- Rodapé com identificação da empresa  

### Conta e personalização

- Perfil: técnico, empresa, telefone  
- **PRO:** upload de logotipo + cor de marca (usada no PDF)  
- Gestão de plano FREE ↔ PRO (upgrade simulado no MVP)

---

## Planos SaaS

| Recurso | FREE | PRO |
|---------|------|-----|
| Relatórios PDF / mês | **5** | **Ilimitados** |
| Dashboard e CRUD | ✅ | ✅ |
| Diagnóstico + Score | ✅ | ✅ |
| PDF padrão | ✅ | ✅ |
| Logotipo próprio no PDF | ❌ | ✅ |
| Cor de marca personalizada | ❌ | ✅ |

> **Nota MVP:** o upgrade para PRO é simulado (botão em Definições → Plano), sem gateway de pagamento. Ideal para demonstração e desenvolvimento.

O limite FREE é contado pelo número de registos em `reports` no mês civil atual (`datetime.utcnow()`).

---

## Stack tecnológica

| Camada | Tecnologia | Versão |
|--------|------------|--------|
| Linguagem | Python | 3.12+ |
| Framework web | Flask | 3.0.3 |
| ORM | Flask-SQLAlchemy | 3.1.1 |
| Autenticação | Flask-Login | 0.6.3 |
| Formulários / CSRF | Flask-WTF | 1.2.1 |
| Base de dados | SQLite (dev) | via SQLAlchemy |
| PDF | ReportLab | 4.2.0 |
| Imagens | Pillow | 10.4.0 |
| Frontend | HTML5 + CSS3 + JavaScript vanilla | — |

Dependências completas: [`requirements.txt`](requirements.txt).

---

## Arquitetura

Aplicação Flask modular com **Application Factory** e **Blueprints**:

```
┌─────────────────────────────────────────────────────────┐
│                      Browser (UI)                       │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼─────────────────────────────┐
│  Flask App (create_app)                                 │
│  ├── auth          /auth/*                              │
│  ├── dashboard     /                                    │
│  ├── computers     /computers/*                         │
│  ├── reports       /reports/*                           │
│  └── settings      /settings/*                          │
└───────┬─────────────────────┬───────────────────────────┘
        │                     │
        ▼                     ▼
┌───────────────┐   ┌─────────────────────┐
│  SQLAlchemy   │   │  Services           │
│  Models       │   │  · health_score     │
│  SQLite       │   │  · pdf_generator    │
└───────────────┘   │  · plan_limits      │
                    └─────────────────────┘
```

### Princípios

- **Blueprints** isolados por domínio  
- **Services** para lógica de negócio (score, PDF, limites)  
- **Models** sem lógica de apresentação  
- Templates Jinja2 com layout partilhado (`layouts/base.html`)  
- CSRF em todos os POST  
- Ownership checks (`user_id`) em recursos privados  

Documentação detalhada: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Modelo de dados

```
User 1──* Computer 1──1 Diagnosis
              │
              ├──* ServicePerformed
              └──* Report
User 1──* Report
```

| Tabela | Descrição |
|--------|-----------|
| `users` | Conta do técnico / empresa, plano, logo, cor |
| `computers` | Equipamento + scores calculados |
| `diagnoses` | Avaliações (1:1 com computer) |
| `services_performed` | Serviços feitos no PC |
| `reports` | Histórico de PDFs gerados (conta para o limite mensal) |

Detalhes de campos: [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md).

---

## PC Health Score

Pontuação de **0 a 100**, derivada das avaliações do diagnóstico.

### Pontos por nível

| Nível | Pontos |
|-------|--------|
| Excelente | 100 |
| Bom | 80 |
| Regular | 55 |
| Necessita atenção | 25 |

### Categorias

| Categoria | Fonte |
|-----------|--------|
| **Performance** | `performance` |
| **Sistema** | média de `operating_system` + `updates` |
| **Armazenamento** | `storage` |
| **Segurança** | média de `security` + `overall` |

**Score final** = média aritmética das 4 categorias (arredondada).

### Etiquetas do score

| Intervalo | Etiqueta |
|-----------|----------|
| ≥ 90 | Excelente |
| ≥ 75 | Bom |
| ≥ 55 | Regular |
| < 55 | Necessita atenção |

Implementação: [`app/services/health_score.py`](app/services/health_score.py).

---

## Geração de PDF

Biblioteca: **ReportLab** (Platypus), página A4.

Conteúdo do PDF:

1. Cabeçalho (logo PRO ou nome da empresa + título)  
2. Banner com Health Score e breakdown por categoria  
3. Dados do cliente  
4. Dados do equipamento  
5. Tabela de diagnóstico  
6. Tabela de pontuação por categoria  
7. Serviços realizados  
8. Recomendações / notas  
9. Rodapé  

Implementação: [`app/services/pdf_generator.py`](app/services/pdf_generator.py).

---

## Rotas da aplicação

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/` | Sim* | Dashboard (*convidados → `/landing`) |
| GET | `/landing` | Não | Landing page pública |
| GET/POST | `/auth/register` | Não | Criar conta |
| GET/POST | `/auth/login` | Não | Entrar |
| GET | `/auth/logout` | Sim | Sair |
| GET | `/computers/` | Sim | Listar / pesquisar |
| GET/POST | `/computers/new` | Sim | Novo diagnóstico |
| GET | `/computers/<id>` | Sim | Detalhe + score |
| GET/POST | `/computers/<id>/edit` | Sim | Editar |
| POST | `/computers/<id>/delete` | Sim | Eliminar |
| GET | `/reports/` | Sim | Histórico de relatórios |
| GET | `/reports/preview/<computer_id>` | Sim | Pré-visualização HTML |
| POST | `/reports/generate/<computer_id>` | Sim | Gerar PDF (consome limite) |
| GET | `/reports/<id>/download` | Sim | Descarregar PDF |
| GET/POST | `/settings/` | Sim | Perfil / logo / cor |
| GET/POST | `/settings/billing` | Sim | Plano FREE/PRO |

---

## Instalação e arranque

### Pré-requisitos

- Python 3.12+ (testado em 3.12.3)  
- `pip` e `venv`  
- Sistema Linux / macOS / Windows  

### Passos

```bash
# 1. Clonar
git clone https://github.com/Claudio-Candido/pc-health-check.git
cd pc-health-check

# 2. Ambiente virtual
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Dependências
pip install -r requirements.txt

# 4. (Opcional) variáveis de ambiente
cp .env.example .env
# edite SECRET_KEY em produção

# 5. Arrancar
python run.py
```

Abrir no browser:

- Landing: http://127.0.0.1:5000/landing  
- App (após login): http://127.0.0.1:5000/  

A base SQLite `pc_health.db` é criada automaticamente na raiz do projeto.

---

## Configuração

Variáveis relevantes (`app/config.py` / ambiente):

| Variável | Default | Descrição |
|----------|---------|-----------|
| `SECRET_KEY` | valor de desenvolvimento | Chave Flask / sessões / CSRF |
| `DATABASE_URL` | `sqlite:///.../pc_health.db` | URI SQLAlchemy |
| `FREE_REPORTS_PER_MONTH` | `5` | Limite do plano FREE |

Uploads de logo: `app/static/uploads/logos/` (máx. 2 MB; png/jpg/jpeg/gif/webp/svg).

---

## Utilização (fluxo típico)

1. Criar conta em **Registar** (plano FREE).  
2. Ir a **Novo diagnóstico**.  
3. Preencher cliente + specs do PC.  
4. Avaliar as 6 dimensões do diagnóstico.  
5. Marcar serviços realizados.  
6. Escrever recomendações para o cliente.  
7. Guardar → ver **PC Health Score** no detalhe.  
8. **Pré-visualizar** ou **Gerar PDF**.  
9. (Opcional) Em **Plano**, ativar **PRO** e carregar logotipo em **Definições**.  

---

## Testes

Smoke test automatizado com o Flask test client:

```bash
source .venv/bin/activate
python smoke_test.py
```

O script valida:

- Landing e autenticação  
- Criação de computador + diagnóstico + serviços  
- Cálculo do Health Score  
- Geração e download de PDF (`%PDF`)  
- Bloqueio no 6.º relatório FREE  
- Upgrade PRO e relatório adicional  
- Páginas autenticadas (200)  

---

## Estrutura de pastas

```
pc-health-check/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuração
│   ├── extensions.py            # db, login, csrf
│   ├── blueprints/
│   │   ├── auth/                # Registo / login / logout
│   │   ├── dashboard/           # Home autenticada
│   │   ├── computers/           # CRUD + diagnóstico
│   │   ├── reports/             # PDF + histórico
│   │   └── settings/            # Perfil + billing
│   ├── models/
│   │   ├── user.py
│   │   ├── computer.py          # Computer, Diagnosis, ServicePerformed
│   │   └── report.py
│   ├── services/
│   │   ├── health_score.py
│   │   ├── pdf_generator.py
│   │   └── plan_limits.py
│   ├── templates/               # Jinja2
│   └── static/
│       ├── css/app.css
│       ├── js/app.js
│       └── uploads/logos/
├── docs/                        # Documentação detalhada
├── run.py                       # Entry point
├── smoke_test.py
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Segurança

- Palavras-passe com hash (`werkzeug.security`)  
- Sessões Flask-Login  
- Proteção **CSRF** em formulários POST  
- Verificação de ownership em computadores/relatórios (403)  
- Upload de logo com extensão allowlist + `secure_filename`  
- `SECRET_KEY` configurável por ambiente  

> Em produção: altere `SECRET_KEY`, use HTTPS, e prefira PostgreSQL em vez de SQLite.

---

## Roadmap

Ideias pós-MVP:

- [ ] Pagamentos reais (Stripe / Paddle)  
- [ ] Multi-técnico por empresa (roles)  
- [ ] Exportação Excel / envio por email  
- [ ] Templates de relatório customizáveis  
- [ ] API REST para integrações  
- [ ] Histórico de alterações do equipamento  
- [ ] Deploy Docker + PostgreSQL  

---

## Documentação adicional

| Documento | Conteúdo |
|-----------|----------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arquitetura, blueprints, fluxo de pedidos |
| [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) | Esquema de base de dados |
| [`docs/SCORING.md`](docs/SCORING.md) | Algoritmo do PC Health Score |
| [`docs/API_ROUTES.md`](docs/API_ROUTES.md) | Catálogo completo de rotas |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Deploy e boas práticas |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | Guia do utilizador |

---

## Licença

Distribuído sob a licença [MIT](LICENSE).

---

**PC Health Check** — diagnósticos técnicos claros, relatórios que o cliente entende.
