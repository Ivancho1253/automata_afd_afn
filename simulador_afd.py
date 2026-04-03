"""
Simulador Interactivo de Autómatas Finitos Deterministas (AFD)
==============================================================
Este script permite definir formalmente un AFD, validar su determinismo,
simular el procesamiento de cadenas paso a paso y visualizar el autómata
y el camino recorrido mediante diagramas generados con Graphviz.

Dependencias:
    - pip install graphviz (Librería de Python)
    - Graphviz instalado en el sistema operativo (https://graphviz.org/download/)
"""

import graphviz  # Librería para generar los diagramas visuales (.dot y .png)
import sys       # Para funciones del sistema como sys.exit()
import os        # Para gestionar rutas de archivos y variables de entorno

# --- CONFIGURACIÓN DE RUTAS DE GRAPHVIZ ---
# Estas líneas aseguran que Python encuentre el ejecutable de Graphviz en diferentes sistemas operativos.

# Para Windows: se intenta añadir la ruta común de instalación si no está en el PATH.
_graphviz_path = r"C:\Program Files\Graphviz\bin"
if os.path.isdir(_graphviz_path) and _graphviz_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _graphviz_path + os.pathsep + os.environ.get("PATH", "")

# Para macOS: se añaden rutas comunes (Homebrew) para evitar errores de ejecución.
for _mac_path in ("/opt/homebrew/bin", "/usr/local/bin"):
    if os.path.isdir(_mac_path) and _mac_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _mac_path + os.pathsep + os.environ.get("PATH", "")


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE ENTRADA / DEFINICIÓN DEL AUTÓMATA (LA QUINTUPLA)
# ═══════════════════════════════════════════════════════════════════════════════

def ingresar_estados():
    """Solicita al usuario el conjunto de estados (Q), separados por comas."""
    while True:
        # Pide la entrada y elimina espacios en blanco extras.
        entrada = input("\n  Ingrese los estados separados por comas (ej: q0,q1,q2): ").strip()
        if not entrada:
            print("  ⚠  Debe ingresar al menos un estado.")
            continue
        
        # Divide la cadena por comas y limpia cada nombre de estado resultando en una lista.
        estados = [e.strip() for e in entrada.split(",") if e.strip()]
        
        if not estados:
            print("  ⚠  No se detectaron estados válidos.")
            continue
            
        # Comprueba que no haya nombres repetidos usando un conjunto (set).
        if len(estados) != len(set(estados)):
            print("  ⚠  Hay estados duplicados. Inténtelo de nuevo.")
            continue
        return estados


def ingresar_alfabeto():
    """Solicita al usuario el alfabeto del autómata (Σ), separado por comas."""
    while True:
        # Pide la entrada al usuario.
        entrada = input("\n  Ingrese el alfabeto separado por comas (ej: 0,1): ").strip()
        if not entrada:
            print("  ⚠  Debe ingresar al menos un símbolo.")
            continue
            
        # Genera la lista de símbolos limpiando espacios.
        alfabeto = [s.strip() for s in entrada.split(",") if s.strip()]
        
        if not alfabeto:
            print("  ⚠  No se detectaron símbolos válidos.")
            continue
            
        # Verifica que no haya símbolos repetidos.
        if len(alfabeto) != len(set(alfabeto)):
            print("  ⚠  Hay símbolos duplicados. Inténtelo de nuevo.")
            continue
        return alfabeto


def ingresar_estado_inicial(estados):
    """Solicita y valida que el estado inicial (q0) pertenezca al conjunto Q."""
    while True:
        entrada = input(f"\n  Ingrese el estado inicial (opciones: {', '.join(estados)}): ").strip()
        # Verifica si el estado escrito está en la lista de estados previamente definida.
        if entrada in estados:
            return entrada
        print(f"  ⚠  '{entrada}' no pertenece al conjunto de estados.")


