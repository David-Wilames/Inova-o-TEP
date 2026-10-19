// =====================================================
// CONFIGURAÇÃO DO MAPBOX
// =====================================================

mapboxgl.accessToken = "pk.eyJ1IjoiZGF2aWR3aWxhbWVzIiwiYSI6ImNtdWRlMTVwYjAwNm8yeXB3bWhhZDdwMnoifQ.Hjmu1uYJKydEjIUzhexcsQ";

// =====================================================
// LOCALIZAÇÃO DA INSTITUIÇÃO — CAJAMAR
// =====================================================

const INSTITUICAO = [-46.8769, -23.3561];

// =====================================================
// LIMITES DA ÁREA DE CAJAMAR
// =====================================================

const LIMITES_CAJAMAR = [
    [-46.98, -23.45], // sudoeste
    [-46.78, -23.25]  // nordeste
];

// =====================================================
// VARIÁVEIS
// =====================================================

let marcadorUsuario = null;
let marcadorColaboradorCEP = null;

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
// MARCADOR DA INSTITUIÇÃO
// =====================================================


// =====================================================
// ATUALIZAR CARD DE ROTA
// =====================================================

function atualizarCard(titulo, distancia, tempo) {
    const tituloElemento = document.getElementById("route-title");
    const distanciaElemento = document.getElementById("route-distance");
    const tempoElemento = document.getElementById("route-time");

    if (tituloElemento) {
        tituloElemento.textContent = titulo;
    }

    if (distanciaElemento) {
        distanciaElemento.textContent = distancia;
    }

    if (tempoElemento) {
        tempoElemento.textContent = tempo;
    }
}

// =====================================================
// CRIAR ROTA
// =====================================================

async function criarRota(
    inicioLng,
    inicioLat,
    destinoLng,
    destinoLat
) {
    atualizarCard("Calculando rota...", "--", "--");

    try {
        const url =
            `https://api.mapbox.com/directions/v5/mapbox/driving/` +
            `${inicioLng},${inicioLat};${destinoLng},${destinoLat}` +
            `?geometries=geojson` +
            `&overview=full` +
            `&steps=false` +
            `&access_token=${mapboxgl.accessToken}`;

        const resposta = await fetch(url);

        if (!resposta.ok) {
            throw new Error(
                "Erro ao calcular rota: " + resposta.status
            );
        }

        const dados = await resposta.json();

        if (!dados.routes || !dados.routes.length) {
            atualizarCard("Rota não encontrada", "--", "--");
            return;
        }

        const rota = dados.routes[0];

        // DISTÂNCIA
        const distanciaKm = (rota.distance / 1000).toFixed(1);

        // TEMPO
        const tempoMin = Math.round(rota.duration / 60);

        // ATUALIZAR CARD
        atualizarCard(
            "Rota encontrada",
            distanciaKm + " km",
            tempoMin + " min"
        );

        // REMOVER ROTA ANTIGA
        if (mapa.getLayer("rota")) {
            mapa.removeLayer("rota");
        }

        if (mapa.getSource("rota")) {
            mapa.removeSource("rota");
        }

        // ADICIONAR ROTA
        mapa.addSource("rota", {
            type: "geojson",
            data: {
                type: "Feature",
                properties: {},
                geometry: rota.geometry
            }
        });

        mapa.addLayer({
            id: "rota",
            type: "line",
            source: "rota",
            layout: {
                "line-join": "round",
                "line-cap": "round"
            },
            paint: {
                "line-color": "#111111",
                "line-width": 7,
                "line-opacity": 0.9
            }
        });

        // ENQUADRAR ROTA
        const coordenadas = rota.geometry.coordinates;

        const limites = coordenadas.reduce(
            (bounds, coordenada) => bounds.extend(coordenada),
            new mapboxgl.LngLatBounds(
                coordenadas[0],
                coordenadas[0]
            )
        );

        mapa.fitBounds(limites, {
            padding: 80,
            duration: 1000
        });

    } catch (erro) {
        console.error("Erro ao calcular rota:", erro);

        atualizarCard(
            "Erro ao calcular rota",
            "--",
            "--"
        );
    }
}

// =====================================================
// LOCALIZAÇÃO DO USUÁRIO
// =====================================================

