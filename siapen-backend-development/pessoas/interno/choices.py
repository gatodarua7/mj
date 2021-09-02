from dataclasses import dataclass, asdict

@dataclass
class Cutis:
    BRANCA: str = 'Branca'
    AMARELA: str = 'Amarela'
    PARDA: str = 'Parda'
    PRETA: str = 'Preta'

@dataclass
class CorCabelo:
    PRETO: str = 'Preto'
    CASTANHO: str = 'Castanho'
    RUIVO: str = 'Ruivo'
    LOIRO: str = 'Loiro'
    GRISALHO: str = 'Grisalho'
    BRANCO: str = 'Branco'

@dataclass
class TipoCabelo:
    LISO: str = 'Liso'
    CRESPO: str = 'Crespo'
    ONDULADO: str = 'Ondulado'
    CARAPINHA: str = 'Carapinha'

@dataclass
class TipoRosto:
    ACHATADO: str = 'Achatado'
    COMPRIDO: str = 'Comprido'
    OVALADO: str = 'Ovalado'
    QUADRADO: str = 'Quadrado'
    REDONDO: str = 'Redondo'

@dataclass
class TipoTesta:
    ALTA: str = 'Alta'
    COM_ENTRADAS: str = 'Com entradas'
    CURTA: str = 'Curta'

@dataclass
class Sobrancelhas:
    APARADAS: str = 'Aparadas'
    FINAS: str = 'Finas'
    GROSSAS: str = 'Grossas'
    PINTADAS: str = 'Pintadas'
    SEPARADAS: str = 'Separadas'
    UNIDAS: str = 'Unidas'

@dataclass
class TipoOlhos:
    FUNDOS: str = 'Fundos'
    GRANDES: str = 'Grandes'
    ORIENTAIS: str = 'Orientais'
    PEQUENOS: str = 'Pequenos'
    SALTADOS: str = 'Saltados'

@dataclass
class CorOlhos:
    PRETOS: str = 'Pretos'
    CASTANHO: str = 'Castanho'
    AZUIS: str = 'Azuis'
    VERDES: str = 'Verdes'
    DUAS_CORES: str = 'Duas cores'
    INDEFINIDOS_CLAROS: str = 'Indefinidos claros'
    INDEFINIDOS_ESCUROS: str = 'Indefinidos escuros'

@dataclass
class Nariz:
    ACHATADO: str = 'Achatado'
    ADUNCO: str = 'Adunco'
    AFILADO: str = 'Afilado'
    ARREBITADO: str = 'Arrebitado'
    GRANDE: str = 'Grande'
    MEDIO: str = 'Médio'
    PEQUENO: str = 'Pequeno'

@dataclass
class Orelhas:
    GRANDES: str = 'Grandes'
    MEDIAS: str = 'Médias'
    PEQUENAS: str = 'Pequenas'
    LOBULOS_FECHADOS: str = 'Lóbulos fechados'
    LOBULOS_ABERTOS: str = ' Lóbulos abertos'

@dataclass
class Labios:
    FINOS: str = 'Finos'
    MEDIOS: str = 'Médios'
    GROSSOS: str = 'Grossos'
    LEPORINOS: str = 'Leporinos'

@dataclass
class Compleicao:
    GORDA: str = 'Gorda'
    MEDIA: str = 'Média'
    MAGRA: str = 'Magra'
    MUSCULOSA: str = 'Musculosa'
    RAQUITICA: str = 'Raquítica'

@dataclass
class Caracteristicas:
    cutis: Cutis = Cutis()
    cor_cabelo: CorCabelo = CorCabelo()
    tipo_cabelo: TipoCabelo = TipoCabelo()
    tipo_rosto: TipoRosto = TipoRosto()
    tipo_testa: TipoTesta = TipoTesta()
    sobrancelhas: Sobrancelhas = Sobrancelhas()
    tipo_olhos: TipoOlhos = TipoOlhos()
    cor_olhos: CorOlhos = CorOlhos()
    nariz: Nariz = Nariz()
    orelhas: Orelhas = Orelhas()
    labios: Labios = Labios()
    compleicao: Compleicao = Compleicao()

CARACTERISTICAS_DICT = asdict(Caracteristicas())