def ingresar_estados_finales(estados):
    """Solicita y valida el conjunto de estados de aceptación (F)."""
    while True:
        entrada = input(f"\n  Ingrese los estados finales separados por comas (opciones: {', '.join(estados)}): ").strip()
        if not entrada:
            print("  ⚠  Debe ingresar al menos un estado final.")
            continue
            
        # Crea la lista de estados finales ingresados.
        finales = [e.strip() for e in entrada.split(",") if e.strip()]
        
        # Filtra e identifica si algún estado ingresado NO está en el conjunto general Q.
        invalidos = [e for e in finales if e not in estados]
        if invalidos:
            print(f"  ⚠  Los siguientes estados no son válidos: {', '.join(invalidos)}")
            continue
            
        # Verifica duplicados en la lista de estados finales.
        if len(finales) != len(set(finales)):
            print("  ⚠  Hay estados finales duplicados. Inténtelo de nuevo.")
            continue
        return finales


def ingresar_transiciones(estados, alfabeto):
    """
    Construye la función de transición (δ) de forma dinámica.
    Para cada par (estado_actual, símbolo) se define exactamente un (estado_destino).
    """
    print("\n  ── Función de Transición ──")
    print("  Para cada estado y símbolo, ingrese el estado destino.\n")

    transiciones = {}
    # Itera por cada estado definido.
    for estado in estados:
        transiciones[estado] = {} # Crea un sub-diccionario para cada estado.
        # Itera por cada símbolo del alfabeto para cumplir con la definición de AFD (totalidad).
        for simbolo in alfabeto:
            while True:
                # Solicita a dónde va el autómata desde 'estado' leyendo 'simbolo'.
                destino = input(f"    δ({estado}, {simbolo}) = ").strip()
                # En un AFD, el destino DEBE ser uno de los estados definidos.
                if destino not in estados:
                    print(f"    ⚠  '{destino}' no pertenece al conjunto de estados. Intente de nuevo.")
                    continue
                # Guarda la transición en la estructura del diccionario.
                transiciones[estado][simbolo] = destino
                break
    return transiciones


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDACIÓN DEL AUTÓMATA
# ═══════════════════════════════════════════════════════════════════════════════

def validar_determinismo(afd):
    """
    Verifica que la función de transición sea completa:
    Cada par (estado, símbolo) debe tener una transición definida.
    """
    errores = []
    # Recorre todos los estados y símbolos posibles.
    for estado in afd["estados"]:
        for simbolo in afd["alfabeto"]:
            # Verifica si el estado existe en el diccionario de transiciones.
            if estado not in afd["transiciones"]:
                errores.append(f"  Falta la fila de transiciones para el estado '{estado}'.")
                continue
            # Verifica si hay un destino para ese símbolo específico.
            if simbolo not in afd["transiciones"][estado]:
                errores.append(f"  Falta transición: δ({estado}, {simbolo})")
    return errores


# ═══════════════════════════════════════════════════════════════════════════════
# SIMULACIÓN DE CADENAS
# ═══════════════════════════════════════════════════════════════════════════════

def simular_cadena(afd, cadena):
    """
    Simula el proceso de reconocimiento de una cadena por el AFD.
    Retorna: El camino de estados, si es aceptada, y posibles errores.
    """
    # El proceso siempre comienza en el estado inicial (q0).
    estado_actual = afd["estado_inicial"]
    camino = [estado_actual] # Guardamos el inicio como primer paso del camino.

    # Itera sobre cada símbolo de la cadena ingresada por el usuario.
    for i, simbolo in enumerate(cadena):
        # Si el símbolo no está en el alfabeto, la cadena es inválida formalmente.
        if simbolo not in afd["alfabeto"]:
            return camino, False, f"El símbolo '{simbolo}' (posición {i}) no pertenece al alfabeto."
        
        # Aplicamos la función de transición: δ(actual, símbolo) -> siguiente.
        estado_actual = afd["transiciones"][estado_actual][simbolo]
        # Registramos el nuevo estado alcanzado en el camino.
        camino.append(estado_actual)

    # La cadena se acepta si el estado final del recorrido (qf) está en el conjunto F.
    aceptada = estado_actual in afd["estados_finales"]
    return camino, aceptada, None


