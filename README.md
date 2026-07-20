# Guía del Proyecto 1 — qué hicimos, por qué, y cómo explicarlo

Documento de estudio. Sigue el orden de las actividades del PDF.
Los números citados son los de la corrida real (9,706 registros).

---

## La idea general, en un párrafo

El MINEDUC publica los establecimientos educativos del país en una página web con un formulario
de búsqueda. No hay botón de descarga ni API. Entonces el proyecto consiste en: **sacar** esos
datos automáticamente (actividades 1–2), **diagnosticar** en qué estado vienen (actividad 3),
**planificar** cómo arreglarlos antes de tocarlos (actividad 4), **arreglarlos** variable por
variable (actividad 5), **dejar constancia** de todo lo que se cambió (actividad 6), **probar**
que quedó bien (actividad 7), **medir** la mejora (actividad 8), **exportar** el resultado
(actividad 9) y **documentarlo** para que alguien más lo entienda (actividad 10).

La idea de fondo que atraviesa todo el proyecto: **una limpieza buena hace visibles los problemas
en lugar de esconderlos.** Es fácil entregar datos que se ven impecables si borras lo dudoso y
rellenas lo que falta. Pero ese conjunto miente, porque quien lo reciba no sabe qué se perdió.

---

## ACTIVIDADES 1 y 2 — Obtener los datos

### Qué vimos
La página del MINEDUC (`BUSCAESTABLECIMIENTO_GE`) es un formulario ASP.NET con seis desplegables:
departamento, municipio, nivel, sector, plan y modalidad. Cada consulta devuelve una tabla HTML.
**No se pueden pedir los 22 departamentos de una sola vez**: el formulario obliga a elegir uno.

### Qué se hizo
Un script con **Selenium** que abre Chrome, llena el formulario 22 veces (una por departamento)
con `NIVEL = DIVERSIFICADO` y todo lo demás en `TODOS`, y convierte cada tabla HTML a `DataFrame`
con `pd.read_html`. Al final concatena las 22 consultas y guarda `establecimientos.csv`.

### Por qué así
- **Selenium y no `requests`:** la página usa *postbacks* de ASP.NET. Al elegir un departamento,
  el combo de municipios se recarga solo. Eso no se puede simular con una petición HTTP simple;
  hay que manejar un navegador real. Por eso está el `time.sleep(2)`, que le da tiempo al combo
  de recargarse.
- **Un departamento a la vez:** es la única forma que permite el formulario. La "unión" de los 22
  resultados es parte de lo que evalúa la rúbrica (5 puntos: "obtención, documentación y unión").
- **El `if not os.path.exists("establecimientos.csv")`:** hace el notebook reproducible sin ser
  destructivo. Si el crudo ya existe, se salta el scraping. Así puedes correr el notebook
  completo mil veces sin volver a bajar los datos ni arriesgarte a que la página cambie.
- **Se guarda el crudo sin modificar:** lo pide la actividad 2. Es el punto de partida al que
  siempre se puede volver.

---

## ACTIVIDAD 3 — Diagnóstico (15 puntos)

Antes de limpiar, hay que saber qué está roto. Esta actividad **no modifica nada**, solo mide.

Primero se carga el crudo con `dtype=str` (todo como texto, para que pandas no adivine tipos) y se
filtra a `NIVEL == "DIVERSIFICADO"`. Ese filtro es defensivo: aunque el scraping ya bajó solo
diversificado, si alguien regenera el archivo con más niveles el notebook sigue funcionando.

### 3a — Registros y variables
**9,706 registros × 17 variables.** El punto de partida.

### 3b — Tipo de dato de cada variable
**Lo que vimos:** todo llegó como texto. Es inevitable: viene de una tabla HTML, donde no hay
tipos, solo cadenas.

**Lo que se hizo:** una tabla que compara el tipo actual con el tipo que *debería* tener cada
variable.

