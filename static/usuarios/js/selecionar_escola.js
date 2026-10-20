document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.querySelector(".formulario");
    const escolaSelect = document.querySelector("#escola");
    const senhaInput = document.querySelector("#senha");
    const painelDireito = document.querySelector(".painel-direito");

    if (!formulario || !escolaSelect || !senhaInput || !painelDireito) {
        console.error("Não foi possível encontrar os elementos do formulário.");
        return;
    }

    // Área dinâmica do painel direito.
    const conteudoOriginal = painelDireito.innerHTML;

    painelDireito.innerHTML = `
        <div class="conteudo-dinamico" id="conteudo-dinamico">
            <div class="icone-painel">🏫</div>
            <h2>Encontre sua instituição</h2>
            <p>
                Selecione uma escola e informe a senha
                para consultar as informações cadastradas.
            </p>
        </div>
    `;

    const areaResultado = document.querySelector("#conteudo-dinamico");

    let temporizador = null;
    let ultimaConsulta = 0;

    function mostrarMensagem(titulo, mensagem, tipo = "normal") {
        areaResultado.innerHTML = `
            <div class="resultado-painel resultado-${tipo}">
                <div class="icone-painel">
                    ${tipo === "erro" ? "⚠️" : "🏫"}
                </div>

                <h2>${titulo}</h2>

                <p>${mensagem}</p>
            </div>
        `;
    }

    function mostrarCarregamento() {
        areaResultado.innerHTML = `
            <div class="carregamento-painel">
                <div class="spinner-instituicao"></div>

                <h2>Buscando instituição...</h2>

                <p>
                    Estamos verificando os dados e filtrando
                    as informações cadastradas.
                </p>
            </div>
        `;
    }

    function mostrarInstituicao(dados) {
        if (!dados.registros || dados.registros.length === 0) {
            mostrarMensagem(
                "Nenhuma informação encontrada",
                "A instituição foi verificada, mas ainda não possui informações cadastradas.",
                "normal"
            );

            return;
        }

        const registrosHTML = dados.registros.map((registro) => `
            <article class="cartao-informacao">
                <div class="cartao-informacao-cabecalho">
                    <span class="etiqueta-materia">
                        ${escaparHTML(registro.materia || "Matéria não informada")}
                    </span>

                    <span class="etiqueta-tipo">
                        ${escaparHTML(registro.tipo || "Tipo não informado")}
                    </span>
                </div>

                <h3>
                    ${escaparHTML(registro.escola || dados.nome_escola)}
                </h3>

                <p>
                    <strong>Quantidade:</strong>
                    ${escaparHTML(registro.quantidade || "Não informada")}
                </p>

                <p>
                    <strong>Endereço:</strong>
                    ${escaparHTML(registro.endereco || "Não informado")}
                </p>

                <p>
                    <strong>Município:</strong>
                    ${escaparHTML(registro.municipio || "Não informado")}
                </p>

                <p>
                    <strong>CEP:</strong>
                    ${escaparHTML(registro.cep || "Não informado")}
                </p>

                <p>
                    <strong>Responsável:</strong>
                    ${escaparHTML(registro.responsavel || "Não informado")}
                </p>

                ${registro.observacoes
                ? `<p class="observacoes-instituicao">
                            <strong>Observações:</strong>
                            ${escaparHTML(registro.observacoes)}
                           </p>`
                : ""
            }
                            <button
                    type="button"
                    class="botao-excluir-registro"
                    data-registro-id="${escaparHTML(registro.id)}"
                >
                    Excluir registro
                </button>
            </article>
        `).join("");

        areaResultado.innerHTML = `
            <div class="resultado-painel resultado-sucesso">
                <div class="cabecalho-resultado">
                    <div class="icone-painel">✓</div>

                    <h2>Instituição encontrada!</h2>

                    <p>${escaparHTML(dados.nome_escola)}</p>

                    <span class="contador-registros">
                        ${dados.registros.length}
                        ${dados.registros.length === 1
                ? "registro encontrado"
                : "registros encontrados"}
                    </span>
                </div>

                <div class="lista-informacoes">
                    ${registrosHTML}
                </div>
            </div>
        `;
    }

    // Evita inserir HTML executável vindo do banco de dados.
    function escaparHTML(valor) {
        return String(valor ?? "").replace(/[&<>"']/g, (caractere) => {
            const entidades = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#39;"
            };

            return entidades[caractere];
        });
    }

    async function verificarInstituicao() {
        clearTimeout(temporizador);

        const escolaId = escolaSelect.value;
        const senha = senhaInput.value.trim();

        if (!escolaId || !senha) {
            mostrarMensagem(
                "Encontre sua instituição",
                "Selecione uma escola e informe a senha para consultar as informações cadastradas."
            );

            return;
        }

        const consultaAtual = ++ultimaConsulta;

        mostrarCarregamento();

        try {
            const csrfToken = formulario.querySelector(
                '[name="csrfmiddlewaretoken"]'
            )?.value;

            const corpo = new URLSearchParams({
                escola_id: escolaId,
                senha: senha
            });

            const configuracao = document.querySelector("#configuracao-instituicao");
            const urlVerificacao = configuracao.dataset.urlVerificacao;

            const resposta = await fetch(urlVerificacao, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                    "X-CSRFToken": csrfToken || ""
                },
                body: corpo.toString(),
                credentials: "same-origin"
            }
            );

            const dados = await resposta.json();

            // Ignora resultados de consultas anteriores.
            if (consultaAtual !== ultimaConsulta) {
                return;
            }

            if (!resposta.ok || !dados.sucesso) {
                mostrarMensagem(
                    "Não foi possível acessar",
                    dados.mensagem || "Confira a instituição e a senha.",
                    "erro"
                );

                return;
            }

            mostrarInstituicao(dados);

        } catch (erro) {
            console.error("Erro ao consultar instituição:", erro);

            if (consultaAtual !== ultimaConsulta) {
                return;
            }

            mostrarMensagem(
                "Erro de conexão",
                "Não foi possível consultar as informações. Tente novamente.",
                "erro"
            );
        }
    }

    // Aguarda o usuário parar de digitar antes de consultar o servidor.
    function agendarConsulta() {
        clearTimeout(temporizador);

        const escolaId = escolaSelect.value;
        const senha = senhaInput.value.trim();

        if (!escolaId || !senha) {
            ultimaConsulta++;

            mostrarMensagem(
                "Encontre sua instituição",
                "Selecione uma escola e informe a senha para consultar as informações cadastradas."
            );

            return;
        }

        temporizador = setTimeout(verificarInstituicao, 500);
    }
    areaResultado.addEventListener("click", async (evento) => {
        const botao = evento.target.closest(".botao-excluir-registro");

        if (!botao || botao.disabled) {
            return;
        }

        const confirmado = window.confirm(
            "Excluir este registro definitivamente do banco de dados?"
        );

        if (!confirmado) {
            return;
        }

        const escolaId = escolaSelect.value;
        const senha = senhaInput.value.trim();

        const configuracao = document.getElementById("configuracao-instituicao");
        const csrfToken = formulario.querySelector(
            '[name="csrfmiddlewaretoken"]'
        )?.value;

        botao.disabled = true;
        botao.textContent = "Excluindo...";

        try {
            const resposta = await fetch(configuracao.dataset.urlExclusao, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                    "X-CSRFToken": csrfToken || ""
                },
                credentials: "same-origin",
                body: new URLSearchParams({
                    escola_id: escolaId,
                    registro_id: botao.dataset.registroId,
                    senha: senha
                }).toString()
            });

            const dados = await resposta.json();

            if (!resposta.ok || !dados.sucesso) {
                window.alert(dados.mensagem || "Não foi possível excluir o registro.");
                return;
            }

            // Consulta novamente para atualizar os cartões e o contador.
            await verificarInstituicao();
        } catch (erro) {
            console.error("Erro na exclusão:", erro);
            window.alert(
                "Não foi possível confirmar o resultado. Consulte novamente os registros antes de tentar excluir outra vez."
            );
        } finally {
            botao.disabled = false;
            botao.textContent = "Excluir registro";
        }
    });
    escolaSelect.addEventListener("change", agendarConsulta);
    senhaInput.addEventListener("input", agendarConsulta);

    // Impede o envio tradicional do formulário, que recarregaria a página.
    formulario.addEventListener("submit", (evento) => {
        evento.preventDefault();
        verificarInstituicao();
    });
});