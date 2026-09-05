# Contribuir para o PC Health Check

Obrigado pelo interesse em contribuir.

## Ambiente de desenvolvimento

```bash
git clone https://github.com/Claudio-Candido/pc-health-check.git
cd pc-health-check
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Antes de abrir um PR, execute:

```bash
python smoke_test.py
```

## Convenções

- Python: código claro, type hints onde fizer sentido, sem dependências desnecessárias.  
- UI: manter o design system em `app/static/css/app.css` e textos em português.  
- Novas funcionalidades de domínio → preferir **services** + **blueprints**, não lógica pesada nos templates.  
- Não commitar `.env`, bases SQLite, logos de clientes nem `__pycache__`.  

## Pull requests

1. Descreva o problema e a solução.  
2. Inclua screenshots se alterar UI.  
3. Atualize a documentação em `docs/` quando mudar comportamento ou rotas.  
4. Mantenha o PR focado (um tema por PR).  

## Reportar bugs

Abra uma issue com:

- Passos para reproduzir  
- Comportamento esperado vs obtido  
- Versão do Python / SO  
- Logs relevantes (sem dados sensíveis de clientes)
