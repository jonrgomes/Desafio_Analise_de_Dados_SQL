# Design: Starter Kit de Análise de Dados com Python e PostgreSQL

> Plan from this document. Each slice below carries its own shape - copy it, do not re-derive it.
> Status: confirmed by USER, 2026-10-20

## Situation

- Project: in active construction
- Decision: committed by USER, 2026-10-20, in user request
- In flight: copies existing relational schema (`database/schema.sql`) and IBGE/Faker seed generator (`scripts/gerar_seed.py`); replaces empty `src/main.py` and unformatted `Install.md`.
- At stake: onboarding failure for beginner Python learners if environment setup, database loading, or analysis scripts are confusing or crash on execution.

## Problem

Iniciantes em Python e SQL que buscam realizar sua primeira análise de dados realistas enfrentam forte atrito técnico ao configurar bancos relacionais locais, aplicar migrations/schemas, carregar seeds com integridade referencial (FKs) e conectar Python ao PostgreSQL. Sem um guia didático sequencial e um script de entrada funcional em `src/main.py`, o aluno abandona o projeto antes de extrair qualquer valor analítico. Custo atual: barreira total de entrada no repositório.

## Success

- Worked if: Um iniciante clona o repositório e, seguindo estritamente o `README.md`, configura o ambiente Python, inicializa o PostgreSQL, carrega o schema e os seeds, e executa `python src/main.py`, visualizando relatórios analíticos formatados no terminal em menos de 15 minutos.
- Going wrong: Aluno trava em erros de conexão (`psycopg2`), variáveis de ambiente ausentes, caminhos de importação incorretos (`ModuleNotFoundError`) ou comandos de terminal não explicados.
- Review: Validação de execução ponta a ponta do fluxo completo a partir de um terminal limpo.

## Boundary

In:
- `README.md` unificado, pedagógico e sequencial dividido em 3 capítulos principais:
  1. Instalação e Preparação do Ambiente Python;
  2. Configuração e Carga do Banco PostgreSQL (Schema + Seeds);
  3. Execução da Análise de Dados com `src/main.py`.
- Implementação de `src/main.py` importando `src.db.query.obter_relatorio_vendas`, armazenando o resultado em variável e realizando análises exploratórias fundamentais (faturamento total, ticket médio, vendas por status, métodos de pagamento, top produtos e estados).
- Configuração de ambiente limpa: `.gitignore` abrangente, `.env.example` comentado e `docker-compose.yml` para inicialização imediata do PostgreSQL com um comando.
- Limpeza e depreciação de `Install.md` (integrado ao `README.md`).

Out:
- Criação de dashboards web (Streamlit, Flask, FastAPI ou React) — o escopo didático é focado em Python padrão e terminal.
- Alteração na modelagem relacional de `database/schema.sql` ou reescrita das regras de negócio do gerador do IBGE em `scripts/gerar_seed.py`.
- Uso de ferramentas avançadas de migração (ex: Alembic, Liquibase, Flyway).

Unchanged:
- `database/schema.sql`
- `scripts/gerar_seed.py`
- `database/seeds/`
- `database/vendas_exemplo.json`

## Prior art

- Setup de banco: Docker Compose oferece a experiência de container local rápido, Supabase permite infraestrutura gerenciada na nuvem 100% gratuita sem instalar nada na máquina, e comandos manuais cobrem quem já possui PostgreSQL nativo.
- Interface visual para banco (Cliente SQL): Beekeeper Studio destaca-se como alternativa leve, moderna e amigável para iniciantes em comparação ao pgAdmin tradicional, enquanto o SQL Editor web do Supabase oferece execução sem instalação local.
- Execução de scripts Python em subpastas (`src/`): Iniciantes costumam rodar tanto `python src/main.py` quanto `python -m src.main`. O código deve tratar `sys.path` preventivamente para nunca estourar `ModuleNotFoundError`.
- Formatação de saída analítica: Em vez de despejar JSON puro na tela, relatórios tabulares em texto simples com separadores visuais facilitam a compreensão dos dados por iniciantes.

## Shape

A arquitetura do kit didático é baseada em três etapas lineares: isolamento de ambiente (`venv` + dependências), persistência relacional populada (`schema.sql` + seeds) e camada de consumo analítico (`src/main.py` chamando `src/db/query.py`). O ponto crítico de reversibilidade é o contrato de dados gerado pela query SQL agregada em JSON, que alimenta a lógica do Python em memória. A alternativa mais pesada seria a introdução de ORM (SQLAlchemy) e bibliotecas de Data Science (Pandas), que só se justificaria se o volume de dados excedesse centenas de milhares de linhas ou exigisse persistência bidirecional.

## Key decisions