**Por qué importa:** hay dos casos donde "texto" es la respuesta correcta y hay que justificarlo:
- `TELEFONO` parece numérico, pero no lo es. Nadie suma teléfonos. Y como una celda puede traer
  dos números, convertirlo a entero sería imposible.
- `CODIGO` y `DISTRITO` traen guiones y ceros a la izquierda. Si los conviertes a entero,
  `01-05-0234-43` se vuelve basura.

### 3c — Valores faltantes
**Lo que vimos:** 2,555 celdas vacías, el **1.55%** del total. Concentradas en `DIRECTOR`,
`TELEFONO` y `SUPERVISOR`.

**Por qué importa:** que `DIRECTOR` sea la más vacía tiene una lectura que no es obvia — puede
ser una **vacante real**, no un error de captura. Esa distinción decide todo el tratamiento
posterior (por eso no se imputa nada).

### 3d — Valores únicos
**Lo que se hizo:** contar cuántos valores distintos tiene cada variable.

**Para qué sirve:** distingue tres tipos de variable de un vistazo.
- Pocos valores únicos (2, 5, 13) → es **categórica**: `AREA`, `SECTOR`, `MODALIDAD`.
- Tantos valores únicos como registros → es un **identificador**: `CODIGO`.
- Muchos pero no todos → es **texto libre**: `ESTABLECIMIENTO`, `DIRECCION`.

### 3e — Duplicados exactos
**Lo que vimos: cero.** No hay ninguna fila idéntica a otra en las 17 columnas, ni filas 100%
vacías. El MINEDUC entrega un conjunto limpio en ese sentido.

**Por qué se midió de varias formas:** la tabla mide duplicados con `keep=False` (todas las
ocurrencias) y sin él (solo las repeticiones), más las filas vacías y los códigos repetidos. Esto
es porque un "duplicado" puede significar cosas distintas, y hay que ser explícito sobre cuál se
está contando.

### 3f — Valores fuera de dominio
**Lo que vimos:**
- `AREA` debería ser solo {URBANA, RURAL} pero trae **`SIN ESPECIFICAR`**, que no es ninguna de
  las dos.
- `TELEFONO` trae longitudes **de 1 a 16 dígitos**, cuando un teléfono guatemalteco tiene 8.
- `STATUS` trae categorías raras (`TEMPORAL NOMBRAMIENTO`, `TEMPORAL TITULOS`) que **sí son
  válidas** administrativamente, solo poco frecuentes.
- `DEPARTAMENTO` y `CODIGO` están **impecables**.

**La distinción clave:** "raro" no es lo mismo que "inválido". `SIN ESPECIFICAR` está fuera del
dominio; `TEMPORAL TITULOS` solo es infrecuente. Al primero se le hace algo, al segundo no.

### 3g — Formatos inconsistentes
**Lo que vimos: 3 variables con problemas de formato.**
- `ESTABLECIMIENTO`: mezcla comillas dobles y simples, y algunas quedan **sin cerrar**.
- `TELEFONO`: guiones, comas y texto mezclados con los números.
- `DISTRITO`: **dos convenciones distintas coexisten** (`NN-NNN` y `NN-NN-NNNN`), más valores
  truncados.

### 3h — Problemas potenciales de calidad
**Lo que se hizo:** tres chequeos que no caben en los incisos anteriores.
- ¿`DEPARTAMENTAL` contradice a `DEPARTAMENTO`? → No, ninguna contradicción.
- ¿Hay caracteres invisibles (saltos de línea, BOM, espacios de ancho cero)? → Se cuentan por
  columna. Son peligrosos porque son **invisibles**: dos valores que se ven idénticos pueden no
  serlo para la computadora.
- ¿Cuántos municipios distintos hay, de los 340 del país? → Menos. Y hay que averiguar si es por
  errores de escritura o porque hay municipios sin oferta de Diversificado.

---

## ACTIVIDAD 4 — Plan de limpieza (10 puntos)

