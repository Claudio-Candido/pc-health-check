# PC Health Score — Algoritmo

Ficheiro de implementação: `app/services/health_score.py`.

## Objetivo

Converter avaliações qualitativas do técnico numa pontuação **objetiva e reproduzível** de 0 a 100, com breakdown por categoria.

## Mapeamento rating → pontos

```python
RATING_POINTS = {
    "excelente": 100,
    "bom": 80,
    "regular": 55,
    "necessita_atencao": 25,
}
```

Qualquer valor desconhecido cai em **55** (Regular) como fallback seguro.

## Categorias

| Categoria | Campo(s) do Diagnosis | Cálculo |
|-----------|----------------------|---------|
| Performance | `performance` | pontos diretos |
| Sistema | `operating_system`, `updates` | média arredondada |
| Armazenamento | `storage` | pontos diretos |
| Segurança | `security`, `overall` | média arredondada |

## Score final

```
health_score = round( (performance + system + storage + security) / 4 )
```

O resultado é limitado a `[0, 100]`.

## Exemplo

Diagnóstico:

| Item | Rating | Pontos |
|------|--------|--------|
| Desempenho | Bom | 80 |
| Armazenamento | Excelente | 100 |
| SO | Bom | 80 |
| Segurança | Regular | 55 |
| Atualizações | Necessita atenção | 25 |
| Estado geral | Bom | 80 |

Categorias:

- Performance = **80**  
- Sistema = round((80 + 25) / 2) = **52**  
- Armazenamento = **100**  
- Segurança = round((55 + 80) / 2) = **68**  

Final = round((80 + 52 + 100 + 68) / 4) = round(75) = **75** → etiqueta **Bom**.

## Etiquetas e cores (UI / PDF)

| Score | Etiqueta | Cor |
|-------|----------|-----|
| ≥ 90 | Excelente | `#16a34a` (verde) |
| ≥ 75 | Bom | `#2563eb` (azul) |
| ≥ 55 | Regular | `#d97706` (âmbar) |
| < 55 | Necessita atenção | `#dc2626` (vermelho) |

Funções: `score_label(score)`, `score_color(score)`.

## Quando é calculado

- Ao **criar** um computador (`computers.create`)  
- Ao **editar** um computador (`computers.edit`)  

Os valores ficam persistidos nas colunas `score_*` e `health_score` da tabela `computers`.

Ao gerar um relatório, o `health_score` atual é **copiado** para `reports.health_score` (snapshot histórico).

## Extensões possíveis

- Pesos diferentes por categoria (ex.: Segurança 30%)  
- Penalizações automáticas (SO sem updates críticas)  
- Benchmarks por tipo de equipamento (portátil vs desktop)  
- Histórico de scores ao longo do tempo para o mesmo cliente  
