"""
Simulador Interactivo de Autómatas Finitos Deterministas (AFD)
==============================================================
Permite al usuario definir un AFD, simular cadenas paso a paso,
y generar diagramas con Graphviz (incluyendo resaltado del camino recorrido).

Dependencias:
    pip install graphviz
    + Graphviz instalado en el sistema (https://graphviz.org/download/)
"""

import graphviz
import sys
import os

# Agregar Graphviz al PATH en Windows si no está disponible
_graphviz_path = r"C:\Program Files\Graphviz\bin"
if os.path.isdir(_graphviz_path) and _graphviz_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _graphviz_path + os.pathsep + os.environ.get("PATH", "")


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE ENTRADA / DEFINICIÓN DEL AUTÓMATA
# ═══════════════════════════════════════════════════════════════════════════════

def ingresar_estados():
    """Solicita al usuario el conjunto de estados, separados por comas."""
    while True:
        entrada = input("\n  Ingrese los estados separados por comas (ej: q0,q1,q2): ").strip()
        if not entrada:
            print("  ⚠  Debe ingresar al menos un estado.")
            continue
        estados = [e.strip() for e in entrada.split(",") if e.strip()]
        if not estados:
            print("  ⚠  No se detectaron estados válidos.")
            continue
        # Verificar duplicados
        if len(estados) != len(set(estados)):
            print("  ⚠  Hay estados duplicados. Inténtelo de nuevo.")
            continue
        return estados


def ingresar_alfabeto():
    """Solicita al usuario el alfabeto del autómata, separado por comas."""
    while True:
        entrada = input("\n  Ingrese el alfabeto separado por comas (ej: 0,1): ").strip()
        if not entrada:
            print("  ⚠  Debe ingresar al menos un símbolo.")
            continue
        alfabeto = [s.strip() for s in entrada.split(",") if s.strip()]
        if not alfabeto:
            print("  ⚠  No se detectaron símbolos válidos.")
            continue
        if len(alfabeto) != len(set(alfabeto)):
            print("  ⚠  Hay símbolos duplicados. Inténtelo de nuevo.")
            continue
        return alfabeto


def ingresar_estado_inicial(estados):
    """Solicita y valida el estado inicial."""
    while True:
        entrada = input(f"\n  Ingrese el estado inicial (opciones: {', '.join(estados)}): ").strip()
        if entrada in estados:
            return entrada
        print(f"  ⚠  '{entrada}' no pertenece al conjunto de estados.")


def ingresar_estados_finales(estados):
    """Solicita y valida los estados de aceptación."""
    while True:
        entrada = input(f"\n  Ingrese los estados finales separados por comas (opciones: {', '.join(estados)}): ").strip()
        if not entrada:
            print("  ⚠  Debe ingresar al menos un estado final.")
            continue
        finales = [e.strip() for e in entrada.split(",") if e.strip()]
        invalidos = [e for e in finales if e not in estados]
        if invalidos:
            print(f"  ⚠  Los siguientes estados no son válidos: {', '.join(invalidos)}")
            continue
        if len(finales) != len(set(finales)):
            print("  ⚠  Hay estados finales duplicados. Inténtelo de nuevo.")
            continue
        return finales


def ingresar_transiciones(estados, alfabeto):
    """
    Construye la tabla de transición de forma dinámica.
    Para cada par (estado, símbolo) se solicita el estado destino.
    Valida que el destino pertenezca al conjunto de estados (determinismo).
    Retorna un dict de dicts: transiciones[estado][simbolo] = estado_destino
    """
    print("\n  ── Función de Transición ──")
    print("  Para cada estado y símbolo, ingrese el estado destino.\n")

    transiciones = {}
    for estado in estados:
        transiciones[estado] = {}
        for simbolo in alfabeto:
            while True:
                destino = input(f"    δ({estado}, {simbolo}) = ").strip()
                if destino not in estados:
                    print(f"    ⚠  '{destino}' no pertenece al conjunto de estados. Intente de nuevo.")
                    continue
                transiciones[estado][simbolo] = destino
                break
    return transiciones


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDACIÓN DEL AUTÓMATA
# ═══════════════════════════════════════════════════════════════════════════════

def validar_determinismo(afd):
    """
    Verifica que la función de transición sea completa y determinista:
    cada par (estado, símbolo) debe tener exactamente un destino.
    """
    errores = []
    for estado in afd["estados"]:
        for simbolo in afd["alfabeto"]:
            if estado not in afd["transiciones"]:
                errores.append(f"  Falta la fila de transiciones para el estado '{estado}'.")
                continue
            if simbolo not in afd["transiciones"][estado]:
                errores.append(f"  Falta transición: δ({estado}, {simbolo})")
    return errores


