# 📘 DATADIS Analyzer — Guía Técnica de Arquitectura y Operación

> Guía exhaustiva y didáctica para entender cómo DATADIS Analyzer (`da`) descubre, valida, procesa y visualiza datos de consumo horario de electricidad para comunidades de propietarios.

---

> [!IMPORTANT]
> ### 🪢 Arnés de Mantenimiento Documental y Directiva de Sincronización
> Esta guía constituye la referencia técnica oficial para desarrolladores y agentes autónomos de IA.
> **Siempre que se modifique el código fuente, DEBE verificarse y actualizarse esta documentación si los cambios afectan a:**
> 1. **Esquemas de Entrada o Formatos de Archivo:** Columnas obligatorias, codificaciones, formatos de fecha o directorios en [`src/config.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/config.py) y [`src/ingestion/`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/ingestion/).
> 2. **Matemáticas de Procesamiento e Invariantes:** Fórmula de reparto al 100,00%, comprobaciones de completitud de meses de calendario o agregaciones en [`src/processing/aggregator.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/processing/aggregator.py).
> 3. **Heurísticas de Clasificación:** Distintivos de consumidores (`★` dominante $>30\%$, `(0)` inactivo $<1\text{ kWh}$) en [`src/presentation/views.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/presentation/views.py).
> 4. **Comandos y Opciones CLI:** Subcomandos, banderas o formatos de informe en [`src/cli.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/cli.py).
> 5. **Invariantes de Privacidad y Seguridad:** Patrones de CUPS sintéticos autorizados o reglas del auditor en [`src/security.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/security.py).

---

## 1. 🎯 Propósito y Principios Fundamentales

### ¿Qué es DATADIS?
En España, **DATADIS** ([datadis.es](https://datadis.es)) es la plataforma digital unificada operada por las empresas distribuidoras de electricidad que permite a los consumidores y administradores acceder a las lecturas horarias de los contadores eléctricos.

### El Desafío en Comunidades de Propietarios
En edificios residenciales (*comunidades de vecinos*), coexisten simultáneamente múltiples puntos de suministro:
- Viviendas individuales de los propietarios.
- Servicios comunes generales (ascensores, climatización centralizada, bombas de achique/presión, iluminación de garajes, depuradoras, zonas comunes).

Cada suministro dispone de exportaciones CSV horarias independientes con hasta **8.760 lecturas anuales**, delimitadores heterogéneos (`;` frente a `,`), diversas codificaciones (`UTF-8` frente a `ISO-8859-1`) y números con coma decimal (`0,152`).

`datadis-analyzer` (`da`) automatiza la consolidación de estos archivos aportando:
1. **Descubrimiento e Ingesta Automatizados:** Lectura segura de exportaciones CSV crudas sin formateo manual previo.
2. **Reparto Porcentual Equitativo:** Cálculo matemático exacto de la cuota de participación energética de cada suministro.
3. **Comparativas Interanuales Homogéneas:** Análisis interanual riguroso que detecta y aísla meses incompletos o en curso.
4. **Visualizaciones Enriquecidas e Informes Markdown:** Paneles de terminal e informes persistentes de auditoría.
5. **Privacidad Absoluta con Cero Filtraciones:** Bloqueo estricto para evitar comprometer códigos reales de puntos de suministro (CUPS).

---

## 2. 🏛️ Visión Arquitectónica y Ciclo de Vida del Dato

La aplicación sigue una arquitectura limpia en cuatro capas por las que los datos fluyen unidireccionalmente:
1. **Ingesta y Normalización:** [`DatadisLoader`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/ingestion/loader.py) descubre los archivos CSV en `./.input/<año>/`, mientras [`DatadisValidator`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/ingestion/validator.py) analiza codificaciones y delimitadores antes de normalizar las columnas en un DataFrame unificado de Pandas.
2. **Motor de Cálculo y Analítica:** [`DataAggregator`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/processing/aggregator.py) agrupa las series temporales, evalúa la completitud de los meses entre años y calcula cuotas de reparto exactas en dataclasses de dominio en [`src/processing/models.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/processing/models.py).
3. **Presentación e Informes:** [`src/presentation/views.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/presentation/views.py) genera tablas Rich en 80 columnas, [`src/presentation/charts.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/presentation/charts.py) produce gráficos Matplotlib y [`src/presentation/export.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/presentation/export.py) genera resúmenes en Markdown.
4. **Seguridad y Privacidad:** [`src/security.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/security.py) audita continuamente el repositorio y el hook pre-commit para evitar que se registren códigos CUPS reales, credenciales o coordenadas.

