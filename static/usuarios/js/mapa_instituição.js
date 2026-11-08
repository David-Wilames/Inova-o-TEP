// =====================================================
// MAPA DA INSTITUIÇÃO — TODOS OS COLABORADORES ATIVOS
// =====================================================

mapboxgl.accessToken = "pk.eyJ1IjoiZGF2aWR3aWxhbWVzIiwiYSI6ImNtdWRlMTVwYjAwNm8yeXB3bWhhZDdwMnoifQ.Hjmu1uYJKydEjIUzhexcsQ";

const INSTITUICAO = [-46.8769, -23.3561];

let mapa;
let mapaPronto = false;
let marcadoresColaboradores = [];
let carregamentoEmAndamento = false;
let colaboradoresJaCarregados = false;

// -----------------------------------------------------
// CRIAÇÃO DO MAPA
// -----------------------------------------------------

mapa = new mapboxgl.Map({
    container: "map",
    style: "mapbox://styles/mapbox/standard",
    center: INSTITUICAO,
    zoom: 12
});

mapa.addControl(new mapboxgl.NavigationControl(), "bottom-right");

mapa.on("load", async function () {
    mapa.resize();
    mapaPronto = true;

    // Se a instituição já estiver autenticada na sessão,
    // os colaboradores aparecem automaticamente ao abrir a página.
    await window.carregarColaboradoresNoMapa();
});

window.addEventListener("resize", function () {
    if (mapaPronto) mapa.resize();
});

// -----------------------------------------------------
// ELEMENTOS DE STATUS DO CARD DE ROTA
// -----------------------------------------------------

function atualizarCard(titulo, distancia = "--", tempo = "--") {
    const tituloElemento = document.getElementById("route-title");
    const distanciaElemento = document.getElementById("route-distance");
    const tempoElemento = document.getElementById("route-time");

    if (tituloElemento) tituloElemento.textContent = titulo;
    if (distanciaElemento) distanciaElemento.textContent = distancia;
    if (tempoElemento) tempoElemento.textContent = tempo;
}

// -----------------------------------------------------
// GEOLOCALIZAÇÃO DA ORIGEM E CÁLCULO DE ROTA
// -----------------------------------------------------

function obterLocalizacaoAtual() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error("Este navegador não oferece geolocalização."));
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (posicao) => resolve({
                longitude: posicao.coords.longitude,
                latitude: posicao.coords.latitude
            }),
            reject,
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    });
}

async function criarRota(destinoLng, destinoLat, nomeDestino) {
    atualizarCard(`Calculando rota até ${nomeDestino}...`);

    try {
        const origem = await obterLocalizacaoAtual();
        const url = new URL(
            `https://api.mapbox.com/directions/v5/mapbox/driving/${origem.longitude},${origem.latitude};${destinoLng},${destinoLat}`
        );

        url.searchParams.set("geometries", "geojson");
        url.searchParams.set("overview", "full");
        url.searchParams.set("steps", "false");
        url.searchParams.set("access_token", mapboxgl.accessToken);

        const resposta = await fetch(url);
        if (!resposta.ok) throw new Error(`Erro do serviço de rotas: ${resposta.status}`);

        const dados = await resposta.json();
        if (!dados.routes || !dados.routes.length) {
            atualizarCard("Não foi possível encontrar uma rota.");
            return;
        }

        const rota = dados.routes[0];
        atualizarCard(
            `Rota até ${nomeDestino}`,
            `${(rota.distance / 1000).toFixed(1)} km`,
            `${Math.round(rota.duration / 60)} min`
        );

        if (mapa.getLayer("rota-colaborador")) mapa.removeLayer("rota-colaborador");
        if (mapa.getSource("rota-colaborador")) mapa.removeSource("rota-colaborador");

        mapa.addSource("rota-colaborador", {
            type: "geojson",
            data: {
                type: "Feature",
                properties: {},
                geometry: rota.geometry
            }
        });

        mapa.addLayer({
            id: "rota-colaborador",
            type: "line",
            source: "rota-colaborador",
            layout: { "line-join": "round", "line-cap": "round" },
            paint: {
                "line-color": "#1769d2",
                "line-width": 5,
                "line-opacity": 0.9
            }
        });

        const coordenadas = rota.geometry.coordinates;
        const limites = coordenadas.reduce(
            (bounds, coordenada) => bounds.extend(coordenada),
            new mapboxgl.LngLatBounds(coordenadas[0], coordenadas[0])
        );
        mapa.fitBounds(limites, { padding: 80, duration: 1000 });
    } catch (erro) {
        console.error("Erro ao calcular rota:", erro);
        atualizarCard("Não foi possível calcular a rota.");
        alert("Não foi possível calcular a rota. Confira a permissão de localização do navegador.");
    }
}

// -----------------------------------------------------
// GEOCODIFICAÇÃO DO ENDEREÇO DE UM COLABORADOR
// -----------------------------------------------------

