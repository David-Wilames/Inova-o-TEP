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

'''
class InformacoesColaborador(models.Model):

    # ==========================================
    # IDENTIFICAÇÃO DO USUÁRIO
    # ==========================================

    usuario = models.OneToOneField(
        'usuario.Usuarios',
        on_delete=models.CASCADE,
        related_name='informacoes_colaborador'
    )

    # ==========================================
    # DADOS PESSOAIS
    # ==========================================

    nome_completo = models.CharField(max_length=255)
    nome_social = models.CharField(max_length=255, blank=True, default='')
    data_nascimento = models.DateField(null=True, blank=True)

    genero = models.CharField(
        max_length=30,
        blank=True,
        default=''
    )

    possui_deficiencia = models.CharField(
        max_length=10,
        blank=True,
        default=''
    )

    necessidades_acessibilidade = models.TextField(
        blank=True,
        default=''
    )

    # ==========================================
    # CONTATO
    # ==========================================

    email = models.EmailField(max_length=254, blank=True, default='')
    telefone = models.CharField(max_length=20, blank=True, default='')

    # ==========================================
    # ENDEREÇO
    # ==========================================

    cep = models.CharField(max_length=9, blank=True, default='')
    numero = models.CharField(max_length=20, blank=True, default='')
    logradouro = models.CharField(max_length=255, blank=True, default='')
    complemento = models.CharField(max_length=255, blank=True, default='')
    bairro = models.CharField(max_length=100, blank=True, default='')
    municipio = models.CharField(max_length=100, blank=True, default='')
    uf = models.CharField(max_length=2, blank=True, default='')

    # ==========================================
    # DOCUMENTOS
    # ==========================================

    tipo_documento = models.CharField(
        max_length=20,
        blank=True,
        default=''
    )

    rg = models.CharField(max_length=30, blank=True, default='')
    cpf = models.CharField(max_length=14, blank=True, default='')

    # ==========================================
    # ÁREA DE ATUAÇÃO
    # ==========================================

    materia = models.CharField(max_length=100, blank=True, default='')

    # ==========================================
    # DISPONIBILIDADE
    # ==========================================

    tempo_integral = models.BooleanField(default=False)

    horario_inicio = models.TimeField(null=True, blank=True)
    horario_fim = models.TimeField(null=True, blank=True)

    # ==========================================
    # FORMAÇÃO
    # ==========================================

    formacao = models.CharField(max_length=255, blank=True, default='')
    pos_graduacao = models.CharField(max_length=255, blank=True, default='')

    # ==========================================
    # DISCIPLINAS
    # ==========================================

    disciplinas = models.JSONField(default=list, blank=True)

    # ==========================================
    # OBSERVAÇÕES
    # ==========================================

    observacoes = models.TextField(
        max_length=1000,
        blank=True,
        default=''
    )

    # ==========================================
    # CONFIGURAÇÕES DA TABELA
    # ==========================================

    class Meta:
        db_table = 'informacoes_colaborador'
        verbose_name = 'Informação do colaborador'
        verbose_name_plural = 'Informações dos colaboradores'

    def __str__(self):
        return self.nome_completo
'''