1. **Guia mestre unificado em `README.md` com índice sequencial.** Centraliza toda a jornada de aprendizado em um único arquivo de referência, eliminando dispersão em múltiplos arquivos e guiando o aluno cronologicamente pelas 3 etapas essenciais.
2. **`src/main.py` importa `obter_relatorio_vendas` e armazena em variável.** Atende ao requisito estrito do desafio, isolando a camada de consulta do banco (`src/db/query.py`) da camada de análise exploratória e agregação de negócio (`src/main.py`).
3. **Resiliência de importação em `src/main.py`.** Adiciona configuração de `sys.path` para garantir que o script funcione perfeitamente tanto sendo executado da raiz (`python src/main.py`) quanto como módulo (`python -m src.main`).
4. **Análises didáticas nativas em Python puro.** Processa métricas essenciais (faturamento total, ticket médio, distribuição por método de pagamento, top categorias e top estados) com código limpo, didático e amplamente comentado, permitindo que o aluno compreenda a lógica sem abstrações complexas.
5. **Opções duplas para PostgreSQL (Docker e Nativo).** Oferece um `docker-compose.yml` pré-configurado para subida do banco com `docker compose up -d`, mantendo instruções equivalentes para quem utiliza `psql` ou pgAdmin.
6. **Higiene de repositório com `.gitignore` e `.env.example` sanitizado.** Impede versionamento acidental de credenciais (`.env`), pastas virtuais (`venv/`) e caches (`__pycache__/`).

## Work

| Slice | Delivers | Status |
|---|---|---|
| [EnvironmentSetup](#environmentspec) | Arquivos de suporte a ambiente: `.gitignore`, `.env.example` corrigido e `docker-compose.yml` | clear |
| [MainAnalysisApp](#mainanalysisapp) | `src/main.py` funcional importando `query.py`, armazenando dados e executando análises formatadas | clear |
| [PedagogicalReadme](#pedagogicalreadme) | `README.md` pedagógico completo em 3 capítulos com sumário interativo | clear |

Order: EnvironmentSetup → MainAnalysisApp → PedagogicalReadme.

Already handled by existing code:
- Estrutura de tabelas e chaves estrangeiras → `database/schema.sql`
- Geração de dados de localidades IBGE e Faker → `scripts/gerar_seed.py`
- Arquivos de carga SQL prontos → `database/seeds/*.sql`
- Conexão PostgreSQL e extração de relatório em JSON estruturado → `src/db/query.py`

Derivable from the repository, left to the plan:
- Detalhes de formatação de moeda e porcentagem no terminal.
- Comentários educativos linha a linha em Python.

---

### EnvironmentSetup

**Delivers** Higiene de repositório e infraestrutura leve com `.gitignore`, `.env.example` e `docker-compose.yml`. **Status: clear.**

| State | What should happen | Caller sees |
|---|---|---|
| Repositório clonado | Usuário duplica `.env.example` para `.env` | Variáveis prontas com valores padrão locais |
| Docker instalado | Usuário roda `docker compose up -d` | Container PostgreSQL `db_vendas` saudável na porta 5432 |
| Execução do Python | Git ignora arquivos temporários e pastas virtuais | Repositório limpo sem `venv/` e `__pycache__/` rastreados |

Alternatives considered:
- Forçar instalação local de PostgreSQL com instalador oficial (.exe) - wins if ambiente do aluno não suportar virtualização/Docker. Mantido como alternativa documentada no README.

---

### MainAnalysisApp

**Delivers** Script `src/main.py` que importa `src.db.query`, armazena os dados de vendas e gera análises descritivas formatadas no terminal. **Status: clear.**

| State | What should happen | Caller sees |
|---|---|---|
| Banco conectado e populado | Importa `obter_relatorio_vendas()`, armazena em `vendas`, calcula métricas de negócio e imprime relatório formatado | Sumário executivo com Faturamento Total, Ticket Médio, Top Categorias, Top Estados e Status |
| Banco vazio (0 vendas) | Detecta lista vazia e avisa sobre execução dos seeds | Mensagem amigável indicando que o banco precisa ser populado |
| Falha de conexão com PostgreSQL | Captura retorno vazio ou exceção amigavelmente | Orientação clara para verificar variáveis do `.env` e status do banco |

Alternatives considered:
- Utilizar biblioteca `pandas` para as métricas - wins if foco fosse ciência de dados avançada. Rejeitado para manter zero atrito de instalação e focar na lógica fundamental de Python para iniciantes.

---

### PedagogicalReadme

**Delivers** `README.md` completo estruturado em 3 etapas sequenciais e detalhadas. **Status: clear.**

| State | What should happen | Caller sees |
|---|---|---|
| Leitura da Etapa 1 (Instalação) | Explica criação de `venv`, ativação (Windows/Linux/Mac), instalação do `requirements.txt` e configuração do `.env` | Passos exatos com explicação do *porquê* de cada comando |
| Leitura da Etapa 2 (Banco & Seeds) | Explica o que é `schema.sql`, como subir o Postgres (Docker ou local) e como carregar ou gerar os dados de seed | Comandos claros para carga sequencial das tabelas respeitando chaves estrangeiras |
| Leitura da Etapa 3 (Execução) | Explica como rodar `python src/main.py`, o que o código faz e como interpretar as análises | Instruções de execução e sugestões de desafios extras para estudo |

Alternatives considered:
- Separar documentação em múltiplos arquivos `.md` na pasta `docs/` - wins if repositório contivesse múltiplos subsistemas complexos. Rejeitado para evitar navegação fragmentada para iniciantes.

---

## Sources

- Repositório local: `database/schema.sql`, `scripts/gerar_seed.py`, `src/db/query.py`.
- Requisito do usuário: Alinhamento confirmado em 2026-10-20.
