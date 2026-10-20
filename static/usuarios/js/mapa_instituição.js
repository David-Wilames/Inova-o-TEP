
// =====================================================
// CONFIGURAÇÃO DO MAPBOX
// =====================================================

mapboxgl.accessToken = "pk.eyJ1IjoiZGF2aWR3aWxhbWVzIiwiYSI6ImNtdWRlMTVwYjAwNm8yeXB3bWhhZDdwMnoifQ.Hjmu1uYJKydEjIUzhexcsQ";

// =====================================================
// CONFIGURAÇÃO DO MAPA — CAJAMAR
// =====================================================

const INSTITUICAO = [-46.8769, -23.3561];

const LIMITES_CAJAMAR = [
    [-46.98, -23.45],
    [-46.78, -23.25]
];

// =====================================================
// VARIÁVEIS
// =====================================================

let marcadorColaboradorCEP = null;
let localizacaoColaborador = null;

// =====================================================
// CRIAR MAPA
// =====================================================

const mapa = new mapboxgl.Map({
    container: "map",
    style: "mapbox://styles/mapbox/standard",
    center: INSTITUICAO,
    zoom: 13,
    maxBounds: LIMITES_CAJAMAR,
    minZoom: 11,
    maxZoom: 18
});

// =====================================================
// CONTROLES DO MAPA
// =====================================================

mapa.addControl(
    new mapboxgl.NavigationControl(),
    "bottom-right"
);

// =====================================================
// CARREGAR MAPA E LOCALIZAÇÃO DO COLABORADOR
// =====================================================

mapa.on("load", async function () {
    mapa.resize();
    await carregarLocalizacaoColaborador();
});

window.addEventListener("resize", function () {
    mapa.resize();
});

setTimeout(function () {
    mapa.resize();
}, 500);

// =====================================================
// LOCALIZAR COLABORADOR PELO CEP CADASTRADO
// =====================================================

