from django.db import models


class Usuarios(models.Model):
    nome_completo = models.CharField(max_length=255)
    email = models.EmailField()
    username = models.CharField(max_length=150, unique=True)
    senha = models.CharField(max_length=255)
    perfil_de_acesso = models.CharField(max_length=50, db_column="perfil de acesso")

    class Meta:
        db_table = "usuarios"

    def __str__(self):
        return self.username


class InformacoesColaborador(models.Model):
    # Vincula as informações adicionais ao usuário cadastrado
    usuario = models.OneToOneField(
        Usuarios, on_delete=models.CASCADE, related_name="informacoes_colaborador"
    )

    # DADOS PESSOAIS
    nome_completo = models.CharField(max_length=255, blank=True)
    nome_social = models.CharField(max_length=255, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=30, blank=True)
    possui_deficiencia = models.CharField(max_length=10, blank=True)
    necessidades_acessibilidade = models.TextField(blank=True)

    # CONTATO
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=20, blank=True)

    # ENDEREÇO
    cep = models.CharField(max_length=9, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    logradouro = models.CharField(max_length=255, blank=True)
    complemento = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    uf = models.CharField(max_length=2, blank=True)

    # DOCUMENTOS
    tipo_documento = models.CharField(max_length=20, blank=True)
    rg = models.CharField(max_length=30, blank=True)
    cpf = models.CharField(max_length=14, blank=True)

    # ÁREA DE ATUAÇÃO
    materia = models.CharField(max_length=100, blank=True)

    # DISPONIBILIDADE
    tempo_integral = models.BooleanField(default=False)
    horario_inicio = models.TimeField(null=True, blank=True)
    horario_fim = models.TimeField(null=True, blank=True)

    # FORMAÇÃO
    formacao = models.CharField(max_length=255, blank=True)
    pos_graduacao = models.CharField(max_length=255, blank=True)

    # DISCIPLINAS
    disciplinas = models.JSONField(default=list, blank=True)

    # OBSERVAÇÕES
    observacoes = models.TextField(max_length=1000, blank=True)

    class Meta:
        db_table = "informacoes_colaborador"
        verbose_name = "Informação do colaborador"
        verbose_name_plural = "Informações dos colaboradores"

    def __str__(self):
        return f"Informações de {self.usuario.username}"

    perfil_ativo = models.BooleanField(
        default=True, verbose_name="Perfil visível para instituições"
    )