Se escribe **antes** de tocar los datos. Para cada una de las 17 variables, tres columnas:

1. **Problema encontrado** — sale del diagnóstico.
2. **Regla de corrección** y por qué debería funcionar.
3. **Riesgos** de aplicar esa regla.

**La tercera columna es la que da los puntos.** Ejemplo concreto: la regla para `TELEFONO` es
"quedarse con el primer número de 8 dígitos". Suena inofensiva. Pero si una celda traía
`"2233-4455 (antiguo), 7788-9900"`, te quedas con el viejo y descartas el vigente. Ese riesgo hay
que dejarlo por escrito.

**Por qué se hace antes:** obliga a pensar la limpieza en lugar de improvisarla, y deja evidencia
de que las decisiones fueron deliberadas. La actividad 6 es el espejo: el plan dice qué *pensabas*
hacer, el registro dice qué *hiciste*.

---

## ACTIVIDAD 5 — La limpieza (30 puntos, la mitad de todo)

### 5.0 — Renombrado de columnas
`CODIGO` → `codigo_establecimiento`, `STATUS` → `estado`, etc. Nombres descriptivos en
`snake_case`. Lo pide la actividad 9c, pero tiene que pasar antes de limpiar.

A partir de aquí se trabaja sobre `df`. **`df_raw` se conserva intacto** para poder comparar en la
actividad 8.

---

### 5a — Faltantes, cadenas vacías y placeholders

**Qué vimos:** además de los `NA` reales, había celdas que *fingían* tener información: `"-"`,
`"N/A"`, `"NULL"`, `"SIN DATO"`, `"XXX"`, `"@"`, y celdas con solo espacios.

**Qué se hizo:**
1. Eliminar filas 100% vacías (en este conjunto: ninguna).
2. Cadenas vacías y celdas de puros espacios → `NA`.
3. Placeholders → `NA`, comparando en mayúsculas y sin espacios (para que `" n/a "` también caiga).

**Por qué así:** un `"-"` no es un dato, es un dato ausente disfrazado de texto. Si lo dejas,
cualquier `value_counts()` posterior va a contar `"-"` como si fuera una categoría real.
Convertirlo a `NA` **hace visible un problema que estaba escondido**.

**La decisión más importante: no se imputa nada.** No se rellena ningún faltante con la media, la
moda ni nada. Razón: un establecimiento sin director puede tener una **vacante real**. Inventar un
nombre metería un error que el analista no podría detectar jamás.

---

### 5b — Tipos de dato

**Qué se hizo:** dos listas.
- `VARIABLES_STRING` (7): identificadores y texto libre → tipo `string`.
- `VARIABLES_CATEGORICAS` (10) → se dejan como `string` **durante** la limpieza y se convierten a
  `category` hasta el final, en la actividad 9.

**Por qué se posterga la conversión a `category`:** porque en 5c, 5d y 5f las categorías todavía
cambian. Si conviertes antes, cada modificación tendría que actualizar la lista de categorías
permitidas y se vuelve un enredo.

**Por qué `category` al final:** una variable categórica con 4 valores repetidos 9,706 veces ocupa
mucha menos memoria como `category` que como texto, y además pandas puede validar que no
aparezcan valores fuera de la lista.

---

### 5c — Normalización de texto

**Qué se hizo, en este orden:**

| Paso | Qué arregla |
|---|---|
| `unicodedata.normalize("NFKC")` | caracteres compuestos y variantes raras de Unicode |
| eliminar categorías `Cc`/`Cf` | caracteres **invisibles**: saltos de línea, BOM, espacio de ancho cero |
| `re.sub(r"\s+", " ")` | espacios múltiples y tabuladores internos |
| `.strip()` | espacios al inicio y al final |
| reemplazo de `“ ” ‘ ’` por `"` y `'` | comillas tipográficas de Word |
| `.upper()` | mayúsculas consistentes |

