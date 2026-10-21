import json
import os
from dotenv import load_dotenv
import psycopg2

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


def obter_relatorio_vendas(id_venda=None):
  # Configuração de conexão buscando diretamente do .env
  db_params = {
      'host': os.getenv('DB_HOST', 'localhost'),
      'port': int(os.getenv('DB_PORT', 5432)),
      'database': os.getenv('DB_NAME', 'db_vendas'),
      'user': os.getenv('DB_USER', 'admin'),
      'password': os.getenv('DB_PASSWORD', 'adminpassword'),
  }

  query = """
    SELECT json_build_object(
        'id_venda', v.id_venda,
        'data_venda', to_char(v.data_venda AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
        'status', v.status,
        'valor_total', v.valor_total,
        'cliente', json_build_object(
            'id_cliente', c.id_cliente,
            'nome', c.nome,
            'email', c.email,
            'telefone', c.telefone
        ),
        'endereco_entrega', json_build_object(
            'rua', e.rua,
            'cep', e.cep,
            'cidade', json_build_object(
                'id_cidade', cid.id_cidade,
                'codigo_ibge', cid.id_cidade,
                'nome', cid.nome,
                'id_estado', est.id_estado,
                'estado', json_build_object(
                    'id_estado', est.id_estado,
                    'sigla', est.sigla,
                    'nome', est.nome
                )
            )
        ),
        'pagamento', json_build_object(
            'metodo', p.metodo,
            'status', p.status,
            'parcelas', p.parcelas
        ),
        'itens', (
            SELECT json_agg(
                json_build_object(
                    'id_produto', pr.id_produto,
                    'nome', pr.nome,
                    'quantidade', iv.quantidade,
                    'preco_unitario', iv.preco_unitario,
                    'categoria', json_build_object(
                        'id_categoria', cat.id_categoria,
                        'nome', cat.nome
                    )
                )
            )
            FROM itens_venda iv
            JOIN produtos pr ON pr.id_produto = iv.id_produto
            JOIN categorias cat ON cat.id_categoria = pr.id_categoria
            WHERE iv.id_venda = v.id_venda
        )
    ) AS relatorio
    FROM vendas v
    JOIN clientes c ON c.id_cliente = v.id_cliente
    JOIN enderecos e ON e.id_endereco = v.id_endereco_entrega
    JOIN cidades cid ON cid.id_cidade = e.id_cidade
    JOIN estados est ON est.id_estado = cid.id_estado
    LEFT JOIN pagamentos p ON p.id_venda = v.id_venda
    """

  if id_venda:
    query += ' WHERE v.id_venda = %s;'
    params = (id_venda,)
  else:
    query += ';'
    params = None

  try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute(query, params) if params else cursor.execute(query)
    resultados = cursor.fetchall()

    relatorios = [row[0] for row in resultados]

    cursor.close()
    conn.close()

    return relatorios

  except Exception as e:
    print(f'Erro ao conectar ou consultar o banco de dados: {e}')
    return []


if __name__ == '__main__':
  # Executa a busca de relatório
  relatorios = obter_relatorio_vendas()

  if relatorios:
    print(
        f'Foram encontradas {len(relatorios)} vendas. Exemplo da primeira'
        ' venda:'
    )
    print(json.dumps(relatorios[0], indent=2, ensure_ascii=False))