def mostrar_resultado(cadena, camino, aceptada, error):
    """Muestra en consola el resumen visual de la simulación."""
    print("\n  ╔══════════════════════════════════════════╗")
    print("  ║        RESULTADO DE LA SIMULACIÓN        ║")
    print("  ╠══════════════════════════════════════════╣")

    # Si hubo un error (como un símbolo fuera del alfabeto), se informa y termina.
    if error:
        print(f"  ║  ❌ Error: {error}")
        print("  ╚══════════════════════════════════════════╝")
        return

    # Si la cadena está vacía, se maneja como épsilon (ε).
    cadena_mostrar = cadena if cadena else "ε (cadena vacía)"
    print(f"  ║  Cadena: {cadena_mostrar}")
    # Une los estados del camino con flechas para visualizar el recorrido.
    print(f"  ║  Camino: {' → '.join(camino)}")

    # Veredicto final.
    if aceptada:
        print("  ║  Resultado: ✅ ACEPTADA")
    else:
        print("  ║  Resultado: ❌ RECHAZADA")

    print("  ╚══════════════════════════════════════════╝")


# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZACIÓN CON GRAPHVIZ (GENERACIÓN DE PNG)
# ═══════════════════════════════════════════════════════════════════════════════

def generar_diagrama(afd, nombre_archivo="afd", directorio="."):
    """Crea un objeto Digraph para dibujar el autómata completo."""
    dot = graphviz.Digraph(
        name="AFD",
        format="png",
        engine="dot",
        # Atributos generales del gráfico (dirección Izquierda-Derecha, resolución, etc.).
        graph_attr={
            "rankdir": "LR",
            "dpi": "150",
            "bgcolor": "white",
            "pad": "0.5",
        },
        # Estilo de los nodos (círculos, colores, tipografía).
        node_attr={
            "shape": "circle",
            "style": "filled",
            "fillcolor": "#E8F4FD",
            "color": "#2C3E50",
            "fontname": "Arial",
            "fontsize": "14",
            "penwidth": "2",
        },
        # Estilo de las flechas (aristas).
        edge_attr={
            "fontname": "Arial",
            "fontsize": "12",
            "color": "#2C3E50",
            "penwidth": "1.5",
        },
    )

    # Crea una flecha de entrada al estado inicial (nodo invisible -> inicial).
    dot.node("__inicio__", "", shape="point", width="0")
    dot.edge("__inicio__", afd["estado_inicial"], arrowsize="1.2")

    # Dibuja todos el conjunto de estados (Q).
    for estado in afd["estados"]:
        attrs = {}
        # Los estados finales (F) se dibujan con doble círculo por convención.
        if estado in afd["estados_finales"]:
            attrs["shape"] = "doublecircle"
            attrs["fillcolor"] = "#D5F5E3" # Color verde suave.
            attrs["color"] = "#1E8449"
        dot.node(estado, estado, **attrs)

    # Agrupa las transiciones para que si hay varias flechas entre los mismos nodos,
    # aparezcan como una sola flecha con etiquetas separadas por comas.
    aristas = _agrupar_transiciones(afd)
    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        dot.edge(origen, destino, label=f"  {etiqueta}  ")

    # Genera el archivo PNG final en el directorio especificado.
    ruta_completa = os.path.join(directorio, nombre_archivo)
    dot.render(ruta_completa, cleanup=True)
    return f"{ruta_completa}.png"


