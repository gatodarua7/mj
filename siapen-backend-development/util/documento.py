from cadastros.models import Documentos
from mj_crypt.mj_crypt import AESCipher
import base64
import io as BytesIO


def documento(obj):
    crypt = AESCipher()
    doc = Documentos.objects.get(id=obj, excluido=False)
    arquivo = crypt.decrypt(doc.arquivo)
    return arquivo
