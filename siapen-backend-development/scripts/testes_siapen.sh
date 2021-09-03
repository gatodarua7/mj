 #!/bin/bash
# Script para rodar os testes
echo "RECRIANDO A BASE DE TESTES..."
sh scripts/recria_db.sh
echo ""

echo "EFETUANDO A CARGA DOS DADOS..."
sh scripts/carga.sh
echo ""

# Popula banco com fixtures e roda aplicação
echo "RODANDO SERVIDOR DE TESTES..."

if [ "$2" ]; then
    python manage.py test $1.tests.test_$2
elif [ "$1" ]; then
    python manage.py test $1
else
    python manage.py test
fi
