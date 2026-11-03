# Dataset sintético Aurora Café — 3 CSVs para o workshop Lakeflow Designer.
# Seed 42. Qualidade intencional: duplicatas, nulos, espaços, status inválido.

from __future__ import annotations

import csv
from pathlib import Path

from datetime import date, timedelta

OUT = Path(__file__).resolve().parents[1] / "dados"
OUT.mkdir(exist_ok=True)

CIDADES = [
    ("São Paulo", "SP"),
    ("Rio de Janeiro", "RJ"),
    ("Curitiba", "PR"),
    ("Belo Horizonte", "MG"),
    ("Porto Alegre", "RS"),
]
PRODUTOS = [
    ("Espresso", "Bebida", 8.50),
    ("Cappuccino", "Bebida", 14.90),
    ("Latte", "Bebida", 16.50),
    ("Pão de Queijo", "Salgado", 9.90),
    ("Bolo de Cenoura", "Doce", 12.50),
    ("Combo Brunch", "Combo", 42.00),
]
NOMES = [
    "Ana Souza", "Bruno Lima", "Carla Mendes", "Diego Alves", "Elena Costa",
    "Felipe Rocha", "Gabriela Nunes", "Henrique Dias", "Isabela Pinto", "João Martins",
    "Karina Lopes", "Lucas Ferreira", "Marina Teixeira", "Nicolas Barbosa", "Olivia Ramos",
    "Paulo Vieira", "Quezia Andrade", "Rafael Cunha", "Sofia Ribeiro", "Thiago Moreira",
    "Úrsula Campos", "Vinícius Azevedo", "Wanessa Freitas", "Xavier Gomes", "Yasmin Duarte",
    "Zeca Carvalho", "Beatriz Moura", "Caio Fernandes", "Daniela Castro", "Eduardo Pires",
    "Fernanda Araujo", "Gustavo Melo", "Helena Cardoso", "Igor Santana", "Julia Peixoto",
    "Kevin Borges", "Larissa Monteiro", "Mateus Silveira", "Natália Farias", "Otávio Reis",
    "Priscila Nogueira", "Renato Sampaio", "Samara Brito", "Túlio Magalhães", "Valentina Cruz",
    "Wagner Tavares", "Ximena Prado", "Yuri Albuquerque", "Zélia Fonseca", "Amanda Correia",
    "Bernardo Pacheco", "Camila Vasconcelos", "Davi Figueiredo", "Elisa Guimarães", "Fabio Antunes",
    "Giovana Macedo", "Heitor Barros", "Ingrid Leal", "Jorge Caldas", "Leticia Siqueira",
    "Murilo Batista", "Nina Coelho", "Otto Viana", "Patricia Neves", "Quirino Lacerda",
    "Rita Assis", "Sérgio Padilha", "Tainá Guedes", "Ulisses Prado", "Vera Lins",
    "William Canto", "Yara Braga", "Zion Matos", "Alice Furtado", "Breno Aguiar",
    "Cecília Torres", "Danilo Esteves", "Eva Lambert", "Flávio Neri", "Glória Pimentel",
]

COMENTARIOS_POS = [
    "Simplesmente perfeito, nada a reclamar.",
    "Muito satisfeito com a agilidade na entrega.",
    "O cappuccino chegou quente e o pão de queijo estava crocante.",
    "Atendimento excelente na loja da Paulista.",
    "Pedido online chegou antes do prazo. Recomendo!",
]
COMENTARIOS_MIX = [
    "O preço está um pouco alto, mas a qualidade justifica.",
    "Gostei do produto, porém o aplicativo travou no checkout.",
    "Sabor ótimo, mas a espera na loja foi longa.",
    "Combo brunch bom, só veio sem o molho pedido.",
]
COMENTARIOS_NEG = [
    "O suporte demorou 3 dias para responder um oi. Inaceitável.",
    "O tamanho veio errado e a troca está demorando muito. Péssimo.",
    "Não consigo rastrear meu pedido online. O sistema dá erro.",
    "Quero cancelar meu pedido mas não encontro o botão no app.",
    "Café frio e pão de queijo murcho. Não volto.",
]


