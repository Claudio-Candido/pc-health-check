# Screenshots — PC Health Check

Capturas reais da interface do MVP (desktop 1440×900 e mobile 390×844).

## Landing page

![Landing](screenshots/01-landing.png)

Versão mobile:

![Landing mobile](screenshots/15-landing-mobile.png)

## Autenticação

| Registo | Login |
|---------|-------|
| ![Registo](screenshots/02-register.png) | ![Login](screenshots/14-login.png) |

## Dashboard

Com dados de exemplo (computadores, score médio, utilização do plano):

![Dashboard](screenshots/09-dashboard.png)

Estado inicial (sem diagnósticos):

![Dashboard vazio](screenshots/03-dashboard-empty.png)

## Novo diagnóstico

Formulário completo: equipamento, avaliações, serviços e recomendações.

![Novo diagnóstico](screenshots/04-new-diagnosis.png)

## Detalhe do computador + PC Health Score

![Detalhe](screenshots/05-computer-detail.png)

## Lista de computadores

![Lista](screenshots/06-computers-list.png)

## Pré-visualização do relatório

![Preview](screenshots/07-report-preview.png)

## Relatórios gerados

![Relatórios](screenshots/08-reports-list.png)

## PDF gerado (1.ª página)

![PDF](screenshots/16-pdf-report.png)

Ficheiro de exemplo: [`sample-report.pdf`](screenshots/sample-report.pdf)

## Definições e planos

| Perfil | Plano FREE | Plano PRO |
|--------|------------|-----------|
| ![Settings](screenshots/10-settings.png) | ![Billing](screenshots/11-billing.png) | ![Billing PRO](screenshots/12-billing-pro.png) |

Definições com personalização PRO (cor / logo):

![Settings PRO](screenshots/13-settings-pro.png)

---

Para regenerar as capturas (requer servidor em `http://127.0.0.1:5000` e Playwright):

```bash
python scripts/capture_screenshots.py
```
