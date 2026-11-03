"""Gera notebook_guia_workshop.ipynb no formato Databricks."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "notebook_guia_workshop.ipynb"


def nuid() -> str:
    return str(uuid.uuid4())


def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {
            "application/vnd.databricks.v1+cell": {
                "cellMetadata": {},
                "inputWidgets": {},
                "nuid": nuid(),
                "showTitle": False,
                "tableResultSettingsMap": {},
                "title": "",
            }
        },
        "source": [line + "\n" for line in source.strip("\n").split("\n")],
    }


def sql(source: str) -> dict:
    text = source.strip("\n") + "\n"
    return {
        "cell_type": "code",
        "execution_count": 0,
        "metadata": {
            "application/vnd.databricks.v1+cell": {
                "cellMetadata": {
                    "byteLimit": 2048000,
                    "implicitDf": True,
                    "rowLimit": 10000,
                },
                "inputWidgets": {},
                "nuid": nuid(),
                "showTitle": False,
                "tableResultSettingsMap": {},
                "title": "",
            }
        },
        "outputs": [],
        "source": [text] if "\n" not in text[:-1] else [line + "\n" for line in text[:-1].split("\n")],
    }


def py(source: str) -> dict:
    text = source.strip("\n") + "\n"
    return {
        "cell_type": "code",
        "execution_count": 0,
        "metadata": {
            "application/vnd.databricks.v1+cell": {
                "cellMetadata": {
                    "byteLimit": 2048000,
                    "rowLimit": 10000,
                },
                "inputWidgets": {},
                "nuid": nuid(),
                "showTitle": False,
                "tableResultSettingsMap": {},
                "title": "",
            }
        },
        "outputs": [],
        "source": [line + "\n" for line in text[:-1].split("\n")],
    }


cells = [
    md(
        """# Workshop Databricks — Lakeflow Designer
### Guia passo a passo (PT-BR)

Bem-vindo(a)! Neste workshop você monta um **visual data prep** no Lakeflow Designer para a **Aurora Café**: qualidade de dados, união de canais, joins, IA em tickets de suporte, ranking de produtos e escrita no Unity Catalog.

**Não usamos o operador Python.** Toda a lógica extra entra no operador **SQL**.

**Agenda**

| # | Módulo | O que você vai fazer |
|---|---|---|
| 1 | Upload de CSVs | Subir 3 arquivos e criar tabelas |
| 2 | Canvas e fontes | Source, Enter Data, parâmetro |
| 3 | Qualidade | Unique, Prepare, Guardrails, Filter, Combine |
| 4 | Relacionar | Join, Select, SQL com parâmetro |
| 5 | IA e ouro | AI Function, Aggregate, Pivot, Sort, Limit |
| 6 | Publicar | Output, Visualization, Group, Note |
| 7 | Genie Code *(opcional)* | Recriar o fluxo em linguagem natural |

