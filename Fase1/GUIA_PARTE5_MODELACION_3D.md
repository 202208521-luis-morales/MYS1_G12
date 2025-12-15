Esa variable no aparece con ese nombre exacto en el PDF, ya que es un **valor calculado** que debes construir utilizando los datos de las tablas proporcionadas. En el contexto de Simio, representa la suma de los costos de mano de obra y recursos durante la Fase 5.

Para obtenerla o calcularla, debes cruzar la información de la **Tabla 1** y la **Tabla 6**:

###1. Componentes del Costo (Fuente: Tabla 1)Debes extraer los costos por hora (Q/h) del personal involucrado en la encuadernación:

* 
**Guillotinista:** Q40.91 por hora.


* 
**Operador pegadora:** Q40.91 por hora.


* 
**Jefe de área encuadernación:** Q8.70 por hora.


* 
**Personal de empaque/revisión:** Q40.91 por hora.



###2. Tiempos de Procesamiento (Fuente: Tabla 6)Cada proceso de encuadernación consume una cantidad de tiempo proporcional a las **resmas** del pedido:

* 
**Compaginado:** Triangular(0.068, 0.084, 0.100) horas/resma.


* 
**Corte y rasurado:** Triangular(0.068, 0.084, 0.100) horas/resma.


* 
**Armado:** Triangular(0.090, 0.112, 0.134) horas/resma.


* 
**Prensado:** Triangular(0.045, 0.056, 0.067) horas/resma.


* 
**Encuadernado:** Triangular(0.045, 0.056, 0.067) horas/resma.


* 
**Secado:** Triangular(0.022, 0.028, 0.034) horas/resma.


* 
**Empaque:** Triangular(0.022, 0.028, 0.034) horas/resma.



---

###¿Cómo implementarlo en Simio?No necesitas crear una variable manual si configuras bien los **Workers**. Simio calcula el costo automáticamente si sigues estos pasos:

1. 
**Configura los Workers:** En la pestaña *Definitions*, asigna a cada trabajador (Guillotinista, Operador, etc.) su `Static Cost Rate` según la **Tabla 1**.


2. **Usa Secondary Resources:** En cada servidor de la Fase 5 (Corte, Pegado, etc.), agrega al trabajador correspondiente en la propiedad **Secondary Resources > For Processing**.
3. **Cálculo Automático:** Simio acumulará el costo en la propiedad interna del objeto: `Resource.CostIncurred`.
4. **Para el Costo Total:** Si quieres actualizar tu variable global `gCostoTotal` al final de la fase, la lógica sería:
> `gCostoTotal = gCostoTotal + (Tiempo_Procesamiento * Tasa_Salarial_Total)`



**Resumen de la "variable":** Es el resultado de multiplicar el tiempo que el libro pasa en cada máquina (Tabla 6) por el salario de los trabajadores que lo atienden (Tabla 1).

¿Quieres que te ayude a configurar la **Fase 6: Control de Calidad**, donde se aplican las probabilidades de rechazo del 8% que menciona la Tabla 7?