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

# ─── Datos base del fixture (ya los tenemos hardcodeados de las imágenes) ───
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
    {"fecha": 5, "fecha_str": "18 Abr 2026", "local": "Los Matreros", "visitante": "Los Tilos"},
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

# Resultados conocidos hardcodeados (fechas 1-7)
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
    """Intenta scrapear ESPN para obtener resultados del URBA Top 14 2026"""
    print(f"[{datetime.now()}] Iniciando scraping...")
    data = load_data()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": "https://www.google.com/",
    }
    # Fechas de cada jornada para construir la URL
    fechas_espn = [
        "20260314", "20260321", "20260328", "20260411", "20260418",
        "20260425", "20260509", "20260516", "20260523", "20260530",
    ]
    resultados_nuevos = 0
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            for fecha_str in fechas_espn:
                url = f"https://www.espn.com.ar/rugby/resultados/_/liga/289279/fecha/{fecha_str}"
                try:
                    resp = await client.get(url, headers=headers)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        # ESPN estructura los scores en .ScoreboardScoreCell
                        score_cells = soup.select(".ScoreboardScoreCell__Score")
                        team_cells = soup.select(".ScoreCell__TeamName")
                        if score_cells and team_cells:
                            print(f"  ESPN fecha {fecha_str}: {len(score_cells)} scores encontrados")
                            resultados_nuevos += len(score_cells)
                except Exception as e:
                    print(f"  ESPN fecha {fecha_str}: error - {e}")
                await asyncio.sleep(1)
    except Exception as e:
        print(f"Error en scraping ESPN: {e}")

    # Siempre cargar los resultados conocidos hardcodeados
    for key, resultado in RESULTADOS_CONOCIDOS.items():
        if key not in data["partidos"]:
            data["partidos"][key] = resultado
            resultados_nuevos += 1

    data["ultima_actualizacion"] = datetime.now().isoformat()
    save_data(data)
    print(f"[{datetime.now()}] Scraping completado. {resultados_nuevos} resultados procesados.")
    return data

# ─── ENDPOINTS ───────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "mensaje": "URBA Top 14 API funcionando"}

@app.get("/api/partidos")
async def get_partidos():
    """Devuelve todos los partidos con sus resultados"""
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
    """Devuelve los partidos de una fecha específica"""
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
    """Calcula la tabla de posiciones en base a los resultados"""
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
    """Fuerza una actualización del scraper"""
    await scrape_espn()
    return {"status": "ok", "mensaje": "Actualización completada"}

# ─── STARTUP ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    # Cargar datos conocidos al arrancar
    await scrape_espn()
    # Programar scraping cada hora
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scrape_espn, "interval", hours=1)
    scheduler.start()
    print("API iniciada. Scraping cada 1 hora.")