async function geocodificarColaborador(colaborador) {
    const logradouro = String(colaborador.logradouro || "").trim();
    const numero = String(colaborador.numero || "").trim();

    if (!logradouro) return null;

    const enderecoComNumero = [
        logradouro,
        numero,
        colaborador.complemento,
        colaborador.bairro,
        colaborador.municipio,
        colaborador.uf,
        colaborador.cep,
        "Brasil"
    ].filter((valor) => String(valor || "").trim()).join(", ");

    // Segunda tentativa sem número caso o serviço não encontre o endereço completo.
    const enderecoSemNumero = [
        logradouro,
        colaborador.bairro,
        colaborador.municipio,
        colaborador.uf,
        colaborador.cep,
        "Brasil"
    ].filter((valor) => String(valor || "").trim()).join(", ");

    const consultas = [enderecoComNumero, enderecoSemNumero];
    if (colaborador.cep) {
        consultas.push(`${colaborador.cep}, ${colaborador.municipio || ""}, ${colaborador.uf || ""}, Brasil`);
    }

    for (const consulta of consultas) {
        try {
            const url = new URL("https://api.mapbox.com/search/geocode/v6/forward");
            url.searchParams.set("q", consulta);
            url.searchParams.set("country", "BR");
            url.searchParams.set("language", "pt");
            url.searchParams.set("limit", "1");
            url.searchParams.set("proximity", `${INSTITUICAO[0]},${INSTITUICAO[1]}`);
            url.searchParams.set("access_token", mapboxgl.accessToken);

            const resposta = await fetch(url);
            if (!resposta.ok) {
                console.warn("Falha ao pesquisar endereço no mapa:", resposta.status);
                continue;
            }

            const dados = await resposta.json();
            const feature = dados.features?.[0];
            if (!feature?.geometry?.coordinates) continue;

            const [longitude, latitude] = feature.geometry.coordinates;
            return { longitude, latitude, consultaUsada: consulta };
        } catch (erro) {
            console.warn("Erro ao geocodificar endereço:", erro);
        }
    }

    return null;
}

// -----------------------------------------------------
// POPUP DOS COLABORADORES
// -----------------------------------------------------

function criarPopupGrupo(grupo) {
    const conteudo = document.createElement("div");
    conteudo.style.minWidth = "230px";
    conteudo.style.maxWidth = "300px";
    conteudo.style.fontFamily = "Arial, sans-serif";

    const titulo = document.createElement("h3");
    titulo.textContent = grupo.length > 1
        ? `${grupo.length} profissionais neste endereço`
        : "Profissional localizado";
    titulo.style.margin = "0 0 10px";
    titulo.style.fontSize = "16px";
    conteudo.appendChild(titulo);

    grupo.forEach((colaborador) => {
        const bloco = document.createElement("section");
        bloco.style.padding = "8px 0";
        bloco.style.borderTop = "1px solid #e5e7eb";

        const nome = document.createElement("strong");
        nome.textContent = colaborador.nome || "Nome não informado";
        bloco.appendChild(nome);

        const materia = document.createElement("p");
        materia.textContent = `Matéria: ${colaborador.materia || "Não informada"}`;
        materia.style.margin = "5px 0";
        bloco.appendChild(materia);

        const endereco = document.createElement("p");
        endereco.textContent = [
            colaborador.logradouro,
            colaborador.numero,
            colaborador.bairro,
            colaborador.municipio,
            colaborador.uf
        ].filter(Boolean).join(", ");
        endereco.style.margin = "5px 0";
        bloco.appendChild(endereco);

        const acoes = document.createElement("div");
        acoes.style.display = "flex";
        acoes.style.gap = "6px";
        acoes.style.flexWrap = "wrap";

        const botaoPerfil = document.createElement("button");
        botaoPerfil.type = "button";
        botaoPerfil.className = "profile-btn";
        botaoPerfil.dataset.colaboradorId = colaborador.id;
        botaoPerfil.textContent = "Ver perfil";
        acoes.appendChild(botaoPerfil);

        const botaoRota = document.createElement("button");
        botaoRota.type = "button";
        botaoRota.textContent = "Traçar rota";
        botaoRota.addEventListener("click", () => {
            criarRota(grupo[0].longitude, grupo[0].latitude, colaborador.nome || "colaborador");
        });
        acoes.appendChild(botaoRota);

        bloco.appendChild(acoes);
        conteudo.appendChild(bloco);
    });

    return conteudo;
}

// -----------------------------------------------------
// ADICIONAR MARCADORES; AGRUPAR PONTOS IGUAIS
// -----------------------------------------------------

function removerMarcadoresAnteriores() {
    marcadoresColaboradores.forEach((marcador) => marcador.remove());
    marcadoresColaboradores = [];
}

