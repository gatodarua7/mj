# Generated by Django 3.1.5 on 2021-04-29 21:41

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cadastros', '0003_auto_20210428_1656'),
        ('localizacao', '0001_initial'),
        ('social', '0001_initial'),
        ('comum', '0001_initial'),
        ('vinculos', '0002_remove_vinculo_vinculo'),
        ('pessoas', '0003_auto_20210417_1146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interno',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ativo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('delete_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('excluido', models.BooleanField(default=False)),
                ('nome', models.CharField(max_length=150)),
                ('nome_social', models.CharField(blank=True, max_length=150, null=True)),
                ('cpf', models.CharField(max_length=14, validators=[django.core.validators.RegexValidator(message='CPF inválido', regex='[0-9]{3}\\.?[0-9]{3}\\.?[0-9]{3}\\-?[0-9]{2}')])),
                ('nome_mae', models.CharField(blank=True, max_length=150, null=True)),
                ('nome_pai', models.CharField(blank=True, max_length=150, null=True)),
                ('mae_falecido', models.BooleanField(default=False)),
                ('mae_nao_declarado', models.BooleanField(default=False)),
                ('pai_falecido', models.BooleanField(default=False)),
                ('pai_nao_declarado', models.BooleanField(default=False)),
                ('caracteristicas_cutis', models.CharField(choices=[('BRANCA', 'Branca'), ('AMARELA', 'Amarela'), ('PARDA', 'Parda'), ('PRETA', 'Preta')], max_length=20)),
                ('caracteristicas_cor_cabelo', models.CharField(choices=[('PRETO', 'Preto'), ('CASTANHO', 'Castanho'), ('RUIVO', 'Ruivo'), ('LOIRO', 'Loiro'), ('GRISALHO', 'Grisalho'), ('BRANCO', 'Branco')], max_length=20)),
                ('caracteristicas_tipo_cabelo', models.CharField(choices=[('LISO', 'Liso'), ('CRESPO', 'Crespo'), ('ONDULADO', 'Ondulado'), ('CARAPINHA', 'Carapinha')], max_length=20)),
                ('caracteristicas_tipo_rosto', models.CharField(choices=[('ACHATADO', 'Achatado'), ('COMPRIDO', 'Comprido'), ('OVALADO', 'Ovalado'), ('QUADRADO', 'Quadrado'), ('REDONDO', 'Redondo')], max_length=20)),
                ('caracteristicas_tipo_testa', models.CharField(choices=[('ALTA', 'Alta'), ('COM_ENTRADAS', 'Com entradas'), ('CURTA', 'Curta')], max_length=20)),
                ('caracteristicas_tipo_olhos', models.CharField(choices=[('FUNDOS', 'Fundos'), ('GRANDES', 'Grandes'), ('ORIENTAIS', 'Orientais'), ('PEQUENOS', 'Pequenos'), ('SALTADOS', 'Saltados')], max_length=20)),
                ('caracteristicas_cor_olhos', models.CharField(choices=[('PRETOS', 'Pretos'), ('CASTANHO', 'Castanho'), ('AZUIS', 'Azuis'), ('VERDES', 'Verdes'), ('DUAS_CORES', 'Duas cores'), ('INDEFINIDOS_CLAROS', 'Indefinidos claros'), ('INDEFINIDOS_ESCUROS', 'Indefinidos escuros')], max_length=20)),
                ('caracteristicas_nariz', models.CharField(choices=[('ACHATADO', 'Achatado'), ('ADUNCO', 'Adunco'), ('AFILADO', 'Afilado'), ('ARREBITADO', 'Arrebitado'), ('GRANDE', 'Grande'), ('MEDIO', 'Médio'), ('PEQUENO', 'Pequeno')], max_length=20)),
                ('caracteristicas_labios', models.CharField(choices=[('FINOS', 'Finos'), ('MEDIOS', 'Médios'), ('GROSSOS', 'Grossos'), ('LEPORINOS', 'Leporinos')], max_length=20)),
                ('caracteristicas_compleicao', models.CharField(choices=[('GORDA', 'Gorda'), ('MEDIA', 'Média'), ('MAGRA', 'Magra'), ('MUSCULOSA', 'Musculosa'), ('RAQUITICA', 'Raquítica')], max_length=20)),
                ('caracteristicas_sobrancelhas', models.CharField(choices=[('APARADAS', 'Aparadas'), ('FINAS', 'Finas'), ('GROSSAS', 'Grossas'), ('PINTADAS', 'Pintadas'), ('SEPARADAS', 'Separadas'), ('UNIDAS', 'Unidas')], max_length=20)),
                ('caracteristicas_orelhas', models.CharField(choices=[('GRANDES', 'Grandes'), ('MEDIAS', 'Médias'), ('PEQUENAS', 'Pequenas'), ('LOBULOS_FECHADOS', 'Lóbulos fechados'), ('LOBULOS_ABERTOS', 'Lóbulos abertos')], max_length=20)),
                ('data_nascimento', models.DateField()),
                ('documentos', models.ManyToManyField(blank=True, related_name='documentos_interno_related', to='cadastros.Documentos')),
                ('estado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='estado_pessoas_interno_related', to='localizacao.estado')),
                ('estado_civil', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='estado_civil_pessoas_interno_related', to='social.estadocivil')),
                ('foto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fotopessoas_interno_related', to='cadastros.foto')),
                ('genero', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='genero_pessoas_interno_related', to='cadastros.genero')),
                ('grau_instrucao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='grau_instrucao_pessoas_interno_related', to='social.graudeinstrucao')),
                ('nacionalidade', models.ManyToManyField(blank=True, default=None, related_name='nacionalidade_pessoas_interno_related', to='localizacao.Pais')),
                ('naturalidade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='naturalidade_pessoas_interno_related', to='localizacao.cidade')),
                ('necessidade_especial', models.ManyToManyField(blank=True, related_name='necessidades_pessoas_interno_related', to='social.NecessidadeEspecial')),
                ('orientacao_sexual', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='orientacao_sexual_pessoas_interno_related', to='social.orientacaosexual')),
                ('profissao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='profissao_interno_related', to='social.profissao')),
                ('raca', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='raca_pessoas_interno_related', to='social.raca')),
                ('religiao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='religiao_pessoas_interno_related', to='social.religiao')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('usuario_edicao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='updatedpessoas_interno_related', to=settings.AUTH_USER_MODEL)),
                ('usuario_exclusao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deletepessoas_interno_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='servidor',
            name='estado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='estado_pessoas_servidor_related', to='localizacao.estado'),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='estado_civil',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='estado_civil_pessoas_servidor_related', to='social.estadocivil'),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='foto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fotopessoas_servidor_related', to='cadastros.foto'),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='genero',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='genero_pessoas_servidor_related', to='cadastros.genero'),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='grau_instrucao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='grau_instrucao_pessoas_servidor_related', to='social.graudeinstrucao'),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='nacionalidade',
            field=models.ManyToManyField(blank=True, default=None, related_name='nacionalidade_pessoas_servidor_related', to='localizacao.Pais'),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='naturalidade',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='naturalidade_pessoas_servidor_related', to='localizacao.cidade'),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='necessidade_especial',
            field=models.ManyToManyField(blank=True, related_name='necessidades_pessoas_servidor_related', to='social.NecessidadeEspecial'),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='orientacao_sexual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='orientacao_sexual_pessoas_servidor_related', to='social.orientacaosexual'),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='raca',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='raca_pessoas_servidor_related', to='social.raca'),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='religiao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='religiao_pessoas_servidor_related', to='social.religiao'),
        ),
        migrations.CreateModel(
            name='Vulgo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ativo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('delete_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('excluido', models.BooleanField(default=False)),
                ('nome', models.CharField(max_length=150)),
                ('interno', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='models_vulgo', related_query_name='model_vulgo', to='pessoas.interno')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('usuario_edicao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='updatedpessoas_vulgo_related', to=settings.AUTH_USER_MODEL)),
                ('usuario_exclusao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deletepessoas_vulgo_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Vulgo',
                'verbose_name_plural': 'Vulgos',
            },
        ),
        migrations.CreateModel(
            name='SinaisParticulares',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ativo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('delete_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('excluido', models.BooleanField(default=False)),
                ('area', models.CharField(max_length=50)),
                ('position_x', models.FloatField()),
                ('position_y', models.FloatField()),
                ('tipo', models.CharField(choices=[('SINAL', 'Sinal Particular'), ('TATUAGEM', 'Tatuagem')], max_length=20)),
                ('descricao', models.TextField(max_length=200)),
                ('foto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='foto_sinais_related', to='cadastros.foto')),
                ('interno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='interno_sinais_related', to='pessoas.interno')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('usuario_edicao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='updatedpessoas_sinaisparticulares_related', to=settings.AUTH_USER_MODEL)),
                ('usuario_exclusao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deletepessoas_sinaisparticulares_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rg',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ativo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('delete_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('excluido', models.BooleanField(default=False)),
                ('numero', models.CharField(max_length=15)),
                ('interno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rg_interno', to='pessoas.interno')),
                ('orgao_expedidor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orgao_expedidor_interno', to='cadastros.orgaoexpedidor')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('usuario_edicao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='updatedpessoas_rg_related', to=settings.AUTH_USER_MODEL)),
                ('usuario_exclusao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deletepessoas_rg_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'RG',
                'verbose_name_plural': 'RG',
            },
        ),
        migrations.CreateModel(
            name='OutroNome',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ativo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('delete_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('excluido', models.BooleanField(default=False)),
                ('nome', models.CharField(max_length=150)),
                ('interno', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='models_outro_nome', related_query_name='model_outro_nome', to='pessoas.interno')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('usuario_edicao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='updatedpessoas_outronome_related', to=settings.AUTH_USER_MODEL)),
                ('usuario_exclusao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deletepessoas_outronome_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Outro Nome',
                'verbose_name_plural': 'Outros Nomes',
            },
        ),
        migrations.CreateModel(
            name='Contatos',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ativo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('delete_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('excluido', models.BooleanField(default=False)),
                ('nome', models.CharField(max_length=100)),
                ('enderecos', models.ManyToManyField(blank=True, related_name='endereco_contato_related', to='comum.Endereco')),
                ('interno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='interno_contato_related', to='pessoas.interno')),
                ('telefones', models.ManyToManyField(blank=True, related_name='telefone_contato_related', to='comum.Telefone')),
                ('tipo_vinculo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tipo_vinculo_contato_related', to='vinculos.tipovinculo')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('usuario_edicao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='updatedpessoas_contatos_related', to=settings.AUTH_USER_MODEL)),
                ('usuario_exclusao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deletepessoas_contatos_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
