from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("instituicao", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SolicitacaoInstituicao",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("telefone", models.CharField(max_length=30, blank=True)),
                ("cep", models.CharField(max_length=15, blank=True)),
                ("endereco", models.CharField(max_length=255, blank=True)),
                ("municipio", models.CharField(max_length=100, blank=True)),
                ("bairro", models.CharField(max_length=100, blank=True)),
                ("materia", models.CharField(max_length=150)),
                ("tipo_aula", models.CharField(max_length=20)),
                ("quantidade", models.PositiveIntegerField()),
                ("responsavel", models.CharField(max_length=255)),
                ("observacoes", models.TextField(blank=True)),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
                (
                    "escola",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="solicitacoes",
                        to="instituicao.escolas",
                    ),
                ),
            ],
            options={
                "db_table": "solicitacoes_instituicao",
                "verbose_name": "Solicitação de instituição",
                "verbose_name_plural": "Solicitações de instituições",
            },
        ),
    ]
