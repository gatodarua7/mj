# Backend do SIAPEN

Repositório referente ao Backend do projeto SIAPEN do Ministério da Justiça e Segurança Pública.

Esse repositório constitui a **API** (_Application Programing Interface_) do sistema, sendo construído:

- Na linguagem de programação **Python**
- Com o _framework_ de desenvolvimento web **Django**; 
- Com o _framework_ para construções de APIs **Django REST Framework**;

## Configuração Inicial

- Crie um arquivo `.env` na raíz do projeto com as seguintes variáveis e preenchas os valores de acordo com o ambiente:

    - `ALLOWED_HOSTS=*`: Uma lista de strings (sem colchetes e sem aspas/apóstrofos) que representam os nomes de hosts/domínios que o sistema pode servir (exemplo de lista: `ALLOWED_HOSTS=hml.siapen.depen.gov.br,tst.siapen.depen.gov.br`).
    - `DEBUG=True|False`: Seta o modo `DEBUG` do Django (`True` ou `False`). 
    - `SECRET_KEY=''`: Variável de segurança do Django (usar valores aleatórios).
    - `JWT_KEY=''`: Chave de segurança JWT.
    - `DB_NAME=''`: Nome do `database` no PostgreSQL.
    - `DB_USER=''`: Usuário de acesso ao banco de dados PostgreSQL.
    - `DB_PASS=''`: Senha de acesso ao banco de dados PostgreSQL.
    - `DB_HOST=''`: IP onde o servidor do PostgreSQL está executando (não é necessário informar porta caso se esteja utilizando a porta padrão, 5432, do PostgreSQL).
    - `TOKEN_LIFETIME=''`: Defina o tempo em horas para expirar o TOKEN de acesso.
    - `REFRESH_TOKEN_LIFETIME=''`: Defina o tempo em horas para refresh do TOKEN de acesso.
    - `BASE_URL=''`: Domínio de local onde será executado o backend. Ex.:`http://localhost:8000`
    - `BASE_URL_FRONT=''`: Domínio de local onde será executado o frontend. Ex.:`http://localhost:8080`
- Acesse o banco de dados (ou requisite o DBA) e instale a extensão UNACCENT no banco de dados com `CREATE EXTENSION UNACCENT` ([documentação](https://www.postgresql.org/docs/9.1/unaccent.html)).

## Ambiente de Desenvolvimento

1) Certifique-se que o Python instalado em sua máquina seja, no mínimo, a versão 3.7 com `python --version`.
2) Instale o `virtualenv` com o comando `pip install virtualenv` (tutorial: [link](https://pythonacademy.com.br/blog/python-e-virtualenv-como-programar-em-ambientes-virtuais)).
3) Acesse a raíz do projeto (diretório `backend`).
4) Crie um ambiente virtual com `virtualenv venv` e o ative com `source venv/bin/activate`.
5) Instale as dependências do projeto com `pip install -r requirements.txt`
6) Na pasta raiz do projeto execute o comando com permissão de execução `./scripts/recria_db.sh` para criar a estrutura da base de dados.
7) Na pasta raiz do projeto execute o comando com permissão de execução `./scripts/carga.sh` para importar a massa de dados inicial.
8) Execute o backend com o comando `python manage.py runserver` (com isso, o servidor de desenvolvimento Django será executado na porta 8000).

**Obs**: As credenciais de acesso ao ambiente como superusuário já foi gerado pelo script, no entanto pode ser gerado outro com o comando `python manage.py createsuperuser`

## Ambiente Docker

1) Certifique-se que o Docker está instalado.
2) Alterar na variável de ambiente o valor `DB_HOST` para `<nome-container-database>`.
3) Execute na raiz do projeto `docker-compose up --build -d` para subir o projeto.
4) Para criar a estrutura básica do banco execute o comando `docker exec -it <nome-container-database> sh /opt/recria_db_docker.sh`
5) Para importar a massa inicial dos dados execute o comando `docker exec -it <nome-container-django> sh /usr/src/app/scripts/carga.sh`

**Obs**: As credenciais de acesso ao ambiente como superusuário já foi gerado pelo script, no entanto pode ser gerado outro com o comando `docker exec -it <nome-container-django> python manage.py createsuperuser`
## Testes

Para executar os testes funcionais do Backend do SIAPEN, é necessário:

1) Iniciar o servidor do Django.
2) Executar o script `sh scripts/testes_siapen.sh`, caso precise executar o teste de 1 app específico, o mesmo deve ser passado como parâmetro, como por exemplo: `sh scripts/testes_siapen.sh prisional`. Caso deseje executar um teste específico basta executar `sh scripts/testes_siapen.sh <app> <nome-teste>`, como por exemplo `sh scripts/testes_siapen.sh prisional faccao`