---

## 3. 📥 Canal de Ingesta de Datos (Cómo Obtiene la Información)

El canal de ingesta transforma los archivos CSV heterogéneos en un DataFrame estructurado y validado.

### A. Estructura de Directorios Anualizada
- **Directorio por Defecto:** Los archivos CSV se organizan por año bajo `./.input/<año>/` (por ejemplo, `./.input/2024/*.csv`, `./.input/2025/*.csv`).
- **Estrategia de Descubrimiento:** [`DatadisLoader.discover_files`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/ingestion/loader.py#L34-L67) explora la carpeta del año indicado, recurriendo a una búsqueda recursiva bajo `./.input/` si no se aplica filtro, ignorando archivos ocultos o de respaldo.

### B. Detección Inteligente de Formato y Esquema
[`DatadisValidator`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/ingestion/validator.py#L10-L147) detecta automáticamente variaciones entre distribuidoras:
1. **Codificación de Caracteres:** Evalúa variantes UTF-8 (`utf-8`, `utf-8-sig`) mediante muestras de bytes, con respaldo seguro en Latin-1 (`iso-8859-1` / `cp1252`).
2. **Detección de Delimitador:** Cuenta los separadores candidatos (`;`, `,`, `\t`) priorizando el punto y coma (`;`) y utilizando `csv.Sniffer` como respaldo.
3. **Columnas Obligatorias:** Exige los cuatro campos indispensables: `cups` (código de suministro), `fecha` (fecha de lectura), `hora` (tramo `01:00`–`24:00`) y `consumo_kWh` (energía consumida).

### C. Normalización Vectorizada del DataFrame
En [`DatadisLoader.load_file`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/ingestion/loader.py#L69-L150), los datos se procesan en memoria:
1. **Carga como Texto (`dtype=str`):** Evita errores prematuros de redondeo o conversiones fallidas.
2. **Estandarización de Cabeceras:** Mapea variaciones (`consumo_kWh`, `consumoKwh`, `CONSUMO_KWH`) a constantes internas unificadas.
3. **Conversión de Decimales Europeos:** Convierte comas en puntos (`0,152` ➔ `0.152`), asignando `0.0` a valores inválidos.
4. **Interpretación Flexible de Fechas:** Usa `pd.to_datetime(format="mixed")` para interpretar fechas tanto españolas (`DD/MM/YYYY`) como ISO (`YYYY-MM-DD`).
5. **Particionado Temporal:** Extrae columnas enteras `year` y `month` (1–12) para agrupaciones vectorizadas inmediatas.

---

## 4. 🧮 Motor de Procesamiento y Agregación (Cómo Procesa la Información)

[`DataAggregator`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/processing/aggregator.py#L26-L440) ejecuta los cálculos estadísticos y modelos de reparto.

### A. La Invariante Matemática del Reparto al 100,00%
Para cualquier ventana temporal $T$ (un mes, un año natural o el histórico global), el porcentaje de participación de cada contador se calcula mediante:

$$\text{Porcentaje}_i = \left( \frac{\sum_{t \in T} \text{kWh}_{i, t}}{\sum_{j \in \text{Comunidad}} \sum_{t \in T} \text{kWh}_{j, t}} \right) \times 100$$

> [!NOTE]
> La suma de los porcentajes de todos los CUPS en cualquier período $T$ equivale de manera garantizada al **$100,00\%$** (salvo redondeos visuales). Si el consumo comunitario es nulo, los porcentajes se fijan en $0,00\%$.

### B. Heurísticas de Clasificación de Consumidores
El motor clasifica cada suministro con distintivos visuales en terminal e informes:

| Clasificación | Distintivo | Condición de Umbral | Significado Práctico Habitual |
| :--- | :---: | :--- | :--- |
| **Consumidor Dominante** | `★` *(Magenta)* | $\text{Porcentaje}_i > 30,0\%$ (posición #1) | Climatización central, bombas de calor/achique, ascensores o alta potencia compartida. |
| **Consumidor Estándar** | *(Número de orden)* | $1,0\text{ kWh} \le \text{Consumo} \le 30,0\%$ | Vivienda particular o local comercial habitual. |
| **Suministro Inactivo / Latente** | `(0)` *(Atenuado)* | $\text{Consumo} < 1,0\text{ kWh}$ | Piso desocupado, suministro de temporada o contador dado de baja temporal. |

### C. Motor de Comparación Interanual (La Heurística Homogénea)
Al contrastar varios años mediante `da compare`, comparar meses incompletos frente a meses cerrados distorsiona las tendencias. [`DataAggregator.compare_years`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/processing/aggregator.py#L224-L440) aplica una **Heurística de Completitud de Meses de Calendario**:
1. **Verificación de Días:** Calcula mediante `calendar.monthrange(año, m)[1]` los días naturales exactos de cada mes $m \in \{1 \dots 12\}$, considerando años bisiestos.
2. **Clasificación del Mes:** Determina si el mes está `complete` (`días_reales == días_esperados`), `incomplete` (`días_reales < días_esperados`) o `no_data`.
3. **Invariante de Variación:** Las diferencias absolutas ($\Delta\text{kWh}$) y porcentuales ($\%\Delta$) se evalúan **estrictamente sobre meses completos en todos los años comparados**:
   $$\Delta\text{kWh}_m = \text{kWh}_{\text{año\_reciente}, m} - \text{kWh}_{\text{año\_base}, m} \quad (\text{solo si está completo en todos los años})$$
   $$\%\Delta_m = \left( \frac{\Delta\text{kWh}_m}{\text{kWh}_{\text{año\_base}, m}} \right) \times 100$$
4. Los meses incompletos se señalan (`[Inc]`, `[--]`) y se aíslan de las métricas de variación anual para garantizar rigor analítico.

---

## 5. 🖥️ Resultados Esperados y Capa de Presentación

La herramienta ofrece tres canales de presentación complementarios:

### 1. Interfaz de Terminal Enriquecida (Estándar de 80 Columnas)
Diseñada con [Rich](https://github.com/Textualize/rich) y ajuste estricto (`no_wrap=True`) en cifras numéricas:
- **Ficha Resumen de la Comunidad:** Consumo total, total de lecturas, número de contadores y meses pico/mínimo.
- **Tablas de Reparto Anual por CUPS:** Clasificación ordenada de suministros, kWh consumidos, cuota porcentual y barras gráficas (`make_share_bar`).
- **Trayectoria Mensual por Contador:** Evolución mes a mes para un contador específico o para la comunidad completa.
- **Tablas Comparativas Interanuales:** Columnas anuales paralelas con deltas codificados por color (verde para descensos, rojo para aumentos).

### 2. Gráficos Comparativos en Alta Resolución (`.output/charts/*.png`)
Generados con [Matplotlib](https://matplotlib.org) sin entorno gráfico (`Agg`) y almacenados en `./.output/charts/`:
- **Gráfico Comunitario (`community_monthly_<años>.png`):** Barras agrupadas con el consumo global en los 12 meses naturales.
- **Gráficos por CUPS (`<CUPS>_monthly_<años>.png`):** Diagramas mensuales independientes para cada contador de la comunidad.

### 3. Informes Resumen en Markdown (`.output/*.md`)
Informes de auditoría fechados (`AAAAMMDD_HHMMSS_*.md`) en formato GitHub Flavored Markdown:
- Barras gráficas en ASCII (`████░░░░░░░░`) y enlaces directos a las imágenes PNG generadas.
- Versión activa de CalVer, marca temporal de ejecución y notas de privacidad legal.

---

## 6. 🔒 Motor de Seguridad y Anonimización de Datos

Conforme al Real Decreto **RD 1435/2002** y el **RGPD** europeo (Reglamento UE 2016/679), el CUPS constituye un dato personal al identificar inequívocamente un inmueble físico.

### Invariantes de Cero Filtraciones
[`src/security.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/security.py) garantiza que ningún dato residencial real se confirme en Git:
1. **Lista Blanca de CUPS Sintéticos:** Solo se permiten identificadores simulados autorizados (`ES0021000000000001AA`–`ES0021000000009999ZZ`, todo ceros o todo nueves).
2. **Bloqueo de Coordenadas y Direcciones:** Detección de pares de coordenadas decimales o formato DMS que identifiquen ubicaciones de inmuebles.
3. **Protección de Credenciales:** Búsqueda y bloqueo de certificados privados, tokens de API, claves AWS, GitHub PATs o Bearer tokens.
4. **Ejecución Automatizada:** Verificable con `python -m src.security` y garantizada por el hook pre-commit en [`.pre-commit-config.yaml`](file:///Users/marcos/workspace/repo/datadis-analyzer/.pre-commit-config.yaml).
5. **Aislamiento en Git:** Las carpetas con datos del usuario (`.input/`) e informes generados (`.output/`) están permanentemente ignoradas en [`.gitignore`](file:///Users/marcos/workspace/repo/datadis-analyzer/.gitignore).

---

## 7. 🗺️ Índice de Trazabilidad en el Código

| Concepto / Funcionalidad | Archivo Principal | Clase / Función Clave |
| :--- | :--- | :--- |
| **Controlador y Despacho CLI** | [`src/cli.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/cli.py) | `app`, `summary_cmd`, `compare_cmd`, `init_cmd` |
| **Configuración Persistente** | [`src/config.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/config.py) | `AppConfig`, `load_config`, `set_language` |
| **Motor de Versiones CalVer** | [`src/version.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/version.py) | `get_version`, `bump_version_files`, `check_commit_version_bump` |
| **Auditoría de Seguridad y Privacidad** | [`src/security.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/security.py) | `audit_repository`, `scan_content`, `is_allowed_synthetic_cups` |
| **Descubrimiento y Normalización CSV** | [`src/ingestion/loader.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/ingestion/loader.py) | `DatadisLoader.discover_files`, `DatadisLoader.load_file` |
| **Detector de Formato y Esquema** | [`src/ingestion/validator.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/ingestion/validator.py) | `DatadisValidator.detect_delimiter`, `validate_file` |
| **Cálculo de Agregación y Reparto** | [`src/processing/aggregator.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/processing/aggregator.py) | `DataAggregator.aggregate_community`, `_calculate_cups_shares` |
| **Motor Comparativo Interanual** | [`src/processing/aggregator.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/processing/aggregator.py) | `DataAggregator.compare_years` |
| **Modelos de Dominio de Datos** | [`src/processing/models.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/processing/models.py) | `CommunitySummary`, `CupsShare`, `ComparisonSummary` |
| **Vistas de Terminal Enriquecidas** | [`src/presentation/views.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/presentation/views.py) | `render_annual_tables`, `render_monthly_overview`, `render_help` |
| **Generación de Gráficos Matplotlib** | [`src/presentation/charts.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/presentation/charts.py) | `generate_all_comparison_charts`, `generate_community_bar_chart` |
| **Exportador de Informes Markdown** | [`src/presentation/export.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/presentation/export.py) | `export_markdown_summary`, `export_comparison_markdown` |
| **Motor de Idiomas (i18n)** | [`src/i18n.py`](file:///Users/marcos/workspace/repo/datadis-analyzer/src/i18n.py) | `t()`, `get_month_name()`, `TRANSLATIONS` |
