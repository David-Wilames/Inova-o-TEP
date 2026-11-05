# Inovação e Tecnologia na Educação Pública

Sistema web desenvolvido como trabalho em grupo para aproximar
professores e instituições de ensino, facilitando a divulgação
e a consulta de oportunidades de aulas e horas de trabalho.

## Objetivo

Centralizar informações profissionais dos professores e oportunidades
das instituições de ensino, auxiliando na comunicação entre essas partes.

O sistema não realiza pagamentos. Essa responsabilidade permanece
com o ente público responsável pela contratação.

## Funcionalidades

### Professores

- Cadastro e login com nome de usuário ou e-mail.
- Preenchimento de dados pessoais, contato e endereço.
- Registro de documentos, formação, disciplinas e disponibilidade.
- Uso opcional do nome social.
- Controle da visibilidade do perfil para as instituições.
- Consulta de oportunidades e manifestação de interesse.

### Instituições de ensino

- Cadastro de informações sobre oportunidades.
- Consulta dos registros de uma instituição.
- Exclusão de registros mediante confirmação e verificação de acesso.
- Consulta de perfis de professores.
- Recebimento de notificações de interesse nas oportunidades.

### Formulários

- Mensagens de validação nos campos obrigatórios do cadastro de professor, de informações do colaborador e de cadastro de oportunidades da instituição.
- Destaque visual dos campos com preenchimento inválido nesses formulários.

## Tecnologias utilizadas

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript

## Situação do projeto

Projeto acadêmico desenvolvido em grupo.
As funcionalidades e a estrutura podem ser atualizadas ao longo do desenvolvimento.

## Equipe do desenvolvimento do projeto

- Daniel Gomes da Silva, RA: 23217452;
- David Wilames Nunes Batista, RA: 23217049;
- Miguel Silva de Arruda, RA: 24203315;
- Thaise Michelaine Nunes de Oliveira, RA: 24219760;
- Semaías Francisco Xavier, RA: 24224069.

## Como executar o projeto

As instruções abaixo utilizam o PowerShell no Windows.

### Pré-requisitos

- Python 3.14 instalado.
- Git instalado para clonar pelo terminal, ou GitHub Desktop.
- Acesso à pasta do projeto.

### 1. Baixar o projeto

Clone o repositório pelo GitHub Desktop ou execute:

```powershell
git clone https://github.com/David-Wilames/Inova-o-TEP.git
cd Inova-o-TEP
```

Se já baixou pelo GitHub Desktop, abra um terminal na pasta do projeto.

### 2. Criar um ambiente virtual

```powershell
py -3.14 -m venv .venv
```

### 3. Instalar as dependências

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
### 4. Configurar a chave secreta

O projeto lê a variável de ambiente `SECRET_KEY`.
No PowerShell, execute:

```powershell
$env:SECRET_KEY = & .\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Esse comando gera uma chave aleatória para o ambiente local.
A variável fica disponível somente na sessão atual do terminal.

Execute os próximos comandos nesse mesmo terminal.
Se ele for fechado, configure a variável novamente.

O arquivo `.env` não é carregado automaticamente pela configuração
atual do projeto. Não publique chaves secretas no repositório.

### 5. Preparar o banco de dados

O projeto utiliza SQLite, no arquivo `db.sqlite3`, localizado
na pasta principal.

A configuração atual depende de tabelas preexistentes nesse banco.
As migrações ainda não criam toda a estrutura a partir de um banco vazio.
Utilize uma cópia de desenvolvimento disponibilizada pela equipe.

Antes de atualizar um banco que contém dados importantes,
pare o servidor e faça uma cópia de segurança do arquivo.

Com o banco de desenvolvimento disponível, aplique as migrações:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

Se ocorrer algum erro, confira a versão do banco e as orientações
da equipe antes de modificar ou excluir tabelas.

### 6. Iniciar o servidor

No mesmo terminal em que configurou a chave secreta, execute:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload
```

Mantenha o terminal aberto enquanto utiliza o sistema.

Abra o Google Chrome ou outro navegador e acesse:

http://127.0.0.1:8000/

Para parar o servidor, pressione `Ctrl + C` no terminal.

Como o comando utiliza `--noreload`, reinicie o servidor após
alterações no código Python ou nos templates HTML.
Para atualizar os arquivos CSS e JavaScript no navegador,
utilize `Ctrl + F5`.

Esse servidor é destinado ao desenvolvimento local.
A publicação na internet exige uma configuração própria de produção.

## Problemas comuns

### O comando não encontra o arquivo manage.py

Confira se o terminal está na pasta principal do projeto,
onde ficam `manage.py` e `requirements.txt`.

Se estiver em outra pasta, use `cd` para acessar a pasta
do Inova-o-TEP antes de iniciar o servidor.

### O navegador mostra conexão recusada

Confira se o servidor Django está rodando no terminal.
Mantenha esse terminal aberto e acesse:

http://127.0.0.1:8000/

Se o servidor encerrar ou apresentar erro, verifique a mensagem
no terminal antes de tentar novamente.
