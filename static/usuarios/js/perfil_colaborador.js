document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("perfil-modal");
    const botaoFechar = document.getElementById("perfil-fechar");

    const nome = document.getElementById("perfil-nome");
    const materia = document.getElementById("perfil-materia");
    const avatar = document.getElementById("perfil-avatar");

    const carregamento = document.getElementById("perfil-carregamento");
    const conteudo = document.getElementById("perfil-conteudo");
    const erro = document.getElementById("perfil-erro");

    if (
        !modal ||
        !botaoFechar ||
        !nome ||
        !materia ||
        !avatar ||
        !carregamento ||
        !conteudo ||
        !erro
    ) {
        console.error("Os elementos da janela de perfil não foram encontrados.");
        return;
    }

    const valorOuPadrao = (valor) => {
        if (valor === null || valor === undefined || valor === "") {
            return "Não informado";
        }

        return String(valor);
    };

    function preencherCampo(campo, valor) {
        const elemento = conteudo.querySelector(
            `[data-campo="${campo}"]`
        );

        if (elemento) {
            elemento.textContent = valorOuPadrao(valor);
        }
    }

    function abrirModal() {
        modal.classList.add("aberto");
        modal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
        botaoFechar.focus();
    }

    function fecharModal() {
        modal.classList.remove("aberto");
        modal.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
    }

    function limparEstado() {
        carregamento.hidden = false;
        conteudo.hidden = true;
        erro.hidden = true;

        nome.textContent = "Carregando perfil...";
        materia.textContent = "Carregando informações profissionais";
    }

    async function carregarPerfil(colaboradorId, botao) {
        limparEstado();
        abrirModal();

        const nomeOriginal = botao.textContent;

        botao.disabled = true;
        botao.textContent = "Carregando...";

        try {
            const url = `/instituicao/api/colaborador/${encodeURIComponent(
                colaboradorId
            )}/perfil/`;

            const resposta = await fetch(url, {
                method: "GET",
                headers: {
                    Accept: "application/json",
                },
            });

            const resultado = await resposta.json();

            if (!resposta.ok || !resultado.sucesso) {
                throw new Error(
                    resultado.mensagem || "Não foi possível carregar o perfil."
                );
            }

            const colaborador = resultado.colaborador;

            nome.textContent =
                colaborador.nome_social ||
                colaborador.nome_completo ||
                "Nome não informado";

            materia.textContent = valorOuPadrao(colaborador.materia);

            avatar.textContent =
                colaborador.genero?.toLowerCase() === "feminino"
                    ? "👩‍🏫"
                    : "👨‍🏫";

            preencherCampo("nome_completo", colaborador.nome_completo);
            preencherCampo("nome_social", colaborador.nome_social);
            preencherCampo("genero", colaborador.genero);
            preencherCampo("data_nascimento", colaborador.data_nascimento);

            preencherCampo("email", colaborador.email);
            preencherCampo("telefone", colaborador.telefone);

            preencherCampo("municipio", colaborador.municipio);
            preencherCampo("uf", colaborador.uf);
            preencherCampo("cep", colaborador.cep);

            const endereco = [
                colaborador.logradouro,
                colaborador.numero,
                colaborador.complemento,
                colaborador.bairro,
            ]
                .filter((parte) => parte)
                .join(", ");

            preencherCampo("endereco", endereco);

            preencherCampo("materia", colaborador.materia);
            preencherCampo("formacao", colaborador.formacao);
            preencherCampo("pos_graduacao", colaborador.pos_graduacao);

            const disciplinas = Array.isArray(colaborador.disciplinas)
                ? colaborador.disciplinas.join(", ")
                : colaborador.disciplinas;

            preencherCampo("disciplinas", disciplinas);

            preencherCampo(
                "tempo_integral",
                colaborador.tempo_integral ? "Sim" : "Não"
            );

            preencherCampo("horario_inicio", colaborador.horario_inicio);
            preencherCampo("horario_fim", colaborador.horario_fim);

            preencherCampo(
                "possui_deficiencia",
                colaborador.possui_deficiencia
            );

            preencherCampo(
                "necessidades_acessibilidade",
                colaborador.necessidades_acessibilidade
            );

            preencherCampo("observacoes", colaborador.observacoes);

            carregamento.hidden = true;
            conteudo.hidden = false;
        } catch (excecao) {
            console.error("Erro ao carregar perfil:", excecao);

            carregamento.hidden = true;
            erro.textContent =
                excecao.message ||
                "Não foi possível carregar o perfil deste colaborador.";

            erro.hidden = false;
        } finally {
            botao.disabled = false;
            botao.textContent = nomeOriginal;
        }
    }

    document.addEventListener("click", function (evento) {
        const botao = evento.target.closest(".profile-btn");

        if (!botao) {
            return;
        }

        const colaboradorId = botao.dataset.colaboradorId;

        if (!colaboradorId) {
            console.error("O botão não possui o ID do colaborador.");
            return;
        }

        carregarPerfil(colaboradorId, botao);
    });

    botaoFechar.addEventListener("click", fecharModal);

    modal.addEventListener("click", function (evento) {
        if (evento.target === modal) {
            fecharModal();
        }
    });

    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape" && modal.classList.contains("aberto")) {
            fecharModal();
        }
    });
});