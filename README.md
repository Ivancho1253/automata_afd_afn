# Simuladores Interactivos de Autómatas (AFD y AFND)

Este repositorio contiene dos completos scripts en Python diseñados para simular, probar y visualizar de forma interactiva y paso a paso **Autómatas Finitos Deterministas (AFD)** y **Autómatas Finitos No Deterministas (AFND)**.

## 🚀 Características Principales

- 🏗 **Definición Dinámica e Interactiva**: Podrás construir tu autómata directamente por consola ingresando:
  - Conjunto de estados.
  - Alfabeto utilizado.
  - Estado inicial y estados de aceptación.
  - Función de transición completa (evaluando individualmente cada combinación).
- ⚙️ **Soporte Avanzado para AFND**:
  - Manejo eficiente del **no determinismo** (múltiples estados origen-destino para una misma entrada).
  - Cálculo automático de **clausura epsilon** (transiciones nulas `ε`).
- 🔍 **Simulación Paso a Paso**: Rastreo de la cadena ingresada símbolo a símbolo. Observarás cómo evoluciona en la terminal el conjunto de estados en tiempo real (vital para AFND), seguido del veredicto final (✅ ACEPTADA o ❌ RECHAZADA).
- 🖼 **Generación de Gráficos (GraphViz)**:
  - Creación automática de diagramas estilizados de tipo académico al definir tu autómata.
  - Generación de esquemas dinámicos para cada simulación, donde **se resaltan en color** el camino, las aristas recorridas y los vértices/estados visitados a lo largo de la evaluación.

## 📂 Archivos del Proyecto

- `simulador_afd.py`: Motor exclusivo para la definición y simulación de Autómatas Finitos Deterministas.
- `simulador_afnd.py`: Motor de Autómatas Finitos No Deterministas, con soporte interactivo para clausuras *Épsilon*.

## 🛠 Requisitos

El proyecto depende fuertemente de **GraphViz** para generar las representaciones gráficas interactivas del recorrido.

1. **Python 3.x**
2. **Librería de Python `graphviz`**:
   Ejecuta el siguiente comando en tu entorno virtual o terminal:
   ```bash
   pip install graphviz
   ```
3. **Software de Sistema GraphViz**:
   Necesitas instalar el core de GraphViz en tu computadora. Puedes descargarlo de [https://graphviz.org/download/](https://graphviz.org/download/).
   > **Nota en Windows**: El script intenta buscar la ruta estándar (`C:\Program Files\Graphviz\bin`) automáticamente si olvidas agregarlo al PATH durante tu instalación.

## 💻 Instrucciones de Uso

Abre tu línea de comandos en este mismo directorio y ejecuta cualquiera de los simuladores dependiendo de tus necesidades:

**Para el simulador del AFD:**
```bash
python simulador_afd.py
```

**Para el simulador del AFND:**
```bash
python simulador_afnd.py
```

Sigue las instrucciones en pantalla, ingresa el autómata y prueba todas las cadenas necesarias (escribe `salir` para terminar). Las imágenes se guardarán automáticamente en la raíz del proyecto.