**Por qué las mayúsculas omiten `codigo_establecimiento`, `codigo_distrito` y `telefono`:** son
identificadores numéricos. No tienen letras, así que pasarlos a mayúsculas no haría nada — pero
dejarlos fuera documenta que se pensó en ellos.

**La decisión sobre las tildes** (esta es fina y vale la pena entenderla): las tildes **se
conservan** en el valor visible. El nombre correcto es *Sololá*, no *Solola*. Pero para
**comparar** dos valores se usa una función aparte (`quitar_tildes`) que trabaja sobre una copia.

Así se logran dos cosas a la vez: los nombres propios no se corrompen, y aun así se detecta que
`"SOLOLÁ"` y `"SOLOLA"` son el mismo municipio escrito de dos formas.

**La celda que sigue** (`df[VARIABLES_STRING] = ... .astype("string")`) no cambia ningún valor,
solo repone el tipo de dato: `Series.map()` devuelve columnas `object`, así que hay que volver a
fijar `string`. Sin eso, la validación de tipos de la actividad 7 falla.

---

### 5d — Consistencia de categorías

El problema clásico: `Guatemala`, `GUATEMALA`, `guatemala` y `Guatemla` son cuatro categorías
distintas para la computadora, pero un solo valor real.

**Paso 1 — variantes seguras.** Para cada variable categórica se calcula una **clave normalizada**
(sin tildes, sin puntuación, en mayúsculas). Los valores que colapsan a la misma clave son el mismo
valor escrito distinto, y se unifican a **la forma más frecuente**.

*Por qué a la más frecuente y no a una elegida a mano:* porque es una regla objetiva y
reproducible. Elegir a mano introduce criterio personal que nadie puede verificar.

**Paso 2 — municipios por similitud.** Aquí no basta la clave normalizada, porque un error de
dedo (`SOLOLÁ` vs `SOLOLLÁ`) no colapsa a la misma clave. Se usa **RapidFuzz** para encontrar pares
de municipios con similitud ≥ 90%.

*Por qué dentro de cada departamento:* **hay municipios con el mismo nombre en departamentos
distintos.** Unificarlos entre departamentos sería un error grave — estarías fusionando dos lugares
que existen de verdad y son diferentes.

*Por qué este paso solo reporta y no modifica:* se revisaron los pares a mano. El único caso
sospechoso fue **San Juan Atitán**, que parecía un error de "Atitlán" pero **está correctamente
escrito**. Como ningún par resultó ser un error real, no se unificó nada. Reportar sin modificar
es la decisión correcta cuando la evidencia no alcanza.

**Resultado: 0 categorías inconsistentes.** El conjunto ya venía consistente en esto.

---

### 5e — Formatos

#### Teléfonos
En Guatemala el teléfono tiene **8 dígitos**. La celda original mezclaba números, guiones, comas
y texto, y a veces traía **dos teléfonos juntos**.

**La regla:** extraer todas las secuencias de dígitos de la celda, quedarse con las de exactamente
8 dígitos. La primera va a `telefono`, la segunda a `telefono_2`. Si ninguna califica → `NA`.

**Por qué se guarda el segundo en vez de botarlo:** es información real de contacto. Botarla sería
una pérdida gratuita.

**Por qué `NA` y no un valor por defecto:** no se puede inventar un teléfono. Si el dato era
inválido, `NA` es la respuesta honesta.

#### Códigos
- `codigo_establecimiento`: se **valida** el formato `NN-NN-NNNN-NN` pero **no se modifica nada**.
  Es la llave primaria; tocarla sería peligroso.
- `codigo_distrito`: coexisten dos formatos. **No se convierte uno en otro** porque no hay forma de
  hacerlo sin inventar dígitos. En su lugar se documenta cuál usa cada registro en
  `codigo_distrito_formato`, y los truncados pasan a `NA`.

