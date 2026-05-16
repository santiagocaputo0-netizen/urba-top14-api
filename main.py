from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup
import json
import os
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

app = FastAPI(title="URBA Top 14 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Archivo local donde guardamos los datos scrapeados
DATA_FILE = "data.json"

# ─── Datos base del fixture ───
FIXTURE = [
    # FECHA 1 - 14 Mar
    {"fecha": 1, "fecha_str": "14 Mar 2026", "local": "La Plata", "visitante": "Atl. del Rosario"},
    {"fecha": 1, "fecha_str": "14 Mar 2026", "local": "Hindú", "visitante": "Los Tilos"},
    {"fecha": 1, "fecha_str": "14 Mar 2026", "local": "Champagnat", "visitante": "CASI"},
    {"fecha": 1, "fecha_str": "14 Mar 2026", "local": "Alumni", "visitante": "CUBA"},
    {"fecha": 1, "fecha_str": "14 Mar 2026", "local": "Newman", "visitante": "Buenos Aires C&RC"},
    {"fecha": 1, "fecha_str": "14 Mar 2026", "local": "SIC", "visitante": "Belgrano Athletic"},
    {"fecha": 1, "fecha_str": "14 Mar 2026", "local": "Los Matreros", "visitante": "Regatas BV"},
    # FECHA 2 - 21 Mar
    {"fecha": 2, "fecha_str": "21 Mar 2026", "local": "Belgrano Athletic", "visitante": "Newman"},
    {"fecha": 2, "fecha_str": "21 Mar 2026", "local": "Buenos Aires C&RC", "visitante": "Alumni"},
    {"fecha": 2, "fecha_str": "21 Mar 2026", "local": "CUBA", "visitante": "Champagnat"},
    {"fecha": 2, "fecha_str": "21 Mar 2026", "local": "CASI", "visitante": "Hindú"},
    {"fecha": 2, "fecha_str": "21 Mar 2026", "local": "Los Tilos", "visitante": "La Plata"},
    {"fecha": 2, "fecha_str": "21 Mar 2026", "local": "Atl. del Rosario", "visitante": "Regatas BV"},
    {"fecha": 2, "fecha_str": "21 Mar 2026", "local": "SIC", "visitante": "Los Matreros"},
    # FECHA 3 - 28 Mar
    {"fecha": 3, "fecha_str": "28 Mar 2026", "local": "Regatas BV", "visitante": "Los Tilos"},
    {"fecha": 3, "fecha_str": "28 Mar 2026", "local": "La Plata", "visitante": "CASI"},
    {"fecha": 3, "fecha_str": "28 Mar 2026", "local": "Hindú", "visitante": "CUBA"},
    {"fecha": 3, "fecha_str": "28 Mar 2026", "local": "Champagnat", "visitante": "Buenos Aires C&RC"},
    {"fecha": 3, "fecha_str": "28 Mar 2026", "local": "Alumni", "visitante": "Belgrano Athletic"},
    {"fecha": 3, "fecha_str": "28 Mar 2026", "local": "Newman", "visitante": "SIC"},
    {"fecha": 3, "fecha_str": "28 Mar 2026", "local": "Los Matreros", "visitante": "Atl. del Rosario"},
    # FECHA 4 - 11 Abr
    {"fecha": 4, "fecha_str": "11 Abr 2026", "local": "SIC", "visitante": "Alumni"},
    {"fecha": 4, "fecha_str": "11 Abr 2026", "local": "Belgrano Athletic", "visitante": "Buenos Aires C&RC"},
    {"fecha": 4, "fecha_str": "11 Abr 2026", "local": "Buenos Aires C&RC", "visitante": "Hindú"},
    {"fecha": 4, "fecha_str": "11 Abr 2026", "local": "CUBA", "visitante": "La Plata"},
    {"fecha": 4, "fecha_str": "11 Abr 2026", "local": "CASI", "visitante": "Regatas BV"},
    {"fecha": 4, "fecha_str": "11 Abr 2026", "local": "Los Tilos", "visitante": "Atl. del Rosario"},
    {"fecha": 4, "fecha_str": "11 Abr 2026", "local": "Newman", "visitante": "Los Matreros"},
    # FECHA 5 - 18 Abr
    {"fecha": 5, "fecha_str": "18 Abr 2026", "local": "Atl. del Rosario", "visitante": "CASI"},
    {"fecha": 5, "fecha_str": "18 Abr 2026", "local": "Regatas BV", "visitante": "CUBA"},
    {"fecha": 5, "fecha_str": "18 Abr 2026", "local": "La Plata", "visitante": "Buenos Aires C&RC"},
    {"fecha": 5, "fecha_str": "18 Abr 2026", "local": "Hindú", "visitante": "Belgrano Athletic"},
    {"fecha": 5, "fecha_str": "18 Abr 2026", "local": "Alumni", "visitante": "Newman"},
    {"fecha": 5, "fecha_str": "18 Abr 2026", "local": "SIC", "visitante": "Champagnat"},
    {"fecha": 5, "fecha_str": "18 Abr 2026", "local": "Los Tilos", "visitante": "Los Matreros"},
    # FECHA 6 - 25 Abr
    {"fecha": 6, "fecha_str": "25 Abr 2026", "local": "Newman", "visitante": "Champagnat"},
    {"fecha": 6, "fecha_str": "25 Abr 2026", "local": "SIC", "visitante": "Hindú"},
    {"fecha": 6, "fecha_str": "25 Abr 2026", "local": "Belgrano Athletic", "visitante": "La Plata"},
    {"fecha": 6, "fecha_str": "25 Abr 2026", "local": "Buenos Aires C&RC", "visitante": "Regatas BV"},
    {"fecha": 6, "fecha_str": "25 Abr 2026", "local": "CASI", "visitante": "Los Tilos"},
    {"fecha": 6, "fecha_str": "25 Abr 2026", "local": "CUBA", "visitante": "Atl. del Rosario"},
    {"fecha": 6, "fecha_str": "25 Abr 2026", "local": "Alumni", "visitante": "Los Matreros"},
    # FECHA 7 - 9 May
    {"fecha": 7, "fecha_str": "9 May 2026", "local": "Los Tilos", "visitante": "CUBA"},
    {"fecha": 7, "fecha_str": "9 May 2026", "local": "Atl. del Rosario", "visitante": "Buenos Aires C&RC"},
    {"fecha": 7, "fecha_str": "9 May 2026", "local": "Regatas BV", "visitante": "Belgrano Athletic"},
    {"fecha": 7, "fecha_str": "9 May 2026", "local": "La Plata", "visitante": "SIC"},
    {"fecha": 7, "fecha_str": "9 May 2026", "local": "Hindú", "visitante": "Newman"},
    {"fecha": 7, "fecha_str": "9 May 2026", "local": "Champagnat", "visitante": "Alumni"},
    {"fecha": 7, "fecha_str": "9 May 2026", "local": "Los Matreros", "visitante": "CASI"},
    # FECHA 8 - 16 May
    {"fecha": 8, "fecha_str": "16 May 2026", "local": "Alumni", "visitante": "Hindú"},
    {"fecha": 8, "fecha_str": "16 May 2026", "local": "Newman", "visitante": "SIC"},
    {"fecha": 8, "fecha_str": "16 May 2026", "local": "Belgrano Athletic", "visitante": "Atl. del Rosario"},
    {"fecha": 8, "fecha_str": "16 May 2026", "local": "Buenos Aires C&RC", "visitante": "Los Tilos"},
    {"fecha": 8, "fecha_str": "16 May 2026", "local": "CUBA", "visitante": "CASI"},
    {"fecha": 8, "fecha_str": "16 May 2026", "local": "Champagnat", "visitante": "Los Matreros"},
]

RESULTADOS_CONOCIDOS = {
    "Hindú_Los Tilos_1": {"local": 52, "visitante": 18},
    "Champagnat_CASI_1": {"local": 16, "visitante": 40},
    "Alumni_CUBA_1": {"local": 27, "visitante": 25},
    "Newman_Buenos Aires C&RC_1": {"local": 31, "visitante": 3},
    "SIC_Belgrano Athletic_1": {"local": 58, "visitante": 18},
    "Belgrano Athletic_Newman_2": {"local": 25, "visitante": 33},
    "Buenos Aires C&RC_Alumni_2": {"local": 20, "visitante": 15},
    "CUBA_Champagnat_2": {"local": 25, "visitante": 29},
    "CASI_Hindú_2": {"local": 12, "visitante": 15},
    "Los Tilos_La Plata_2": {"local": 17, "visitante": 13},
    "Atl. del Rosario_Regatas BV_2": {"local": 12, "visitante": 20},
    "SIC_Los Matreros_2": {"local": 25, "visitante": 20},
    "Regatas BV_Los Tilos_3": {"local": 29, "visitante": 20},
    "La Plata_CASI_3": {"local": 13, "visitante": 39},
    "Hindú_CUBA_3": {"local": 43, "visitante": 36},
    "Champagnat_Buenos Aires C&RC_3": {"local": 13, "visitante": 10},
    "Alumni_Belgrano Athletic_3": {"local": 26, "visitante": 21},
    "Newman_SIC_3": {"local": 10, "visitante": 37},
    "Los Matreros_Atl. del Rosario_3": {"local": 25, "visitante": 22},
    "SIC_Alumni_4": {"local": 33, "visitante": 23},
    "Buenos Aires C&RC_Hindú_4": {"local": 12, "visitante": 32},
    "CUBA_La Plata_4": {"local": 33, "visitante": 35},
    "CASI_Regatas BV_4": {"local": 38, "visitante": 14},
    "Los Tilos_Atl. del Rosario_4": {"local": 32, "visitante": 39},
    "Newman_Los Matreros_4": {"local": 52, "visitante": 28},
    "Atl. del Rosario_CASI_5": {"local": 28, "visitante": 36},
    "Hindú_Belgrano Athletic_5": {"local": 39, "visitante": 22},
    "Alumni_Newman_5": {"local": 30, "visitante": 32},
    "SIC_Champagnat_5": {"local": 24, "visitante": 7},
    "Newman_Champagnat_6": {"local": 47, "visitante": 8},
    "SIC_Hindú_6": {"local": 31, "visitante": 32},
    "Belgrano Athletic_La Plata_6": {"local": 28, "visitante": 19},
    "Buenos Aires C&RC_Regatas BV_6": {"local": 26, "visitante": 32},
    "CASI_Los Tilos_6": {"local": 33, "visitante": 31},
    "CUBA_Atl. del Rosario_6": {"local": 41, "visitante": 17},
    "Alumni_Los Matreros_6": {"local": 18, "visitante": 23},
    "Los Tilos_CUBA_7": {"local": 33, "visitante": 42},
    "Atl. del Rosario_Buenos Aires C&RC_7": {"local": 59, "visitante": 28},
    "Regatas BV_Belgrano Athletic_7": {"local": 13, "visitante": 15},
    "La Plata_SIC_7": {"local": 31, "visitante": 38},
    "Hindú_Newman_7": {"local": 25, "visitante": 26},
    "Champagnat_Alumni_7": {"local": 7, "visitante": 76},
    "Los Matreros_CASI_7": {"local": 24, "visitante": 48},
}

# Diccionario para normalizar los nombres que vienen de ESPN a los de tu FIXTURE
MAPEO_EQUIPOS = {
    "CASI": "CASI", "Hindu": "Hindú", "Hindú": "Hindú", "SIC": "SIC", "Newman": "Newman", 
    "Alumni": "Alumni", "Regatas Bella Vista": "Regatas BV", "Regatas BV": "Regatas BV",
    "Atletico del Rosario": "Atl. del Rosario", "Atl. del Rosario": "Atl. del Rosario",
    "CUBA": "CUBA", "Los Matreros": "Los Matreros", "Champagnat": "Champagnat",
    "Los Tilos": "Los Tilos", "Belgrano": "Belgrano Athletic", "Belgrano Athletic": "Belgrano Athletic",
    "Buenos Aires C&RC": "Buenos Aires C&RC", "Buenos Aires": "Buenos Aires C&RC", "La Plata": "La Plata"
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"partidos": {}, "ultima_actualizacion": None}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_partido_key(local, visitante, fecha):
    return f"{local}_{visitante}_{fecha}"

async def scrape_espn():
    print(f"[{datetime.now()}] Iniciando scraping de ESPN Rugby...")
    data = load_data()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Mapeamos las fechas a su número correspondiente en tu torneo
    fechas_map = {
        "20260314": 1, "20260321": 2, "20260328": 3, "20260411": 4, 
        "20260418": 5, "20260425": 6, "20260509": 7, "20260516": 8
    }
    
    resultados_nuevos = 0

    # Cargar primero todo lo hardcodeado conocido por seguridad
    for key, resultado in RESULTADOS_CONOCIDOS.items():
        if key not in data["partidos"]:
            data["partidos"][key] = resultado

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for fecha_str, num_fecha in fechas_map.items():
            # Evitamos buscar fechas futuras si el raspador corre antes de tiempo
            if num_fecha > 8:
                continue
                
            url = f"https://www.espn.com.ar/rugby/resultados/_/liga/289279/fecha/{fecha_str}"
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    
                    # Estructura real de los bloques de partidos de ESPN Rugby
                    eventos = soup.select(".custom-scoreboard, .scoreboard")
                    for evento in eventos:
                        teams = [t.get_text().strip() for t in evento.select(".team-name, .ScoreCell__TeamName")]
                        scores = [s.get_text().strip() for s in evento.select(".score, .ScoreboardScoreCell__Score")]
                        
                        if len(teams) >= 2 and len(scores) >= 2:
                            # Normalizamos los nombres de los equipos según tu MAPEO_EQUIPOS
                            loc_norm = MAPEO_EQUIPOS.get(teams[0], teams[0])
                            vis_norm = MAPEO_EQUIPOS.get(teams[1], teams[1])
                            
                            # Validamos si los scores son numéricos válidos
                            if scores[0].isdigit() and scores[1].isdigit():
                                key = get_partido_key(loc_norm, vis_norm, num_fecha)
                                
                                # Guardamos el formato exacto {"local": X, "visitante": Y}
                                data["partidos"][key] = {
                                    "local": int(scores[0]),
                                    "visitante": int(scores[1])
                                }
                                resultados_nuevos += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"  Error raspando fecha {fecha_str}: {e}")

    data["ultima_actualizacion"] = datetime.now().isoformat()
    save_data(data)
    print(f"[{datetime.now()}] Scraping completado con éxito. Base de datos actualizada.")
    return data

