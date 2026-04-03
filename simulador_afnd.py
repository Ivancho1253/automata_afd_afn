"""
Simulador Interactivo de Autómatas Finitos No Deterministas (AFND)
==================================================================
Este script permite definir formalmente un AFND (incluyendo transiciones vacías o épsilon),
validar si una cadena es aceptada manejando múltiples estados simultáneos,
y generar diagramas visuales con Graphviz.

Dependencias:
    - pip install graphviz (Librería de Python)
    - Graphviz instalado en el sistema (https://graphviz.org/download/)
"""

import graphviz  # Generación de diagramas .png
import sys       # Funciones del sistema
import os        # Rutas y variables de sistema

# --- CONFIGURACIÓN GLOBAL ---
# Representación de la transición vacía (épsilon). 
# El usuario debe usar la letra 'e' para definir transiciones que no consumen símbolos.
EPSILON = 'e'  

# Configuración de PATH para localizar el ejecutable de Graphviz (Windows y macOS).
_graphviz_path = r"C:\Program Files\Graphviz\bin"
if os.path.isdir(_graphviz_path) and _graphviz_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _graphviz_path + os.pathsep + os.environ.get("PATH", "")

for _mac_path in ("/opt/homebrew/bin", "/usr/local/bin"):
    if os.path.isdir(_mac_path) and _mac_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _mac_path + os.pathsep + os.environ.get("PATH", "")


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE ENTRADA / DEFINICIÓN DEL AFND
# ═══════════════════════════════════════════════════════════════════════════════

def ingresar_estados():
    """Solicita el conjunto de estados (Q)."""
    while True:
        entrada = input("\n  Ingrese los estados separados por comas (ej: q0,q1,q2): ").strip()
        if not entrada:
            print("  ⚠  Debe ingresar al menos un estado.")
            continue
        # Crea lista de estados quitando espacios.
        estados = [e.strip() for e in entrada.split(",") if e.strip()]
        if not estados:
            continue
        # Verifica que no haya estados con el mismo nombre.
        if len(estados) != len(set(estados)):
            print("  ⚠  Hay estados duplicados. Inténtelo de nuevo.")
            continue
        return estados


def ingresar_alfabeto():
    """Solicita el alfabeto (Σ) sin incluir el símbolo reservado para épsilon."""
    while True:
        entrada = input(f"\n  Ingrese el alfabeto separado por comas (ej: 0,1) [No incluya '{EPSILON}', es para transiciones vacías]: ").strip()
        if not entrada:
            print("  ⚠  Debe ingresar al menos un símbolo.")
            continue
        alfabeto = [s.strip() for s in entrada.split(",") if s.strip()]
        if not alfabeto:
            continue
        # El símbolo 'e' (épsilon) no puede ser parte del alfabeto de entrada.
        if EPSILON in alfabeto:
            print(f"  ⚠  El símbolo '{EPSILON}' está reservado internamente para representar transiciones vacías (ε).")
            continue
        if len(alfabeto) != len(set(alfabeto)):
            print("  ⚠  Hay símbolos duplicados. Inténtelo de nuevo.")
            continue
        return alfabeto


def ingresar_estado_inicial(estados):
    """Solicita y valida el único estado inicial (q0)."""
    while True:
        entrada = input(f"\n  Ingrese el estado inicial (opciones: {', '.join(estados)}): ").strip()
        if entrada in estados:
            return entrada
        print(f"  ⚠  '{entrada}' no pertenece al conjunto de estados.")