#### Direcciones
Espacios y mayúsculas ya se arreglaron en 5c. Aquí solo queda quitar el espacio antes de coma o
punto: `"ZONA 12 ,"` → `"ZONA 12,"`.

#### Nombres — esta es la decisión más interesante del inciso
El plan original decía "unificar comillas simples a dobles". **Se cambió a propósito**, y el
cambio es correcto:

En este conjunto las comillas simples **no son comillas**. Son ortografía real de nombres en
idiomas mayas: `RUK'U'X`, `NALEB'`, `KAQCHIKEL AMAQ'`. También hay posesivos en inglés (`BROWN'S`).
Unificarlas a comillas dobles habría **corrompido esos nombres**.

Entonces solo se corrigen las **comillas dobles sin cerrar** (número impar de `"` en el registro).
Y como no hay forma de saber dónde faltaba la comilla, se eliminan todas las del registro en lugar
de inventar una posición.

---

### 5f — Valores inválidos

**`area = "SIN ESPECIFICAR"` → `NA`.** No pertenece al dominio {URBANA, RURAL} y no aporta
información.

**Por qué no se elimina la fila:** si el MINEDUC lo usara con el sentido de "no aplica", el
registro seguiría siendo útil. Se marca el dato como ausente, no se bota el establecimiento.

**`departamento`** se valida contra los 22 oficiales → ninguno fuera de catálogo.
**`nivel`** se valida como constante `DIVERSIFICADO` → confirma que el filtro funcionó.

---

### 5g — Duplicados

#### Duplicados exactos
**Cero.** No había filas idénticas. La operación se ejecuta igual, por si el conjunto cambia.

#### Duplicados parciales — el hallazgo central del proyecto
**Lo que vimos:** los duplicados de este conjunto **no son exactos, son parciales**. Un mismo
establecimiento aparece varias veces porque ofrece Diversificado en más de una jornada, plan o
sector. La fuente registra **una fila por oferta, no por establecimiento**.

**Cómo se detectan:** similitud de cadenas (RapidFuzz `token_sort_ratio`) sobre
`nombre_establecimiento` **y** `direccion`, exigiendo que ambas superen su umbral (90 y 85), y solo
comparando dentro de cada par (departamento, municipio).

**Las cuatro decisiones de diseño y su porqué:**

| Decisión | Por qué |
|---|---|
| `token_sort_ratio` y no `WRatio` | es insensible al orden de las palabras (`"COLEGIO SAN JOSÉ"` vs `"SAN JOSÉ, COLEGIO"`) pero mucho menos propenso a falsos positivos por coincidencias parciales |
| exigir nombre **y** dirección | solo por nombre es inútil: hay cientos de institutos que se llaman exactamente igual en todo el país. La dirección es lo que distingue una sede de otra |
| comparar solo dentro de cada municipio | dos establecimientos con el mismo nombre en municipios distintos son distintos. Además reduce el costo de O(n²) global a la suma de O(nᵢ²) por municipio |
| umbral 85 en dirección vs 90 en nombre | las direcciones varían más por números de casa o lote sin dejar de ser la misma sede |

**El Union-Find:** si A se parece a B, y B se parece a C, los tres deben quedar en el mismo grupo
aunque A y C no se parezcan directamente. Eso es lo que hace la estructura de `padre_grupo` y la
función `raiz()`.

**La clasificación — lo que convierte un problema inmanejable en algo útil:**
Marcar 5,001 registros como "posibles duplicados" sin más no le sirve a nadie. Por eso cada grupo
se cruza con `jornada`, `plan_educativo` y `sector`:

- Si el grupo tiene **varias combinaciones** → `misma_sede_oferta_distinta`. Es el mismo colegio
  con dos jornadas. **No es un error**, es la granularidad real de la fuente. Son ~4,486 registros.
- Si tiene **una sola combinación** → `posible_duplicado_real`. Mismo nombre, misma dirección,
  misma oferta. Son **515** (5.3%), y esos sí hay que revisarlos a mano.

