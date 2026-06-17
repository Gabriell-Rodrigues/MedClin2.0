# MedClin — Sistema de Gestão para Clínica Médica

Projeto acadêmico da disciplina de Engenharia de Software (UFS). Aplicação web
em **Django** que organiza o dia a dia de uma clínica em módulos: acesso,
cadastros, atendimento, prontuário eletrônico e farmácia, com controle de acesso
por perfil e rastreabilidade das ações.

> **Documentos de referência** (pasta acima desta, `Proj Engenharia de Software 2.0`):
> SRS, **Casos de Uso v3.0**, **Documento de Arquitetura v5** (modelo 4+1 /
> ISO 42010) e **Mapeamento Objeto-Relacional (OR)**. O **OR é a fonte de
> verdade** das entidades; o **BCE** orienta a organização do código.

---

## Visão geral — como funciona

O MedClin é usado por **seis perfis**, cada um enxergando apenas as telas do seu
trabalho (controle de acesso por papel):

- **Paciente** — vê seus agendamentos, marca consultas e consulta seu prontuário.
- **Recepcionista** — cadastra pacientes, agenda/reagenda/cancela consultas.
- **Médico** — vê sua agenda, acessa prontuários e registra evoluções clínicas.
- **Enfermeiro** — consulta prontuários e registra consumo de materiais.
- **Farmacêutico** — verifica estoque e dispensa medicamentos.
- **Gestor** — cadastra funcionários e gerencia os estoques.

**Fluxo típico:** a recepcionista cadastra o paciente e agenda a consulta → o
médico registra a evolução no prontuário → o farmacêutico dispensa o medicamento
(com baixa no estoque) → o gestor acompanha estoques e equipe. Cada ação
relevante fica registrada na trilha de auditoria (log).

### Como o código está dividido

O sistema é um **monólito Django em três camadas** (apresentação / negócio /
dados), organizado por **módulos de negócio** dentro de `apps/`. Cada módulo
segue o padrão **BCE** do Documento de Arquitetura:

| Camada BCE | Pasta | Responsabilidade |
| --- | --- | --- |
| **Boundary** (Tela) | `boundary_tela_*` | telas: views e formulários |
| **Control** (CTR) | `control_ctr_*` | regras de negócio (services) |
| **Entity** | `entity_*` | entidades persistidas (models do OR) |

A configuração do projeto fica em `meu_projeto/`, os templates em `templates/`,
o front em `static/` e os testes em `tests/`.

---

## Tecnologias

- Python 3.11+ e Django 5.2
- Banco de dados: PostgreSQL (padrão) ou SQLite (desenvolvimento/testes)
- Hash de senha: Argon2 (`argon2-cffi`), com PBKDF2 mantido por compatibilidade
- Front-end: templates Django + CSS próprio (tema claro/escuro, responsivo)

## Como executar

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
2. Banco de dados:
   - **SQLite (desenvolvimento/teste, mais simples):** defina `MEDCLIN_DB=sqlite`.
   - **PostgreSQL (padrão):** configure via `MEDCLIN_DB_NAME`, `MEDCLIN_DB_USER`,
     `MEDCLIN_DB_PASSWORD`, `MEDCLIN_DB_HOST`, `MEDCLIN_DB_PORT`.
3. Aplique as migrations:
   ```
   python manage.py migrate
   ```
4. Crie o primeiro Gestor (bootstrap do controle de acesso):
   ```
   python manage.py criar_gestor --nome "Admin" --cpf 529.982.247-25 --email admin@medclin.com --senha senha123
   ```
5. Rode o servidor:
   ```
   python manage.py runserver
   ```

Exemplo completo com SQLite (PowerShell):

```
$env:MEDCLIN_DB="sqlite"
python manage.py migrate
python manage.py runserver
```

> O Gestor logado cadastra os demais funcionários (médicos, enfermeiros, etc.)
> pela tela de Funcionários. **Não** cadastre funcionários pelo admin do Django —
> ele salvaria a senha sem hash e o login falharia.

### Login e redefinição de senha

O acesso é por **e-mail ou CPF** (com ou sem máscara) e senha. A sessão é
gerenciada pelo Django (`request.session`). A página inicial mostra a
apresentação para visitantes e, após o login, vira um painel de atalhos para os
módulos do perfil.