def generar_diagrama_con_camino(afd, camino, nombre_archivo="afd_simulacion", directorio="."):
    """Igual al anterior, pero resalta en rojo los estados y flechas usados en la simulación."""
    
    # Identifica qué nodos y qué aristas (pares origen-destino) fueron visitados.
    nodos_camino = set(camino)
    aristas_camino = set()
    for i in range(len(camino) - 1):
        aristas_camino.add((camino[i], camino[i + 1]))

    dot = graphviz.Digraph(
        name="AFD_Camino",
        format="png",
        engine="dot",
        graph_attr={"rankdir": "LR", "dpi": "150", "bgcolor": "white", "pad": "0.5"},
        node_attr={"shape": "circle", "style": "filled", "fillcolor": "#E8F4FD", "color": "#2C3E50", "fontname": "Arial", "fontsize": "14", "penwidth": "2"},
        edge_attr={"fontname": "Arial", "fontsize": "12", "color": "#2C3E50", "penwidth": "1.5"},
    )

    # Resalta la flecha de inicio si el estado inicial fue parte de la simulación.
    inicio_en_camino = afd["estado_inicial"] in nodos_camino
    color_resalte = "#E74C3C" # Color rojo.
    
    dot.node("__inicio__", "", shape="point", width="0",
             color=color_resalte if inicio_en_camino else "#2C3E50")
    dot.edge("__inicio__", afd["estado_inicial"], arrowsize="1.2",
             color=color_resalte if inicio_en_camino else "#2C3E50",
             penwidth="3" if inicio_en_camino else "1.5")

    # Dibuja nodos resaltando los visitados.
    for estado in afd["estados"]:
        attrs = {}
        esta_en_camino = estado in nodos_camino
        
        if estado in afd["estados_finales"]:
            attrs["shape"] = "doublecircle"
            if esta_en_camino:
                attrs["fillcolor"] = "#FADBD8" # Rojo suave.
                attrs["color"] = color_resalte
                attrs["penwidth"] = "3"
            else:
                attrs["fillcolor"] = "#D5F5E3"
                attrs["color"] = "#1E8449"
        elif esta_en_camino:
            attrs["fillcolor"] = "#FADBD8"
            attrs["color"] = color_resalte
            attrs["penwidth"] = "3"
        dot.node(estado, estado, **attrs)

    # Dibuja aristas resaltando las recorridas.
    aristas = _agrupar_transiciones(afd)
    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        if (origen, destino) in aristas_camino:
            dot.edge(origen, destino, label=f"  {etiqueta}  ",
                     color=color_resalte, penwidth="3", fontcolor=color_resalte)
        else:
            dot.edge(origen, destino, label=f"  {etiqueta}  ")

    ruta_completa = os.path.join(directorio, nombre_archivo)
    dot.render(ruta_completa, cleanup=True)
    return f"{ruta_completa}.png"


def _agrupar_transiciones(afd):
    """Función interna para organizar múltiples símbolos en una sola flecha del gráfico."""
    aristas = {}
    for estado in afd["estados"]:
        for simbolo in afd["alfabeto"]:
            destino = afd["transiciones"][estado][simbolo]
            clave = (estado, destino)
            if clave not in aristas:
                aristas[clave] = []
            aristas[clave].append(simbolo)
    return aristas


# ═══════════════════════════════════════════════════════════════════════════════
# MOSTRAR RESUMEN FORMAL DEL AUTÓMATA
# ═══════════════════════════════════════════════════════════════════════════════

def mostrar_afd(afd):
    """Imprime en consola una representacióntabular de la tabla de transición."""
    print("\n  ╔══════════════════════════════════════════╗")
    print("  ║          AUTÓMATA DEFINIDO (AFD)         ║")
    print("  ╠══════════════════════════════════════════╣")
    print(f"  ║  Estados:       {{ {', '.join(afd['estados'])} }}")
    print(f"  ║  Alfabeto:      {{ {', '.join(afd['alfabeto'])} }}")
    print(f"  ║  Estado inicial: {afd['estado_inicial']}")
    print(f"  ║  Estados finales: {{ {', '.join(afd['estados_finales'])} }}")
    print("  ║")
    print("  ║  Tabla de Transición:")
    print("  ║  " + "-" * 38)

    # Calcula anchos de columna para que la tabla se vea alineada.
    ancho_estado = max(len(e) for e in afd["estados"]) + 2
    cabecera = "  ║  " + "Estado".ljust(ancho_estado)
    for s in afd["alfabeto"]:
        cabecera += f"| {s.center(ancho_estado)}"
    print(cabecera)
    print("  ║  " + "-" * 38)

    # Imprime cada fila (Estado actual | Símbolo 1 -> Destino | Símbolo 2 -> Destino...).
    for estado in afd["estados"]:
        fila = f"  ║  {estado.ljust(ancho_estado)}"
        for simbolo in afd["alfabeto"]:
            destino = afd["transiciones"][estado][simbolo]
            fila += f"| {destino.center(ancho_estado)}"
        print(fila)

    print("  ╚══════════════════════════════════════════╝")