**Ninguno se elimina automáticamente.** Lo exige la guía, pero además es lo correcto: borrar los
4,486 habría destruido información real sobre la oferta educativa del país.

---

### 5h — Consistencia entre variables

Seis cruces que verifican que dos variables no se contradigan:

1. `departamento` ↔ `direccion_departamental` — la dirección departamental siempre debe empezar
   con el nombre del departamento (Guatemala se subdivide en 4, Quiché en 2).
2. `departamento` ↔ prefijo de `codigo_establecimiento` — los dos primeros dígitos del código son
   el departamento.
3. `codigo_establecimiento` ↔ `codigo_distrito` — ambos deben empezar igual.
4. `departamento` ↔ `municipio` — municipios que aparecen en más de un departamento.
5. `jornada` ↔ `plan_educativo` — contexto, para confirmar que las jornadas raras corresponden a
   planes válidos.
6. `area` ↔ `municipio` — contexto, la mezcla urbano/rural es normal.

**Un detalle fino del chequeo 2:** el prefijo esperado de cada departamento **se deduce de los
propios datos** (es el más frecuente dentro de ese departamento), no se transcribe de memoria. Si
lo escribieras de memoria y te equivocaras, marcarías como inválidos registros que están bien.

**El resultado:** las relaciones resultaron **sólidas**. Los únicos "conflictos" son municipios
homónimos, que son legítimos del sistema administrativo guatemalteco.

**Ninguna inconsistencia se corrige automáticamente.** Cuando dos variables se contradicen no hay
forma de saber cuál está mal sin consultar la fuente. Corregir una a partir de la otra
**propagaría** el error en lugar de eliminarlo, y encima lo volvería invisible.

---

### 5i — Variables derivadas

Nueve columnas nuevas. **Ninguna reemplaza a una original**: todas son metadatos de calidad.

| Variable | Para qué |
|---|---|
| `telefono_2` | segundo contacto que se habría perdido |
| `telefono_valido` | filtrar rápido los contactables |
| `telefono_multiple` | trazabilidad: qué celdas hubo que desagregar |
| `codigo_establecimiento_valido` | integridad de la llave primaria |
| `codigo_distrito_formato` | documenta el formato sin alterar el valor |
| `posible_duplicado` | permite un análisis conservador |
| `grupo_posible_duplicado` | inspeccionar juntos los de un mismo grupo |
| `tipo_posible_duplicado` | separa granularidad legítima de duplicado real |
| `departamento_municipio` | llave geográfica que evita sumar municipios homónimos |

**El criterio general: marcar antes que borrar.** Una fila eliminada es información perdida. Una
fila marcada la puede descartar el analista cuando lo necesite. Si alguien no está de acuerdo con
una decisión del equipo, tiene la información para revertirla.

---

## ACTIVIDAD 6 — Registro de transformaciones

Una tabla con una fila por cada cambio: variable, problema, transformación, **registros afectados**
y justificación.

Es el espejo del plan de limpieza. El plan dice qué se pensaba hacer; el registro dice qué se hizo
y a cuántos registros les pegó. Los números salen del código, no se escriben a mano.

---

## ACTIVIDAD 7 — Validación (10 puntos)

Trece pruebas automáticas sobre el conjunto ya limpio: sin duplicados exactos, sin espacios
sobrantes, teléfonos de 8 dígitos, departamentos del catálogo, tipos correctos, sin categorías
duplicadas, `area` solo URBANA/RURAL, `nivel` constante.

**Por qué `raise AssertionError` y no solo un print:** si algo falla, el notebook **se detiene**.
Así el CSV limpio nunca se puede exportar en un estado inválido. Es una red de seguridad, no un
reporte.

**Los códigos repetidos son informativos, no falla dura**, por coherencia con lo que dice 5g: se
reportan para revisión manual en lugar de invalidar todo el conjunto.

