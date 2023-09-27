
from fastapi import FastAPI, HTTPException, Request,Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import math
from operator import itemgetter
templates = Jinja2Templates(directory="templates")  


app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    html_content = """
    <html>
    <head>
        <title>Calcular Ruta</title>
    </head>
    <body bgcolor="green" >
        <h1>Ingresa el máximo de carga</h1>
        <form method="post" action="/vrp">
            <input type="number" id="max_carga" name="max_carga_form"><br><br>
            <input bgcolor="yellow" type="submit" value="Enviar">
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/", response_class=HTMLResponse)
async def process_form(request: Request, max_carga_form: int = Form(...)):
    html_response = f"""
    <html>
    <head>
        <title>Calcular Ruta</title>
    </head>
    <body>
        <h1>Calcular Ruta</h1>
        <p>Maximo de Carga: {max_carga_form}</p>
        <p><a href="/">Volver al formulario</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_response)

coord = {
    'JiloYork': (19.984146, -99.519127),
    'Toluca': (19.286167856525594, -99.65473296644892),
    'Atlacomulco': (19.796802401380955, -99.87643301629244),
    'Guadalajara': (20.655773344775373, -103.35773871581326),
    'Monterrey': (25.675859554333684, -100.31405053526082),
    'Cancún': (21.158135651777727, -86.85092947858692),
    'Morelia': (19.720961251258654, -101.15929186858635),
    'Aguascalientes': (21.88473831747085, -102.29198705069501),
    'Queretaro': (20.57005870003398, -100.45222862892079),
    'CDMX': (19.429550164848152, -99.13000959477478)
}

pedidos = {
    'JiloYork': 10,
    'Toluca': 15,
    'Atlacomulco': 0,
    'Guadalajara': 0,
    'Monterrey': 40,
    'Cancún': 50,
    'Morelia': 25,
    'Aguascalientes': 45,
    'CDMX': 60,
    'Queretaro': 100
}

almacen = (40.23, -3.40)

@app.get("/a")
def index():
    return "¡API VRP funcionando!"

@app.post("/vrp")
def vrp_route(request: Request, max_carga_form: int = Form (None)):
    max_carga = max_carga_form  # El parámetro max_carga se obtiene de la URL
    # Resto del código se mantiene igual
    def distancia(coord1, coord2):
        lat1 = coord1[0]
        lon1 = coord1[1]
        lat2 = coord2[0]
        lon2 = coord2[1]
        return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

    def en_ruta(rutas, c):
        ruta = None
        for r in rutas:
            if c in r:
                ruta = r
        return ruta

    def peso_ruta(ruta):
        total = 0
        for c in ruta:
            total = total + pedidos[c]
        return total

    def vrp_voraz():
        s = {}
        for c1 in coord:
            for c2 in coord:
                if c1 != c2:
                    if not (c2,c1) in s:
                        d_c1_c2 = distancia(coord[c1], coord[c2])
                        d_c1_almacen = distancia(coord[c1], almacen)
                        d_c2_almacen = distancia(coord[c2], almacen)
                        s[c1,c2] = d_c1_almacen + d_c2_almacen - d_c1_c2
        
        s = sorted(s.items(), key=itemgetter(1), reverse=True)
        rutas = []

        for k,v in s:
            rc1 = en_ruta(rutas, k[0])
            rc2 = en_ruta(rutas, k[1])
            if rc1 is None and rc2 is None:
                if peso_ruta([k[0], k[1]]) <= max_carga:
                    rutas.append([k[0], k[1]])
            elif rc1 is not None and rc2 is None:
                if rc1[0] == k[0]:
                    if peso_ruta(rc1) + peso_ruta([k[1]]) <= max_carga:
                        rutas[rutas.index(rc1)].insert(0, k[1])
                elif rc1[len(rc1)-1] == k[0]:
                    if peso_ruta(rc1) + peso_ruta([k[1]]) <= max_carga:
                        rutas[rutas.index(rc1)].append(k[1])
            elif rc1 is None and rc2 is not None:
                if rc2[0] == k[1]:
                    if peso_ruta(rc2) + peso_ruta([k[0]]) <= max_carga:
                        rutas[rutas.index(rc2)].insert(0, k[0])
                elif rc2[len(rc2) - 1] == k[1]:
                    if peso_ruta(rc2) + peso_ruta([k[0]]) <= max_carga:
                        rutas[rutas.index(rc2)].append(k[0])
            elif rc1 is not None and rc2 is not None and rc1 != rc2:
                if rc1[0] == k[0] and rc2[len(rc2) -1] == k[1]:
                    if peso_ruta(rc1) + peso_ruta(rc2) <= max_carga:
                        rutas[rutas.index(rc2)].extend(rc1)
                        rutas.remove(rc1)
                elif rc1[len(rc1) -1] == k[0] and rc2 [0] == k[1]:
                    if peso_ruta(rc1) + peso_ruta(rc2) <= max_carga:
                        rutas[rutas.index(rc1)].extend(rc2)
                        rutas.remove(rc2)
        return rutas

    rutas = vrp_voraz()
    #return {"rutas": rutas}
    return templates.TemplateResponse("resultados.html", {"request": request, "max_carga": max_carga_form, "rutas": rutas})