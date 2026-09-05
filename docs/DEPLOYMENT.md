# Deploy e produção — PC Health Check

Este documento descreve boas práticas para colocar o MVP em produção. O arranque local (`python run.py`) **não** deve ser usado em produção.

## Checklist mínimo

- [ ] Definir `SECRET_KEY` forte e única  
- [ ] Usar base de dados persistente (PostgreSQL recomendado)  
- [ ] Servir com WSGI (Gunicorn / Waitress) atrás de reverse proxy  
- [ ] HTTPS (Let's Encrypt / Cloudflare)  
- [ ] Desativar debug (`debug=False`)  
- [ ] Backups regulares da BD e da pasta de logos  
- [ ] Limitar tamanho de uploads (já há `MAX_CONTENT_LENGTH = 2MB`)  

## Variáveis de ambiente

Ver [`.env.example`](../.env.example).

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export DATABASE_URL="postgresql+psycopg2://pcuser:senha@localhost:5432/pc_health"
```

Para carregar `.env` automaticamente, pode adicionar `python-dotenv` no `run.py` / factory (já está em `requirements.txt`):

```python
from dotenv import load_dotenv
load_dotenv()
```

## Gunicorn (Linux)

```bash
pip install gunicorn psycopg2-binary
gunicorn -w 2 -b 0.0.0.0:8000 "app:create_app()"
```

Nota: o factory atual chama `db.create_all()` dentro de `create_app()`. Em produção com vários workers isso é aceitável para o MVP; a médio prazo prefira migrações Alembic num job único de deploy.

## Nginx (exemplo)

```nginx
server {
    listen 443 ssl;
    server_name health.exemplo.com;

    location /static/ {
        alias /var/www/pc-health-check/app/static/;
        expires 7d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Docker (esqueleto sugerido)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
ENV FLASK_APP=run.py
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:create_app()"]
```

Monte um volume para `uploads/logos` e para a BD (ou use Postgres externo).

## SQLite vs PostgreSQL

| | SQLite | PostgreSQL |
|---|--------|------------|
| Dev / demo | ✅ Ideal | Opcional |
| Multi-worker / produção | ⚠️ Limitado | ✅ Recomendado |
| Backups | Copiar ficheiro `.db` | `pg_dump` |

## Uploads

Pasta: `app/static/uploads/logos/`

Em contentores/ephemeral storage, monte volume persistente. Sem volume, logos PRO perdem-se no redeploy.

## Observabilidade

Sugestões pós-MVP:

- Logging estruturado (pedido, user_id, report_id)  
- Healthcheck `GET /landing` ou rota `/healthz` dedicada  
- Alertas de erro 5xx no reverse proxy  

## Segurança em produção

1. Nunca commitar `.env` nem `pc_health.db` com dados reais  
2. Rodar atrás de HTTPS  
3. Considerar rate-limit em `/auth/login` e `/auth/register`  
4. Substituir upgrade PRO simulado por Stripe/Paddle + webhooks  
5. Revisar `ALLOWED_EXTENSIONS` e validação MIME dos uploads  

## Migração de dados

Exportar SQLite → Postgres (exemplo com `pgloader` ou script SQLAlchemy). Manter paths de `logo_filename` consistentes com o volume de uploads.