Documentação: [operadores nativos](https://docs.databricks.com/aws/en/designer/built-in-operators) · [o que é o Designer](https://docs.databricks.com/aws/en/designer/what-is-lakeflow-designer)
"""
    ),
    md(
        """## Descrição das tabelas

### `clientes` (82 linhas, 2 duplicatas de propósito)

| Coluna | Descrição |
|---|---|
| `cliente_id` | ID do cliente (duplicado em 2 linhas) |
| `nome` | Nome; alguns com espaços extras |
| `email` | Alguns vazios |
| `cidade` / `estado` | Grafia inconsistente em algumas cidades |
| `canal_aquisicao` | `APP`, `LOJA`, `PARCEIRO`, `SITE` |
| `segmento` | `Bronze`, `Prata`, `Ouro` |
| `data_cadastro` | Data de cadastro |
| `ativo` | `true` / `false` |

### `pedidos` (201 linhas)

| Coluna | Descrição |
|---|---|
| `pedido_id` | ID do pedido (há duplicata) |
| `cliente_id` | FK para clientes |
| `produto` / `categoria` | Item e categoria do cardápio |
| `quantidade` / `valor_unitario` / `valor_total` | Há um valor total negativo |
| `canal` | `ONLINE` ou `LOJA` (há variação de caixa/espaço) |
| `status` | `confirmado`, `pendente`, `cancelado` (há `PENDNETE`) |
| `data_pedido` / `loja` | Data e loja Aurora |

### `tickets_suporte` (60 linhas)

| Coluna | Descrição |
|---|---|
| `ticket_id` | ID do ticket |
| `cliente_id` / `pedido_id` | FKs |
| `comentario` | Texto em PT-BR para `ai_classify` |
| `sentimento_esperado` | Gabarito (`positivo`, `misto`, `negativo`) |
"""
    ),
    md(
        """---
## Configuração inicial — widgets

Preencha catálogo, schema e o seu prefixo único (ex.: `ana_`).
"""
    ),
    py(
        """dbutils.widgets.removeAll()

dbutils.widgets.text("nome_catalogo", "workspace_carolina_ferreira_catalog", "Catálogo")
dbutils.widgets.text("nome_schema", "workshop_lakeflow_designer", "Schema")
dbutils.widgets.text("seu_prefixo", "", "Seu Prefixo (ex: ana_)")
"""
    ),
    py(
        """nome_catalogo = dbutils.widgets.get("nome_catalogo")
nome_schema = dbutils.widgets.get("nome_schema")
seu_prefixo = dbutils.widgets.get("seu_prefixo")

print(f"Catálogo : {nome_catalogo}")
print(f"Schema   : {nome_schema}")
print(f"Prefixo  : {seu_prefixo}")
"""
    ),
    md(
        """---
## Módulo 1 — Subindo arquivos manualmente (CSV)

### O que é?
O Databricks converte CSV em tabelas Delta no Unity Catalog pela interface — sem código de ingestão.

### Passo a passo

1. No menu lateral, clique em **+ New** → **Add or upload data** (ou **Catalog** → **Create** → **Create table**).
2. Arraste o CSV da pasta `dados/` ou selecione do computador.
3. Revise o schema detectado (tipos das colunas).
4. Escolha **Catálogo**, **Schema** e o nome da tabela **com o seu prefixo**.
5. Clique em **Create table**.
6. Repita para os 3 arquivos.

### Arquivos obrigatórios

| Arquivo | Nome sugerido da tabela |
|---|---|
| `clientes.csv` | `{seu_prefixo}clientes` |
| `pedidos.csv` | `{seu_prefixo}pedidos` |
| `tickets_suporte.csv` | `{seu_prefixo}tickets_suporte` |

> Exemplo: prefixo `ana_` → tabela `ana_clientes`.

### Validação rápida

Depois do upload, confira no **Catalog** se as 3 tabelas aparecem e abra **Sample data**. Rode as células SQL abaixo.
"""
    ),
    sql(
        """%sql
SELECT COUNT(*) AS qtd_clientes
FROM `${nome_catalogo}`.`${nome_schema}`.`${seu_prefixo}clientes`;
"""
    ),
    sql(
        """%sql
SELECT cliente_id, COUNT(*) AS ocorrencias
FROM `${nome_catalogo}`.`${nome_schema}`.`${seu_prefixo}clientes`
GROUP BY cliente_id
HAVING COUNT(*) > 1
ORDER BY ocorrencias DESC;
"""
    ),
    sql(
        """%sql
SELECT canal, status, COUNT(*) AS qtd, ROUND(SUM(valor_total), 2) AS receita
FROM `${nome_catalogo}`.`${nome_schema}`.`${seu_prefixo}pedidos`
GROUP BY canal, status
ORDER BY canal, status;
"""
    ),
    sql(
        """%sql
SELECT sentimento_esperado, COUNT(*) AS qtd
FROM `${nome_catalogo}`.`${nome_schema}`.`${seu_prefixo}tickets_suporte`
GROUP BY sentimento_esperado
ORDER BY qtd DESC;
"""
    ),
    md(
        """**Checkpoint do Módulo 1**

- [ ] 3 tabelas no seu schema
- [ ] `clientes` tem mais de 80 linhas (duplicatas visíveis)
- [ ] `pedidos` tem canais ONLINE e LOJA
- [ ] `tickets_suporte` tem 60 comentários
"""
    ),
    md(
        """---
## Módulo 2 — Canvas, Source, Enter Data e parâmetro

### 2.1 Criar o visual data prep

1. Clique em **New** na barra lateral → **Visual data prep**.
2. Renomeie o arquivo no topo para `{seu_prefixo}aurora_performance`.
3. No seletor de compute, escolha **Serverless**.

Interface: painel de operadores à esquerda, canvas no centro, configuração à direita, preview embaixo, prompt do **Genie Code** acima do canvas. Ver [interface](https://docs.databricks.com/aws/en/designer/interface).

### 2.2 Source — três tabelas

O operador **Source** importa uma tabela do Unity Catalog (ou arquivo). Depois de selecionar, o painel mostra nome, dono e última atualização.

Para cada tabela:

1. No painel **Operators**, clique em **Source** (ou arraste a tabela do painel **Catalog**).
2. Busque `{seu_prefixo}clientes` e selecione. Renomeie o operador para `clientes`.
3. Repita para `pedidos` e `tickets_suporte`.
4. Clique em cada Source e confira o preview.

### 2.3 Enter Data — metas por cidade

**Enter Data** cria uma tabela digitada no canvas (lookup / dados de teste), sem CSV extra.

1. Adicione **Enter Data**.
2. Renomeie para `metas_cidade`.
3. Primeira linha = cabeçalho. Digite:

| cidade | meta_receita |
|---|---|
| São Paulo | 2500 |
| Rio de Janeiro | 1800 |
| Curitiba | 900 |
| Belo Horizonte | 1100 |
| Porto Alegre | 800 |

4. Apply e confira o preview.

### 2.4 Parâmetro de cidade (como no workshop de Sidney)

1. Painel esquerdo → **Parameters** → adicionar parâmetro.
2. Nome: `cidade_filtro`
3. Tipo texto, valor padrão: `São Paulo`

Você vai usar esse parâmetro no operador **SQL** (`:cidade_filtro`).
"""
    ),
    md(
        """---
## Módulo 3 — Qualidade: Unique, Prepare, Guardrails, Filter, Combine

Neste módulo você trata a sujeira **intencional** dos CSVs.

### 3.1 Unique em clientes

**Unique** remove duplicatas. Por padrão, compara todas as colunas; aqui a chave é `cliente_id`.

1. A partir de `clientes`, adicione **Unique**. Nome: `clientes_unicos`.
2. Unique by: **Selected columns** → `cliente_id`.
3. Order by: `email` DESC (mantém a linha que tem e-mail preenchido).
4. Preview: a duplicata some.

### 3.2 Prepare em clientes

**Prepare** encadeia ações de limpeza. Adicione **Prepare** depois de `clientes_unicos`. Nome: `clientes_limpos`.

Ações (nessa ordem):

| Ação | Configuração |
|---|---|
| Trim | coluna `nome` |
| Text case | `cidade` → Title (ou fórmula para padronizar) |
| Fill nulls | `email` → `sem_email@auroracafe.com` |
| Replace value | `cidade` valor `SAO PAULO` → `São Paulo` |
| Replace value | `cidade` valor `curitiba` → `Curitiba` |
| Formula | `nome_limpo` = `trim(nome)` (se ainda não tiver feito no Trim) |

Dica: na Formula, descreva em linguagem natural (*padronizar cidade para Title Case*) — o Genie Code gera a expressão. O menu `@` lista colunas e funções SQL.

### 3.3 Unique + Prepare em pedidos

1. **Unique** em `pedidos` → `pedidos_unicos`, chave `pedido_id`.
2. **Prepare** → `pedidos_preparados`:
   - Trim em `canal`
   - Text case **upper** em `canal`
   - Replace `Loja` / `online` para `LOJA` / `ONLINE` se ainda restar variação
   - Change type: `data_pedido` para Date (Parse date se vier string)
   - Formula: `receita = quantidade * valor_unitario` (não confie só em `valor_total`, há valor negativo)

### 3.4 Guardrails em pedidos

**Guardrails** valida regras e separa **Passed** / **Failed** / **Errors**.

1. Adicione **Guardrails** depois de `pedidos_preparados`. Nome: `qualidade_pedidos`.
2. Checks:
   - **Not null**: `pedido_id`, `cliente_id`, `produto`
   - **Accepted values**: `status` ∈ `confirmado`, `pendente`, `cancelado`
   - **Accepted values**: `canal` ∈ `ONLINE`, `LOJA`
   - **Value range**: `valor_total` ≥ 0 (ou `receita` ≥ 0)
3. When a check fails: **Warn and continue with passed rows**.
4. Inspecione as 3 saídas. O status `PENDNETE` e o valor negativo devem ir para **Failed**.
5. Siga o workshop pela saída **Passed**.

### 3.5 Filter — duas saídas (Included / Excluded)

**Filter** não descarta o resto: **Included** = quem passa; **Excluded** = quem não passa (e nulos).

1. A partir de **Passed**, adicione **Filter**. Nome: `separa_canal`.
2. Condição: `canal` **Is equal to** `ONLINE`.
3. Preview:
   - Included = pedidos online
   - Excluded = pedidos de loja

Esse padrão é o mesmo do tutorial oficial (filtro `status = confirmed`).

### 3.6 Prepare em cada ramo + Combine (Union)

1. No **Included**, Prepare `marca_online`: Formula `origem = 'ONLINE'`.
2. No **Excluded**, Prepare `marca_loja`: Formula `origem = 'LOJA'`.
3. Adicione **Combine**. Nome: `uniao_canais`.
4. Ligue as duas saídas.
5. Set operation: **Union**.
6. Merge strategy: **All**.
7. Advanced: **Union by name** + **Allow missing columns**.

Você acaba de unificar dois fluxos sem Python — equivalente ao union online/offline do material de referência.
"""
    ),
    md(
        """---
## Módulo 4 — Join, Select e SQL com parâmetro

### 4.1 Join pedidos × clientes

**Join** (2 tabelas) tem, por padrão, **3 saídas**: Left unmatched, Matched, Right unmatched. Para um único resultado, escolha o tipo (Inner / Left / …).

1. Adicione **Join**. Nome: `pedidos_clientes`.
2. Entrada 1: `uniao_canais`. Entrada 2: `clientes_limpos`.
3. Condição: `cliente_id` = `cliente_id`.
4. Join type: **Inner join** (uma saída só).
5. Match case: off (padrão).
6. Preview: cada pedido ganha cidade, segmento, canal de aquisição.

Inspecione também um Join **sem** tipo (split): clientes sem pedido aparecem em Right unmatched — ótimo para falar de qualidade de relacionamento.

### 4.2 Select — enxugar colunas

**Select** escolhe, renomeia e reordena. Também aceita regra dinâmica (tipo, nome, fórmula em metadados).

1. Adicione **Select**. Nome: `colunas_analise`.
2. Start with no columns e marque:
   `pedido_id`, `cliente_id`, `nome`, `cidade`, `segmento`, `produto`, `categoria`, `origem`, `status`, `receita`, `data_pedido`, `loja`
3. Renomeie `origem` → `canal_venda` se quiser deixar o nome de negócio.

### 4.3 SQL — filtro por parâmetro

O operador **SQL** cobre o que os blocos visuais não fazem. Referencie o operador de cima **pelo nome** e parâmetros com `:nome`.

1. Adicione **SQL**. Nome: `filtra_cidade`.
2. Query:

```sql
SELECT *
FROM colunas_analise
WHERE cidade = :cidade_filtro
   OR :cidade_filtro = 'TODAS'
```

3. Troque o parâmetro entre `São Paulo` e `TODAS` e veja o preview mudar — mesmo padrão do Sidney (`WHERE city = :city_filter`).

### 4.4 Filter de negócio: só confirmados

A partir de `filtra_cidade`, Filter `status` **Is equal to** `confirmado`. Nome: `pedidos_confirmados`.

Use **Included** daqui para frente.
"""
    ),
    md(
        """---
## Módulo 5 — AI Function, Aggregate, Pivot, Sort, Limit

Espelha o grupo **Review Sentiment Pipeline** do workshop de Sidney, sem Python.

Crie um **Group** no canvas chamado `Pipeline de sentimento` e coloque os operadores 5.1–5.4 dentro dele ([Group](https://docs.databricks.com/aws/en/designer/built-in-operators#group)).

### 5.1 Join tickets × clientes

1. Source `tickets_suporte` (já criado) → Join com `clientes_limpos` em `cliente_id`.
2. Inner join. Nome: `tickets_enriquecidos`.

### 5.2 Filter de texto

Filter: `comentario` **Is not null**. Nome: `tickets_com_texto`.

### 5.3 AI Function — classificar sentimento

**AI Function** roda uma função de IA nativa. Aqui: `ai_classify`.

1. Adicione **AI Function**. Nome: `classifica_sentimento`.
2. Function: `ai_classify`.
3. Input: coluna `comentario`.
4. Labels: `positivo`, `misto`, `negativo`.
5. Output column: `sentimento`.
6. Preview (pode levar alguns segundos). Compare com `sentimento_esperado`.

Funções disponíveis no mesmo operador (não todas neste lab): `ai_analyze_sentiment`, `ai_extract`, `ai_summarize`, `ai_translate`, `ai_query`, `ai_mask`, etc. Ver [AI Function](https://docs.databricks.com/aws/en/designer/built-in-operators#ai-function).

### 5.4 Aggregate + Pivot de sentimento

1. **Aggregate** `agg_sentimento`:
   - Group by: `cidade`, `produto`, `sentimento`
   - Aggregate: `COUNT` de `ticket_id` → `qtd_tickets`
2. **Pivot** `pivot_sentimento` (aba Rows → Columns):
   - Pivot column: `sentimento`
   - Value & aggregation: `qtd_tickets` / `SUM`
   - Colunas fixas: `cidade`, `produto`
3. Resultado esperado: colunas `positivo`, `misto`, `negativo`.

No Sidney, um bloco Python garantia colunas ausentes. Aqui, se faltar uma coluna, use **SQL** (não Python):

```sql
SELECT
  cidade,
  produto,
  COALESCE(positivo, 0) AS positivo,
  COALESCE(misto, 0) AS misto,
  COALESCE(negativo, 0) AS negativo
FROM pivot_sentimento
```

Nome sugerido: `sentimento_completo`.

### 5.5 Aggregate de receita + Join com sentimento

Volte ao ramo de vendas (`pedidos_confirmados`):

1. **Aggregate** `agg_produto`:
   - Group by: `cidade`, `produto`, `categoria`
   - `SUM(receita)` → `receita_total`
   - `COUNT(pedido_id)` → `qtd_pedidos`
   - `AVG(receita)` → `ticket_medio`
2. **Join** `vendas_sentimento`: `agg_produto` ⋈ `sentimento_completo` em `cidade` + `produto`.
   - Use **Left join** (produto sem ticket continua no ranking).
3. **Prepare** `score_experiencia`: Formula, por exemplo  
   `score_sentimento = coalesce(positivo,0) - coalesce(negativo,0)`

### 5.6 Join com metas (Enter Data)

Join `vendas_sentimento` ⋈ `metas_cidade` em `cidade`. Left join. Formula: `atingimento = receita_total / meta_receita`.

### 5.7 Sort + Limit

1. **Sort**: `receita_total` DESC, depois `score_sentimento` DESC.
2. **Limit**: máximo **10** linhas. Nome: `top10_produtos`.
"""
    ),
    md(
        """---
## Módulo 6 — Output, Visualization, Note e mapa do canvas

### 6.1 Output — gravar no Unity Catalog

**Output** escreve tabela, materialized view ou arquivo em Volume. Write mode: Overwrite / Append / Merge.

1. A partir de `top10_produtos`, adicione **Output**.
2. Output type: **Table**.
3. Table name: `{seu_prefixo}aurora_product_performance`
4. Location: seu catálogo.schema
5. Write mode: **Overwrite**
6. Clique em **Run** (não só o preview). Se a tabela não existir, o operador cria.

Opcional: um segundo Output tipo **File** (CSV no Volume) para mostrar split / header.

### 6.2 Visualization

1. Adicione **Visualization** ligado a `agg_produto` (antes do Limit, para ver o mix completo).
2. Tipo: **Bar**.
3. Eixo: `produto` × `receita_total`.

### 6.3 Note

Adicione **Note** no canvas:

> Aurora Café — performance de produto. Ramos: (1) qualidade e união de canais (2) sentimento de tickets via AI Function. Parâmetro `cidade_filtro` restringe a cidade.

### 6.4 Groups sugeridos

| Group | Operadores |
|---|---|
| `Fontes` | 3× Source + Enter Data |
| `Qualidade e canais` | Unique, Prepare, Guardrails, Filter, Combine |
| `Pipeline de sentimento` | Join tickets, Filter, AI Function, Aggregate, Pivot, SQL |
| `Ouro` | Aggregate receita, Joins, Sort, Limit, Output, Visualization |

Você pode **minimizar** um grupo e **Disable** para pular o ramo de IA se o workspace não tiver AI Functions.

### Mapa final (sem Python)

```
clientes ── Unique ── Prepare ─────────────────────────┐
                                                        ├─ Join ─ Select ─ SQL(:cidade) ─ Filter confirmado ─┐
pedidos ── Unique ── Prepare ── Guardrails ── Filter     │                                                     │
                              │ Included ─ Prepare ─┐    │                                                     ├─ Agg receita ─ Join sentimento ─ Join metas ─ Sort ─ Limit ─ Output
                              │ Excluded ─ Prepare ─┴ Combine                                                 │
                                                                                                               │
tickets ── Join clientes ── Filter ── AI classify ── Agg ── Pivot ── SQL ─────────────────────────────────────┘
metas_cidade (Enter Data) ─────────────────────────────────────────────────────────────── Join metas ─────────┘
```
"""
    ),
    md(
        """---
## Módulo 7 — Genie Code *(opcional)*

Em um **novo** visual data prep, descreva:

> Usando as tabelas {prefixo}clientes, {prefixo}pedidos e {prefixo}tickets_suporte: deduplicar clientes e pedidos, padronizar canal, validar status e valor, unir ONLINE e LOJA, juntar com clientes, ficar só com pedidos confirmados, classificar sentimento dos comentários em positivo/misto/negativo, agregar receita e tickets por produto e cidade, ordenar por receita e escrever top 10 em {prefixo}aurora_product_performance.

Confira cada operador gerado. Ver [Genie Code](https://docs.databricks.com/aws/en/designer/genie-code).
"""
    ),
    md(
        """---
## Validação final (SQL)

Depois do **Run** do Output, confira a tabela ouro.
"""
    ),
    sql(
        """%sql
SELECT *
FROM `${nome_catalogo}`.`${nome_schema}`.`${seu_prefixo}aurora_product_performance`
ORDER BY receita_total DESC;
"""
    ),
    sql(
        """%sql
SELECT produto, ROUND(SUM(receita_total), 2) AS receita
FROM `${nome_catalogo}`.`${nome_schema}`.`${seu_prefixo}aurora_product_performance`
GROUP BY produto
ORDER BY receita DESC;
"""
    ),
    md(
        """## Checklist de operadores

Marque o que você usou no canvas:

| Operador | Feito |
|---|---|
| Source | ☐ |
| Enter Data | ☐ |
| Unique | ☐ |
| Prepare | ☐ |
| Guardrails | ☐ |
| Filter (Included + Excluded) | ☐ |
| Combine (Union) | ☐ |
| Join | ☐ |
| Select | ☐ |
| SQL + parâmetro | ☐ |
| AI Function (`ai_classify`) | ☐ |
| Aggregate | ☐ |
| Pivot | ☐ |
| Sort | ☐ |
| Limit | ☐ |
| Output | ☐ |
| Visualization | ☐ |
| Group | ☐ |
| Note | ☐ |

## Próximos passos

- Agendar o visual data prep como Job ([schedule](https://docs.databricks.com/aws/en/designer/schedule))
- Materialized view no Output para consumo no AI/BI Dashboard
- Operadores customizados compartilhados, se o time precisar de lógica de negócio reutilizável

**Você terminou o workshop.** O canvas gera código versionável em Git e pode ir para produção como pipeline Lakeflow — o mesmo caminho do workshop de Sidney, agora em PT-BR e sem Python.
"""
    ),
]

nb = {
    "cells": cells,
    "metadata": {
        "application/vnd.databricks.v1+notebook": {
            "computePreferences": None,
            "dashboards": [],
            "environmentMetadata": None,
            "inputWidgetPreferences": None,
            "language": "python",
            "notebookOrigID": 0,
        },
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}

OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote {OUT} cells={len(cells)}")


if __name__ == "__main__":
    pass
