

def diretorio_upload(instance, arquivo):

    if type(instance).__name__ == 'FotoPessoa':
        return 'fotos/{0}/{1}'.format(instance.pessoa.id, arquivo)

    elif type(instance).__name__ == 'CaracteristicaFisica':
        return 'caracteristicas/{0}/{1}'.format(instance.pessoa.id, arquivo)

    elif type(instance).__name__ == 'DocumentoMovimentacaoExterna':
        return 'documentoMovimentacaoExterna/{0}/{1}'.format(instance.pessoa.id, arquivo)
