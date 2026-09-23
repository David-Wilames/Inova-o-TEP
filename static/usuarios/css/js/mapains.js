/* =====================================================
CONFIGURAÇÃO
===================================================== */

const INSTITUICAO = [-23.3561, -46.8769];

const LIMITES_CAJAMAR = [
[-23.50, -47.05],
[-23.20, -46.70]
];

let mapa;
let marcadorInstituicao = null;
let marcadorUsuario = null;
let marcadorDestino = null;
let circuloUsuario = null;
let controleRota = null;

/* =====================================================
CRIAR MAPA
===================================================== */

mapa = L.map("map", {
zoomControl: false,
maxBounds: LIMITES_CAJAMAR,
maxBoundsViscosity: 1.0
}).setView(INSTITUICAO, 14);

/* =====================================================
MAPA CARTO
===================================================== */

L.tileLayer(
"https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
{
attribution: "© OpenStreetMap contributors © CARTO",
subdomains: "abcd",
maxZoom: 20
}
).addTo(mapa);

/* =====================================================
CONTROLE DE ZOOM
===================================================== */

L.control.zoom({
position: "bottomright"
}).addTo(mapa);

/* =====================================================
MARCADOR DA INSTITUIÇÃO
===================================================== */

marcadorInstituicao = L.marker(INSTITUICAO)
.addTo(mapa);

marcadorInstituicao.bindPopup(
"<strong>Sua instituição</strong><br>Cajamar - SP"
);

/* =====================================================
ATUALIZAR CARD
===================================================== */

function atualizarCard(titulo, distancia, tempo) {

const tituloElemento =
    document.getElementById("route-title");

const distanciaElemento =
    document.getElementById("route-distance");

const tempoElemento =
    document.getElementById("route-time");

if (tituloElemento) {
    tituloElemento.innerText = titulo;
}

if (distanciaElemento) {
    distanciaElemento.innerText = distancia;
}

if (tempoElemento) {
    tempoElemento.innerText = tempo;
}

}

/* =====================================================
CRIAR ROTA
===================================================== */

function criarRota(
inicioLat,
inicioLng,
destinoLat,
destinoLng
) {

if (controleRota) {
    mapa.removeControl(controleRota);
    controleRota = null;
}

atualizarCard(
    "Calculando rota...",
    "--",
    "--"
);

controleRota = L.Routing.control({

    waypoints: [
        L.latLng(
            inicioLat,
            inicioLng
        ),

        L.latLng(
            destinoLat,
            destinoLng
        )
    ],

    routeWhileDragging: false,
    showAlternatives: false,
    addWaypoints: false,
    draggableWaypoints: false,
    fitSelectedRoutes: true,

    language: "pt-BR",

    createMarker: function () {
        return null;
    },

    lineOptions: {
        styles: [
            {
                color: "#ffffff",
                opacity: 0.9,
                weight: 10
            },
            {
                color: "#111111",
                opacity: 0.95,
                weight: 7
            }
        ]
    },

    show: false

}).addTo(mapa);


/* =================================================
   ROTA ENCONTRADA
================================================= */

controleRota.on(
    "routesfound",
    function (evento) {

        const rota = evento.routes[0];

        const distancia = (
            rota.summary.totalDistance / 1000
        ).toFixed(1);

        const tempo = Math.round(
            rota.summary.totalTime / 60
        );

        atualizarCard(
            "Rota encontrada",
            distancia + " km",
            tempo + " min"
        );
    }
);


/* =================================================
   ERRO
================================================= */

controleRota.on(
    "routingerror",
    function () {

        atualizarCard(
            "Não foi possível calcular",
            "--",
            "--"
        );
    }
);

}

