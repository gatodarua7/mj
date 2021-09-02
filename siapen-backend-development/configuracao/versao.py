from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def get_versao(self):
    versao = dict()
    versao_numero = read_file()
    versao['numero'] = versao_numero
    return Response(versao, status=status.HTTP_200_OK)

def read_file():
 return open('VERSION', 'r').read().strip()