A **redefinição de senha (UC-02)** segue o fluxo por link: em "Esqueci minha
senha" o usuário informa o e-mail e recebe um **link válido por 30 minutos**;
ao abri-lo, define a nova senha e o link deixa de valer (uso único). Não há
tabela de token — usa-se token assinado (`django.core.signing`), mantendo a
aderência ao OR. Em desenvolvimento, o e-mail é impresso no **console** (backend
`console`); em produção, configure SMTP/SES via `MEDCLIN_EMAIL_BACKEND`.

## Testes

Suíte automatizada em `tests/` (login, RBAC, dispensação/consumo de estoque,
prontuário, conflito de horário, auditoria e redefinição de senha):

```
$env:MEDCLIN_DB="sqlite"
python manage.py test tests
```

## Integração contínua (CI)

`/.github/workflows/ci.yml` executa, a cada push/pull request: instalação das
dependências, `manage.py check` e a suíte de testes (com SQLite). Passa a rodar
automaticamente assim que o projeto for versionado no GitHub.

## Segurança e rastreabilidade

- Senhas com **Argon2** (DA-004 do Documento de Arquitetura).
- `SECRET_KEY` lido da variável de ambiente `MEDCLIN_SECRET_KEY` (com fallback
  apenas para desenvolvimento).
- **RBAC** por perfil (ver matriz abaixo) — verificação no backend e ocultação
  de links/botões na interface.
- Operações de estoque usam transação com trava de linha (`select_for_update`),
  evitando baixa concorrente.
- **Auditoria**: ações relevantes são registradas em `logs/auditoria.log` (via
  `logging`). Optou-se por log em arquivo, e **não** por uma tabela, para não
  criar entidade fora do Mapeamento Objeto-Relacional.

## Controle de acesso (RBAC)

| Módulo / ação | Perfis permitidos |
| --- | --- |
| Login / Redefinir senha | Todos (UC-01, UC-02) |
| Cadastro de funcionários | Gestor (UC-08) |
| Pacientes (cadastro/busca) | Recepcionista (UC-06) |
| Agendar consulta | Recepcionista, Paciente (UC-05) |
| Reagendar / cancelar / agendas | Recepcionista (UC-21) |
| Minha agenda (do médico) | Médico (UC-19) |
| Minhas consultas / detalhe | Paciente (UC-03, UC-04) |
| Prontuário (visualizar) | Médico, Enfermeiro, Farmacêutico, Paciente (UC-11) |
| Registrar evolução / conceder acesso / inicializar | Médico (UC-12, UC-18) |
| Verificar acesso ao prontuário | Médico, Enfermeiro, Farmacêutico |
| Estoque (visualizar / verificar) | Enfermeiro, Farmacêutico, Gestor (UC-15, UC-16) |
| Cadastrar item / inserir lote / gerenciar estoque | Gestor (UC-20) |
| Solicitar reposição | Enfermeiro, Farmacêutico (UC-14, UC-17) |
| Dispensar medicamento | Farmacêutico (UC-13) |
| Registrar consumo de material | Enfermeiro |

## Módulos (padrão BCE)

- **acesso** — Recepcionista, Médico, Enfermeiro, Farmacêutico, Gestor;
  login/logout, redefinição de senha e cadastro de funcionários (UC-01, UC-02, UC-08).
- **cadastros** — Paciente; cadastro e busca (UC-06).
- **atendimento** — Agenda e Consulta; agendamento, reagendamento, agenda do
  médico e do paciente, com regra de conflito de horário (UC-04, UC-05, UC-19, UC-21).
- **prontuario** — Prontuário Eletrônico; evolução clínica como addendum e
  acesso autorizado por perfil (UC-11, UC-12, UC-18).
- **farmacia** — Material e Medicamento; dispensação, consumo, verificação e
  gestão de estoque, com registros rastreáveis (UC-13 a UC-17, UC-20).
- **financeiro** — **fora do escopo atual** (ver Pendências).

## Estrutura do projeto

