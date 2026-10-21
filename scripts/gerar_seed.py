import argparse
import gzip
import json
import os
import random
import urllib.request
from dotenv import load_dotenv
from faker import Faker

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o Faker com localização do Brasil
fake = Faker('pt_BR')

# Definição de caminhos do projeto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
OUTPUT_DIR = os.path.join(ROOT_DIR, 'database')


def ler_configuracoes():
  """Lê parâmetros da CLI ou faz fallback para variáveis do .env"""
  parser = argparse.ArgumentParser(
      description='Gerador de Seeds SQL divididos por tabelas.'
  )
  parser.add_argument(
      '--users',
      type=int,
      default=int(os.getenv('GENERATE_USERS_QTD', 50)),
      help='Quantidade de clientes a gerar',
  )
  parser.add_argument(
      '--products',
      type=int,
      default=int(os.getenv('GENERATE_PRODUCTS_QTD', 100)),
      help='Quantidade de produtos a gerar',
  )
  parser.add_argument(
      '--sales',
      type=int,
      default=int(os.getenv('GENERATE_SALES_QTD', 200)),
      help='Quantidade de vendas a gerar',
  )

  args = parser.parse_args()
  return args.users, args.products, args.sales


def fetch_json(url):
  """Auxiliar para consumir dados da API do IBGE"""
  req = urllib.request.Request(
      url, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'}
  )
  with urllib.request.urlopen(req) as response:
    data = response.read()
    if (
        response.info().get('Content-Encoding') == 'gzip'
        or data[:2] == b'\x1f\x8b'
    ):
      data = gzip.decompress(data)
    return json.loads(data.decode('utf-8'))


def extrair_info_uf(cid):
  """Tratamento seguro para árvore de localidades do IBGE"""
  micro = cid.get('microrregiao')
  if micro and isinstance(micro, dict):
    meso = micro.get('mesorregiao')
    if meso and isinstance(meso, dict) and meso.get('UF'):
      uf = meso['UF']
      return uf.get('sigla'), uf.get('id')

  imediata = cid.get('regiao-imediata')
  if imediata and isinstance(imediata, dict):
    inter = imediata.get('regiao-intermediaria')
    if inter and isinstance(inter, dict) and inter.get('UF'):
      uf = inter['UF']
      return uf.get('sigla'), uf.get('id')

  return None, None


def gerar_produtos_fake(qtd_produtos):
  """Gera categorias e produtos fictícios"""
  nomes_categorias = [
      'Periféricos',
      'Hardware',
      'Monitores',
      'Acessórios de TI',
      'Móveis de Escritório',
      'Áudio',
      'Armazenamento',
      'Redes e Conectividade',
  ]

  categorias = [
      {'id_categoria': idx + 1, 'nome': cat}
      for idx, cat in enumerate(nomes_categorias)
  ]

  prefixos = [
      'Teclado',
      'Mouse',
      'Monitor',
      'Cadeira',
      'Headset',
      'SSD',
      'Placa de Vídeo',
      'Gabinete',
      'Webcam',
      'Roteador',
      'Mesa',
      'Microfone',
  ]
  sufixos = [
      'Pro',
      'Ultra',
      'Gamer',
      'Ergonômico',
      'RGB',
      'Wireless',
      'Basic',
      'EVO',
      'Master',
      'Silent',
  ]

  produtos = []
  for i in range(1, qtd_produtos + 1):
    nome_prod = f'{random.choice(prefixos)} {random.choice(sufixos)} {fake.word().capitalize()}'
    categoria = random.choice(categorias)
    preco = round(random.uniform(49.90, 3500.00), 2)

    produtos.append({
        'id_produto': i + 500,
        'nome': nome_prod,
        'preco_unitario': preco,
        'id_categoria': categoria['id_categoria'],
    })

  return categorias, produtos


def salvar_arquivo_sql(nome_arquivo, conteudo_linhas):
  """Grava o conjunto de linhas em um arquivo SQL na pasta database/"""
  os.makedirs(OUTPUT_DIR, exist_ok=True)
  caminho_completo = os.path.join(OUTPUT_DIR+'/seeds', nome_arquivo)
  with open(caminho_completo, 'w', encoding='utf-8') as f:
    f.writelines(conteudo_linhas)
  print(f'  [+] Gerado: database/{nome_arquivo}')


