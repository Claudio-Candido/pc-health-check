# Guia do utilizador — PC Health Check

Guia prático para técnicos que usam a plataforma no dia a dia.

## 1. Criar conta

1. Abra a landing page e clique em **Criar conta**.  
2. Preencha nome do técnico, empresa, email e palavra-passe (≥ 6 caracteres).  
3. A conta nasce no plano **FREE** (5 relatórios PDF por mês).  

## 2. Entrar e navegar

Após login vê o **Dashboard** com:

- Número de computadores  
- Relatórios gerados  
- Score médio  
- Uso do plano no mês  

Menu lateral:

| Item | Função |
|------|--------|
| Dashboard | Resumo |
| Computadores | Lista de equipamentos |
| Novo diagnóstico | Formulário completo |
| Relatórios | Histórico de PDFs |
| Definições | Perfil e logo |
| Plano | FREE / PRO |

Em ecrãs pequenos use o botão **☰** para abrir o menu.

## 3. Registar um diagnóstico

1. Clique em **Novo diagnóstico**.  
2. Preencha os dados do **cliente** e do **equipamento**.  
3. Na secção **Diagnóstico**, escolha o nível de cada item (Excelente → Necessita atenção).  
4. Em **Serviços realizados**, marque o que foi feito e, se quiser, adicione uma descrição.  
5. Escreva **recomendações** para o cliente (aparecem no PDF).  
6. Use **notas técnicas** só para informação interna.  
7. Clique em **Registar diagnóstico**.  

O sistema calcula automaticamente o **PC Health Score**.

## 4. Interpretar o score

| Score | Significado típico |
|-------|--------------------|
| 90–100 | Equipamento em excelente estado |
| 75–89 | Bom estado geral |
| 55–74 | Atenção a alguns pontos |
| 0–54 | Intervenção prioritária |

As quatro barras (Performance, Sistema, Armazenamento, Segurança) ajudam a explicar ao cliente **onde** está o problema.

## 5. Gerar o PDF

Na página do computador:

1. **Pré-visualizar** — vê o conteúdo em HTML (não gasta o limite mensal).  
2. **Gerar PDF** — cria um registo de relatório e descarrega o ficheiro.  

No plano FREE, ao atingir 5 PDFs no mês corrente, o sistema pede upgrade para PRO.

Pode voltar a descarregar PDFs antigos em **Relatórios** → botão **PDF** (o download de um relatório já gerado **não** cria um novo registo; só `Gerar PDF` consome o limite).

> Nota técnica: cada clique em **Gerar PDF** cria um novo `Report` e conta para o limite, mesmo que seja o mesmo computador.

## 6. Editar ou eliminar

- **Editar** — altere specs, ratings ou serviços; o score é recalculado.  
- **Eliminar** — remove o computador e dados associados (diagnóstico, serviços, relatórios desse PC). Confirme o diálogo.

## 7. Pesquisar equipamentos

Em **Computadores**, use a caixa de pesquisa por nome do cliente, marca ou modelo.

## 8. Personalizar a marca (PRO)

1. Em **Plano**, clique em **Ativar PRO (MVP)**.  
2. Em **Definições**:  
   - escolha a **cor de marca** (aparece no PDF);  
   - carregue o **logotipo** (PNG/JPG/etc.).  
3. Gere um novo PDF para ver a marca aplicada.

## 9. Boas práticas

- Seja consistente nos critérios de avaliação entre técnicos.  
- Escreva recomendações em linguagem clara para o cliente final.  
- Inclua sempre a data real da análise.  
- No plano FREE, planeie os 5 PDFs do mês (ex.: só gerar quando for entregar ao cliente).  
- Guarde cópia local dos PDFs importantes.

## 10. Problemas comuns

| Sintoma | Solução |
|---------|---------|
| “Limite do plano FREE atingido” | Aguarde o próximo mês ou ative PRO |
| PDF sem logo | Conta PRO + upload em Definições |
| Não vejo um computador | Confirme que está na conta correta; use a pesquisa |
| Formulário rejeitado | Preencha todos os campos com `*` |
| Sessão expirada | Volte a entrar em `/auth/login` |

## 11. Atalhos úteis (URLs)

| URL | Página |
|-----|--------|
| `/landing` | Marketing |
| `/computers/new` | Novo diagnóstico |
| `/reports/` | Histórico |
| `/settings/billing` | Planos |
