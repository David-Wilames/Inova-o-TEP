import pytest


@pytest.fixture(scope="session", autouse=True)
def criar_tabela_usuarios_no_banco_de_testes(
    django_db_setup,
    django_db_blocker,
):
    from django.apps import apps
    from django.db import connection

    # Acessa o modelo Usuarios
    Usuarios = apps.get_model("usuario", "Usuarios")

    # Libera o acesso ao banco de testes
    with django_db_blocker.unblock():

        # Verifica se a tabela já existe
        tabelas = connection.introspection.table_names()

        if Usuarios._meta.db_table not in tabelas:

            # Cria a tabela somente no banco de testes
            with connection.schema_editor() as editor:
                editor.create_model(Usuarios)

            print(
                "Tabela usuarios criada no banco de testes!"
            )

        else:
            print(
                "Tabela usuarios já existe no banco de testes!"
            )