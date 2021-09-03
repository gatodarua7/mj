
#!/bin/sh
# Realiza o setup do projeto
python manage.py makemigrations cadastros comum juridico localizacao movimentacao orcrim prisional social vinculos
python manage.py migrate


echo "Efetuando a carga de dados..."
echo "USUÁRIOS"
python manage.py loaddata fixtures/usuarios/usuario.json
echo "PAÍSES"
python manage.py loaddata fixtures/localizacao/paises.json
echo "ESTADOS"
python manage.py loaddata fixtures/localizacao/estados.json
echo "MUNICIPIOS"
python manage.py loaddata fixtures/localizacao/municipios.json
echo "SOCIAL"
python manage.py loaddata fixtures/social/orientacao_sexual.json
python manage.py loaddata fixtures/social/estado_civil.json
python manage.py loaddata fixtures/social/grau_instrucao.json
python manage.py loaddata fixtures/social/necessidade_especial.json
python manage.py loaddata fixtures/social/profissao.json
python manage.py loaddata fixtures/social/raca.json
python manage.py loaddata fixtures/social/religiao.json
echo "COMUM"
python manage.py loaddata fixtures/comum/telefone.json
python manage.py loaddata fixtures/comum/endereco.json
echo "CADASTROS"
python manage.py loaddata fixtures/cadastro/orgao_expedidor.json
python manage.py loaddata fixtures/cadastro/periculosidade.json
python manage.py loaddata fixtures/cadastro/regime_prisional.json
python manage.py loaddata fixtures/cadastro/genero.json
python manage.py loaddata fixtures/cadastro/cargo.json
python manage.py loaddata fixtures/cadastro/funcao.json
python manage.py loaddata fixtures/cadastro/foto.json
python manage.py loaddata fixtures/cadastro/setor.json
python manage.py loaddata fixtures/cadastro/tipo_documento.json
python manage.py loaddata fixtures/cadastro/pessoa.json
python manage.py loaddata fixtures/cadastro/comportamento_interno.json
echo "ORCRIM"
python manage.py loaddata fixtures/orcrim/faccao.json
python manage.py loaddata fixtures/orcrim/pessoa_faccao.json
echo "PRISIONAL"
python manage.py loaddata fixtures/prisional/sistema.json
python manage.py loaddata fixtures/prisional/unidade.json
python manage.py loaddata fixtures/prisional/bloco.json
python manage.py loaddata fixtures/prisional/cela.json
echo "VÍNCULOS"
python manage.py loaddata fixtures/vinculos/tipo_vinculo.json
echo "JURÍDICO"
python manage.py loaddata fixtures/juridico/titulo-lei.json
python manage.py loaddata fixtures/juridico/normas-juridicas.json
echo "PESSOAS"
python manage.py loaddata fixtures/pessoas/interno.json
python manage.py loaddata fixtures/pessoas/servidor.json
python manage.py loaddata fixtures/pessoas/advogado.json
python manage.py loaddata fixtures/pessoas/rg.json
python manage.py loaddata fixtures/pessoas/visitante.json
echo "MOVIMENTACAO"
python manage.py loaddata fixtures/movimentacao/fases.json
python manage.py loaddata fixtures/movimentacao/pedido-inclusao.json
python manage.py loaddata fixtures/movimentacao/pedido-movimentacao.json
echo "Processo finalizado"
