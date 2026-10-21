import json
import urllib.request

def fetch_json(url):
    """Função auxiliar para fazer o download dos dados do IBGE"""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def gerar_seed_sql():
    print("1. A descarregar dados do IBGE...")
    estados_ibge = fetch_json("https://servicodados.ibge.gov.br/api/v1/localidades/estados")
    cidades_ibge = fetch_json("https://servicodados.ibge.gov.br/api/v1/localidades/municipios")
    
    print("2. A ler o ficheiro vendas_200.json...")
    with open('vendas_200.json', 'r', encoding='utf-8') as f:
        vendas = json.load(f)

    # Estruturas de dados para deduplicação
    clientes = {}
    categorias = {}
    produtos = {}
    enderecos = {}
    
    # Dicionário de busca rápida para o ID da cidade do IBGE: (nome_cidade, sigla_estado) -> id_cidade
    mapa_cidades = {
        (c['nome'].lower(), c['microrregiao']['mesorregiao']['UF']['sigla'].lower()): c['id']
        for c in cidades_ibge
    }

    print("3. A processar entidades únicas do JSON...")
    for venda in vendas:
        # Clientes
        c = venda['cliente']
        clientes[c['id_cliente']] = c
        
        # Endereços
        end = venda['endereco_entrega']
        chave_cidade = (end['cidade'].lower(), end['estado'].lower())
        id_cidade_ibge = mapa_cidades.get(chave_cidade, 'NULL')
        
        # Cria uma chave única para o endereço com base na rua e código postal (cep)
        chave_end = f"{end['rua']}-{end['cep']}"
        if chave_end not in enderecos:
            enderecos[chave_end] = {
                "id_endereco": len(enderecos) + 1,
                "rua": end['rua'],
                "cep": end['cep'].replace('-', ''), # Guarda apenas os números
                "id_cidade": id_cidade_ibge
            }
            
        # Itens, Produtos e Categorias
        for item in venda['itens']:
            cat = item['categoria']
            categorias[cat['id_categoria']] = cat['nome']
            
            if item['id_produto'] not in produtos:
                produtos[item['id_produto']] = {
                    "nome": item['nome'],
                    "id_categoria": cat['id_categoria']
                }

    print("4. A escrever o ficheiro seed.sql (Otimizado para PostgreSQL)...")
    with open('seed.sql', 'w', encoding='utf-8') as sql:
        sql.write("-- ==========================================\n")
        sql.write("-- SEED GERADO AUTOMATICAMENTE (POSTGRESQL)\n")
        sql.write("-- ==========================================\n\n")

        # 1. Estados
        sql.write("-- ESTADOS (IBGE)\n")
        for est in estados_ibge:
            nome = est['nome'].replace("'", "''")
            sql.write(f"INSERT INTO estados (id_estado, sigla, nome) VALUES ({est['id']}, '{est['sigla']}', '{nome}') ON CONFLICT (id_estado) DO NOTHING;\n")
        
        # 2. Cidades 
        sql.write("\n-- CIDADES (IBGE)\n")
        for cid in cidades_ibge:
            id_est = cid['microrregiao']['mesorregiao']['UF']['id']
            nome_cid = cid['nome'].replace("'", "''")
            sql.write(f"INSERT INTO cidades (id_cidade, nome, id_estado) VALUES ({cid['id']}, '{nome_cid}', {id_est}) ON CONFLICT (id_cidade) DO NOTHING;\n")

        # 3. Categorias
        sql.write("\n-- CATEGORIAS\n")
        for id_cat, nome_cat in categorias.items():
            sql.write(f"INSERT INTO categorias (id_categoria, nome) VALUES ({id_cat}, '{nome_cat}') ON CONFLICT (id_categoria) DO NOTHING;\n")

        # 4. Produtos
        sql.write("\n-- PRODUTOS\n")
        for id_prod, p in produtos.items():
            sql.write(f"INSERT INTO produtos (id_produto, nome, id_categoria) VALUES ({id_prod}, '{p['nome']}', {p['id_categoria']}) ON CONFLICT (id_produto) DO NOTHING;\n")

        # 5. Clientes
        sql.write("\n-- CLIENTES\n")
        for id_cli, c in clientes.items():
            sql.write(f"INSERT INTO clientes (id_cliente, nome, email, telefone) VALUES ({id_cli}, '{c['nome']}', '{c['email']}', '{c['telefone']}') ON CONFLICT (id_cliente) DO NOTHING;\n")

        # 6. Endereços
        sql.write("\n-- ENDERECOS\n")
        for end in enderecos.values():
            # Inserimos com o ID explícito para poder relacionar nas Vendas futuramente
            sql.write(f"INSERT INTO enderecos (id_endereco, rua, cep, id_cidade) VALUES ({end['id_endereco']}, '{end['rua']}', '{end['cep']}', {end['id_cidade']}) ON CONFLICT (id_endereco) DO NOTHING;\n")

        # Ajuste inteligente da Sequence: evita erros na API ao criar um novo endereço
        sql.write("\n-- AJUSTA A SEQUENCE DE ENDERECOS PARA O AUTO-INCREMENTO\n")
        sql.write("SELECT setval('enderecos_id_endereco_seq', (SELECT MAX(id_endereco) FROM enderecos));\n")

        # 7. Vendas, Pagamentos e Itens
        sql.write("\n-- VENDAS, PAGAMENTOS E ITENS\n")
        for venda in vendas:
            end = venda['endereco_entrega']
            chave_end = f"{end['rua']}-{end['cep']}"
            id_endereco = enderecos[chave_end]['id_endereco']
            
            # Venda
            sql.write(f"INSERT INTO vendas (id_venda, id_cliente, id_endereco_entrega, data_venda, status, valor_total) VALUES ({venda['id_venda']}, {venda['cliente']['id_cliente']}, {id_endereco}, '{venda['data_venda']}', '{venda['status']}', {venda['valor_total']}) ON CONFLICT (id_venda) DO NOTHING;\n")
            
            # Pagamento (Sem informar o id_pagamento, deixando o Postgres gerar pelo SERIAL)
            pag = venda['pagamento']
            sql.write(f"INSERT INTO pagamentos (id_venda, metodo, status, parcelas) VALUES ({venda['id_venda']}, '{pag['metodo']}', '{pag['status']}', {pag['parcelas']});\n")
            
            # Itens da Venda
            for item in venda['itens']:
                sql.write(f"INSERT INTO itens_venda (id_venda, id_produto, quantidade, preco_unitario) VALUES ({venda['id_venda']}, {item['id_produto']}, {item['quantidade']}, {item['preco_unitario']}) ON CONFLICT (id_venda, id_produto) DO NOTHING;\n")

    print("Concluído! Ficheiro 'seed.sql' gerado com sucesso para PostgreSQL.")

if __name__ == "_main_":