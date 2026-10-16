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
let marcadorDestino = null;


// =====================================================
// CRIAR MAPA
// =====================================================

const mapa = new mapboxgl.Map({

    container: "map",

    style: "mapbox://styles/mapbox/standard",

    center: INSTITUICAO,

    zoom: 13,

    // Impede sair da região definida
    maxBounds: LIMITES_CAJAMAR,

    // Zoom mínimo
    minZoom: 11,

    // Zoom máximo
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

new mapboxgl.Marker()
    .setLngLat(INSTITUICAO)
    .setPopup(
        new mapboxgl.Popup().setHTML(
            "<strong>Sua instituição</strong><br>Cajamar - SP"
        )
    )
    .addTo(mapa);


// =====================================================
// ATUALIZAR CARD DE ROTA
// =====================================================

function atualizarCard(
    titulo,
    distancia,
    tempo
) {

    const tituloElemento =
        document.getElementById("route-title");

    const distanciaElemento =
        document.getElementById("route-distance");

    const tempoElemento =
        document.getElementById("route-time");


    if (tituloElemento) {

        tituloElemento.textContent =
            titulo;
    }


    if (distanciaElemento) {

        distanciaElemento.textContent =
            distancia;
    }


    if (tempoElemento) {

        tempoElemento.textContent =
            tempo;
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

    atualizarCard(
        "Calculando rota...",
        "--",
        "--"
    );


    try {

        const url =
            `https://api.mapbox.com/directions/v5/mapbox/driving/` +
            `${inicioLng},${inicioLat};` +
            `${destinoLng},${destinoLat}` +
            `?geometries=geojson` +
            `&overview=full` +
            `&steps=false` +
            `&access_token=${mapboxgl.accessToken}`;


        const resposta =
            await fetch(url);


        if (!resposta.ok) {

            throw new Error(
                "Erro ao calcular rota: " +
                resposta.status
            );
        }


        const dados =
            await resposta.json();


        if (
            !dados.routes ||
            !dados.routes.length
        ) {

            atualizarCard(
                "Rota não encontrada",
                "--",
                "--"
            );

            return;
        }


        const rota =
            dados.routes[0];


        // =============================================
        // DISTÂNCIA
        // =============================================

        const distanciaKm =
            (rota.distance / 1000).toFixed(1);


        // =============================================
        // TEMPO
        // =============================================

        const tempoMin =
            Math.round(
                rota.duration / 60
            );


        // =============================================
        // ATUALIZAR CARD
        // =============================================

        atualizarCard(
            "Rota encontrada",
            distanciaKm + " km",
            tempoMin + " min"
        );


        // =============================================
        // REMOVER ROTA ANTIGA
        // =============================================

        if (mapa.getSource("rota")) {

            if (
                mapa.getLayer("rota")
            ) {

                mapa.removeLayer("rota");
            }

            mapa.removeSource("rota");
        }


        // =============================================
        // ADICIONAR ROTA
        // =============================================

        mapa.addSource(
            "rota",
            {

                type: "geojson",

                data: {

                    type: "Feature",

                    properties: {},

                    geometry:
                        rota.geometry
                }
            }
        );


        mapa.addLayer({

            id: "rota",

            type: "line",

            source: "rota",

            layout: {

                "line-join":
                    "round",

                "line-cap":
                    "round"
            },

            paint: {

                "line-color":
                    "#111111",

                "line-width":
                    7,

                "line-opacity":
                    0.9
            }
        });


        // =============================================
        // ENQUADRAR ROTA
        // =============================================

        const coordenadas =
            rota.geometry.coordinates;


        const limites =
            coordenadas.reduce(

                (
                    bounds,
                    coordenada
                ) => {

                    return bounds.extend(
                        coordenada
                    );

                },

                new mapboxgl.LngLatBounds(
                    coordenadas[0],
                    coordenadas[0]
                )
            );


        mapa.fitBounds(
            limites,
            {

                padding: 80,

                duration: 1000
            }
        );

    }

    catch (erro) {

        console.error(
            "Erro ao calcular rota:",
            erro
        );


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

        alert(
            "Seu navegador não suporta localização."
        );

        return;
    }


    navigator.geolocation.getCurrentPosition(

        function (position) {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;


            // =========================================
            // REMOVER MARCADOR ANTIGO
            // =========================================

            if (marcadorUsuario) {

                marcadorUsuario.remove();
            }


            // =========================================
            // CRIAR MARCADOR DO USUÁRIO
            // =========================================

            marcadorUsuario =
                new mapboxgl.Marker({

                    color: "#1473e6"

                })

                    .setLngLat([
                        longitude,
                        latitude
                    ])

                    .setPopup(

                        new mapboxgl.Popup()
                            .setHTML(
                                "<strong>Você está aqui</strong>"
                            )
                    )

                    .addTo(mapa);


            // =========================================
            // CENTRALIZAR NO USUÁRIO
            // =========================================

            mapa.flyTo({

                center: [
                    longitude,
                    latitude
                ],

                zoom: 15,

                duration: 1200
            });


            // =========================================
            // ROTA ATÉ A INSTITUIÇÃO
            // =========================================

            criarRota(

                longitude,
                latitude,

                INSTITUICAO[0],
                INSTITUICAO[1]
            );
        },


        function (erro) {

            console.error(
                "Erro de localização:",
                erro
            );


            alert(
                "Não foi possível acessar sua localização. " +
                "Verifique a permissão do navegador."
            );
        },


        {

            enableHighAccuracy:
                true,

            timeout:
                10000,

            maximumAge:
                0
        }
    );
}


// =====================================================
// BOTÃO MINHA LOCALIZAÇÃO
// =====================================================

const botaoLocalizacao =
    document.getElementById(
        "location-button"
    );


if (botaoLocalizacao) {

    botaoLocalizacao.addEventListener(
        "click",
        localizarUsuario
    );
}


// =====================================================
// PESQUISAR ENDEREÇO
// =====================================================

async function pesquisarEndereco() {

    const campo =
        document.getElementById(
            "address-search"
        );


    if (!campo) {

        console.error(
            "Campo address-search não encontrado."
        );

        return;
    }


    const endereco =
        campo.value.trim();


    if (!endereco) {

        alert(
            "Digite um endereço."
        );

        return;
    }


    atualizarCard(
        "Pesquisando endereço...",
        "--",
        "--"
    );


    try {

        const resposta =
            await fetch(

                "https://nominatim.openstreetmap.org/search" +

                "?format=json" +

                "&limit=1" +

                "&countrycodes=br" +

                "&q=" +
                encodeURIComponent(
                    endereco
                )
            );


        if (!resposta.ok) {

            throw new Error(
                "Erro HTTP: " +
                resposta.status
            );
        }


        const dados =
            await resposta.json();


        if (!dados.length) {

            atualizarCard(
                "Endereço não encontrado",
                "--",
                "--"
            );

            alert(
                "Endereço não encontrado."
            );

            return;
        }


        const latitude =
            parseFloat(
                dados[0].lat
            );


        const longitude =
            parseFloat(
                dados[0].lon
            );


        // =============================================
        // VERIFICAR SE ESTÁ NA ÁREA DE CAJAMAR
        // =============================================

        if (
            !pontoDentroDeCajamar(
                longitude,
                latitude
            )
        ) {

            atualizarCard(
                "Fora da área de Cajamar",
                "--",
                "--"
            );

            alert(
                "Esse endereço está fora da área permitida de Cajamar."
            );

            return;
        }


        // =============================================
        // REMOVER DESTINO ANTIGO
        // =============================================

        if (marcadorDestino) {

            marcadorDestino.remove();
        }


        // =============================================
        // CRIAR DESTINO
        // =============================================

        marcadorDestino =
            new mapboxgl.Marker({

                color: "#e53935"

            })

                .setLngLat([
                    longitude,
                    latitude
                ])

                .setPopup(

                    new mapboxgl.Popup()
                        .setHTML(
                            "<strong>Destino</strong><br>" +
                            dados[0].display_name
                        )
                )

                .addTo(mapa);


        marcadorDestino.togglePopup();


        // =============================================
        // CRIAR ROTA
        // =============================================

        if (marcadorUsuario) {

            const posicao =
                marcadorUsuario.getLngLat();


            criarRota(

                posicao.lng,
                posicao.lat,

                longitude,
                latitude
            );

        }

        else {

            criarRota(

                INSTITUICAO[0],
                INSTITUICAO[1],

                longitude,
                latitude
            );
        }

    }

    catch (erro) {

        console.error(
            "Erro ao pesquisar endereço:",
            erro
        );


        atualizarCard(
            "Erro na pesquisa",
            "--",
            "--"
        );


        alert(
            "Erro ao pesquisar o endereço."
        );
    }
}


// =====================================================
// BOTÃO PESQUISAR
// =====================================================

const botaoPesquisa =
    document.getElementById(
        "search-button"
    );


if (botaoPesquisa) {

    botaoPesquisa.addEventListener(
        "click",
        pesquisarEndereco
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
// CLIQUE NO MAPA
// =====================================================

mapa.on("click", function (evento) {

    const longitude = evento.lngLat.lng;
    const latitude = evento.lngLat.lat;


    // =============================================
    // VERIFICAR LIMITE DE CAJAMAR
    // =============================================

    if (!pontoDentroDeCajamar(longitude, latitude)) {

        alert(
            "Selecione um ponto dentro da área de Cajamar."
        );

        return;
    }


    // =============================================
    // REMOVER DESTINO ANTIGO
    // =============================================

    if (marcadorDestino) {
        marcadorDestino.remove();
    }


    // =============================================
    // CRIAR NOVO DESTINO
    // =============================================

    marcadorDestino = new mapboxgl.Marker({
        color: "#e53935"
    })
        .setLngLat([
            longitude,
            latitude
        ])
        .setPopup(
            new mapboxgl.Popup()
                .setHTML(
                    "<strong>Destino selecionado</strong>"
                )
        )
        .addTo(mapa);


    marcadorDestino.togglePopup();


    // =============================================
    // CRIAR ROTA
    // =============================================

    if (marcadorUsuario) {

        const posicao =
            marcadorUsuario.getLngLat();

        criarRota(
            posicao.lng,
            posicao.lat,
            longitude,
            latitude
        );

    } else {

        criarRota(
            INSTITUICAO[0],
            INSTITUICAO[1],
            longitude,
            latitude
        );

    }

});


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
        console.warn("CEP inválido:", oportunidade.escola, cep);
        return;
    }

    const endereco = [
        oportunidade.endereco,
        oportunidade.bairro,
        oportunidade.municipio,
        "São Paulo",
        "Brasil"
    ].filter(Boolean).join(", ");

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
            url.searchParams.set("access_token", mapboxgl.accessToken);

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
                console.warn("Endereço não encontrado:", consulta);
                continue;
            }

            const [longitude, latitude] = local.geometry.coordinates;

            if (!pontoDentroDeCajamar(longitude, latitude)) {
                console.warn(
                    "Localização fora dos limites definidos:",
                    consulta,
                    longitude,
                    latitude
                );
                continue;
            }

            const conteudo = document.createElement("div");

            conteudo.style.minWidth = "220px";
            conteudo.style.maxWidth = "280px";
            conteudo.style.fontFamily = "Arial, sans-serif";

            const titulo = document.createElement("h3");
            titulo.textContent = oportunidade.escola || "Escola";
            titulo.style.margin = "0 0 10px";
            titulo.style.fontSize = "16px";

            conteudo.appendChild(titulo);

            const enderecoTexto = document.createElement("p");
            enderecoTexto.textContent =
                oportunidade.endereco || "Endereço não informado";

            enderecoTexto.style.margin = "5px 0";

            conteudo.appendChild(enderecoTexto);

            const bairroTexto = document.createElement("p");
            bairroTexto.textContent =
                "Bairro: " + (oportunidade.bairro || "Não informado");

            bairroTexto.style.margin = "5px 0";

            conteudo.appendChild(bairroTexto);

            const cepTexto = document.createElement("p");
            cepTexto.textContent =
                "CEP: " + (oportunidade.cep || "Não informado");

            cepTexto.style.margin = "5px 0";

            conteudo.appendChild(cepTexto);

            const botao = document.createElement("button");

            botao.type = "button";
            botao.textContent = "Traçar rota até esta escola";

            botao.style.padding = "10px";
            botao.style.marginTop = "10px";
            botao.style.width = "100%";
            botao.style.cursor = "pointer";

            botao.addEventListener("click", () => {
                if (!navigator.geolocation) {
                    alert("Seu navegador não oferece suporte à localização.");
                    return;
                }

                botao.disabled = true;
                botao.textContent = "Obtendo localização...";

                navigator.geolocation.getCurrentPosition(
                    async (posicao) => {
                        try {
                            await criarRota(
                                posicao.coords.longitude,
                                posicao.coords.latitude,
                                longitude,
                                latitude
                            );
                        } catch (erro) {
                            console.error("Erro ao traçar rota:", erro);
                            alert("Não foi possível traçar a rota.");
                        } finally {
                            botao.disabled = false;
                            botao.textContent = "Traçar rota até esta escola";
                        }
                    },
                    (erro) => {
                        console.error("Erro de localização:", erro);

                        alert(
                            "Não foi possível obter sua localização. " +
                            "Verifique a permissão do navegador."
                        );

                        botao.disabled = false;
                        botao.textContent = "Traçar rota até esta escola";
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            });

            conteudo.appendChild(botao);

            conteudo.appendChild(botao);

            new mapboxgl.Marker({ color: "#16803c" })
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
            console.error("Erro ao localizar escola:", consulta, erro);
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
            throw new Error(`Erro HTTP ${resposta.status}`);
        }

        const dados = await resposta.json();
        const oportunidades = dados.oportunidades || [];

        console.log("Oportunidades recebidas:", oportunidades);

        if (oportunidades.length === 0) {
            console.warn("A API não retornou oportunidades.");
            return;
        }

        for (const oportunidade of oportunidades) {
            await localizarEscolaPorCEP(oportunidade);
        }

        console.log("Finalizado o carregamento das escolas.");
    } catch (erro) {
        console.error("Erro ao carregar escolas:", erro);
    }
}


// Executar somente uma vez, quando o mapa estiver pronto.
mapa.once("load", carregarEscolasNoMapa);