/* =====================================================
LOCALIZAÇÃO DO USUÁRIO
===================================================== */

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


        /* Remove marcador antigo */

        if (marcadorUsuario) {
            mapa.removeLayer(
                marcadorUsuario
            );
        }

        if (circuloUsuario) {
            mapa.removeLayer(
                circuloUsuario
            );
        }


        /* PONTO AZUL */

        marcadorUsuario =
            L.circleMarker(
                [
                    latitude,
                    longitude
                ],
                {
                    radius: 9,
                    color: "#ffffff",
                    weight: 3,
                    fillColor: "#1473e6",
                    fillOpacity: 1
                }
            ).addTo(mapa);


        marcadorUsuario.bindPopup(
            "<strong>Você está aqui</strong>"
        );


        /* CÍRCULO DE PRECISÃO */

        circuloUsuario =
            L.circle(
                [
                    latitude,
                    longitude
                ],
                {
                    radius:
                        position.coords.accuracy || 100,

                    color: "#1473e6",

                    fillColor: "#1473e6",

                    fillOpacity: 0.08,

                    weight: 1
                }
            ).addTo(mapa);


        /* CENTRALIZAR */

        mapa.setView(
            [
                latitude,
                longitude
            ],
            15
        );


        /* ROTA ATÉ A INSTITUIÇÃO */

        criarRota(
            latitude,
            longitude,
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
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
    }
);

}

/* =====================================================
BOTÃO MINHA LOCALIZAÇÃO
===================================================== */

const botaoLocalizacao =
document.getElementById("location-button");

if (botaoLocalizacao) {

botaoLocalizacao.addEventListener(
    "click",
    localizarUsuario
);

}

/* =====================================================
PESQUISA DE ENDEREÇO
===================================================== */

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
    "Pesquisando...",
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
            encodeURIComponent(endereco)
        );


    if (!resposta.ok) {

        throw new Error(
            "Erro HTTP: " + resposta.status
        );
    }


    const dados =
        await resposta.json();


    if (!dados.length) {

        alert(
            "Endereço não encontrado."
        );

        atualizarCard(
            "Endereço não encontrado",
            "--",
            "--"
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


    /* REMOVE DESTINO ANTIGO */

    if (marcadorDestino) {

        mapa.removeLayer(
            marcadorDestino
        );
    }


    /* NOVO MARCADOR */

    marcadorDestino =
        L.marker(
            [
                latitude,
                longitude
            ]
        ).addTo(mapa);


    marcadorDestino.bindPopup(
        "<strong>Destino</strong>"
    ).openPopup();


    /* CENTRALIZAR */

    mapa.setView(
        [
            latitude,
            longitude
        ],
        16
    );


    /* CRIAR ROTA */

    if (marcadorUsuario) {

        const pos =
            marcadorUsuario.getLatLng();

        criarRota(
            pos.lat,
            pos.lng,
            latitude,
            longitude
        );

    } else {

        criarRota(
            INSTITUICAO[0],
            INSTITUICAO[1],
            latitude,
            longitude
        );
    }

}

catch (erro) {

    console.error(
        "Erro ao pesquisar endereço:",
        erro
    );

    alert(
        "Erro ao pesquisar o endereço."
    );
}

}

/* =====================================================
BOTÃO PESQUISAR
===================================================== */

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

/* =====================================================
ENTER NA PESQUISA
===================================================== */

const campoPesquisa =
document.getElementById(
"address-search"
);

if (campoPesquisa) {

campoPesquisa.addEventListener(
    "keydown",
    function (evento) {

        if (evento.key === "Enter") {

            evento.preventDefault();

            pesquisarEndereco();
        }
    }
);


}

/* =====================================================
CLICAR NO MAPA
===================================================== */

mapa.on(
"click",
function (evento) {


    const latitude =
        evento.latlng.lat;

    const longitude =
        evento.latlng.lng;


    /* Remove marcador antigo */

    if (marcadorDestino) {

        mapa.removeLayer(
            marcadorDestino
        );
    }


    /* Novo destino */

    marcadorDestino =
        L.marker(
            [
                latitude,
                longitude
            ]
        ).addTo(mapa);


    marcadorDestino.bindPopup(
        "<strong>Destino selecionado</strong>"
    ).openPopup();


    /* CRIAR ROTA */

    if (marcadorUsuario) {

        const pos =
            marcadorUsuario.getLatLng();

        criarRota(
            pos.lat,
            pos.lng,
            latitude,
            longitude
        );

    } else {

        criarRota(
            INSTITUICAO[0],
            INSTITUICAO[1],
            latitude,
            longitude
        );
    }
}


);

/* =====================================================
CORRIGIR TAMANHO DO MAPA
===================================================== */

setTimeout(
function () {


    mapa.invalidateSize();

},
400


);
