# PROPLAN-TOOLS - Biblioteca do Sistema de Dados: CODEINFO - UFPB
<!-- Desenvolvido por: Sullivan Lima - Versão 1.0 - Mês: Outubro Ano: 2025 -->


PROPLAN-TOOLS - Biblioteca do Sistema de Dados: CODEINFO - UFPB é uma biblioteca criada com forma modular e desenvolvida utilizando tecnologias e linguagens de progragramação como: python, typescript, javascript, bibliotecas react, frameworks Next JS e Flask. Tem como objetivo **unificar e padronizar os processos de engenharia, análise, tratamento, visualização e trabalho com dados institucionais da Universidade Federal da Paraíba, oferecendo componentes reutilizáveis para Extrair, Transformar e Carregar dados (ETL/ELT), realizar integração com **bancos de dados relacionais e/ou não relacionais, dar suporte suporte a visualização de dados nas operações de frontend**, bem como na visualização de dados ou quaisquer outros trabalhos que tenham como foco a manipulação de dados para gerações de informações para tomadas de decisões, ou ainda, na geração de conhecimento institucional orientado por evidências e avaliação de políticas públicas. 

A premissa e foco do projeto foi estruturado na *reutilização, escalabilidade e clareza arquitetural*, utilizando as boas práticas do desenvolvimento, podendo ser aplicado em múltiplos datalakes, datawarehouses, pipelines de dados ou demais aplicações analíticas.

---

## 🎯 *Escopo do Projeto*

A biblioteca foi criada com o objetivo de *servir como base unificada* para diferentes projetos de dados e/ou aplicações na PROPLAN da Universidade Federal da Paraíba.

Seu escopo abrange:

### 1. *Uso na Camada de Banco de Dados (database/)*

> Neste conjunto utilizaremos classes e funções para conexão, leitura para realizar consultas, aplicar atualizações, realizar escritas e operações de deletar ou criar índices para consultas otimizadas dos dados em diferentes bancos de dados.

- Teremos Suporte a bancos *relacionais* como, por exemplo (MySQL, PostgreSQL, SQL Server, Oracle);
- Teremos Suporte a bancos *não relacionais* (MongoDB);
- Faremos Escrita e leitura padronizada usando *fábricas de conexão*;
- Teremos Classes genéricas e extensíveis por exemplo (BaseWriter, BaseReader).

---

### 2. *Uso na Camada ETL (etl/)*
> Neste Conjunto de módulos utilizaremos o necessário para extração, transformação e carregamento de dados de diversas fontes.

- Realizar Extração Oriundas de *e-mails e outras fontes trabalhando com arquivos CSVs, JSONs, XML entre outros*;
- Realizar Transformações genéricas (limpeza, normalização, enriquecimento);
- Realizar Carregamento para *bancos, datalakes e sistemas de destino*;
- Proporcinoar Estrutura compatível com orquestradores (Airflow, Github Actions).

---

### 3. *Uso na Camada Frontend (frontend/)*
> Aqui teremos módulos de apoio à camada de visualização e integração com frontends e APIs para partes textuais, gráficos etc.

- Padronização de Formatação e apresentação de valores (datas, moedas, textos);
- Possibilidade de conversões e serializações (DataFrame → JSON);
- Integração com APIs REST e dashboards.

---

### 4. *Uso Camada Utilitária (utils/)*
> Teremos funções de apoio e infraestrutura reutilizáveis em todos os módulos.

- Gerenciamento de configurações via .env (Config);
- Registro de logs e auditoria (Logger);
- Funções de validação e utilitários diversos;
- Outras funções não especificas que estejam inseridas no ETL, Databases ou Frontend;

---

## 🧩 *Forma da Arquitetura Modular*

A forma que essa biblioteca foi pensada segue o princípio *"Separar, mas conectar"* — cada módulo possui responsabilidade única, mas se integra de forma padronizada, de modo a minimizar os aparecimentos de bugs, facilitar a manutenabilidade do código e escalar para possíveis melhorias futuras que forem acrescentadas ao código.

=======
