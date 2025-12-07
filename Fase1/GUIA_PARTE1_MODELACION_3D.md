### Documentación Técnica: Fase 1 - Recepción y Evaluación

#### 1. Definiciones Globales (Model Logic)
Se configuraron las variables de estado y horarios base para la simulación.
* **States (Manuscrito):**
    * `TipoPublicacion`: Entero (1=Libro, 2=Revista, 3=Manual, 4=Institucional).
    * `TotalRevisiones`: Entero (Meta de revisiones necesaria: 1, 2 o 3).
    * `Contador`: Entero (Acumulador de revisiones realizadas).
* **WorkSchedule (`StandardWeek`):**
    * Configurado según restricción laboral: Lunes a Viernes, **07:00-12:00** y **13:00-15:00**.
* **Colores Entidades (Manuscrito):**
    * En el Source **Llegada**, en una row de State Assigments > Before Exiting, está configurado que:
      * State Variable Name: Manuscrito.Picture
      * New Value: Manuscrito.TipoPublicacion - 1
    Básicamente significa que el nuevo valor equivale al ID (0, 1 ,2 o 3) de un Symbol, que es básicamente el "triangulito" con un color diferente 

#### 2. Lógica de Entrada (Source: Llegada)
Al crearse la entidad, se inicializan sus atributos mediante *State Assignments (Before Exiting)*:
* **Tipo de Doc:** Asignación aleatoria (ej. 25% c/u).
* **Meta de Revisiones:** `Random.Discrete(1, 0.6, 2, 0.9, 3, 1.0)` (60% requiere 1, 30% requiere 2, 10% requiere 3).
* **Contador:** Inicializado en `0`.

#### 3. Ruteo de Clasificación (Paths de Entrada)
Desde el nodo de llegada hacia los 4 servidores paralelos (ver diagrama). Se usa la propiedad **Selection Weight** en cada *Path* para filtrar:

* **Path hacia `Server_Libro`:** `Manuscrito.TipoPublicacion == 1`
* **Path hacia `Server_Revista`:** `Manuscrito.TipoPublicacion == 2`
* **Path hacia `Server_Manual`:** `Manuscrito.TipoPublicacion == 3`
* **Path hacia `Server_Inst`:** `Manuscrito.TipoPublicacion == 4`

#### 4. Configuración de Servidores (Procesamiento)
Cada servidor (`Server_Libro`, etc.) comparte la misma configuración lógica:
* **Capacity Type:** `WorkSchedule` (Usando `StandardWeek`).
* **Processing Time:** `Math.Round(Random.Uniform(3, 5))`
* **Units:** `Days`.

#### 5. Lógica de Ciclo y Salida (Loop Logic)
El control de flujo ocurre en el **Output Node** de cada servidor y sus paths salientes.

**A. Actualización de Estado (En el Output Node):**
* *State Assignment (On Entered):* `Manuscrito.Contador = Manuscrito.Contador + 1`

**B. Decisión de Ruteo (Paths de Salida):**
Se evalúa si el documento cumplió su meta o debe regresar.
* **Path de Regreso (Loop):** Conecta del OutputNode al InputNode del mismo server.
    * *Selection Weight:* `Manuscrito.Contador < Manuscrito.TotalRevisiones`
* **Path de Salida (Éxito):** Conecta hacia la siguiente fase (Diagramación).
    * *Selection Weight:* `Manuscrito.Contador >= Manuscrito.TotalRevisiones`

---
**Resumen del Ciclo para Devs:**
> La entidad entra al server específico por su `Tipo`. Al salir, incrementa su `Contador`. Los paths evalúan: si `Contador` es menor a `Meta`, el path de retorno se vuelve "True" y la entidad reingresa a la cola. Si `Contador` iguala a la `Meta`, el path de salida se habilita y la entidad avanza.