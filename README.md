# API de Consulta de Ações e Mercado Financeiro 📈

![Versão](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue?logo=python)
![Framework](https://img.shields.io/badge/framework-FastAPI-green?logo=fastapi)
![Licença](https://img.shields.io/badge/license-MIT-green)

Uma API completa e de alta performance construída em Python com FastAPI para consulta de dados de ações, índices e eventos do mercado financeiro brasileiro. O projeto inclui um web scraper para coleta de dados, um agendador de tarefas, e uma interface gráfica em Tkinter para interação e gerenciamento.

---

## ✨ Funcionalidades Principais

A API foi projetada para ser robusta e atender a uma variedade de requisitos de negócio:

* **Consultas de Ações:** Busca de dados de ações por ticker (individual ou múltiplos).
* **Dados Históricos:** Fornece dados formatados para a criação de gráficos de linha de preços.
* **Gráficos Comparativos:** Endpoint para comparar a performance normalizada de todas as ações cadastradas.
* **Eventos Corporativos:** Consulta de dividendos, JCPs, e outros eventos de um ticker.
* **Índices do Mercado:** Retorna os valores dos principais índices como IBOV e IFIX.
* **CRUD de Tickers e Usuários:** Gerenciamento completo (Criar, Ler, Atualizar, Deletar) para tickers e usuários.
* **Segurança:** Autenticação via Chave de API e Rate Limiting para prevenir abuso.
* **Coleta de Dados:** Inclui um web scraper para popular o banco de dados com informações do site Status Invest.
* **Automação:** Possui um agendador para executar a coleta de dados automaticamente.
* **Logging:** Registra todas as requisições na API e os eventos de coleta de dados no banco de dados.
* **Interface Gráfica:** Acompanha um painel de controle construído em Tkinter para interagir com todas as funcionalidades da API.

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias e bibliotecas:

* **Backend:** Python 3.9+, FastAPI
* **Banco de Dados:** PostgreSQL
* **ORM:** SQLAlchemy
* **Validação de Dados:** Pydantic
* **Web Scraping:** Requests, BeautifulSoup4
* **Manipulação de Dados:** Pandas
* **Agendamento de Tarefas:** Schedule
* **Interface Gráfica:** Tkinter (ttk)
* **Gráficos:** Matplotlib

## 📂 Estrutura do Projeto

O projeto segue uma arquitetura limpa, separando as responsabilidades em diferentes camadas:
