# Workshop Databricks — Lakeflow Designer

Workshop hands-on em **português (Brasil)** para times de negócio e analytics. O material cobre upload de dados no Unity Catalog e um visual data prep no [Lakeflow Designer](https://docs.databricks.com/aws/en/designer/what-is-lakeflow-designer) explorando o máximo de [operadores nativos](https://docs.databricks.com/aws/en/designer/built-in-operators) — **sem bloco Python**.

O fluxo cobre fontes, qualidade, join, IA em texto e output, no cenário **Aurora Café**.

---

## Estrutura do repositório

```
.
├── notebook_guia_workshop.ipynb   # Guia passo a passo do workshop
├── dados/
│   ├── clientes.csv               # Cadastro de clientes (com duplicatas e nulos de propósito)
│   ├── pedidos.csv                # Pedidos loja + online (com sujeira de qualidade)
│   └── tickets_suporte.csv        # Comentários de suporte para AI Function
└── scripts/
    └── gerar_dados.py             # Regenera os CSVs (opcional)
```

---

## Contexto de negócio

A **Aurora Café** opera lojas físicas e um canal online. O time de operações quer um pipeline visual (sem código) para:

| Tema | Perguntas típicas |
|---|---|
| Qualidade | Quais pedidos estão duplicados, com valor negativo ou status inválido? |
| Canais | Qual a receita de **LOJA** vs **ONLINE** depois de unificar os fluxos? |
| Receita | Quanto de receita cada cidade gera? |
| Experiência | Qual o sentimento do ticket ligado a cada pedido (produto, receita, status)? |

---

## Módulos do workshop

| # | Módulo | Obrigatório? | O que você faz |
|---|---|---|---|
| 1 | **Upload de arquivos (CSV)** | Sim | Subir os 3 CSVs e criar tabelas no Unity Catalog |
| 2 | **Lakeflow Designer — canvas e fontes** | Sim | Criar o visual data prep, Source, preview e parâmetros |
| 3 | **Qualidade e combinação** | Sim | Unique, Prepare, Guardrails, Filter (2 saídas), Combine |
| 4 | **Join, Select e SQL** | Sim | Juntar clientes + pedidos, selecionar colunas, filtrar por parâmetro |
| 5 | **IA e join do pedido** | Sim | AI Function, Join em `pedido_id` com o pedido filtrado por cidade, Select |
| 6 | **Output e canvas** | Sim | Output (tabela), Group |
| 7 | **Genie Code *(opcional)*** | Não | Descrever o fluxo em linguagem natural |
| 8 | **Dashboard *(opcional)*** | Não | Prompt no Genie Code para um AI/BI Dashboard da tabela ouro |

Não há operador **Python** neste workshop. Quando a lógica não couber em um bloco visual, use **SQL**.

---

## Pasta `dados/`

| Arquivo | Tabela sugerida | Linhas | Descrição |
|---|---|---|---|
| `clientes.csv` | `{prefixo}clientes` | 82 | Cadastro + 2 duplicatas, espaços, cidade inconsistente, e-mails vazios |
| `pedidos.csv` | `{prefixo}pedidos` | 201 | Pedidos ONLINE/LOJA + duplicata, valor negativo, status inválido |
| `tickets_suporte.csv` | `{prefixo}tickets_suporte` | 60 | Comentários em PT-BR para classificar sentimento |

> Prefixo: use um identificador único por participante (ex.: `ana_`, `joao_`) para evitar conflito de tabelas.

A sujeira nos CSVs é **intencional**: ela alimenta Unique, Prepare e Guardrails.

---

## Schema das tabelas

### `clientes`

| Coluna | Tipo | Descrição |
|---|---|---|
| `cliente_id` | INTEGER | Identificador do cliente (há duplicatas de propósito) |
| `nome` | STRING | Nome (alguns com espaços extras) |
| `email` | STRING | E-mail; alguns vazios |
| `cidade` | STRING | Cidade (grafia inconsistente em algumas linhas) |
| `estado` | STRING | UF |
| `canal_aquisicao` | STRING | `APP`, `LOJA`, `PARCEIRO` ou `SITE` |
| `segmento` | STRING | `Bronze`, `Prata` ou `Ouro` |
| `data_cadastro` | DATE | Data de cadastro |
| `ativo` | BOOLEAN | Cliente ativo |

### `pedidos`

| Coluna | Tipo | Descrição |
|---|---|---|
| `pedido_id` | INTEGER | Identificador do pedido (há duplicata) |
| `cliente_id` | INTEGER | FK para `clientes` |
| `produto` | STRING | Item do cardápio |
| `categoria` | STRING | `Bebida`, `Salgado`, `Doce` ou `Combo` |
| `quantidade` | INTEGER | Quantidade |
| `valor_unitario` | FLOAT | Preço unitário em R$ |
| `valor_total` | FLOAT | Total da linha (há valor negativo) |
| `canal` | STRING | `ONLINE` ou `LOJA` (há variação de maiúsculas/espaços) |
| `status` | STRING | `confirmado`, `pendente`, `cancelado` (há valor inválido) |
| `data_pedido` | DATE | Data do pedido |
| `loja` | STRING | Loja Aurora da cidade |

### `tickets_suporte`

| Coluna | Tipo | Descrição |
|---|---|---|
| `ticket_id` | STRING | Identificador do ticket |
| `cliente_id` | INTEGER | FK para `clientes` |
| `pedido_id` | INTEGER | FK para `pedidos` |
| `prioridade` | STRING | `baixa`, `media`, `alta` |
| `status` | STRING | `aberto`, `pendente`, `fechado` |
| `comentario` | STRING | Texto livre em PT-BR |
| `sentimento_esperado` | STRING | Gabarito para conferência (`positivo`, `misto`, `negativo`) |
| `data_abertura` | DATE | Data de abertura |

---

## Relações entre as tabelas

```
clientes (cliente_id)
   ├──< pedidos (cliente_id)
   │       └──< tickets_suporte (pedido_id)
   └──< tickets_suporte (cliente_id)
```

---

## Operadores cobertos

Referência oficial: [Built-in operators in Lakeflow Designer](https://docs.databricks.com/aws/en/designer/built-in-operators).

| Categoria | Operador | Como aparece no workshop |
|---|---|---|
| Input / output | **Source** | 3 tabelas UC |
| Clean | **Filter** | Separa ONLINE (Included) e LOJA (Excluded) |
| Clean | **Guardrails** | Not null, accepted values, value range |
| Clean | **Prepare** | Trim, fórmula, parse date, fill nulls, text case |
| Clean | **Select** | Escolhe / renomeia colunas |
| Clean | **Unique** | Deduplica clientes e pedidos |
| Combine | **Combine** | Union dos ramos LOJA + ONLINE |
| Combine | **Join** | Pedidos×clientes (`cliente_id`) e tickets×pedidos (`pedido_id`) |
| Transform | **AI Function** | `ai_classify` nos comentários |
| Code | **SQL** | Filtro `:cidade_filtro` |
| Canvas | **Group** | Agrupa o ramo de sentimento |
| Output | **Output** | Tabela `{prefixo}aurora_experiencia_pedido` |

Fora de escopo (de propósito): **Python**, **HTML**, **ai_parse_document**.

---

## Como usar

1. Clone ou baixe este repositório.
2. Importe `notebook_guia_workshop.ipynb` no Databricks.
3. Baixe a pasta `dados/` e siga o Módulo 1 (upload dos CSVs).
4. Abra **New → Visual data prep** e siga os módulos 2–6 no canvas.
5. (Opcional) Recrie o fluxo com Genie Code (Módulo 7).
6. (Opcional) Crie um AI/BI Dashboard da tabela `{prefixo}aurora_experiencia_pedido` com o prompt do Genie Code (Módulo 8).

---

## Pré-requisitos no workspace

- Unity Catalog habilitado
- Permissão para criar tabelas em um catálogo/schema
- Compute **serverless** (ou all-purpose) com `CAN USE`
- Lakeflow Designer disponível no workspace
- (Recomendado) AI Functions habilitadas para o operador AI Function

---

## Referências

- [What is Lakeflow Designer?](https://docs.databricks.com/aws/en/designer/what-is-lakeflow-designer)
- [Built-in operators](https://docs.databricks.com/aws/en/designer/built-in-operators)
- [Tutorial: Build a visual data prep](https://docs.databricks.com/aws/en/designer/build-transformation)
- [Use Genie Code](https://docs.databricks.com/aws/en/designer/genie-code)
- [The Lakeflow Designer interface](https://docs.databricks.com/aws/en/designer/interface)
- [AI/BI dashboards](https://docs.databricks.com/aws/en/dashboards/)
