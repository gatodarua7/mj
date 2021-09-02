from mj_crypt.mj_crypt import AESCipher
from cadastros.models import Foto


def get_thumbnail(foto_id=None):
    thumbnail = None
    crypt = AESCipher()

    if foto_id:
        foto = Foto.objects.get(id=foto_id)
        if foto:
            thumbnail = crypt.decrypt(foto.thumbnail)
    return thumbnail