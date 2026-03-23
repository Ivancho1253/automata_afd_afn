"""
Simulador Interactivo de Autómatas Finitos No Deterministas (AFND)
==================================================================
Permite al usuario definir un AFND, simular cadenas paso a paso,
y generar diagramas con Graphviz (incluyendo resaltado del camino recorrido).

Dependencias:
    pip install graphviz
    + Graphviz instalado en el sistema (https://graphviz.org/download/)
"""

import graphviz
import sys
import os

EPSILON = 'e'  # Representación de cadena/transición vacía en entrada

# Agregar Graphviz al PATH en Windows si no está disponible
_graphviz_path = r"C:\Program Files\Graphviz\bin"
if os.path.isdir(_graphviz_path) and _graphviz_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _graphviz_path + os.pathsep + os.environ.get("PATH", "")


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE ENTRADA / DEFINICIÓN DEL AUTÓMATA
# ═══════════════════════════════════════════════════════════════════════════════

def ingresar_estados():
    """Solicita al usuario el conjunto de estados."""
    while True:
        entrada = input("\n  Ingrese los estados separados por comas (ej: q0,q1,q2): ").strip()
        if not entrada:
            print("  ⚠  Debe ingresar al menos un estado.")
            continue
        estados = [e.strip() for e in entrada.split(",") if e.strip()]
        if not estados:
            continue
        if len(estados) != len(set(estados)):
            print("  ⚠  Hay estados duplicados. Inténtelo de nuevo.")
            continue
        return estados