---

## ACTIVIDAD 8 — Informe de calidad (10 puntos)

| Métrica | Antes | Después |
|---|---|---|
| Registros | 9,706 | 9,706 |
| Variables | 17 | 26 |
| Valores faltantes | 2,555 (1.55%) | 2,688 (1.63%) |
| Duplicados exactos | 0 | 0 |
| Posibles duplicados | no evaluado | 5,001 (515 candidatos reales) |
| Formato inconsistente | 3 | 0 |
| Categorías inconsistentes | 0 | 0 |

**Las dos cosas que hay que saber explicar:**

**Por qué los faltantes SUBEN (+133).** No es un error. Esas 133 celdas ya eran datos ausentes,
solo que disfrazados de texto: `"-"`, `"SIN DATO"`, teléfonos inválidos, códigos truncados,
`SIN ESPECIFICAR`. Convertirlos a `NA` los hace visibles. La alternativa —dejarlos como texto—
daría un informe más bonito y un conjunto menos honesto.

**Por qué los registros NO bajan.** Porque no había nada que eliminar: cero filas vacías, cero
duplicados exactos. Que el número no cambie confirma que la limpieza fue **no destructiva**.

**El argumento central:** la mejora no está en los conteos agregados, que casi no se mueven. Está
en tres cosas que el crudo no tenía: los datos ausentes ahora son detectables, los formatos son
verificables por pruebas automáticas, y la duplicación parcial pasó de invisible a cuantificada.

---

## ACTIVIDAD 9 — Conjunto limpio (10 puntos)

Un solo CSV con los 22 departamentos. Las columnas se ordenan por lógica (identificación →
geografía → descripción → contacto → clasificación → metadatos de calidad), las categóricas se
convierten a `category` y todo se ordena por departamento, municipio y nombre.

---

## ACTIVIDAD 10 — Libro de códigos (10 puntos)

Para cada variable: descripción, tipo, dominio permitido, valores posibles, tratamiento aplicado,
si es derivada. Más fuente, fecha de extracción y versión.

Se genera desde el notebook para que las cifras nunca se desincronicen de los datos.

---

## Cómo explicarlo en dos minutos

> "Bajamos 9,706 establecimientos de diversificado del portal del MINEDUC con Selenium, porque el
> sitio no tiene descarga y hay que consultar departamento por departamento.
>
> El diagnóstico mostró que el conjunto venía en mejor estado del esperado: cero duplicados
> exactos, cero categorías mal escritas. Los problemas reales eran tres: valores ausentes
> disfrazados de texto, el campo de teléfono que mezclaba varios números por celda, y una
> duplicación parcial que no se veía a simple vista.
>
> La limpieza siguió un criterio: hacer visibles los problemas en lugar de esconderlos. No
> imputamos ningún faltante, no borramos ningún registro con información y toda decisión discutible
> quedó marcada en una columna en vez de aplicada en silencio.
>
> El hallazgo principal es que la fuente registra **una fila por oferta educativa, no por
> establecimiento**. Por eso 5,001 registros caen en grupos de similitud, pero solo 515 son
> candidatos a duplicado real; el resto es el mismo colegio con distintas jornadas o planes.
> Ninguno se eliminó: se entregan marcados para que el analista decida.
>
> Al final, 13 pruebas automáticas verifican el conjunto y detienen el proceso si algo falla."



**"¿Por qué subimos los faltantes si limpiaron?"**
Porque los placeholders ya eran datos ausentes disfrazados de texto. Convertirlos a `NA` hace
visible un problema que estaba escondido.

**"Marcamos el 51% del conjunto como posible duplicado, ¿no es demasiado?"**
La mayoría es `misma_sede_oferta_distinta`: el mismo establecimiento con varias jornadas. No es un
error, es la granularidad de la fuente. Los candidatos a duplicado real son 515, el 5.3%.
