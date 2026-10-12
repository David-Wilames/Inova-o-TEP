import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [

        # Registra o modelo Usuarios no estado das migrações,
        # sem criar ou modificar a tabela usuarios no banco.
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Usuarios",
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
                        ("nome_completo", models.CharField(max_length=255)),
                        ("email", models.EmailField(max_length=254)),
                        ("username", models.CharField(max_length=150, unique=True)),
                        ("senha", models.CharField(max_length=255)),
                        (
                            "perfil_de_acesso",
                            models.CharField(
                                db_column="perfil de acesso",
                                max_length=50,
                            ),
                        ),
                    ],
                    options={
                        "db_table": "usuarios",
                    },
                ),
            ],
        ),

        # Cria somente a nova tabela informacoes_colaborador.
        migrations.CreateModel(
            name="InformacoesColaborador",
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
                ("nome_completo", models.CharField(blank=True, max_length=255)),
                ("nome_social", models.CharField(blank=True, max_length=255)),
                ("data_nascimento", models.DateField(blank=True, null=True)),
                ("genero", models.CharField(blank=True, max_length=30)),
                ("possui_deficiencia", models.CharField(blank=True, max_length=10)),
                ("necessidades_acessibilidade", models.TextField(blank=True)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("telefone", models.CharField(blank=True, max_length=20)),
                ("cep", models.CharField(blank=True, max_length=9)),
                ("numero", models.CharField(blank=True, max_length=20)),
                ("logradouro", models.CharField(blank=True, max_length=255)),
                ("complemento", models.CharField(blank=True, max_length=255)),
                ("bairro", models.CharField(blank=True, max_length=100)),
                ("municipio", models.CharField(blank=True, max_length=100)),
                ("uf", models.CharField(blank=True, max_length=2)),
                ("tipo_documento", models.CharField(blank=True, max_length=20)),
                ("rg", models.CharField(blank=True, max_length=30)),
                ("cpf", models.CharField(blank=True, max_length=14)),
                ("materia", models.CharField(blank=True, max_length=100)),
                ("tempo_integral", models.BooleanField(default=False)),
                ("horario_inicio", models.TimeField(blank=True, null=True)),
                ("horario_fim", models.TimeField(blank=True, null=True)),
                ("formacao", models.CharField(blank=True, max_length=255)),
                ("pos_graduacao", models.CharField(blank=True, max_length=255)),
                ("disciplinas", models.JSONField(blank=True, default=list)),
                ("observacoes", models.TextField(blank=True, max_length=1000)),
                (
                    "usuario",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="informacoes_colaborador",
                        to="usuario.usuarios",
                    ),
                ),
            ],
            options={
                "verbose_name": "Informação do colaborador",
                "verbose_name_plural": "Informações dos colaboradores",
                "db_table": "informacoes_colaborador",
            },
        ),
    ]