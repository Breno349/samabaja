<<<<<<< HEAD
# samabaja
Repositório exclusivo para o site do samabaja!
=======
# Site Samabaja IFES SM

Este é um aplicativo web Flask desenvolvido para a equipe Samabaja do IFES Campus São Mateus. Ele inclui:

*   Página inicial e página sobre a história da equipe.
*   Sistema de autenticação de usuários com diferentes níveis de acesso (Gestão, Gerente, Membro, Pendente).
*   Sistema de ponto eletrônico para registro de horas de trabalho.
*   Sistema de ordens de serviço para gerenciamento de tarefas.
*   Sistema de organização de documentos (similar ao Notion) com suporte a Markdown.
*   Painel administrativo para gerenciamento de usuários.

## Requisitos

*   Python 3.11+
*   MySQL (ou outro banco de dados compatível com SQLAlchemy, com ajustes na URI de conexão)
*   Dependências listadas em `requirements.txt`

## Configuração

1.  **Clone o repositório ou extraia o arquivo zip.**
2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate  # Windows
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure o Banco de Dados:**
    *   Certifique-se de que um servidor MySQL esteja rodando.
    *   Crie um banco de dados (por exemplo, `samabaja_db`).
    *   Configure as variáveis de ambiente para a conexão com o banco de dados (ou modifique a string de conexão diretamente em `src/main.py` - não recomendado para produção):
        *   `DB_USERNAME`: Nome de usuário do banco de dados (padrão: `root`)
        *   `DB_PASSWORD`: Senha do banco de dados (padrão: `password`)
        *   `DB_HOST`: Host do banco de dados (padrão: `localhost`)
        *   `DB_PORT`: Porta do banco de dados (padrão: `3306`)
        *   `DB_NAME`: Nome do banco de dados (padrão: `mydb`)
    *   Configure uma chave secreta para o Flask (importante para segurança):
        *   `SECRET_KEY`: Uma string longa e aleatória.

5.  **Crie as tabelas do banco de dados e o usuário administrador inicial:**
    *   Execute o script `create_admin.py`:
        ```bash
        python create_admin.py 
        ```
    *   Isso irá apagar e recriar todas as tabelas e criar um usuário `admin` com senha `adminpassword`.

## Executando a Aplicação

1.  **Defina a variável de ambiente FLASK_APP:**
    ```bash
    export FLASK_APP=src/main:app  # Linux/macOS
    # set FLASK_APP=src/main:app  # Windows
    ```
2.  **Execute o servidor de desenvolvimento Flask:**
    ```bash
    flask run --host=0.0.0.0 --port=5000
    ```
3.  Acesse a aplicação em `http://localhost:5000` (ou o IP da sua máquina na porta 5000).

## Funcionalidades Principais

*   **Registro:** Novos usuários podem se registrar, mas precisam ser aprovados por um administrador (Gestão).
*   **Login:** Usuários aprovados podem fazer login.
*   **Ponto Eletrônico:** Registrar entrada e saída, visualizar histórico recente.
*   **Ordens de Serviço:** Criar novas ordens, visualizar ordens (Gestão vê todas, outros veem as do seu setor).
*   **Documentos:** Criar, visualizar, editar e listar documentos internos usando Markdown.
*   **Admin:** Gerenciar usuários (aprovar, definir cargo/setor, ativar/desativar).

## Próximos Passos / Melhorias

*   Implementar funcionalidade de "Registrar ocorrência" no ponto.
*   Adicionar edição e atualização de status para Ordens de Serviço.
*   Implementar exclusão de documentos.
*   Adicionar paginação para listas longas (usuários, ordens, documentos).
*   Melhorar o design e a interface do usuário (CSS, JavaScript).
*   Implementar testes automatizados.
*   Usar Flask-Migrate para gerenciar migrações de banco de dados em vez de `db.drop_all()`/`db.create_all()`.
*   Configurar um servidor WSGI (como Gunicorn ou Waitress) para produção.

>>>>>>> b9a5c7b (primeiro git para adicionar as paradas)
