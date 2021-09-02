# Generated by Django 3.1.5 on 2021-05-20 13:42

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('localizacao', '0001_initial'),
        ('pessoas', '0008_auto_20210510_1348'),
        ('juridico', '0008_auto_20210512_1143'),
        ('cadastros', '0003_auto_20210428_1656'),
        ('social', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('movimentacao', '0003_auto_20210511_1531'),
    ]

    operations = [
        migrations.CreateModel(
            name='NormasJuridicasMotivosThroughModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PedidoInclusao',
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
                ('data_nascimento', models.DateField()),
                ('preso_extraditando', models.BooleanField(default=False)),
                ('interesse', models.CharField(choices=[('PRESO', 'Preso'), ('SEGURANCA_PUBLICA', 'SEGURANÇA PÚBLICA')], max_length=20)),
                ('tipo_inclusao', models.CharField(choices=[('EMERGENCIAL', 'Emergencial'), ('DEFINITIVO', 'Definitivo')], max_length=20)),
                ('numero_sei', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Nº SEI inválido', regex='\\d{5}\\.\\d{6}\\/[A-Z]{4}\\-\\d{2}')])),
                ('data_pedido_sei', models.DateField()),
                ('motivo_exclusao', models.TextField(blank=True, default=None, max_length=200, null=True)),
                ('estado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='estado_movimentacao_pedidoinclusao_related', to='localizacao.estado')),
                ('estado_solicitante', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='estado_solicitante_movimentacao_pedidoinclusao_related', to='localizacao.estado')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PedidoInclusaoMotivos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('norma_juridica', models.CharField(choices=[('EMENDA_CONSTITUICAO', 'Emenda à Constituição'), ('LEI_COMPLEMENTAR', 'Lei Complementar'), ('LEI_ORDINARIA', 'Lei Ordinária'), ('LEI_DELEGADA', 'Lei Delegada'), ('MEDIDA_PROVISORIA', 'Medida Provisória'), ('DECRETO_LEGISLATIVO', 'Decreto Legislativo'), ('RESOLUCAO', 'Resolução')], max_length=50)),
                ('descricao', models.ManyToManyField(through='movimentacao.NormasJuridicasMotivosThroughModel', to='juridico.NormasJuridicas')),
                ('pedido_inclusao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='movimentacao.pedidoinclusao')),
                ('titulo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juridico.titulolei')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PedidoInclusaoOutroNome',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ativo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('delete_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('excluido', models.BooleanField(default=False)),
                ('nome', models.CharField(max_length=150)),
                ('pedido_inclusao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='models_outro_nome', related_query_name='model_outro_nome', to='movimentacao.pedidoinclusao')),
                ('usuario_cadastro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('usuario_edicao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='updatedmovimentacao_pedidoinclusaooutronome_related', to=settings.AUTH_USER_MODEL)),
                ('usuario_exclusao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deletemovimentacao_pedidoinclusaooutronome_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Outro Nome',
                'verbose_name_plural': 'Outros Nomes',
            },
        ),
        migrations.CreateModel(
            name='VulgosThroughModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('pedido_inclusao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='movimentacao.pedidoinclusao')),
                ('vulgo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pessoas.vulgo')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='movimentacaoexterna',
            name='estado_destino',
        ),
        migrations.RemoveField(
            model_name='movimentacaoexterna',
            name='interno',
        ),
        migrations.RemoveField(
            model_name='movimentacaoexterna',
            name='status_movimentacao',
        ),
        migrations.RemoveField(
            model_name='movimentacaoexterna',
            name='tipo_movimentacao',
        ),
        migrations.RemoveField(
            model_name='movimentacaoexterna',
            name='unidade_destino',
        ),
        migrations.RemoveField(
            model_name='movimentacaoexterna',
            name='unidade_origem',
        ),
        migrations.RemoveField(
            model_name='movimentacaoexterna',
            name='usuario_cadastro',
        ),
        migrations.RemoveField(
            model_name='movimentacaointerna',
            name='cela_destino',
        ),
        migrations.RemoveField(
            model_name='movimentacaointerna',
            name='cela_origem',
        ),
        migrations.RemoveField(
            model_name='movimentacaointerna',
            name='interno',
        ),
        migrations.RemoveField(
            model_name='movimentacaointerna',
            name='tipo_movimentacao',
        ),
        migrations.RemoveField(
            model_name='movimentacaointerna',
            name='usuario_cadastro',
        ),
        migrations.AlterField(
            model_name='fasespedido',
            name='grupo',
            field=models.CharField(choices=[('EMERGENCIAL', 'Emergencial'), ('DEFINITIVO', 'Definitivo')], max_length=20),
        ),
        migrations.DeleteModel(
            name='DocumentoMovimentacaoExterna',
        ),
        migrations.DeleteModel(
            name='MovimentacaoExterna',
        ),
        migrations.DeleteModel(
            name='MovimentacaoInterna',
        ),
        migrations.DeleteModel(
            name='StatusMovimentacao',
        ),
        migrations.DeleteModel(
            name='TipoMovimentacao',
        ),
        migrations.AddField(
            model_name='pedidoinclusao',
            name='fase_pedido',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='movimentacao.fasespedido'),
        ),
        migrations.AddField(
            model_name='pedidoinclusao',
            name='foto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fotomovimentacao_pedidoinclusao_related', to='cadastros.foto'),
        ),
        migrations.AddField(
            model_name='pedidoinclusao',
            name='genero',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='genero_movimentacao_pedidoinclusao_related', to='cadastros.genero'),
        ),
        migrations.AddField(
            model_name='pedidoinclusao',
            name='nacionalidade',
            field=models.ManyToManyField(blank=True, default=None, related_name='nacionalidade_movimentacao_pedidoinclusao_related', to='localizacao.Pais'),
        ),
        migrations.AddField(
            model_name='pedidoinclusao',
            name='naturalidade',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='naturalidade_movimentacao_pedidoinclusao_related', to='localizacao.cidade'),
        ),
        migrations.AddField(
            model_name='pedidoinclusao',
            name='necessidade_especial',
            field=models.ManyToManyField(blank=True, related_name='necessidades_movimentacao_pedidoinclusao_related', to='social.NecessidadeEspecial'),
        ),
        migrations.AddField(
            model_name='pedidoinclusao',
            name='regime_prisional',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cadastros.regimeprisional'),
        ),
        migrations.AddField(
            model_name='pedidoinclusao',
            name='usuario_cadastro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pedidoinclusao',
            name='usuario_edicao',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='updatedmovimentacao_pedidoinclusao_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pedidoinclusao',
            name='usuario_exclusao',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='deletemovimentacao_pedidoinclusao_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pedidoinclusao',
            name='vulgo',
            field=models.ManyToManyField(through='movimentacao.VulgosThroughModel', to='pessoas.Vulgo'),
        ),
        migrations.AddField(
            model_name='normasjuridicasmotivosthroughmodel',
            name='motivo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='movimentacao.pedidoinclusaomotivos'),
        ),
        migrations.AddField(
            model_name='normasjuridicasmotivosthroughmodel',
            name='norma',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juridico.normasjuridicas'),
        ),
    ]
