"""
Módulo Principal de Análise de Dados
-----------------------------------
Este script é o ponto de entrada para o iniciante em Python.
Ele se conecta ao banco de dados PostgreSQL através do módulo 'src.db.query',
recebe os registros de vendas em uma variável e realiza uma análise descritiva
e exploratória dos dados com foco em regras de negócio.
"""

from collections import Counter, defaultdict
import os
import sys
from turtle import update

# Garante suporte adequado a UTF-8 em terminais Windows
if sys.platform.startswith('win'):
  try:
    if hasattr(sys.stdout, 'reconfigure'):
      sys.stdout.reconfigure(encoding='utf-8') # type: ignore
  except Exception:
    pass

# ---------------------------------------------------------------------------
# Ajuste de Caminho (sys.path)
# ---------------------------------------------------------------------------
# Garante que o diretório raiz do projeto esteja no caminho de busca de módulos.
# Isso permite que o script seja executado tanto via 'python src/main.py'
# quanto via 'python -m src.main' sem erros de importação.
DIRETORIO_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRETORIO_RAIZ not in sys.path:
  sys.path.insert(0, DIRETORIO_RAIZ)

# Importa a função de consulta desenvolvida para o PostgreSQL
from src.db.query import obter_relatorio_vendas

def main():
  """Ponto de entrada do script."""
  print('\n[1/2] Conectando ao PostgreSQL e executando a consulta...')

  # Executa a query de vendas e armazena os dados em uma variável
  vendas = obter_relatorio_vendas()

  # Validação de integridade do resultado obtido
  if not vendas:
    print('\n[Atenção] Nenhuma venda foi retornada do banco de dados.')
    print('Verifique se:')
    print('  1. O banco de dados PostgreSQL está em execução.')
    print('  2. As credenciais no arquivo .env estão corretas.')
    print('  3. O script de schema e os seeds foram executados com sucesso.')
    return

  print(f'[2/2] {len(vendas):,} registros encontrados com sucesso!')
  
  print("\nRELATÓRIO DE VENDAS - E-COMERCE 2026 - BRASIL\n")
  print("\n1 - Visão geral das finanças:\n")
  vendas_concluidas = 0
  faturamento = 0
  qtd_vendas_conluidas = 0
  for venda in vendas:
    faturamento += venda["valor_total"]
    if venda["status"] == "CONCLUIDO":
        vendas_concluidas += venda["valor_total"]
        qtd_vendas_conluidas += 1
        
  ticket_medio = vendas_concluidas / qtd_vendas_conluidas

  print(f'Total de vendas: R$ {faturamento:,.2f}')
  print(f'Total de vendas concluídas: R$ {vendas_concluidas:,.2f}')
  print(f'Ticket médio por VENDA CONCLUÍDA: R$ {ticket_medio:,.2f}')
  print("\n2 - Distribição por Status de Pedido:\n")
  concluidos = 0
  cancelado = 0
  pendente = 0
  
  for venda in vendas:
    if venda["status"] == "CONCLUIDO":
      concluidos += 1 
    if venda['status'] == "CANCELADO":
      cancelado += 1
    if venda["status"] == "PENDENTE":
      pendente += 1
      
  pctconcluidos = (concluidos / len(vendas) *100) 
  pctcancelados = (cancelado / len(vendas) *100)
  pctpendente = (pendente / len(vendas) *100)
      
          
  print(f"CONCLUIDOS: {concluidos} pedidos ({pctconcluidos:.2f}%)")   
  print(f"CANCELADOS: {cancelado} pedidos ({pctcancelados:.2f}%)")   
  print(f"PENDENTE: {pendente} pedidos ({pctcancelados:.2f}%)")   
  
  
  
   
 
  
  
if __name__ == '__main__':
  main()
