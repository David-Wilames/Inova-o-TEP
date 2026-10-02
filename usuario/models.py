from django.db import models


class Usuarios(models.Model):
    nome_usuario = models.TextField(blank=True, null=True)
    senha = models.TextField(blank=True, null=True)
    perfil_de_acesso = models.TextField(db_column='perfil de acesso', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usuarios'

    def __str__(self):
        return self.nome_usuario or f"Usuario {self.pk}"