def ingresar_estados_finales(estados):
    """Solicita el conjunto de estados finales (F)."""
    while True:
        entrada = input(f"\n  Ingrese los estados finales separados por comas (opciones: {', '.join(estados)}): ").strip()
        if not entrada:
            print("  ⚠  Debe ingresar al menos un estado final.")
            confirmacion = input("  ¿Confirmar que NO hay estados finales? (s/n): ").strip().lower()
            if confirmacion == 's':
                return []
            continue
        finales = [e.strip() for e in entrada.split(",") if e.strip()]
        # Valida que todos los destinos existan en Q.
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
    Construye la función de transición (δ) de un AFND.
    A diferencia del AFD, aquí un (estado, símbolo) puede ir a un CONJUNTO de estados.
    """
    print("\n  ── Función de Transición ──")
    print("  Ingrese los estados destino separados por comas (ej: q0,q1).")
    print(f"  Nota: Use '{EPSILON}' para definir transiciones épsilon (ε).\n")

    # Incluimos épsilon como una columna extra en la definición de transiciones.
    simbolos = alfabeto + [EPSILON]
    transiciones = {}
    
    for estado in estados:
        transiciones[estado] = {}
        for simbolo in simbolos:
            etiqueta_simb = "ε (vacía)" if simbolo == EPSILON else simbolo
            while True:
                # El usuario ingresa una lista de destinos (ej: "q1,q2").
                destino = input(f"    δ({estado}, {etiqueta_simb}) = ").strip()
                if not destino:
                    # En AFND es válido no tener transición para un símbolo particular.
                    transiciones[estado][simbolo] = set() 
                    break
                
                # Procesamos la lista de destinos ingresada.
                destinos = [d.strip() for d in destino.split(",") if d.strip()]
                invalidos = [d for d in destinos if d not in estados]
                if invalidos:
                    print(f"    ⚠  Destinos '{', '.join(invalidos)}' no existen. Reintente.")
                    continue
                
                # Guardamos los destinos como un conjunto (set) para eficiencia.
                transiciones[estado][simbolo] = set(destinos)
                break
    return transiciones


# ═══════════════════════════════════════════════════════════════════════════════
# LÓGICA DE PROCESAMIENTO NO DETERMINISTA
# ═══════════════════════════════════════════════════════════════════════════════

def clausura_epsilon(estados_iniciales, transiciones):
    """
    Calcula la ε-closure (clausura épsilon).
    Determina todos los estados alcanzables desde un conjunto dado usando SOLO saltos vacíos.
    """
    # Empezamos con el conjunto de estados actuales.
    clausura = set(estados_iniciales)
    # Lista de estados pendientes de revisar.
    pila = list(estados_iniciales)
    
    while pila:
        estado = pila.pop()
        # Buscamos si el estado tiene salidas épsilon.
        destinos_eps = transiciones.get(estado, {}).get(EPSILON, set())
        for d in destinos_eps:
            # Si el destino no ha sido visitado, lo agregamos.
            if d not in clausura:
                clausura.add(d)
                pila.append(d) # Al agregarlo a la pila, buscaremos sus propias salidas ε (recursividad).
                
    return clausura

def mover(estados_actuales, simbolo, transiciones):
    """
    Calcula el movimiento básico δ(conjunto_estados, símbolo).
    Retorna todos los estados a los que se puede ir consumiendo exactamente un símbolo.
    """
    alcanzables = set()
    for estado in estados_actuales:
        # Obtenemos los destinos directos desde cada estado bajo el símbolo dado.
        destinos = transiciones.get(estado, {}).get(simbolo, set())
        alcanzables.update(destinos) # Los unimos todos en un único conjunto.
    return alcanzables


# ═══════════════════════════════════════════════════════════════════════════════
# SIMULACIÓN DE CADENAS
# ═══════════════════════════════════════════════════════════════════════════════

def simular_cadena(afnd, cadena):
    """
    Simula el AFND procesando la cadena. 
    Mantiene un conjunto de estados posibles en cada paso.
    """
    # PASO INICIAL: Estado inicial + su clausura épsilon.
    estados_actuales = clausura_epsilon({afnd["estado_inicial"]}, afnd["transiciones"])
    
    # Historial para depuración: (Estado previo, Símbolo leído, Estados resultantes).
    historial = [("INICIO", "", set(estados_actuales))]
    
    # Para el diagrama: guardaremos qué se usó en total durante el proceso.
    nodos_visitados = set(estados_actuales)
    aristas_usadas = set() # (origen, destino)
    
    # Registra las aristas épsilon iniciales (del q0 a su clausura inicial).
    for o in estados_actuales:
        for d in afnd["transiciones"].get(o, {}).get(EPSILON, set()):
            if d in estados_actuales:
                aristas_usadas.add((o, d))
                
    # Procesamiento de cada símbolo de la cadena.
    for i, simbolo in enumerate(cadena):
        if simbolo not in afnd["alfabeto"]:
            return historial, False, f"El símbolo '{simbolo}' no está en el alfabeto.", nodos_visitados, aristas_usadas
            
        estados_previos = set(estados_actuales)
        
        # 1. MOVER: Estados alcanzables consumiendo 'simbolo'.
        estados_tras_simbolo = mover(estados_actuales, simbolo, afnd["transiciones"])
        
        # Registrar aristas directas detectadas en este paso.
        for o in estados_actuales:
            for d in afnd["transiciones"].get(o, {}).get(simbolo, set()):
                if d in estados_tras_simbolo:
                    aristas_usadas.add((o, d))
                    nodos_visitados.add(d)
                    
        # 2. CLAUSURA-ε: Ampliamos el conjunto con todos los saltos vacíos posibles.
        estados_actuales = clausura_epsilon(estados_tras_simbolo, afnd["transiciones"])
        nodos_visitados.update(estados_actuales)
        
        # Registrar aristas épsilon detectadas en la clausura.
        for o in estados_actuales:
            for d in afnd["transiciones"].get(o, {}).get(EPSILON, set()):
                if d in estados_actuales:
                    aristas_usadas.add((o, d))
        
        # Guardamos el estado del sistema tras procesar este símbolo.
        historial.append((estados_previos, simbolo, set(estados_actuales)))

    # Aceptada si AL MENOS UNO de los estados actuales es un estado final (F).
    aceptada = bool(estados_actuales.intersection(set(afnd["estados_finales"])))
    return historial, aceptada, None, nodos_visitados, aristas_usadas


def mostrar_resultado(cadena, historial, aceptada, error):
    """Muestra el rastro de la computación no determinista."""
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
    
    # Imprime paso a paso los conjuntos de estados posibles.
    for paso, (prev, simb, actual) in enumerate(historial):
        if prev == "INICIO":
            estados_str = "{" + ", ".join(sorted(actual)) + "}"
            print(f"  ║  Paso Inicial (clausura ε): {estados_str}")
        else:
            prev_str = "{" + ", ".join(sorted(prev)) + "}"
            act_str = "{" + ", ".join(sorted(actual)) + "}" if actual else "∅ (muerte)"
            print(f"  ║  Paso {paso} (lee '{simb}'): {prev_str} ──> {act_str}")

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
    """Combina etiquetas en flechas comunes entre los mismos estados."""
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
    """Genera el diagrama estático del AFND."""
    dot = graphviz.Digraph(
        name="AFND",
        format="png",
        engine="dot",
        graph_attr={"rankdir": "LR", "dpi": "150", "bgcolor": "white"},
        node_attr={"shape": "circle", "style": "filled", "fillcolor": "#E8F4FD", "fontname": "Arial"},
        edge_attr={"fontname": "Arial", "fontsize": "12"},
    )

    # Flecha inicial.
    dot.node("__inicio__", "", shape="point", width="0")
    dot.edge("__inicio__", afnd["estado_inicial"], arrowsize="1.2")

    # Dibujar nodos.
    for estado in afnd["estados"]:
        attrs = {}
        if estado in afnd["estados_finales"]:
            attrs["shape"] = "doublecircle"
            attrs["fillcolor"] = "#D5F5E3"
        dot.node(estado, estado, **attrs)

    # Aristas.
    aristas = _agrupar_transiciones(afnd)
    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        dot.edge(origen, destino, label=f"  {etiqueta}  ")

    ruta_completa = os.path.join(directorio, nombre_archivo)
    dot.render(ruta_completa, cleanup=True)
    return f"{ruta_completa}.png"


def generar_diagrama_simulacion(afnd, nodos_visitados, aristas_usadas, nombre_archivo="afnd_simulacion", directorio="."):
    """Diagrama dinámico que resalta todo lo que el AFND 'exploró' en la simulación."""
    dot = graphviz.Digraph(
        name="AFND_Simulacion",
        format="png",
        engine="dot",
        graph_attr={"rankdir": "LR", "dpi": "150", "bgcolor": "white"},
        node_attr={"shape": "circle", "style": "filled", "fillcolor": "#E8F4FD", "fontname": "Arial"},
        edge_attr={"fontname": "Arial", "fontsize": "12"},
    )

    color_resalte = "#E74C3C" # Rojo.

    # Resaltar inicio si se visitó.
    inicio_visitado = afnd["estado_inicial"] in nodos_visitados
    dot.node("__inicio__", "", shape="point", width="0",
             color=color_resalte if inicio_visitado else "#2C3E50")
    dot.edge("__inicio__", afnd["estado_inicial"], arrowsize="1.2",
             color=color_resalte if inicio_visitado else "#2C3E50",
             penwidth="3" if inicio_visitado else "1.5")

    # Dibujar todos los nodos resaltando los visitados.
    for estado in afnd["estados"]:
        attrs = {}
        visitado = estado in nodos_visitados
        if estado in afnd["estados_finales"]:
            attrs["shape"] = "doublecircle"
            if visitado:
                attrs["fillcolor"] = "#FADBD8"
                attrs["color"] = color_resalte
                attrs["penwidth"] = "3"
            else:
                attrs["fillcolor"] = "#D5F5E3"
        elif visitado:
            attrs["fillcolor"] = "#FADBD8"
            attrs["color"] = color_resalte
            attrs["penwidth"] = "3"
        dot.node(estado, estado, **attrs)

    # Dibujar aristas resaltando las usadas.
    aristas = _agrupar_transiciones(afnd)
    for (origen, destino), simbolos in aristas.items():
        etiqueta = ", ".join(sorted(simbolos))
        if (origen, destino) in aristas_usadas:
            dot.edge(origen, destino, label=f"  {etiqueta}  ",
                     color=color_resalte, penwidth="3", fontcolor=color_resalte)
        else:
            dot.edge(origen, destino, label=f"  {etiqueta}  ")

    ruta_completa = os.path.join(directorio, nombre_archivo)
    dot.render(ruta_completa, cleanup=True)
    return f"{ruta_completa}.png"


# ═══════════════════════════════════════════════════════════════════════════════
# RESUMEN DEL AUTÓMATA (TABLA DE TRANSICIÓN)
# ═══════════════════════════════════════════════════════════════════════════════

def mostrar_afnd(afnd):
    """Genera una tabla visual de la función de transición δ(q, σ)."""
    print("\n  ╔══════════════════════════════════════════╗")
    print("  ║         AUTÓMATA DEFINIDO (AFND)         ║")
    print("  ╠══════════════════════════════════════════╣")
    print(f"  ║  Estados:       {{ {', '.join(afnd['estados'])} }}")
    print(f"  ║  Alfabeto:      {{ {', '.join(afnd['alfabeto'])} }}")
    print(f"  ║  Estado inicial: {afnd['estado_inicial']}")
    print(f"  ║  Estados finales: {{ {', '.join(afnd['estados_finales'])} }}")
    print("  ║")
    
    simbolos = afnd["alfabeto"] + [EPSILON]
    
    # Determinar anchos de columna dinámicos según el contenido.
    anchos = {}
    for estado in afnd["estados"]:
        for sim in simbolos:
            destinos = afnd["transiciones"].get(estado, {}).get(sim, set())
            anchos[(estado, sim)] = len("{" + ",".join(destinos) + "}") if destinos else 1
    
    ancho_estado = max(len(e) for e in afnd["estados"]) + 2
    ancho_columna = max(max(anchos.values()) if anchos else 0, 8) + 2

    # Línea separadora.
    separador = "  ║  " + "-" * (ancho_estado + len(simbolos) * (ancho_columna + 1) + 1)
    
    print(separador)
    cabecera = "  ║  " + "Estado".ljust(ancho_estado)
    for s in simbolos:
        texto_simbolo = "ε" if s == EPSILON else s
        cabecera += f"| {texto_simbolo.center(ancho_columna)}"
    print(cabecera)
    print(separador)

    # Imprimir filas de la tabla: Estado | Conjunto de destinos para cada símbolo.
    for estado in afnd["estados"]:
        fila = f"  ║  {estado.ljust(ancho_estado)}"
        for simbolo in simbolos:
            destinos = afnd["transiciones"].get(estado, {}).get(simbolo, set())
            texto_destinos = "{" + ",".join(sorted(destinos)) + "}" if destinos else "∅"
            fila += f"| {texto_destinos.center(ancho_columna)}"
        print(fila)

    print("  ╚══════════════════════════════════════════╝")


# ═══════════════════════════════════════════════════════════════════════════════
# MENÚ Y FLUJO PRINCIPAL
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

    # ── Paso 1: Definición semi-formal ───────────────────────────────────
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

    # ── Paso 2: Diagrama inicial ─────────────────────────────────────────
    print("\n  ━━━ PASO 2: GENERANDO DIAGRAMA ━━━")
    directorio = os.path.dirname(os.path.abspath(__file__))
    try:
        archivo_diagrama = generar_diagrama(afnd, directorio=directorio)
        print(f"\n  ✅ Diagrama general generado: {archivo_diagrama}")
    except Exception as e:
        print(f"\n  ⚠  Error al generar diagrama: {e}")

    # ── Paso 3: Interacción con el usuario para simular cadenas ──────────
    print("\n  ━━━ PASO 3: SIMULAR CADENAS ━━━")
    while True:
        cadena = input("\n  Ingrese cadena a simular (o 'salir' para terminar): ").strip()
        if cadena.lower() == "salir":
            print("\n  👋 ¡Vuelva pronto!")
            break

        # Ejecuta la simulación con rastreo de estados y aristas.
        historial, aceptada, error, nodos_v, aristas_u = simular_cadena(afnd, cadena)
        mostrar_resultado(cadena, historial, aceptada, error)

        # Genera el diagrama con el rastro de la computación resaltado.
        if not error:
            try:
                archivo_camino = generar_diagrama_simulacion(
                    afnd, nodos_v, aristas_u, directorio=directorio
                )
                print(f"\n  🖼  Diagrama con simulación resaltada: {archivo_camino}")
            except Exception as e:
                print(f"\n  ⚠  Error al generar diagrama de simulación: {e}")


if __name__ == "__main__":
    main()
