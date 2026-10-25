document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("form[data-validar]").forEach((formulario) => {
        // A validação será apresentada abaixo dos campos.
        formulario.noValidate = true;

        const mensagens = new Map();

        function atualizarErro(campo) {
            if (!campo.willValidate) {
                return;
            }

            let mensagem = mensagens.get(campo);

            if (campo.validity.valid) {
                mensagem?.remove();
                mensagens.delete(campo);
                campo.removeAttribute("aria-invalid");
                return;
            }

            if (!mensagem) {
                mensagem = document.createElement("p");
                mensagem.className = "erro-campo";
                mensagem.setAttribute("role", "alert");
                campo.insertAdjacentElement("afterend", mensagem);
                mensagens.set(campo, mensagem);
            }

            mensagem.textContent = campo.validity.valueMissing
                ? "Preencha este campo."
                : campo.validationMessage;

            campo.setAttribute("aria-invalid", "true");
        }

        formulario.addEventListener("submit", (evento) => {
            const campos = Array.from(formulario.elements);

            campos.forEach(atualizarErro);

            const primeiroInvalido = campos.find(
                (campo) => campo.willValidate && !campo.validity.valid
            );

            if (primeiroInvalido) {
                evento.preventDefault();
                primeiroInvalido.focus();
            }
        });

        formulario.addEventListener("input", (evento) => {
            if (mensagens.has(evento.target)) {
                atualizarErro(evento.target);
            }
        });

        formulario.addEventListener("change", (evento) => {
            if (mensagens.has(evento.target)) {
                atualizarErro(evento.target);
            }
        });
    });
});