def main() -> None:
    clientes = []
    for i, nome in enumerate(NOMES, start=1):
        cidade, uf = CIDADES[(i - 1) % len(CIDADES)]
        canal = ["APP", "LOJA", "PARCEIRO", "SITE"][(i - 1) % 4]
        cadastro = date(2024, 1, 1) + timedelta(days=(i * 7) % 400)
        email = f"{nome.split()[0].lower()}.{nome.split()[-1].lower()}@auroracafe.com"
        clientes.append(
            {
                "cliente_id": i,
                "nome": nome,
                "email": email,
                "cidade": cidade,
                "estado": uf,
                "canal_aquisicao": canal,
                "segmento": ["Bronze", "Prata", "Ouro"][(i - 1) % 3],
                "data_cadastro": cadastro.isoformat(),
                "ativo": "true" if i % 11 else "false",
            }
        )

    # sujeira proposital
    clientes[2]["nome"] = "  Carla Mendes  "
    clientes[7]["cidade"] = "curitiba"
    clientes[11]["email"] = ""
    clientes[18]["email"] = ""
    clientes[24]["cidade"] = "SAO PAULO"
    clientes.append(dict(clientes[0]))  # duplicata cliente 1
    clientes.append(dict(clientes[4]))  # duplicata cliente 5
    clientes[-1]["email"] = "elena.costa.dup@auroracafe.com"

    with (OUT / "clientes.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(clientes[0].keys()))
        w.writeheader()
        w.writerows(clientes)

    pedidos = []
    pedido_id = 1000
    for i in range(1, 201):
        cliente_id = ((i - 1) % 80) + 1
        produto, categoria, preco = PRODUTOS[(i - 1) % len(PRODUTOS)]
        qtd = 1 + (i % 3)
        canal = "ONLINE" if i % 3 else "LOJA"
        status = ["confirmado", "confirmado", "confirmado", "pendente", "cancelado"][i % 5]
        dt = date(2025, 10, 1) + timedelta(days=i % 45)
        cidade, _ = CIDADES[(cliente_id - 1) % len(CIDADES)]
        loja = f"Aurora {cidade}"
        pedidos.append(
            {
                "pedido_id": pedido_id,
                "cliente_id": cliente_id,
                "produto": produto,
                "categoria": categoria,
                "quantidade": qtd,
                "valor_unitario": f"{preco:.2f}",
                "valor_total": f"{preco * qtd:.2f}",
                "canal": canal,
                "status": status,
                "data_pedido": dt.isoformat(),
                "loja": loja,
            }
        )
        pedido_id += 1

    # sujeira: duplicata, valor negativo, status inválido, canal com espaço
    pedidos.append(dict(pedidos[9]))
    pedidos[14]["valor_total"] = "-12.50"
    pedidos[21]["status"] = "PENDNETE"
    pedidos[33]["canal"] = "online "
    pedidos[40]["canal"] = "Loja"

    with (OUT / "pedidos.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pedidos[0].keys()))
        w.writeheader()
        w.writerows(pedidos)

    tickets = []
    pools = [COMENTARIOS_POS, COMENTARIOS_MIX, COMENTARIOS_NEG]
    labels = ["positivo", "misto", "negativo"]
    for i in range(1, 61):
        pool = pools[(i - 1) % 3]
        tickets.append(
            {
                "ticket_id": f"tk_{2000 + i}",
                "cliente_id": ((i - 1) % 80) + 1,
                "pedido_id": 1000 + ((i - 1) % 200),
                "prioridade": ["baixa", "media", "alta"][(i - 1) % 3],
                "status": ["aberto", "pendente", "fechado"][(i - 1) % 3],
                "comentario": pool[(i - 1) % len(pool)],
                "sentimento_esperado": labels[(i - 1) % 3],
                "data_abertura": (date(2025, 10, 5) + timedelta(days=i % 40)).isoformat(),
            }
        )

    with (OUT / "tickets_suporte.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(tickets[0].keys()))
        w.writeheader()
        w.writerows(tickets)

    print(f"clientes={len(clientes)} pedidos={len(pedidos)} tickets={len(tickets)}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