```
MedClin-main/
├── manage.py
├── requirements.txt
├── README.md
├── .github/workflows/ci.yml      # Integração contínua
│
├── meu_projeto/                  # Configuração do projeto Django
│   ├── settings.py
│   ├── urls.py
│   ├── views.py                  # view da página inicial (landing/painel)
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/                         # Módulos de negócio (padrão BCE)
│   ├── acesso/
│   │   ├── boundary_tela_funcionario/   # telas (views/forms)
│   │   ├── control_ctr_funcionario/     # regras de negócio (services)
│   │   ├── entity_funcionario/          # entidades (models)
│   │   ├── decorators.py                # RBAC (@perfis_permitidos)
│   │   ├── context_processors.py        # flags de navegação por perfil
│   │   └── management/commands/criar_gestor.py
│   ├── cadastros/
│   ├── atendimento/
│   ├── prontuario/
│   ├── farmacia/
│   └── financeiro/               # stub (fora do escopo)
│
├── templates/                    # HTML (base, home e por módulo)
├── static/                       # CSS (tema claro/escuro) e JS
│   ├── css/  (variables, base, layout, components, home)
│   └── js/   (app.js — menu e alternância de tema)
│
├── tests/                        # Suíte de testes automatizados
│   ├── helpers.py
│   ├── test_acesso.py
│   ├── test_atendimento.py
│   ├── test_farmacia.py
│   ├── test_prontuario.py
│   ├── test_auditoria.py
│   └── test_redefinicao.py
│
├── logs/                         # auditoria.log (gerado em runtime; no .gitignore)
├── config/  e  core/             # pacotes reservados (placeholders)
├── docs/
├── db.sqlite3                    # banco local (SQLite)
└── db.sql
```

---

## Pendências e incoerências conhecidas

> Seção para a equipe ficar ciente. Compara a aplicação com os documentos
> entregues. **Regra adotada: em caso de conflito, a aplicação segue o OR.**
> Como os documentos já foram entregues, as divergências ficam registradas aqui.

### 1. Fora de escopo (proposital)

- **Módulo Financeiro** (UC-07 Registrar Pagamento, UC-09 Relatório Financeiro,
  UC-10 Status de Pagamentos): o OR **não define entidades financeiras**, então
  o módulo não foi implementado (existe apenas como stub, fora do `INSTALLED_APPS`).

### 2. Arquitetura-alvo × implementação de referência

O Documento de Arquitetura v5 descreve uma arquitetura-alvo que a implementação
acadêmica (monólito Django) não segue. São divergências **conscientes** (ISO
42010 §5.7.1 — inconsistências conhecidas), não bugs:

| Documento (alvo) | Implementação | 
| --- | --- |
| Autenticação **JWT** (DA-002) | Sessão do Django |
| **API REST `/api/v1/`** + OpenAPI (DA-003) | Views renderizando templates (server-side) |
| **Front-end separado** (SPA, Bootstrap/Tailwind) | Templates Django + CSS próprio |
| Subcamada **`repositories.py`** (§9.3/§11.3) | Services usam o ORM diretamente |
| **AES-256-GCM + AWS KMS** em repouso (DA-004) | Apenas hash de senha (Argon2) |
| **AWS** (EC2, RDS, S3, SES, KMS, Secrets, CloudWatch — §12) | Execução local |
| **Upload de arquivos / S3** (DA-005) | Não há upload |

### 3. Incoerências internas dos documentos (app segue o OR)

- **Financeiro como módulo**: aparece no Escopo (§1.2), na Camada de Negócio
  (§7.2.2) e no repositório (§11.2), mas **some** da Visão Lógica (§9.2) e do
  BCE (§8), que listam dois módulos de estoque no lugar.
- **Farmácia**: a app usa **um** módulo (materiais + medicamentos); a Visão
  Lógica/BCE separa em **dois**. O conteúdo (entidades/CTRs) é equivalente.
- **Tabela 18 (BCE Prontuário)** omite `historicoEvolucoes` nos atributos, mas
  ele consta no OR e na §9.2 — a app segue o OR (campo presente).
- **Matriz de Atores (UC-08)** marca todos os perfis para "Cadastrar
  Funcionários", mas a descrição diz "o gestor cadastra" — a app restringe ao
  Gestor (coerente com a descrição).
- **UC-18** tem o texto copiado do UC-12 (erro de redação no documento).

### 4. Pendências funcionais dentro do escopo (opcionais)

- **`Gestor_Material` / `Gestor_Medicamento`**: tabelas existem (fiéis ao OR),
  mas o vínculo de supervisão não é populado no fluxo do gestor (UC-20).
- **Solicitar reposição (UC-14/UC-17)**: apenas registra no log — o OR não define
  tabela de "solicitação de reposição".

> **Resolvido:** UC-02 (Redefinir Senha) agora segue o fluxo por link com
> validade de 30 minutos e uso único (ver "Login e redefinição de senha").
