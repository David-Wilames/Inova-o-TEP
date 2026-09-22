# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib import admin


class Escolas(models.Model):
    nome_unidade_escolar = models.TextField(unique=True)
    telefone = models.TextField(db_column='Telefone')  # Fieldname made lowercase. This field type is a guess.
    endereco = models.TextField()
    municipio = models.TextField()
    bairro_localidade = models.TextField(db_column='Bairro/Localidade')  # Field name made lowercase. Field renamed to removeunsuitable characters.
    cep = models.TextField(db_column='CEP')  # Field name madelowercase.
    diretor_a_field = models.TextField(db_column='Diretor(a)') # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    categoria = models.TextField(db_column='Categoria')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Escolas'


class Professores(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nome_completo = models.TextField(db_column='Nome Completo')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    data_nascimento = models.TextField(db_column='Data Nascimento')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    cpf = models.TextField(db_column='CPF', unique=True)  # Field name made lowercase.
    endereço = models.TextField(db_column='Endereço')  # Fieldname made lowercase.
    município = models.TextField(db_column='Município')  # Field name made lowercase.
    bairro = models.TextField(db_column='Bairro')  # Field name made lowercase.
    cep = models.TextField(db_column='CEP', blank=True, null=True)  # Field name made lowercase.
    disciplina = models.TextField(db_column='Disciplina')  # Field name made lowercase.
    formação = models.TextField(db_column='Formação')  # Fieldname made lowercase.
    telefone = models.TextField(db_column='Telefone', unique=True)  # Field name made lowercase.
    e_mail = models.TextField(db_column='E-mail', unique=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    situação = models.TextField(db_column='Situação')  # Fieldname made lowercase.

    class Meta:
        managed = True
        db_table = 'professores'