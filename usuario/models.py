from django.db import models


class Usuarios(models.Model):
    nome_completo = models.CharField(max_length=255)
    email = models.EmailField()
    username = models.CharField(max_length=150, unique=True)
    senha = models.CharField(max_length=255)
    perfil_de_acesso = models.CharField(
        max_length=50,
        db_column='perfil de acesso'
    )

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.username