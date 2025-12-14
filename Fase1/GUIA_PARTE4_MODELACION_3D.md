Esta es la **Guía Técnica de Implementación para la Fase 4: Impresión**. Está diseñada bajo una arquitectura orientada a objetos donde cada componente tiene sus propios atributos (estados), métodos (procesos) y reglas de animación (Request Move).

---

###1. Definición de Elementos (Arquitectura de Datos)####A. Atributos de la Entidad (`Manuscrito`)Configura estos estados en la pestaña **Definitions > States**:

* **`Paginas`**: Entero.
* **`Tirada`**: Entero.
* **`ID_Pedido`**: Entero (clave para el Combiner).
* **`Resmas`**: Real. Cálculo: `((Paginas / 4) * Tirada) / 500`.

####B. Atributos del Modelo (Globales)* **`gCostoTotal`**: Real. Acumula todos los costos de la editorial.

####C. Recursos Disponibles (`Workers`)En cada objeto Worker, ve a **Financials** y asigna:

* **`Operador_Offset`**: Usage/Idle Cost = Q40.91/h.
* **`Jefe_Area`**: Usage/Idle Cost = Q48.70/h.
* **`Tecnico`**: Usage/Idle Cost = Q40.91/h.

---

###2. Estructura de Flujo (Graphviz)```dot
digraph Fase4_Impresion {
    rankdir=LR;
    node [shape=box, style=filled, color="#E3F2FD", fontname="Consolas"];

    // Entrada y Decisión
    In [label="TransferNode:\nSalida_Fase3", shape=diamond, color=orange];
    Decide [label="¿Tirada > 1000?", shape=parallelogram, color=yellow];

    // Rama Externa
    Externo [label="Server_Externo\nU(12, 20) días\nQ500/resma", color="#FFEBEE"];

    // Rama Interna
    Split [label="Separator:\nCrear Portada", color="#E1F5FE"];
    Offset [label="Server_Offset\n(Interiores)\nCap: 4", color="#E8F5E9"];
    Laser [label="Server_Laser\n(Portadas)\nCap: 2", color="#E8F5E9"];
    Join [label="Combiner:\nEnsamble_Fisico", color="#E1F5FE"];

    Out [label="Hacia Fase 5", shape=diamond, color=orange];

    // Conexiones
    In -> Decide;
    Decide -> Externo [label="True"];
    Decide -> Split [label="False"];
    Split -> Offset [label="Parent"];
    Split -> Laser [label="Member"];
    Offset -> Join [label="ParentInput"];
    Laser -> Join [label="MemberInput"];
    Externo -> Out;
    Join -> Out;
}

```

---

###3. Configuración Detallada de Objetos####A. Horario Laboral (`Schedule_Editorial`)* **Pestaña Data > Work Schedules**: 07:00-12:00 y 13:00-15:00 (Lunes a Viernes).
* **Aplicación**: En `Server_Offset`, `Server_Laser` y todos los `Workers`, pon `Capacity Type = WorkSchedule`.
* **Off-shift Rule**: `Suspend` (para no perder progreso a las 15:00).

####B. Server_Offset (Configuración de Recursos y Movimiento)Aquí aplicamos la lógica de vinculación de personal y el **Request Move**:

1. **Secondary Resources (Operador y Jefe)**:
* Abre el *Repeat Group* en **Secondary Resources > For Processing**.
* **Fila 1 (Operador)**:
* Resource Name: `Operador_Offset`.
* Destination Type: `To Node`.
* Node Name: `Server_Offset.Input`.


* **Fila 2 (Jefe)**:
* Resource Name: `Jefe_Area`.
* Destination Type: `None` (Supervisa sin caminar).




2. **Reliability Logic (Fallas)**:
* Failure Type: `Calendar Time Based`.
* Uptime: `Random.Exponential(120)` Hours.
* Repair Time: `Random.Exponential(8)` Hours.


3. **Lógica de Reparación (Opción B: Eventos)**:
* Ve a la pestaña **Add-on Process Triggers**.
* **Failure Occurred**: Crea un proceso con un paso **`Seize`**.
* Resource Name: `Tecnico`.
* Destination Type: `To Node`.
* Node Name: `Server_Offset.Input`.


* **Repair Completed**: Crea un proceso con un paso **`Release`**.
* Resource Name: `Tecnico`.





####C. Server_Laser (Portadas)* **Capacity**: 2 (Usa `WorkSchedule`).
* **Processing Time**: `Random.Uniform(45, 50)` Horas.
* **Secondary Resources**: Misma lógica que el Offset (Operador + Jefe).

####D. Server_Externo (Tercerización)* **Capacity**: `Infinity`.
* **Processing Time**: `Random.Uniform(12, 20)` Días.
* **State Assignment (On Entering)**:
* `gCostoTotal = gCostoTotal + (Manuscrito.Resmas * 500)`.



---

###4. Sincronización y Salida####Combiner (`Ensamble_Fisico`)Para que el libro sea una unidad antes de Encuadernación:

* **Matching Rule**: `Match Members`.
* **Member Query**: `Entity.Manuscrito.ID_Pedido == Parent.Manuscrito.ID_Pedido`.

####Lógica de Costo de Papel InternoEn los servidores internos (`Offset` y `Laser`), ve a **State Assignments > On Exited**:

* `gCostoTotal = gCostoTotal + (Manuscrito.Resmas * 50)`.

###💡 Notas de Animación para el "Dev"* **Worker Idle Action**: Para el **Técnico**, selecciona `Go to Home` en su propiedad de *Idle Action*. Así, tras el `Release` en el evento "Repair Completed", volverá a su estación y no se quedará estorbando en el nodo de entrada de la máquina.
* **Paths**: Asegúrate de que los caminos que conectan a los Workers con los servidores tengan la propiedad `Allow Passing = True` para evitar bloqueos visuales.

Con esta configuración, tu Fase 4 es técnicamente perfecta y sigue los estándares de **SASMAA7**. ¿Listo para la **Fase 5: Encuadernación**?