# ═══════════════════════════════════════════════════════════════════════════════
# SIMULACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def simular_cadena(afd, cadena):
    """
    Simula el AFD con la cadena dada.
    Retorna:
        camino  — lista de estados visitados (incluye el inicial)
        aceptada — True si el último estado es de aceptación
        error   — mensaje de error si un símbolo no pertenece al alfabeto, o None
    """
    estado_actual = afd["estado_inicial"]
    camino = [estado_actual]

    for i, simbolo in enumerate(cadena):
        if simbolo not in afd["alfabeto"]:
            return camino, False, f"El símbolo '{simbolo}' (posición {i}) no pertenece al alfabeto."
        estado_actual = afd["transiciones"][estado_actual][simbolo]
        camino.append(estado_actual)

    aceptada = estado_actual in afd["estados_finales"]
    return camino, aceptada, None


def mostrar_resultado(cadena, camino, aceptada, error):
    """Imprime el recorrido paso a paso y el veredicto."""
    print("\n  ╔══════════════════════════════════════════╗")
    print("  ║        RESULTADO DE LA SIMULACIÓN        ║")
    print("  ╠══════════════════════════════════════════╣")

    if error:
        print(f"  ║  ❌ Error: {error}")
        print("  ╚══════════════════════════════════════════╝")
        return

    cadena_mostrar = cadena if cadena else "ε (cadena vacía)"
    print(f"  ║  Cadena: {cadena_mostrar}")
    print(f"  ║  Camino: {' → '.join(camino)}")

    if aceptada:
        print("  ║  Resultado: ✅ ACEPTADA")
    else:
        print("  ║  Resultado: ❌ RECHAZADA")

    print("  ╚══════════════════════════════════════════╝")


# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZACIÓN CON GRAPHVIZ
# ═══════════════════════════════════════════════════════════════════════════════

def generar_diagrama(afd, nombre_archivo="automata", directorio="."):
    """
    Genera un diagrama estilo académico del AFD y lo guarda como PNG.
    - Estados como círculos
    - Estado inicial con flecha desde un nodo invisible
    - Estados finales con doble círculo
    - Transiciones agrupadas (mismas aristas con etiquetas combinadas)
    """
    dot = graphviz.Digraph(
        name="AFD",
        format="png",
        engine="dot",
        graph_attr={
            "rankdir": "LR",
            "dpi": "150",
            "bgcolor": "white",
            "pad": "0.5",
            "nodesep": "0.7",
            "ranksep": "1.0",
        },
        node_attr={
            "shape": "circle",
            "style": "filled",
            "fillcolor": "#E8F4FD",
            "color": "#2C3E50",
            "fontname": "Arial",
            "fontsize": "14",
            "penwidth": "2",
        },
        edge_attr={
            "fontname": "Arial",
            "fontsize": "12",
            "color": "#2C3E50",
            "penwidth": "1.5",
        },
    )

    # Nodo invisible para la flecha de inicio
    dot.node("__inicio__", "", shape="point", width="0")
    dot.edge("__inicio__", afd["estado_inicial"], arrowsize="1.2")

    # Nodos
    for estado in afd["estados"]:
        attrs = {}
        if estado in afd["estados_finales"]:
            attrs["shape"] = "doublecircle"
            attrs["fillcolor"] = "#D5F5E3"
            attrs["color"] = "#1E8449"
        dot.node(estado, estado, **attrs)

    # Agrupar transiciones por (origen, destino) para combinar etiquetas
    aristas = _agrupar_transiciones(afd)
    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        dot.edge(origen, destino, label=f"  {etiqueta}  ")

    ruta_completa = os.path.join(directorio, nombre_archivo)
    dot.render(ruta_completa, cleanup=True)
    return f"{ruta_completa}.png"


def generar_diagrama_con_camino(afd, camino, nombre_archivo="automata_camino", directorio="."):
    """
    Genera el diagrama del AFD resaltando en rojo el camino recorrido
    durante la simulación.
    """
    # Determinar aristas y nodos del camino
    nodos_camino = set(camino)
    aristas_camino = set()
    for i in range(len(camino) - 1):
        aristas_camino.add((camino[i], camino[i + 1]))

    dot = graphviz.Digraph(
        name="AFD_Camino",
        format="png",
        engine="dot",
        graph_attr={
            "rankdir": "LR",
            "dpi": "150",
            "bgcolor": "white",
            "pad": "0.5",
            "nodesep": "0.7",
            "ranksep": "1.0",
        },
        node_attr={
            "shape": "circle",
            "style": "filled",
            "fillcolor": "#E8F4FD",
            "color": "#2C3E50",
            "fontname": "Arial",
            "fontsize": "14",
            "penwidth": "2",
        },
        edge_attr={
            "fontname": "Arial",
            "fontsize": "12",
            "color": "#2C3E50",
            "penwidth": "1.5",
        },
    )

    # Nodo invisible para la flecha de inicio
    inicio_en_camino = afd["estado_inicial"] in nodos_camino
    dot.node("__inicio__", "", shape="point", width="0",
             color="#E74C3C" if inicio_en_camino else "#2C3E50")
    dot.edge("__inicio__", afd["estado_inicial"], arrowsize="1.2",
             color="#E74C3C" if inicio_en_camino else "#2C3E50",
             penwidth="3" if inicio_en_camino else "1.5")

    # Nodos
    for estado in afd["estados"]:
        attrs = {}
        if estado in afd["estados_finales"]:
            attrs["shape"] = "doublecircle"
            if estado in nodos_camino:
                attrs["fillcolor"] = "#FADBD8"
                attrs["color"] = "#E74C3C"
                attrs["penwidth"] = "3"
            else:
                attrs["fillcolor"] = "#D5F5E3"
                attrs["color"] = "#1E8449"
        elif estado in nodos_camino:
            attrs["fillcolor"] = "#FADBD8"
            attrs["color"] = "#E74C3C"
            attrs["penwidth"] = "3"
        dot.node(estado, estado, **attrs)

    # Agrupar transiciones
    aristas = _agrupar_transiciones(afd)
    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        if (origen, destino) in aristas_camino:
            dot.edge(origen, destino, label=f"  {etiqueta}  ",
                     color="#E74C3C", penwidth="3", fontcolor="#E74C3C")
        else:
            dot.edge(origen, destino, label=f"  {etiqueta}  ")

    ruta_completa = os.path.join(directorio, nombre_archivo)
    dot.render(ruta_completa, cleanup=True)
    return f"{ruta_completa}.png"