function adicionarMarcadores(colaboradoresLocalizados) {
    removerMarcadoresAnteriores();

    // Endereços diferentes podem ser retornados pelo geocodificador
    // com a mesma coordenada (por exemplo, quando só a rua é encontrada).
    // Agrupamos esses profissionais no mesmo ponto para ninguém ficar escondido.
    const grupos = new Map();

    colaboradoresLocalizados.forEach((colaborador) => {
        const chave = `${colaborador.longitude.toFixed(5)},${colaborador.latitude.toFixed(5)}`;
        if (!grupos.has(chave)) grupos.set(chave, []);
        grupos.get(chave).push(colaborador);
    });

    const coordenadas = [];

    grupos.forEach((grupo) => {
        const longitude = grupo[0].longitude;
        const latitude = grupo[0].latitude;
        coordenadas.push([longitude, latitude]);

        const elemento = document.createElement("div");
        elemento.setAttribute("role", "button");
        elemento.setAttribute("aria-label", `${grupo.length} profissional(is) neste local`);
        elemento.style.width = grupo.length > 1 ? "34px" : "22px";
        elemento.style.height = grupo.length > 1 ? "34px" : "22px";
        elemento.style.borderRadius = "50%";
        elemento.style.background = grupo.length > 1 ? "#0f766e" : "#1473e6";
        elemento.style.border = "3px solid #ffffff";
        elemento.style.boxShadow = "0 2px 8px rgba(0,0,0,.35)";
        elemento.style.cursor = "pointer";
        elemento.style.display = "flex";
        elemento.style.alignItems = "center";
        elemento.style.justifyContent = "center";
        elemento.style.color = "#ffffff";
        elemento.style.fontSize = "12px";
        elemento.style.fontWeight = "700";

        if (grupo.length > 1) elemento.textContent = String(grupo.length);

        const popup = new mapboxgl.Popup({ offset: 20, maxWidth: "320px" })
            .setDOMContent(criarPopupGrupo(grupo));

        const marcador = new mapboxgl.Marker({
            element: elemento
        })
            .setLngLat([longitude, latitude])
            .setPopup(popup)
            .addTo(mapa);

        marcadoresColaboradores.push(marcador);
    });

    if (coordenadas.length === 1) {
        mapa.flyTo({ center: coordenadas[0], zoom: 15, duration: 1000 });
    } else if (coordenadas.length > 1) {
        const limites = coordenadas.reduce(
            (bounds, coordenada) => bounds.extend(coordenada),
            new mapboxgl.LngLatBounds(coordenadas[0], coordenadas[0])
        );
        mapa.fitBounds(limites, { padding: 70, maxZoom: 15, duration: 1000 });
    }
}

// -----------------------------------------------------
// API: BUSCAR TODOS OS COLABORADORES ATIVOS
// -----------------------------------------------------

window.carregarColaboradoresNoMapa = async function () {
    if (!mapaPronto || carregamentoEmAndamento || colaboradoresJaCarregados) return;

    carregamentoEmAndamento = true;
    atualizarCard("Verificando acesso da instituição...");

    try {
        const resposta = await fetch("/usuario/api/colaboradores-mapa/", {
            method: "GET",
            headers: { "Accept": "application/json" },
            credentials: "same-origin",
            cache: "no-store"
        });

        const dados = await resposta.json();

        if (resposta.status === 403) {
            atualizarCard("Confirme sua instituição para visualizar os profissionais.");
            return;
        }

        if (!resposta.ok) {
            throw new Error(dados.erro || `Erro HTTP ${resposta.status}`);
        }

        const colaboradores = Array.isArray(dados.colaboradores)
            ? dados.colaboradores
            : [];

        if (colaboradores.length === 0) {
            colaboradoresJaCarregados = true;
            removerMarcadoresAnteriores();
            atualizarCard("Nenhum colaborador ativo com endereço cadastrado.", "0", "--");
            return;
        }

        atualizarCard(`Localizando ${colaboradores.length} profissionais...`, "--", "--");

        const localizados = [];
        let naoLocalizados = 0;

        // Consultas sequenciais para não disparar muitas requisições ao Mapbox ao mesmo tempo.
        for (const colaborador of colaboradores) {
            const local = await geocodificarColaborador(colaborador);
            if (!local) {
                naoLocalizados += 1;
                console.warn("Endereço não encontrado para um colaborador:", colaborador.id);
                continue;
            }

            localizados.push({
                ...colaborador,
                longitude: local.longitude,
                latitude: local.latitude
            });
        }

        adicionarMarcadores(localizados);
        colaboradoresJaCarregados = true;

        atualizarCard(
            `${localizados.length} de ${colaboradores.length} profissionais localizados`,
            `${localizados.length} no mapa`,
            naoLocalizados ? `${naoLocalizados} sem localização` : "Todos localizados"
        );

        if (localizados.length === 0) {
            console.warn("Nenhum endereço de colaborador foi localizado pelo Mapbox.");
        }
    } catch (erro) {
        console.error("Erro ao carregar colaboradores no mapa:", erro);
        atualizarCard("Não foi possível carregar os profissionais.");
    } finally {
        carregamentoEmAndamento = false;
    }
};

// Permite atualizar o mapa novamente após a instituição confirmar o acesso.
window.atualizarMapaColaboradores = function () {
    colaboradoresJaCarregados = false;
    return window.carregarColaboradoresNoMapa();
};