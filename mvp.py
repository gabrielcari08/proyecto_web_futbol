# Lista simulada de jugadores (simula ser un JSON)
jugadores = [
    {"id": 1, "nombre": "A. Gómez", "club": "River", "posicion": "Delantero"},
    {"id": 2, "nombre": "F. Pérez", "club": "Boca", "posicion": "Mediocampista"},
    {"id": 3, "nombre": "L. Rodríguez", "club": "Racing", "posicion": "Defensor"},
    {"id": 4, "nombre": "M. Arias", "club": "Racing", "posicion": "Arquero"},
    {"id": 5, "nombre": "J. Ramírez", "club": "Independiente", "posicion": "Delantero"},
    {"id": 6, "nombre": "C. Domínguez", "club": "Lanús", "posicion": "Mediocampista"},
    {"id": 7, "nombre": "E. Díaz", "club": "Huracán", "posicion": "Defensor"},
    {"id": 8, "nombre": "G. Rojas", "club": "San Lorenzo", "posicion": "Defensor"},
    {"id": 9, "nombre": "N. De la Cruz", "club": "River", "posicion": "Mediocampista"},
    {"id": 10, "nombre": "A. Barco", "club": "River", "posicion": "Delantero"},
    {"id": 11, "nombre": "S. Romero", "club": "Boca", "posicion": "Arquero"},
    {"id": 12, "nombre": "M. Rojas", "club": "Racing", "posicion": "Mediocampista"},
    {"id": 13, "nombre": "P. Guerrero", "club": "Independiente", "posicion": "Delantero"},
    {"id": 14, "nombre": "T. Belmonte", "club": "Estudiantes", "posicion": "Mediocampista"},
    {"id": 15, "nombre": "G. Piovi", "club": "Racing", "posicion": "Defensor"}
]

print("--Lista de jugadores disponibles--")
for jugador in jugadores:
    print(f"{jugador['id']} - {jugador['nombre']} - {jugador['club']} - {jugador['posicion']}")
        
jugadores_por_id = {}
for jugador in jugadores:
    jugadores_por_id[jugador['id']] = jugador

equipo_usuario = []

print("\nSelecciona los jugadores que quieres escribiendo su ID\n")

while len(equipo_usuario) < 11:
    try:
        entrada = int(input("Seleccioná el ID del jugador que queres: "))
        if entrada not in jugadores_por_id:
            print("Este jugador no existe, elige otro.")
        elif jugadores_por_id[entrada] in equipo_usuario:
            print("Ya añadiste a este jugador. Adhiere otro")
        else:
            equipo_usuario.append(jugadores_por_id[entrada])
    except ValueError:
        print("Ingresa un numero valido")
        
print("\nEquipo titular\n")
for j in equipo_usuario:
    print(f"- {j['nombre']} ({j['club']} - {j['posicion']})")
    
    
equipo_guardado = []

for jugador in equipo_usuario:
    equipo_guardado.append({
        "id": jugador['id'],
        "nombre": jugador['nombre'],
        "club": jugador['club'],
        "posicion": jugador['posicion'],
        "goles": 0,
        "asistencias": 0,
        "tarjetas": 0,
        "puntaje": 0
    })

print("\nEste es tu equipo guardado\n")
for j in equipo_guardado:
    print(f" - {j["nombre"]} ({j['club']}) - Goles: {j["goles"]} Asist: {j["asistencias"]} T: {j["tarjetas"]} PF: {j["puntaje"]}")


valor_goles = 4
valor_asistencias = 2
valor_tarjetas = -1

print("\nRendimiento de tus jugadores\n")

for jugador in equipo_guardado:
    
    try:
        goles = int(input("Goles: "))
        asistencias = int(input("Asistencias: "))
        tarjetas = int(input("Tarjetas: "))
        
        #Almacenar estos resultados
        jugador["goles"] = goles
        jugador["asistencias"] = asistencias
        jugador["tarjetas"] = tarjetas
        
        jugador["puntos"] = (
            goles * valor_goles +
            asistencias * valor_asistencias +
            tarjetas * valor_tarjetas
        )
    except ValueError:
        print("Se esperaba un numero.")

print("\nPuntaje final\n") 
total_equipo = 0
for j in equipo_guardado:
    print(f"{j['nombre']}: {j['puntos']} pts (G: {j['goles']} / A: {j['asistencias']} / T: {j['tarjetas']})")
    total_equipo += j["puntos"]

print(f"\nTOTAL DEL EQUIPO: {total_equipo} puntos")
    
    