# ═══════════════════════════════════════════════════════════════════════════════
# MENÚ Y FLUJO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def banner():
    """Imprime el título estilizado del programa."""
    print()
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║                                                        ║")
    print("  ║   🤖  SIMULADOR DE AUTÓMATAS FINITOS DETERMINISTAS     ║")
    print("  ║                        (AFD)                           ║")
    print("  ║                                                        ║")
    print("  ╚══════════════════════════════════════════════════════════╝")


def main():
    """Orquesta toda la ejecución del simulador."""
    banner()

    # ── Paso 1: Definir formalmente los componentes de la quintupla ───────
    print("\n  ━━━ PASO 1: DEFINIR EL AUTÓMATA ━━━")

    estados = ingresar_estados()
    alfabeto = ingresar_alfabeto()
    estado_inicial = ingresar_estado_inicial(estados)
    estados_finales = ingresar_estados_finales(estados)
    transiciones = ingresar_transiciones(estados, alfabeto)

    # Creamos el objeto (diccionario) que representa el autómata.
    afd = {
        "estados": estados,
        "alfabeto": alfabeto,
        "estado_inicial": estado_inicial,
        "estados_finales": estados_finales,
        "transiciones": transiciones,
    }

    # Verificamos si el usuario definió transiciones para todos los pares estado/símbolo.
    errores = validar_determinismo(afd)
    if errores:
        print("\n  ⚠  El autómata tiene errores:")
        for err in errores:
            print(f"    • {err}")
        print("  Saliendo del programa.")
        sys.exit(1)

    # Mostramos el resumen en consola.
    mostrar_afd(afd)

    # ── Paso 2: Generar la imagen del autómata ────────────────────────────
    print("\n  ━━━ PASO 2: GENERANDO DIAGRAMA ━━━")
    directorio = os.path.dirname(os.path.abspath(__file__))
    try:
        archivo_diagrama = generar_diagrama(afd, directorio=directorio)
        print(f"\n  ✅ Diagrama generado: {archivo_diagrama}")
    except Exception as e:
        print(f"\n  ⚠  Error al generar el diagrama: {e}")
        print("  Asegúrese de tener Graphviz instalado correctamente.")

    # ── Paso 3: Bucle de simulación para múltiples cadenas ───────────────
    print("\n  ━━━ PASO 3: SIMULAR CADENAS ━━━")

    while True:
        cadena = input("\n  Ingrese una cadena a simular (o 'salir' para terminar): ").strip()

        if cadena.lower() == "salir":
            print("\n  👋 ¡Hasta luego!")
            break

        # Ejecutamos la lógica de simulación.
        camino, aceptada, error = simular_cadena(afd, cadena)
        # Mostramos los resultados en la consola.
        mostrar_resultado(cadena, camino, aceptada, error)

        # Si no hubo errores léxicos, generamos un diagrama dinámico con el camino en rojo.
        if not error:
            try:
                archivo_camino = generar_diagrama_con_camino(
                    afd, camino, directorio=directorio
                )
                print(f"\n  🖼  Diagrama con camino resaltado: {archivo_camino}")
            except Exception as e:
                print(f"\n  ⚠  Error al generar diagrama del camino: {e}")


# Punto de entrada estándar de Python.
if __name__ == "__main__":
    main()