function localizarUsuario() {
    if (!navigator.geolocation) {
        alert("Seu navegador não suporta localização.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function (position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            // CENTRALIZAR NO USUÁRIO
            mapa.flyTo({
                center: [longitude, latitude],
                zoom: 15,
                duration: 1200
            });

            // ROTA ATÉ A INSTITUIÇÃO
            criarRota(
                longitude,
                latitude,
                INSTITUICAO[0],
                INSTITUICAO[1]
            );
        },

        function (erro) {
            console.error("Erro de localização:", erro);

            alert(
                "Não foi possível acessar sua localização. " +
                "Verifique a permissão do navegador."
            );
        },

        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

// =====================================================
// VERIFICAR SE ESTÁ DENTRO DE CAJAMAR
// =====================================================

function pontoDentroDeCajamar(longitude, latitude) {
    const oeste = LIMITES_CAJAMAR[0][0];
    const sul = LIMITES_CAJAMAR[0][1];
    const leste = LIMITES_CAJAMAR[1][0];
    const norte = LIMITES_CAJAMAR[1][1];

    return (
        longitude >= oeste &&
        longitude <= leste &&
        latitude >= sul &&
        latitude <= norte
    );
}

// =====================================================
// CORRIGIR TAMANHO DO MAPA
// =====================================================

mapa.on("load", function () {
    mapa.resize();
});

setTimeout(function () {
    mapa.resize();
}, 500);

// =====================================================
// LOCALIZAR ESCOLA E ADICIONAR AO MAPA
// =====================================================

async function localizarEscolaPorCEP(oportunidade) {
    const cep = String(oportunidade.cep || "").replace(/\D/g, "");

    if (cep.length !== 8) {
        console.warn(
            "CEP inválido:",
            oportunidade.escola,
            cep
        );
        return;
    }

    const endereco = [
        oportunidade.endereco,
        oportunidade.bairro,
        oportunidade.municipio,
        "São Paulo",
        "Brasil"
    ]
        .filter(Boolean)
        .join(", ");

    const consultas = [
        `${endereco}, CEP ${cep}, Cajamar, São Paulo, Brasil`,
        `${cep}, Cajamar, São Paulo, Brasil`
    ];

    for (const consulta of consultas) {
        try {
            const url = new URL(
                "https://api.mapbox.com/search/geocode/v6/forward"
            );

            url.searchParams.set("q", consulta);
            url.searchParams.set("country", "BR");
            url.searchParams.set("language", "pt");
            url.searchParams.set("limit", "1");

            url.searchParams.set(
                "proximity",
                `${INSTITUICAO[0]},${INSTITUICAO[1]}`
            );

            url.searchParams.set(
                "access_token",
                mapboxgl.accessToken
            );

            const resposta = await fetch(url);

            if (!resposta.ok) {
                console.error(
                    "Erro na geocodificação:",
                    resposta.status,
                    await resposta.text()
                );
                continue;
            }

            const dados = await resposta.json();
            const local = dados.features?.[0];

            if (!local) {
                console.warn(
                    "Endereço não encontrado:",
                    consulta
                );
                continue;
            }

            const [longitude, latitude] =
                local.geometry.coordinates;

            // VERIFICAR LIMITE DE CAJAMAR
            if (!pontoDentroDeCajamar(longitude, latitude)) {
                console.warn(
                    "Localização fora dos limites definidos:",
                    consulta,
                    longitude,
                    latitude
                );
                continue;
            }

            // CRIAR CONTEÚDO DO MARCADOR
            const conteudo = document.createElement("div");

            conteudo.style.minWidth = "220px";
            conteudo.style.maxWidth = "280px";
            conteudo.style.fontFamily = "Arial, sans-serif";

            const titulo = document.createElement("h3");

            titulo.textContent = oportunidade.escola || "Escola";
            titulo.style.margin = "0 0 10px";
            titulo.style.fontSize = "16px";

            conteudo.appendChild(titulo);

            // ENDEREÇO
            const enderecoTexto = document.createElement("p");

            enderecoTexto.textContent =
                oportunidade.endereco || "Endereço não informado";

            enderecoTexto.style.margin = "5px 0";

            conteudo.appendChild(enderecoTexto);

            // BAIRRO
            const bairroTexto = document.createElement("p");

            bairroTexto.textContent =
                "Bairro: " +
                (oportunidade.bairro || "Não informado");

            bairroTexto.style.margin = "5px 0";

            conteudo.appendChild(bairroTexto);

            // CEP
            const cepTexto = document.createElement("p");

            cepTexto.textContent =
                "CEP: " +
                (oportunidade.cep || "Não informado");

            cepTexto.style.margin = "5px 0";

            conteudo.appendChild(cepTexto);

            // BOTÃO DE ROTA
            const botao = document.createElement("button");

            botao.type = "button";
            botao.textContent = "Traçar rota até esta escola";
            botao.style.padding = "10px";
            botao.style.marginTop = "10px";
            botao.style.width = "100%";
            botao.style.cursor = "pointer";

            botao.addEventListener("click", function () {
                if (!navigator.geolocation) {
                    alert(
                        "Seu navegador não oferece suporte à localização."
                    );
                    return;
                }

                botao.disabled = true;
                botao.textContent = "Obtendo localização...";

                navigator.geolocation.getCurrentPosition(
                    async function (posicao) {
                        try {
                            await criarRota(
                                posicao.coords.longitude,
                                posicao.coords.latitude,
                                longitude,
                                latitude
                            );
                        } catch (erro) {
                            console.error(
                                "Erro ao traçar rota:",
                                erro
                            );

                            alert(
                                "Não foi possível traçar a rota."
                            );
                        } finally {
                            botao.disabled = false;
                            botao.textContent =
                                "Traçar rota até esta escola";
                        }
                    },

                    function (erro) {
                        console.error(
                            "Erro de localização:",
                            erro
                        );

                        alert(
                            "Não foi possível obter sua localização. " +
                            "Verifique a permissão do navegador."
                        );

                        botao.disabled = false;
                        botao.textContent =
                            "Traçar rota até esta escola";
                    },

                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            });

            conteudo.appendChild(botao);

            // MARCADOR VERDE DA ESCOLA
            new mapboxgl.Marker({
                color: "#16803c"
            })
                .setLngLat([longitude, latitude])
                .setPopup(
                    new mapboxgl.Popup({ offset: 25 })
                        .setDOMContent(conteudo)
                )
                .addTo(mapa);

            console.log(
                "Escola adicionada:",
                oportunidade.escola,
                consulta,
                [longitude, latitude]
            );

            return;

        } catch (erro) {
            console.error(
                "Erro ao localizar escola:",
                consulta,
                erro
            );
        }
    }

    console.warn(
        "Não foi possível adicionar a escola:",
        oportunidade.escola,
        cep
    );
}

// =====================================================
// CARREGAR OPORTUNIDADES DO DJANGO
// =====================================================

async function carregarEscolasNoMapa() {
    console.log("Buscando oportunidades no Django...");

    try {
        const resposta = await fetch(
            "/usuario/api/oportunidades/mapa/"
        );

        if (!resposta.ok) {
            throw new Error(
                `Erro HTTP ${resposta.status}`
            );
        }

        const dados = await resposta.json();
        const oportunidades = dados.oportunidades || [];

        console.log(
            "Oportunidades recebidas:",
            oportunidades
        );

        if (oportunidades.length === 0) {
            console.warn(
                "A API não retornou oportunidades."
            );
            return;
        }

        for (const oportunidade of oportunidades) {
            await localizarEscolaPorCEP(oportunidade);
        }

        console.log(
            "Finalizado o carregamento das escolas."
        );

    } catch (erro) {
        console.error(
            "Erro ao carregar escolas:",
            erro
        );
    }
}

// =====================================================
// CARREGAR AS ESCOLAS QUANDO O MAPA ESTIVER PRONTO
// =====================================================

mapa.once("load", carregarEscolasNoMapa);

// =====================================================
// LOCALIZAÇÃO INDIVIDUAL DO COLABORADOR PELO CEP
// =====================================================

async function carregarLocalizacaoColaborador() {
    try {
        const resposta = await fetch(
            "/usuario/api/localizacao-colaborador/"
        );

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
                "Erro ao consultar o CEP: " + resposta.status
            );
        }

        const dados = await resposta.json();

        const cep = String(dados.cep || "").replace(/\D/g, "");

        if (cep.length !== 8) {
            console.warn(
                "O colaborador não possui um CEP válido cadastrado."
            );
            return;
        }

        const endereco = [
            dados.logradouro,
            dados.numero,
            dados.bairro,
            dados.municipio,
            dados.uf,
            cep,
            "Brasil"
        ]
            .filter(Boolean)
            .join(", ");

        const url = new URL(
            "https://api.mapbox.com/search/geocode/v6/forward"
        );

        url.searchParams.set("q", endereco);
        url.searchParams.set("country", "BR");
        url.searchParams.set("language", "pt");
        url.searchParams.set("limit", "1");
        url.searchParams.set(
            "proximity",
            `${INSTITUICAO[0]},${INSTITUICAO[1]}`
        );
        url.searchParams.set(
            "access_token",
            mapboxgl.accessToken
        );

        const respostaMapa = await fetch(url);

        if (!respostaMapa.ok) {
            throw new Error(
                "Erro do Mapbox: " + respostaMapa.status
            );
        }

        const resultado = await respostaMapa.json();

        const local = resultado.features?.[0];

        if (!local) {
            console.warn(
                "Não foi possível encontrar o CEP do colaborador."
            );
            return;
        }

        const [longitude, latitude] =
            local.geometry.coordinates;

        console.log(
            "Localização do colaborador carregada:",
            cep,
            [longitude, latitude]
        );

    } catch (erro) {
        console.error(
            "Erro ao carregar localização do colaborador:",
            erro
        );
    }
}

// =====================================================
// CARREGAR A LOCALIZAÇÃO DO COLABORADOR
// =====================================================

mapa.once("load", carregarLocalizacaoColaborador);