async function carregarLocalizacaoColaborador() {
    try {
        console.log("Buscando endereço do colaborador...");

        const resposta = await fetch(
            "/usuario/api/localizacao-colaborador/"
        );

        // Verificar resposta da API Django.
        if (!resposta.ok) {
            if (resposta.status === 401) {
                console.warn("Colaborador não autenticado.");
                return;
            }

            if (resposta.status === 404) {
                console.warn(
                    "O colaborador ainda não cadastrou suas informações."
                );
                return;
            }

            throw new Error(
                "Erro ao consultar endereço: " + resposta.status
            );
        }

        const dados = await resposta.json();

        // =====================================================
        // VALIDAR CEP
        // =====================================================

        const cep = String(
            dados.cep || ""
        ).replace(/\D/g, "");

        if (cep.length !== 8) {
            console.warn(
                "O colaborador não possui um CEP válido."
            );
            return;
        }

        // =====================================================
        // OBTER DADOS DO ENDEREÇO PARA GEOCODIFICAÇÃO
        // =====================================================

        const numero = String(
            dados.numero || ""
        ).trim();

        const logradouro = String(
            dados.logradouro || ""
        ).trim();

        const bairro = String(
            dados.bairro || ""
        ).trim();

        const municipio = String(
            dados.municipio || ""
        ).trim();

        const uf = String(
            dados.uf || ""
        ).trim();

        if (!logradouro) {
            console.warn(
                "O colaborador precisa cadastrar o logradouro."
            );
            return;
        }

        // Montar endereço para localizar o marcador.
        const enderecoCompleto = [
            logradouro,
            numero,
            bairro,
            municipio,
            uf,
            cep,
            "Brasil"
        ]
            .filter(valor => String(valor).trim() !== "")
            .join(", ");

        // Criar consultas alternativas para o Mapbox.
        const consultas = [
            enderecoCompleto,
            `${cep}, ${municipio}, ${uf}, Brasil`,
            `${cep}, Brasil`
        ];

        let local = null;

        // =====================================================
        // PROCURAR O ENDEREÇO NO MAPBOX
        // =====================================================

        for (const consulta of consultas) {
            const url = new URL(
                "https://api.mapbox.com/search/geocode/v6/forward"
            );

            url.searchParams.set("q", consulta);
            url.searchParams.set("country", "BR");
            url.searchParams.set("language", "pt");
            url.searchParams.set("limit", "1");
            url.searchParams.set(
                "access_token",
                mapboxgl.accessToken
            );

            const respostaMapa = await fetch(url);

            if (!respostaMapa.ok) {
                console.error(
                    "Erro na consulta ao Mapbox:",
                    respostaMapa.status
                );
                continue;
            }

            const resultado = await respostaMapa.json();

            local = resultado.features?.[0] || null;

            if (local) {
                console.log(
                    "Endereço encontrado:",
                    consulta
                );
                break;
            }
        }

        // =====================================================
        // VERIFICAR SE O ENDEREÇO FOI ENCONTRADO
        // =====================================================

        if (!local) {
            console.warn(
                "Não foi possível encontrar o endereço cadastrado."
            );
            return;
        }

        const [longitude, latitude] =
            local.geometry.coordinates;

        // Guardar coordenadas do colaborador.
        localizacaoColaborador = {
            longitude: longitude,
            latitude: latitude
        };

        // =====================================================
        // POPUP — PERFIL PROFISSIONAL DO COLABORADOR
        // =====================================================

        const popupConteudo = document.createElement("div");

        popupConteudo.style.minWidth = "230px";
        popupConteudo.style.maxWidth = "300px";
        popupConteudo.style.fontFamily = "Arial, sans-serif";
        popupConteudo.style.padding = "5px";

        // Título.
        const titulo = document.createElement("h3");

        titulo.textContent = "Perfil profissional";
        titulo.style.margin = "0 0 12px";
        titulo.style.fontSize = "17px";

        popupConteudo.appendChild(titulo);

        // Função para adicionar informações não vazias.
        function adicionarInformacao(rotulo, valor) {
            if (
                valor === null ||
                valor === undefined ||
                String(valor).trim() === ""
            ) {
                return;
            }

            const linha = document.createElement("p");

            linha.style.margin = "8px 0";
            linha.style.lineHeight = "1.4";

            const campo = document.createElement("strong");
            campo.textContent = rotulo + ": ";

            const conteudo = document.createElement("span");
            conteudo.textContent = String(valor);

            linha.appendChild(campo);
            linha.appendChild(conteudo);

            popupConteudo.appendChild(linha);
        }

        // =====================================================
        // INFORMAÇÕES PROFISSIONAIS
        // =====================================================

        adicionarInformacao(
            "Nome",
            dados.nome_social && dados.nome_social.trim()
                ? dados.nome_social
                : dados.nome_completo
        );

        adicionarInformacao("Matéria", dados.materia);

        adicionarInformacao("Formação", dados.formacao);

        adicionarInformacao("Pós-graduação", dados.pos_graduacao);

        // Disciplinas: permite receber uma lista ou um texto.
        adicionarInformacao(
            "Disciplinas",
            Array.isArray(dados.disciplinas)
                ? dados.disciplinas.join(", ")
                : dados.disciplinas
        );

        // =====================================================
        // DISPONIBILIDADE PROFISSIONAL
        // =====================================================

        let tempoIntegral = dados.tempo_integral;

        if (
            tempoIntegral === true ||
            tempoIntegral === 1 ||
            tempoIntegral === "1" ||
            tempoIntegral === "True" ||
            tempoIntegral === "true"
        ) {
            tempoIntegral = "Sim";
        } else if (
            tempoIntegral === false ||
            tempoIntegral === 0 ||
            tempoIntegral === "0" ||
            tempoIntegral === "False" ||
            tempoIntegral === "false"
        ) {
            tempoIntegral = "Não";
        }

        adicionarInformacao(
            "Tempo integral",
            tempoIntegral
        );

        adicionarInformacao(
            "Horário de início",
            dados.horario_inicio
        );

        adicionarInformacao(
            "Horário de término",
            dados.horario_fim
        );

        // =====================================================
        // OBSERVAÇÕES PROFISSIONAIS
        // =====================================================

        adicionarInformacao(
            "Observações",
            dados.observacoes
        );
        // =====================================================
// REMOVER MARCADOR ANTERIOR, SE EXISTIR
// =====================================================

if (marcadorColaboradorCEP) {
    marcadorColaboradorCEP.remove();
}

// =====================================================
// CRIAR MARCADOR AZUL DO COLABORADOR
// =====================================================

marcadorColaboradorCEP = new mapboxgl.Marker({
    color: "#1473e6"
})
    .setLngLat([longitude, latitude])
    .setPopup(
        new mapboxgl.Popup({
            offset: 25
        }).setDOMContent(popupConteudo)
    )
    .addTo(mapa);

// =====================================================
// CENTRALIZAR MAPA NO ENDEREÇO CADASTRADO
// =====================================================

mapa.flyTo({
    center: [longitude, latitude],
    zoom: 12,
    duration: 1200
});

console.log("Localização do colaborador carregada.", {
    longitude: longitude,
    latitude: latitude
});

} catch (erro) {
    console.error(
        "Erro ao carregar localização do colaborador:",
        erro
    );
}
}