# ─── ENDPOINTS ───────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "mensaje": "URBA Top 14 API funcionando"}

@app.get("/api/partidos")
async def get_partidos():
    data = load_data()
    partidos = []
    for p in FIXTURE:
        key = get_partido_key(p["local"], p["visitante"], p["fecha"])
        resultado = data["partidos"].get(key)
        partidos.append({
            **p,
            "resultado": resultado,
            "jugado": resultado is not None,
        })
    return {
        "partidos": partidos,
        "ultima_actualizacion": data.get("ultima_actualizacion"),
    }

@app.get("/api/partidos/fecha/{num_fecha}")
async def get_partidos_fecha(num_fecha: int):
    data = load_data()
    partidos = []
    for p in FIXTURE:
        if p["fecha"] == num_fecha:
            key = get_partido_key(p["local"], p["visitante"], p["fecha"])
            resultado = data["partidos"].get(key)
            partidos.append({
                **p,
                "resultado": resultado,
                "jugado": resultado is not None,
            })
    return {"fecha": num_fecha, "partidos": partidos}

@app.get("/api/posiciones")
async def get_posiciones():
    data = load_data()
    equipos = {}
    nombres = [
        "CASI", "Hindú", "SIC", "Newman", "Alumni", "Regatas BV",
        "Atl. del Rosario", "CUBA", "Los Matreros", "Champagnat",
        "Los Tilos", "Belgrano Athletic", "Buenos Aires C&RC", "La Plata"
    ]
    for nombre in nombres:
        equipos[nombre] = {"nombre": nombre, "pj": 0, "pg": 0, "pe": 0, "pp": 0, "pf": 0, "pc": 0, "bo": 0, "bd": 0, "pts": 0}

    for p in FIXTURE:
        key = get_partido_key(p["local"], p["visitante"], p["fecha"])
        resultado = data["partidos"].get(key)
        if resultado and p["local"] in equipos and p["visitante"] in equipos:
            local = equipos[p["local"]]
            visit = equipos[p["visitante"]]
            rl, rv = resultado["local"], resultado["visitante"]
            local["pj"] += 1; visit["pj"] += 1
            local["pf"] += rl; local["pc"] += rv
            visit["pf"] += rv; visit["pc"] += rl
            if rl > rv:
                local["pg"] += 1; local["pts"] += 4
                visit["pp"] += 1
                if rl - rv <= 7: visit["bd"] += 1; visit["pts"] += 1
            elif rv > rl:
                visit["pg"] += 1; visit["pts"] += 4
                local["pp"] += 1
                if rv - rl <= 7: local["bd"] += 1; local["pts"] += 1
            else:
                local["pe"] += 1; local["pts"] += 2
                visit["pe"] += 1; visit["pts"] += 2

    tabla = sorted(equipos.values(), key=lambda x: (-x["pts"], -(x["pf"] - x["pc"])))
    for i, e in enumerate(tabla):
        e["pos"] = i + 1
        e["dif"] = e["pf"] - e["pc"]
    return {"tabla": tabla}

@app.post("/api/actualizar")
async def forzar_actualizacion():
    await scrape_espn()
    return {"status": "ok", "mensaje": "Actualización completada"}

# ─── STARTUP ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    await scrape_espn()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scrape_espn, "interval", hours=1)
    scheduler.start()
    print("API iniciada. Scraping cada 1 hora.")
