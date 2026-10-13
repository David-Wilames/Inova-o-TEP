from django.db import models


class Escolas(models.Model):
    id = models.AutoField(primary_key=True)
    nome_unidade_escolar = models.TextField(unique=True)
    telefone = models.TextField(db_column="Telefone")
    endereco = models.TextField()
    municipio = models.TextField()
    bairro_localidade = models.TextField(db_column="Bairro/Localidade")
    cep = models.TextField(db_column="CEP")
    diretor = models.TextField(db_column="Diretor(a)")
    categoria = models.TextField(db_column="Categoria")

    class Meta:
        managed = True
        db_table = "Escolas"
        verbose_name_plural = "Escolas"

    def __str__(self):
        valor = self.nome_unidade_escolar
        if isinstance(valor, bytes):
            return valor.decode("utf-8", errors="ignore")
        return str(valor) if valor else f"Escola {self.id}"


class Professores(models.Model):
    id = models.AutoField(db_column="ID", primary_key=True)
    nome_completo = models.TextField(db_column="Nome Completo")
    data_nascimento = models.TextField(db_column="Data Nascimento")
    cpf = models.TextField(db_column="CPF", unique=True)
    endereco = models.TextField(db_column="Endereço")
    municipio = models.TextField(db_column="Município")
    bairro = models.TextField(db_column="Bairro")
    cep = models.TextField(db_column="CEP", blank=True, null=True)
    disciplina = models.TextField(db_column="Disciplina")
    formacao = models.TextField(db_column="Formação")
    telefone = models.TextField(db_column="Telefone", unique=True)
    email = models.TextField(db_column="E-mail", unique=True)
    situacao = models.TextField(db_column="Situação")

    class Meta:
        managed = True
        db_table = "professores"
        verbose_name_plural = "Professores"

    def __str__(self):
        nome = self.nome_completo
        if isinstance(nome, bytes):
            nome = nome.decode("utf-8", errors="ignore")

        disc = self.disciplina
        if isinstance(disc, bytes):
            disc = disc.decode("utf-8", errors="ignore")

        return f"{nome or 'Professor'} - {disc or ''}"


class InformacoesInstituicao(models.Model):
    escola = models.TextField(db_column="Escola")
    telefone = models.TextField(db_column="Telefone")
    cep = models.TextField(db_column="CEP")
    endereco = models.TextField(db_column="Endereço")
    municipio = models.TextField(db_column="Municipio")
    bairro = models.TextField(db_column="Bairro")
    materia = models.TextField(db_column="Materia")
    tipo = models.TextField(db_column="Tipo")
    quantidade = models.TextField(db_column="Quantidade")
    responsavel = models.TextField(db_column="Nome do responsavel")
    observacoes = models.TextField(
        db_column="Observacoes",
        blank=True,
    )

    class Meta:
        managed = False
        db_table = "informacoes_instituicao"
        verbose_name = "Informação da instituição"
        verbose_name_plural = "Informações da instituição"

    def __str__(self):
        return f"{self.escola} - {self.materia}"
