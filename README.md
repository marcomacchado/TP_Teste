# Trabalho Prático - Teste de Software 2025/2
Trabalho Prático final para a disciplina de Teste de Software

## Membros do grupo:
- Gabriel Henrique Gonçalves Santos
- Marco Antônio de Alcântara Machado

## Explicação do sistema:
O sistema consiste em um gerenciador de tarefas web desenvolvido em Python com o framework Flask. Ele oferece uma interface RESTful para realizar operações de criação, leitura, atualização e exclusão (CRUD) de tarefas, além de permitir o gerenciamento de categorias e prazos.

## Tecnologias utilizadas:
- **Python:** Linguagem de programação.
- **Flask:** Microframework web para Python.
- **Flask-SQLAlchemy:** Extensão do Flask para integração com o SQLAlchemy (ORM - Object-Relational Mapper), permitindo a interação com bancos de dados relacionais.
- **SQLite:** Banco de dados relacional leve utilizado para desenvolvimento e testes.
- **pytest:** Framework para testes em Python.
- **GitHub Actions:** Plataforma de CI/CD para automação de testes e outros processos.

### Como Usar
1. Clone o repositório.
2. Instale as dependências
2. Instale as dependências

    ```
    python3 -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. Configurar arquivo '.env' com as seguintes configurações
    ```
    FLASK_ENV=development
    SECRET_KEY=uma_chave_segura_aleatória
    ```

4. Executar

    ```
    python run.py
    ```

### Como Testar Localmente
1. Com os requrimentos necessários (requeriments.txt) instalados, execute:

    ```
    pytest
    ```