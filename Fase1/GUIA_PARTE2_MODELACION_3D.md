## 📝 Documentación Técnica: Fase 2 - Corrección de Estilo

---

### 1. Nuevas Variables de Estado (Entidad: Manuscrito)

Se agregan dos estados adicionales para controlar el flujo de corrección y retrabajo, y una variable de cálculo:

* **`EsRecorreccion`**: `Boolean` (Inicializado en `False`). Indica si la entidad está en primera corrección o re-corrección.
* **`NecesitaRetrabajo`**: `Entero` (0 o 1). Flag temporal asignado después del *delay* del editor.
* **`Paginas`**: `Entero`. Asignado en *Source* según tipo de publicación para calcular tiempos ajustados.

---

### 2. Entrada a la Fase (TransferNode: Entrada\_Correccion)

* Las entidades llegan desde la convergencia de la Fase 1.
* **`Manuscrito.EsRecorreccion`** está inicializado en `False` por defecto.

---

### 3. Servidor: Server\_Corrector

Representa el recurso humano (**1 corrector**) que revisa manuscritos.

#### ⚙️ Configuración

| Propiedad | Valor | Notas |
| :--- | :--- | :--- |
| **Capacity Type** | `WorkSchedule` | Usa el horario `StandardWeek`. |
| **Initial Capacity** | `1` | |
| **Units** | `Days` | |
| **Resource Logic → Idle Cost Rate** | `55.19` Q/h | Según Tabla 1. |

#### ⏱️ Processing Time (Tiempo de Procesamiento)

$$
\text{Math.If}(\text{Manuscrito.EsRecorreccion} == \text{True}, \quad \text{Random.Triangular}(1, 2, 4) \times (1 + \text{Manuscrito.Paginas}/1000), \quad \text{Random.Uniform}(3, 5) \times (1 + \text{Manuscrito.Paginas}/1000))
$$

* **Primera corrección (EsRecorreccion = False):** $\text{U}(3,5)$ días $\times$ factor de páginas.
* **Re-corrección (EsRecorreccion = True):** $\text{Triangular}(1,2,4)$ días $\times$ factor de páginas.

---

### 4. Delay: Server\_EsperaEditor

Simula el tiempo que tarda el editor en aplicar correcciones. **No consume recursos humanos.**

#### ⚙️ Configuración

* **Capacity Type:** `Fixed Capacity`
* **Initial Capacity:** `Infinity`
* **Processing Time:** `Random.Uniform(1, 3)`
* **Units:** `Days`

#### 💡 Lógica en Output Node (`On Exiting`)

* **State Assignment:**
    $$\text{Manuscrito.NecesitaRetrabajo} = \text{Random.Uniform}(0,1) \le 0.15 \ ? \ 1 \ : \ 0$$
    > Genera flag **Bernoulli(0.15)** para decidir el retrabajo (1 = Sí, 0 = No).

---

### 5. Decisión de Ruteo (Paths desde Output de Server\_EsperaEditor)

Dos *paths* evalúan el *flag* **`NecesitaRetrabajo`**:

* **Path A: Sin Retrabajo (85%)**
    * **Selection Weight:** `Manuscrito.NecesitaRetrabajo == 0`
    * **Destino:** `TransferNode Salida_Correccion` → Diagramación.

* **Path B: Con Retrabajo (15%)**
    * **Selection Weight:** `Manuscrito.NecesitaRetrabajo == 1`
    * **Destino:** `TransferNode Loop_Recorreccion`.

---

### 6. Loop de Re-corrección (TransferNode: Loop\_Recorreccion)

Marca la entidad para que use tiempos de re-corrección en la siguiente pasada.

#### 💡 Lógica (`On Entered`)

* **State Assignment:** `Manuscrito.EsRecorreccion = True`

#### ➡️ Path de Salida

* **Conexión:** Conecta al **InputNode** de **`Server_Corrector`** (cierra el *loop*).
* **Selection Weight:** `1.0` (siempre activo).

---

### 🚀 Resumen del Ciclo para Desarrolladores

> Todas las entidades pasan por **`Server_Corrector`** (tiempo según `EsRecorreccion`) $\rightarrow$ **`Server_EsperaEditor`** (*delay* $\text{U}(1,3)$ días) $\rightarrow$ Decisión $\text{Bernoulli}(0.15)$. Si **`NecesitaRetrabajo == 1`**, marca **`EsRecorreccion = True`** y regresa al corrector con tiempos $\text{Triangular}(1,2,4)$. Si **`NecesitaRetrabajo == 0`**, avanza a Diagramación. El *loop* puede repetirse $\text{N}$ veces con $15\%$ de probabilidad en cada iteración.