def _agrupar_transiciones(afd):
    """Agrupa transiciones por (origen, destino) para combinar etiquetas."""
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
# MOSTRAR RESUMEN DEL AUTÓMATA
# ═══════════════════════════════════════════════════════════════════════════════

def mostrar_afd(afd):
    """Imprime un resumen legible del AFD definido por el usuario."""
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

    # Cabecera
    ancho_estado = max(len(e) for e in afd["estados"]) + 2
    cabecera = "  ║  " + "Estado".ljust(ancho_estado)
    for s in afd["alfabeto"]:
        cabecera += f"| {s.center(ancho_estado)}"
    print(cabecera)
    print("  ║  " + "-" * 38)

    # Filas
    for estado in afd["estados"]:
        fila = f"  ║  {estado.ljust(ancho_estado)}"
        for simbolo in afd["alfabeto"]:
            destino = afd["transiciones"][estado][simbolo]
            fila += f"| {destino.center(ancho_estado)}"
        print(fila)

    print("  ╚══════════════════════════════════════════╝")


# ═══════════════════════════════════════════════════════════════════════════════
# MENÚ PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def banner():
    """Imprime el banner del programa."""
    print()
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║                                                        ║")
    print("  ║   🤖  SIMULADOR DE AUTÓMATAS FINITOS DETERMINISTAS     ║")
    print("  ║                        (AFD)                           ║")
    print("  ║                                                        ║")
    print("  ╚══════════════════════════════════════════════════════════╝")


def main():
    """Función principal que orquesta todo el flujo del simulador."""
    banner()

    # ── Paso 1: Definir el autómata ──────────────────────────────────────
    print("\n  ━━━ PASO 1: DEFINIR EL AUTÓMATA ━━━")

    estados = ingresar_estados()
    alfabeto = ingresar_alfabeto()
    estado_inicial = ingresar_estado_inicial(estados)
    estados_finales = ingresar_estados_finales(estados)
    transiciones = ingresar_transiciones(estados, alfabeto)

    afd = {
        "estados": estados,
        "alfabeto": alfabeto,
        "estado_inicial": estado_inicial,
        "estados_finales": estados_finales,
        "transiciones": transiciones,
    }

    # Validar determinismo
    errores = validar_determinismo(afd)
    if errores:
        print("\n  ⚠  El autómata tiene errores:")
        for err in errores:
            print(f"    • {err}")
        print("  Saliendo del programa.")
        sys.exit(1)

    # Mostrar resumen
    mostrar_afd(afd)

    # ── Paso 2: Generar diagrama base ────────────────────────────────────
    print("\n  ━━━ PASO 2: GENERANDO DIAGRAMA ━━━")

    directorio = os.path.dirname(os.path.abspath(__file__))
    try:
        archivo_diagrama = generar_diagrama(afd, directorio=directorio)
        print(f"\n  ✅ Diagrama generado: {archivo_diagrama}")
    except Exception as e:
        print(f"\n  ⚠  Error al generar el diagrama: {e}")
        print("  Asegúrese de tener Graphviz instalado (https://graphviz.org/download/)")

    # ── Paso 3: Simular cadenas ──────────────────────────────────────────
    print("\n  ━━━ PASO 3: SIMULAR CADENAS ━━━")

    while True:
        cadena = input("\n  Ingrese una cadena a simular (o 'salir' para terminar): ").strip()

        if cadena.lower() == "salir":
            print("\n  👋 ¡Hasta luego!")
            break

        camino, aceptada, error = simular_cadena(afd, cadena)
        mostrar_resultado(cadena, camino, aceptada, error)

        # Generar diagrama con el camino resaltado
        if not error:
            try:
                archivo_camino = generar_diagrama_con_camino(
                    afd, camino, directorio=directorio
                )
                print(f"\n  🖼  Diagrama con camino resaltado: {archivo_camino}")
            except Exception as e:
                print(f"\n  ⚠  Error al generar diagrama del camino: {e}")


if __name__ == "__main__":
    main()