def gerar_seed_sql():
  qtd_users, qtd_products, qtd_sales = ler_configuracoes()

  print(
      f'=== Configuração da Geração ===\n'
      f'Clientes: {qtd_users}\n'
      f'Produtos: {qtd_products}\n'
      f'Vendas:   {qtd_sales}\n'
      f'==============================='
  )

  print('\n1. Baixando e processando localidades do IBGE...')
  estados_ibge = fetch_json(
      'https://servicodados.ibge.gov.br/api/v1/localidades/estados'
  )
  cidades_ibge = fetch_json(
      'https://servicodados.ibge.gov.br/api/v1/localidades/municipios'
  )

  # --- 1. states-seed.sql ---
  linhas_states = ['-- ESTADOS (IBGE)\n']
  for est in estados_ibge:
    nome_est = est['nome'].replace("'", "''")
    linhas_states.append(
        f"INSERT INTO estados (id_estado, sigla, nome) VALUES ({est['id']},"
        f" '{est['sigla']}', '{nome_est}') ON CONFLICT (id_estado) DO"
        ' NOTHING;\n'
    )
  salvar_arquivo_sql('states-seed.sql', linhas_states)

  # --- 2. cities-seed.sql ---
  linhas_cities = ['-- CIDADES (IBGE)\n']
  cidades_validas = []
  for cid in cidades_ibge:
    _, id_est = extrair_info_uf(cid)
    if id_est:
      cidades_validas.append(cid)
      nome_cid = cid['nome'].replace("'", "''")
      linhas_cities.append(
          f"INSERT INTO cidades (id_cidade, nome, id_estado) VALUES ({cid['id']},"
          f" '{nome_cid}', {id_est}) ON CONFLICT (id_cidade) DO NOTHING;\n"
      )
  salvar_arquivo_sql('cities-seed.sql', linhas_cities)

  print('\n2. Gerando entidades dinâmicas com Faker...')
  categorias, produtos = gerar_produtos_fake(qtd_products)

  # --- 3. categories-seed.sql ---
  linhas_categories = ['-- CATEGORIAS\n']
  for cat in categorias:
    linhas_categories.append(
        f"INSERT INTO categorias (id_categoria, nome) VALUES ({cat['id_categoria']},"
        f" '{cat['nome']}') ON CONFLICT (id_categoria) DO NOTHING;\n"
    )
  salvar_arquivo_sql('categories-seed.sql', linhas_categories)

  # --- 4. products-seed.sql ---
  linhas_products = ['-- PRODUTOS\n']
  for p in produtos:
    p_nome = p['nome'].replace("'", "''")
    linhas_products.append(
        'INSERT INTO produtos (id_produto, nome, id_categoria) VALUES'
        f" ({p['id_produto']}, '{p_nome}', {p['id_categoria']}) ON CONFLICT"
        ' (id_produto) DO NOTHING;\n'
    )
  salvar_arquivo_sql('products-seed.sql', linhas_products)

  # --- 5. customers-seed.sql ---
  clientes = []
  linhas_customers = ['-- CLIENTES\n']
  for i in range(1, qtd_users + 1):
    c = {
        'id_cliente': i,
        'nome': fake.name().replace("'", "''"),
        'email': fake.unique.email(),
        'telefone': fake.cellphone_number(),
    }
    clientes.append(c)
    linhas_customers.append(
        f"INSERT INTO clientes (id_cliente, nome, email, telefone) VALUES"
        f" ({c['id_cliente']}, '{c['nome']}', '{c['email']}', '{c['telefone']}')"
        ' ON CONFLICT (id_cliente) DO NOTHING;\n'
    )
  salvar_arquivo_sql('customers-seed.sql', linhas_customers)

  # --- 6. addresses-seed.sql ---
  linhas_addresses = ['-- ENDERECOS\n']
  for i in range(1, qtd_sales + 1):
    cid_sorteada = random.choice(cidades_validas)
    rua = fake.street_address().replace("'", "''")
    cep = fake.postcode().replace('-', '')
    linhas_addresses.append(
        f"INSERT INTO enderecos (id_endereco, rua, cep, id_cidade) VALUES ({i},"
        f" '{rua}', '{cep}', {cid_sorteada['id']}) ON CONFLICT (id_endereco) DO"
        ' NOTHING;\n'
    )
  linhas_addresses.append(
      "\nSELECT setval('enderecos_id_endereco_seq', (SELECT MAX(id_endereco)"
      ' FROM enderecos));\n'
  )
  salvar_arquivo_sql('addresses-seed.sql', linhas_addresses)

  # --- 7. sales-seed.sql ---
  metodos_pagamento = ['PIX', 'BOLETO', 'CARTAO_CREDITO']
  status_venda = ['CONCLUIDO', 'CANCELADO', 'PENDENTE']
  linhas_sales = ['-- VENDAS, PAGAMENTOS E ITENS DE VENDA\n']

  for i in range(1, qtd_sales + 1):
    id_cliente = random.choice(clientes)['id_cliente']
    id_endereco = i
    data_venda = fake.date_time_between(
        start_date='-1y', end_date='now'
    ).strftime('%Y-%m-%dT%H:%M:%SZ')
    status = random.choices(status_venda, weights=[0.85, 0.10, 0.05], k=1)[0]

    produtos_venda = random.sample(
        produtos, k=random.randint(1, min(4, len(produtos)))
    )

    valor_total = 0
    itens_sql = []

    for prod in produtos_venda:
      qtd = random.randint(1, 3)
      preco = prod['preco_unitario']
      valor_total += qtd * preco
      itens_sql.append(
          'INSERT INTO itens_venda (id_venda, id_produto, quantidade,'
          f' preco_unitario) VALUES ({i}, {prod["id_produto"]}, {qtd}, {preco})'
          ' ON CONFLICT (id_venda, id_produto) DO NOTHING;\n'
      )

    valor_total = round(valor_total, 2)

    # Venda
    linhas_sales.append(
        'INSERT INTO vendas (id_venda, id_cliente, id_endereco_entrega,'
        ' data_venda, status, valor_total) VALUES'
        f" ({i}, {id_cliente}, {id_endereco}, '{data_venda}', '{status}',"
        f' {valor_total}) ON CONFLICT (id_venda) DO NOTHING;\n'
    )

    # Pagamento
    metodo = random.choice(metodos_pagamento)
    parcelas = random.randint(1, 12) if metodo == 'CARTAO_CREDITO' else 1
    status_pag = 'APROVADO' if status == 'CONCLUIDO' else 'RECUSADO'
    linhas_sales.append(
        'INSERT INTO pagamentos (id_venda, metodo, status, parcelas) VALUES'
        f" ({i}, '{metodo}', '{status_pag}', {parcelas});\n"
    )

    # Itens de Venda
    linhas_sales.extend(itens_sql)

  salvar_arquivo_sql('sales-seed.sql', linhas_sales)

  print(
      '\n[Sucesso] Todos os arquivos de Seed foram gerados separadamente na'
      ' pasta database/!'
  )


if __name__ == '__main__':
  gerar_seed_sql()