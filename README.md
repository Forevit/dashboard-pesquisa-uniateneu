# 📊 Análise de Satisfação de Alunos — UniAteneu

Dashboard interativo em Python/Streamlit para análise de pesquisas de satisfação de alunos do EAD.  
Desenvolvido como **Projeto de Extensão Curricular** da disciplina *Inovação Tecnológica Aplicada ao Mercado* — UniAteneu 2025.1.1.

---

## 🖥️ Demonstração

O dashboard exibe:

- **KPIs gerais** — alunos únicos, questionários respondidos, % satisfação, % insatisfação e NPS educacional
- **Distribuição geral** — gráfico de rosca com os 6 níveis da escala de satisfação
- **Top 10 disciplinas** — ranking por índice de satisfação
- **Satisfação por dimensão** — as 17 perguntas avaliadas ranqueadas
- **Evolução temporal** — volume de respostas por dia
- **Pontos críticos** — dimensões com maior índice de insatisfação
- **Heatmap** — cruzamento entre dimensão e nível de satisfação
- **Tabela exportável** — dados filtrados com download em CSV

Todos os gráficos respondem aos filtros de semestre, disciplina e dimensão avaliada na sidebar.

---

## 🗂️ Estrutura do projeto

```
analise-satisfacao-alunos/
├── Analise.py          # Script principal do dashboard
├── baseTratada.csv     # Base de dados tratada (não versionada — ver abaixo)
└── README.md
```

> ⚠️ O arquivo `baseTratada.csv` contém dados pessoais de alunos e **não deve ser versionado**. Adicione-o ao `.gitignore`.

---

## ⚙️ Requisitos

- Python 3.9+
- pip

### Dependências

```bash
pip install streamlit plotly pandas
```

---

## 🚀 Como executar

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/analise-satisfacao-alunos.git
cd analise-satisfacao-alunos
```

2. Instale as dependências:

```bash
pip install streamlit plotly pandas
```

3. Coloque o arquivo `baseTratada.csv` na raiz do projeto.

4. Execute o dashboard:

```bash
streamlit run Analise.py
```

5. Acesse no navegador: `http://localhost:8501`

---

## 📁 Formato esperado do CSV

O arquivo `baseTratada.csv` deve usar **ponto e vírgula (`;`)** como separador e conter as seguintes colunas:

| Coluna | Descrição |
|---|---|
| `SEMESTRE` | Semestre letivo (ex: `2025.1.1`) |
| `NOME` | Nome do aluno |
| `RA` | Registro acadêmico |
| `DISCIPLINA` | Nome da disciplina |
| `NOME_PESQUISA` | Nome da pesquisa aplicada |
| `ITEM_TIPO` | Tipo da questão (`multichoice`) |
| `VALOR_ID` | ID único da resposta |
| `VALOR_SELECIONADO` | Resposta selecionada pelo aluno |
| `PESQUISA_COMPLETADO_ID` | ID do questionário respondido |
| `PESQUISA_COMPLETADO_DATA_MODIFICACAO` | Data e hora da submissão |

### Escala de resposta

As respostas válidas para as 17 perguntas de satisfação são:

- Muito satisfeito
- Satisfeito
- Parcialmente satisfeito
- Insatisfeito
- Muito insatisfeito
- Não sei avaliar

### Ordem das 17 perguntas (por questionário)

O script identifica as perguntas pela **posição sequencial** dentro de cada questionário, na seguinte ordem:

1. Participação nas atividades a distância (calendário)
2. Participação nas atividades propostas (fóruns/chat)
3. Utilização do material didático
4. Comunicação e interação com colegas e tutor
5. Qualidade do material didático e-book
6. Qualidade do material didático digital (scorm)
7. Qualidade do material didático digital (videoaula)
8. Linguagem clara e objetiva do conteúdo
9. Conformidade das atividades com o material
10. Organização da Sala Virtual (AVA)
11. Didática e domínio do professor na aula ao vivo
12. Atendimento da tutoria
13. Cumprimento do cronograma de correção pelo tutor
14. Clareza do feedback do tutor
15. Domínio do tutor sobre o conteúdo
16. Esclarecimento de dúvidas pela tutoria
17. Atendimento presencial

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Uso |
|---|---|
| [Python](https://www.python.org/) | Linguagem principal |
| [Streamlit](https://streamlit.io/) | Interface web interativa |
| [Plotly](https://plotly.com/python/) | Visualizações gráficas |
| [Pandas](https://pandas.pydata.org/) | Manipulação e análise dos dados |

---

## 📋 Sobre o projeto de extensão

Este projeto foi desenvolvido no contexto do projeto de extensão **"Inovação Tecnológica Aplicada: Soluções Práticas para o Mercado"** da UniAteneu, orientado pelo Prof. Esp. Bruno Jeronimo Pereira.

A solução se enquadra na vertente de **Análise e Ciência de Dados**, aplicando técnicas de visualização de dados a um problema real da instituição: compreender os níveis de satisfação dos alunos com as disciplinas EAD ao longo do semestre.

**Carga horária:** 60h (Prestação de serviço 30h + Produção intelectual 20h + Evento científico 10h)

---

## 👤 Autores

**Carlos Eduardo Rodrigues Ferreira**  
Engenharia da Computação — 6º semestre · UniAteneu  
Técnico de Suporte de TI · Paerro Tecnologia

**Matheus de Sousa da Silva**
Analise e Desenvolvimento de Sistemas · UniAteneu
Assistente de Ambiente Virtual · UniAteneu

**Caio de Freitas Brandão**
Engenharia da Computação - 6º semestre · UniAnteneu