def ingresar_alfabeto():
    """Solicita al usuario el alfabeto."""
    while True:
        entrada = input(f"\n  Ingrese el alfabeto separado por comas (ej: 0,1) [No incluya '{EPSILON}', es para transiciones vacías]: ").strip()
        if not entrada:
            print("  ⚠  Debe ingresar al menos un símbolo.")
            continue
        alfabeto = [s.strip() for s in entrada.split(",") if s.strip()]
        if not alfabeto:
            continue
        if EPSILON in alfabeto:
            print(f"  ⚠  El símbolo '{EPSILON}' está reservado internamente para representar transiciones vacías (ε).")
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
            print("  ⚠  Debe ingresar al menos un estado final (o deje espacio vacío si de verdad no hay, pero es raro).")
            # Permitiremos un AFND sin finales si el usuario insiste, pero advertimos
            confirmacion = input("  ¿Está seguro que no hay estados finales? (s/n): ").strip().lower()
            if confirmacion == 's':
                return []
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
    Construye la función de transición. Un estado y símbolo puede llevar a múltiples estados.
    Retorna un dict: transiciones[estado][simbolo] = set(estados_destino)
    """
    print("\n  ── Función de Transición ──")
    print("  Ingrese los estados destino separados por comas (ej: q0,q1).")
    print("  Si no hay transición, simplemente presione Enter (dejar vacío).")
    print(f"  Nota: Para transiciones vacías se preguntará usando ε (ingresado como '{EPSILON}' en la lógica).\n")

    simbolos = alfabeto + [EPSILON]
    transiciones = {}
    
    for estado in estados:
        transiciones[estado] = {}
        for simbolo in simbolos:
            etiqueta_simb = "ε (vacía)" if simbolo == EPSILON else simbolo
            while True:
                destino = input(f"    δ({estado}, {etiqueta_simb}) = ").strip()
                if not destino:
                    transiciones[estado][simbolo] = set() # Sin transición
                    break
                
                destinos = [d.strip() for d in destino.split(",") if d.strip()]
                invalidos = [d for d in destinos if d not in estados]
                if invalidos:
                    print(f"    ⚠  '{', '.join(invalidos)}' no válidos. Intente de nuevo.")
                    continue
                
                transiciones[estado][simbolo] = set(destinos)
                break
    return transiciones


# ═══════════════════════════════════════════════════════════════════════════════
# LÓGICA DEL AFND
# ═══════════════════════════════════════════════════════════════════════════════

def clausura_epsilon(estados_iniciales, transiciones):
    """Calcula la clausura epsilon (ε-closure) de un conjunto de estados."""
    clausura = set(estados_iniciales)
    pila = list(estados_iniciales)
    
    while pila:
        estado = pila.pop()
        destinos_eps = transiciones.get(estado, {}).get(EPSILON, set())
        for d in destinos_eps:
            if d not in clausura:
                clausura.add(d)
                pila.append(d)
                
    return clausura

def mover(estados_actuales, simbolo, transiciones):
    """Retorna los estados alcanzables consumiendo 'simbolo' exacto (sin considerar epsilon)."""
    alcanzables = set()
    for estado in estados_actuales:
        destinos = transiciones.get(estado, {}).get(simbolo, set())
        alcanzables.update(destinos)
    return alcanzables


# ═══════════════════════════════════════════════════════════════════════════════
# SIMULACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def simular_cadena(afnd, cadena):
    """
    Simula el AFND con la cadena.
    """
    # Clausura epsilon inicial
    estados_actuales = clausura_epsilon({afnd["estado_inicial"]}, afnd["transiciones"])
    
    # Historial para mostrar en pantalla
    historial = [("INICIO", "", set(estados_actuales))]
    
    # Nodos y aristas activadas (para el diagrama especial)
    nodos_visitados = set(estados_actuales)
    aristas_usadas = set() # tuplas (origen, destino)
    
    # Rastrear posibles aristas epsilon en el estado inicial
    for o in estados_actuales:
        for d in afnd["transiciones"].get(o, {}).get(EPSILON, set()):
            if d in estados_actuales:
                aristas_usadas.add((o, d))
                
    for i, simbolo in enumerate(cadena):
        if simbolo not in afnd["alfabeto"]:
            return historial, False, f"El símbolo '{simbolo}' (posición {i}) no pertenece al alfabeto.", nodos_visitados, aristas_usadas
            
        estados_previos = set(estados_actuales)
        
        # 1. Función de transición pura para el símbolo
        estados_tras_simbolo = mover(estados_actuales, simbolo, afnd["transiciones"])
        
        # Rastrear aristas directas usadas
        for o in estados_actuales:
            for d in afnd["transiciones"].get(o, {}).get(simbolo, set()):
                if d in estados_tras_simbolo:
                    aristas_usadas.add((o, d))
                    nodos_visitados.add(d)
                    
        # 2. Clausura epsilon del resultado
        estados_actuales = clausura_epsilon(estados_tras_simbolo, afnd["transiciones"])
        nodos_visitados.update(estados_actuales)
        
        # Rastrear aristas epsilon usadas aquí
        for o in estados_actuales:
            for d in afnd["transiciones"].get(o, {}).get(EPSILON, set()):
                if d in estados_actuales:
                    aristas_usadas.add((o, d))
        
        historial.append((estados_previos, simbolo, set(estados_actuales)))

    aceptada = bool(estados_actuales.intersection(set(afnd["estados_finales"])))
    return historial, aceptada, None, nodos_visitados, aristas_usadas


def mostrar_resultado(cadena, historial, aceptada, error):
    print("\n  ╔══════════════════════════════════════════╗")
    print("  ║        RESULTADO DE LA SIMULACIÓN        ║")
    print("  ╠══════════════════════════════════════════╣")

    if error:
        print(f"  ║  ❌ Error: {error}")
        print("  ╚══════════════════════════════════════════╝")
        return

    cadena_mostrar = cadena if cadena else "ε (cadena vacía)"
    print(f"  ║  Cadena: {cadena_mostrar}")
    print("  ║")
    
    for paso, (prev, simb, actual) in enumerate(historial):
        if prev == "INICIO":
            estados_str = "{" + ", ".join(sorted(actual)) + "}"
            print(f"  ║  Paso Inicial (clausura ε): {estados_str}")
        else:
            prev_str = "{" + ", ".join(sorted(prev)) + "}"
            act_str = "{" + ", ".join(sorted(actual)) + "}" if actual else "∅"
            print(f"  ║  Paso {paso} (con '{simb}'): {prev_str} ──> {act_str}")

    print("  ║")
    if aceptada:
        print("  ║  Resultado: ✅ ACEPTADA")
    else:
        print("  ║  Resultado: ❌ RECHAZADA")

    print("  ╚══════════════════════════════════════════╝")


# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZACIÓN CON GRAPHVIZ
# ═══════════════════════════════════════════════════════════════════════════════

def _agrupar_transiciones(afnd):
    """Agrupa transiciones por (origen, destino) para combinar etiquetas."""
    aristas = {}
    for estado in afnd["estados"]:
        for simbolo, destinos in afnd["transiciones"].get(estado, {}).items():
            etiqueta = "ε" if simbolo == EPSILON else simbolo
            for destino in destinos:
                clave = (estado, destino)
                if clave not in aristas:
                    aristas[clave] = []
                aristas[clave].append(etiqueta)
    return aristas

def generar_diagrama(afnd, nombre_archivo="afnd", directorio="."):
    """Genera diagrama base del AFND."""
    dot = graphviz.Digraph(
        name="AFND",
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

    dot.node("__inicio__", "", shape="point", width="0")
    dot.edge("__inicio__", afnd["estado_inicial"], arrowsize="1.2")

    for estado in afnd["estados"]:
        attrs = {}
        if estado in afnd["estados_finales"]:
            attrs["shape"] = "doublecircle"
            attrs["fillcolor"] = "#D5F5E3"
            attrs["color"] = "#1E8449"
        dot.node(estado, estado, **attrs)

    aristas = _agrupar_transiciones(afnd)
    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        dot.edge(origen, destino, label=f"  {etiqueta}  ")

    ruta_completa = os.path.join(directorio, nombre_archivo)
    dot.render(ruta_completa, cleanup=True)
    return f"{ruta_completa}.png"


def generar_diagrama_simulacion(afnd, nodos_visitados, aristas_usadas, nombre_archivo="afnd_simulacion", directorio="."):
    """Genera diagrama resaltando estados y aristas recorridos."""
    dot = graphviz.Digraph(
        name="AFND_Simulacion",
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

    inicio_visitado = afnd["estado_inicial"] in nodos_visitados
    dot.node("__inicio__", "", shape="point", width="0",
             color="#E74C3C" if inicio_visitado else "#2C3E50")
    dot.edge("__inicio__", afnd["estado_inicial"], arrowsize="1.2",
             color="#E74C3C" if inicio_visitado else "#2C3E50",
             penwidth="3" if inicio_visitado else "1.5")

    for estado in afnd["estados"]:
        attrs = {}
        if estado in afnd["estados_finales"]:
            attrs["shape"] = "doublecircle"
            if estado in nodos_visitados:
                attrs["fillcolor"] = "#FADBD8"
                attrs["color"] = "#E74C3C"
                attrs["penwidth"] = "3"
            else:
                attrs["fillcolor"] = "#D5F5E3"
                attrs["color"] = "#1E8449"
        elif estado in nodos_visitados:
            attrs["fillcolor"] = "#FADBD8"
            attrs["color"] = "#E74C3C"
            attrs["penwidth"] = "3"
        dot.node(estado, estado, **attrs)

    aristas = _agrupar_transiciones(afnd)
    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        if (origen, destino) in aristas_usadas:
            dot.edge(origen, destino, label=f"  {etiqueta}  ",
                     color="#E74C3C", penwidth="3", fontcolor="#E74C3C")
        else:
            dot.edge(origen, destino, label=f"  {etiqueta}  ")

    ruta_completa = os.path.join(directorio, nombre_archivo)
    dot.render(ruta_completa, cleanup=True)
    return f"{ruta_completa}.png"


# ═══════════════════════════════════════════════════════════════════════════════
# MOSTRAR RESUMEN DEL AUTÓMATA
# ═══════════════════════════════════════════════════════════════════════════════

def mostrar_afnd(afnd):
    print("\n  ╔══════════════════════════════════════════╗")
    print("  ║         AUTÓMATA DEFINIDO (AFND)         ║")
    print("  ╠══════════════════════════════════════════╣")
    print(f"  ║  Estados:       {{ {', '.join(afnd['estados'])} }}")
    print(f"  ║  Alfabeto:      {{ {', '.join(afnd['alfabeto'])} }}")
    print(f"  ║  Estado inicial: {afnd['estado_inicial']}")
    print(f"  ║  Estados finales: {{ {', '.join(afnd['estados_finales'])} }}")
    print("  ║")
    print("  ║  Tabla de Transición:")
    
    simbolos = afnd["alfabeto"] + [EPSILON]
    
    anchos = {}
    for estado in afnd["estados"]:
        for sim in simbolos:
            destinos = afnd["transiciones"].get(estado, {}).get(sim, set())
            anchos[(estado, sim)] = len("{" + ",".join(destinos) + "}") if destinos else 1
    
    ancho_estado = max(len(e) for e in afnd["estados"]) + 2
    ancho_columna = max(max(anchos.values()) if anchos else 0, 8) + 2

    separador = "  ║  " + "-" * (ancho_estado + len(simbolos) * ancho_columna + len(simbolos) + 1)
    
    print(separador)
    cabecera = "  ║  " + "Estado".ljust(ancho_estado)
    for s in simbolos:
        texto_simbolo = "ε" if s == EPSILON else s
        cabecera += f"| {texto_simbolo.center(ancho_columna)}"
    print(cabecera)
    print(separador)

    for estado in afnd["estados"]:
        fila = f"  ║  {estado.ljust(ancho_estado)}"
        for simbolo in simbolos:
            destinos = afnd["transiciones"].get(estado, {}).get(simbolo, set())
            texto_destinos = "{" + ",".join(sorted(destinos)) + "}" if destinos else "∅"
            fila += f"| {texto_destinos.center(ancho_columna)}"
        print(fila)

    print("  ╚══════════════════════════════════════════╝")


# ═══════════════════════════════════════════════════════════════════════════════
# MENÚ PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def banner():
    print()
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║                                                        ║")
    print("  ║  🤖 SIMULADOR DE AUTÓMATAS FINITOS NO DETERMINISTAS    ║")
    print("  ║                        (AFND)                          ║")
    print("  ║                                                        ║")
    print("  ╚══════════════════════════════════════════════════════════╝")


def main():
    banner()

    print("\n  ━━━ PASO 1: DEFINIR EL AUTÓMATA ━━━")
    estados = ingresar_estados()
    alfabeto = ingresar_alfabeto()
    estado_inicial = ingresar_estado_inicial(estados)
    estados_finales = ingresar_estados_finales(estados)
    transiciones = ingresar_transiciones(estados, alfabeto)

    afnd = {
        "estados": estados,
        "alfabeto": alfabeto,
        "estado_inicial": estado_inicial,
        "estados_finales": estados_finales,
        "transiciones": transiciones,
    }

    mostrar_afnd(afnd)

    print("\n  ━━━ PASO 2: GENERANDO DIAGRAMA ━━━")
    directorio = os.path.dirname(os.path.abspath(__file__))
    try:
        archivo_diagrama = generar_diagrama(afnd, directorio=directorio)
        print(f"\n  ✅ Diagrama general generado: {archivo_diagrama}")
    except Exception as e:
        print(f"\n  ⚠  Error al generar el diagrama: {e}")
        print("  Asegúrese de tener Graphviz instalado (https://graphviz.org/download/)")

    print("\n  ━━━ PASO 3: SIMULAR CADENAS ━━━")
    while True:
        cadena = input("\n  Ingrese una cadena a simular (o 'salir' para terminar): ").strip()
        if cadena.lower() == "salir":
            print("\n  👋 ¡Hasta luego!")
            break

        historial, aceptada, error, nodos_visitados, aristas_usadas = simular_cadena(afnd, cadena)
        mostrar_resultado(cadena, historial, aceptada, error)

        if not error:
            try:
                archivo_camino = generar_diagrama_simulacion(
                    afnd, nodos_visitados, aristas_usadas, directorio=directorio
                )
                print(f"\n  🖼  Diagrama con simulación resaltada: {archivo_camino}")
            except Exception as e:
                print(f"\n  ⚠  Error al generar diagrama de simulación: {e}")


if __name__ == "__main__":
    main()
