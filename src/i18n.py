"""Internationalization (i18n) module supporting English and Spanish localization."""

from typing import Any

from src.config import get_language

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # App banner & overview
        "app_title": "⚡ DATADIS ANALYZER",
        "app_subtitle": "Residential Community Electrical Energy Intelligence CLI",
        "overview_heading": "OVERVIEW",
        "overview_text": (
            "Analyzes hourly electrical energy consumption exported from Spain's DATADIS platform "
            "(https://datadis.es) for residential communities (comunidades de vecinos).\n"
            "Automatically detects CSV dialects, groups data by year and month, and calculates each CUPS's percentage share."
        ),
        # Commands
        "available_commands": "AVAILABLE COMMANDS",
        "cmd_name": "Command",
        "cmd_desc": "Description",
        "cmd_summary_desc": "Traverse annualized directories, aggregate consumption by year and month, and display visual share tables.",
        "cmd_init_desc": "Configure the application language (English or Spanish) and persistent preferences.",
        "cmd_cleanup_desc": "Remove generated reports and clear files from the .output directory.",
        "cmd_help_desc": "Display this comprehensive command reference, input structure guidelines, and examples.",
        "cmd_version_desc": "Display the active CalVer version (YYYY.MM.NNN) and exit.",
        # Options
        "options_title": "OPTIONS FOR 'da summary'",
        "opt_name": "Option",
        "opt_type": "Type",
        "opt_default": "Default",
        "opt_desc": "Description",
        "opt_input_dir": "Root directory containing annualized DATADIS CSV exports.",
        "opt_year": "Filter summary analysis to a specific year (e.g. 2025).",
        "opt_view": "View mode: 'all' (annual + monthly summary), 'annual', 'monthly' (full monthly CUPS breakdown).",
        "opt_cups": "Filter results to a specific CUPS identifier.",
        "opt_lang": "Temporary language override for this command ('en' or 'es').",
        # Data layout & examples
        "data_layout_title": "📁 Data Layout",
        "data_layout_desc": (
            "Expected Input Structure:\n"
            "  .input/\n"
            "    ├── 2025/\n"
            "    │   ├── ES0021000000000001AA_Consumo_....csv\n"
            "    │   └── ES0021000000000002BB_Consumo_....csv\n"
            "    └── 2026/\n"
            "        └── ...\n\n"
            "Standard DATADIS CSV columns (cups, fecha, hora, consumo_kWh) and delimiters (;, ,) are automatically validated."
        ),
        "quick_start_title": "🚀 Quick Start Examples",
        "quick_start_col_cmd": "Command / Example",
        "quick_start_col_desc": "Description",
        "quick_start_ex_init": "Configure output language and initialize workspace.",
        "quick_start_ex_summary": "Complete annual & monthly community breakdown.",
        "quick_start_ex_year": "Inspect year 2025 specifically.",
        "quick_start_ex_monthly": "Show full CUPS percentage shares for each month.",
        "quick_start_ex_cups": "Track consumption for one specific meter.",
        "quick_start_ex_compare": "Multi-year consumption comparison and trends.",
        "quick_start_ex_cleanup": "Clear generated reports from .output directory.",
        "quick_start_ex_version": "Display active CalVer application version.",
        "quick_start_text": (
            "$ da init --language es               # Configure output language to Spanish\n"
            "$ da summary                         # Complete annual & monthly community breakdown\n"
            "$ da summary --year 2025            # Inspect year 2025 specifically\n"
            "$ da summary --view monthly         # Show full CUPS percentage shares for each month\n"
            "$ da summary --cups ES0021000000000001AA # Track consumption for one specific meter\n"
            "$ da version                        # Display active CalVer version and exit\n"
        ),
        # Community overview card
        "overview_card_title": "🏢 Residential Community Energy Overview",
        "total_community_consumption": "Total Community Consumption:",
        "active_cups_meters": "Active CUPS Meters:",
        "csv_files_processed": "CSV Files Processed:",
        "date_range": "Date Range:",
        "peak_month": "Peak Month:",
        "total_hourly_readings": "Total Hourly Readings:",
        "meters_count": "{count} meters",
        "files_count": "{count} files",
        "hours_count": "{count:,} hours",
        # Annual table
        "annual_summary_title": "📅 Annual Summary — Year {year}",
        "community_total_label": "Community Total: {total}",
        "col_rank": "#",
        "col_cups": "CUPS",
        "col_consumption": "Consumption",
        "col_share": "Share %",
        "col_distribution": "Distribution",
        "col_total": "TOTAL",
        "annual_legend": "Legend: ★ Dominant Community Load | (0) Inactive Meter (<1 kWh)",
        # Monthly timeline
        "monthly_timeline_title": "📊 Monthly Community Timeline & Top Contributor",
        "col_period": "Period",
        "col_community_total": "Community Total",
        "col_top_cups": "Top Consumer CUPS",
        "col_top_share": "Top Share",
        # Detailed monthly breakdown
        "period_title": "📆 Period {period}",
        # CUPS Trajectory
        "cups_trajectory_title": "🔍 Monthly Trajectory for CUPS: {cups}",
        "col_cups_kwh": "CUPS kWh",
        "col_community_kwh": "Community kWh",
        # Key insights
        "insights_title": "💡 Community Key Insights & Observations",
        "dominant_consumer_insight": (
            "• [bold magenta]Dominant Community Consumer:[/] CUPS [bold]{cups}[/bold] accounts for "
            "[bold yellow]{pct:.2f}%[/bold yellow] of community electricity ({kwh}). In residential buildings, this "
            "typically corresponds to collective equipment (central hot water/HVAC, elevators, or garage ventilation)."
        ),
        "zero_consumer_insight": (
            "• [dim white]Zero / Negligible Consumption:[/] {count} supply point(s) recorded under 1 kWh: "
            "[dim]{cups}[/dim]."
        ),
        "seasonality_insight": (
            "• [cyan]Seasonality & Peaks:[/] Community peak consumption occurred in [bold yellow]{peak_month}[/bold yellow] "
            "({peak_kwh}), while lowest was in [bold cyan]{lowest_month}[/bold cyan] ({lowest_kwh})."
        ),
        # Validation issues
        "validation_warnings_title": "⚠️  Input File Validation Warnings",
        "col_file": "File",
        "col_status": "Status",
        "col_issue": "Issue Details",
        # da init messages
        "init_title": "⚙️ Configuration Initialized",
        "init_version_info": "DATADIS Analyzer Version: [bold cyan]{version}[/bold cyan]",
        "init_language_set": "Output language successfully configured to: [bold green]English[/bold green].",
        "init_folders_created": "Workspace directories initialized: [cyan]{input_dir}/[/cyan] and [cyan]{output_dir}/[/cyan].",
        "init_persistence_note": "This preference is persisted in [cyan]{path}[/cyan] and will apply to all subsequent commands.",
        "init_required_error": "DATADIS Analyzer has not been initialized. You must run 'da init' first before executing any other command.",
        "init_required_tip": "Run 'da init' (or 'da init --language en|es') to configure preferences and initialize workspace directories.",
        "app_version_label": "DATADIS Analyzer Version",
        "col_version": "Version",
        # da cleanup messages
        "cleanup_title": "🧹 Output Directory Cleanup",
        "cleanup_empty": "Output directory [cyan]{dir}[/cyan] is already empty. No files to delete.",
        "cleanup_confirm": "Delete {count} file(s) from [cyan]{dir}[/cyan]?",
        "cleanup_aborted": "Cleanup aborted. No files were deleted.",
        "cleanup_success": "Successfully removed [bold green]{count}[/bold green] file(s) from [cyan]{dir}[/cyan].",
        # Report export
        "report_generated": "Markdown summary report saved to: [cyan]{path}[/cyan]",
        # Markdown specific
        "md_doc_title": "# DATADIS Residential Community Energy Report",
        "md_generated_at": "**Generated:** {datetime}",
        "md_section_overview": "## 1. Executive Summary",
        "md_section_annual": "## 2. Annual Consumption & CUPS Percentage Shares",
        "md_section_timeline": "## 3. Monthly Community Timeline & Peak Contributors",
        "md_section_monthly": "## 4. Detailed Monthly CUPS Breakdown",
        "md_section_insights": "## 5. Key Community Observations",
        # Compare command
        "cmd_compare_desc": "Compare electrical energy consumption and variation percentage across multiple years.",
        "opt_compare_years": "Years to compare (e.g. -y 2024 -y 2025 or --years 2024,2025). Defaults to all available years.",
        "compare_overview_title": "⚡ Multi-Year Community Energy Comparison",
        "compare_years_label": "Years Compared:",
        "compare_overall_change": "Overall Energy Variation:",
        "compare_status_saving": "Community reduced consumption by [bold green]{diff_kwh}[/bold green] ([bold green]{pct}%[/bold green])",
        "compare_status_increase": "Community increased consumption by [bold red]{diff_kwh}[/bold red] ([bold red]+{pct}%[/bold red])",
        "compare_status_stable": "Community consumption remained unchanged ({diff_kwh})",
        "compare_max_decrease": "Biggest Monthly Reduction:",
        "compare_max_increase": "Biggest Monthly Surge:",
        "compare_top_saver": "Top Energy Reducer CUPS:",
        "compare_top_increaser": "Top Energy Increaser CUPS:",
        "compare_monthly_title": "📅 Monthly Community Consumption & Year-over-Year Variation",
        "compare_month_col": "Month",
        "compare_diff_col": "Diff (kWh)",
        "compare_var_col": "Variation",
        "compare_trend_col": "Trend",
        "compare_trend_reduced": "▼ Reduced",
        "compare_trend_increased": "▲ Increased",
        "compare_trend_equal": "— Stable",
        "compare_cups_title": "👥 Supply Points (CUPS) Year-over-Year Evolution",
        "compare_cups_col": "CUPS",
        "compare_need_two_years": "At least two years are required for comparison; found: {years}.",
        "no_data": "No data",
        "incomplete_data": "Incomplete",
        "comparable_period_note": "Comparable period: {period} ({months} months)",
        "comparable_total_label": "Comparable Total ({period})",
        "excluded_months_note": "{count} month(s) excluded due to missing or incomplete data ({months})",
        "charts_generated": "Generated {count} monthly comparison chart(s) in: [cyan]{path}[/cyan]",
        "chart_cups_title": "CUPS: {cups}",
        "chart_subtitle": "Monthly Energy Consumption Comparison ({years})",
        "chart_month_axis": "Month",
        "chart_kwh_axis": "Consumption (kWh)",
        "chart_community_title": "Community Total Energy Consumption",
        "chart_legend_total": "Total: {total}",
        "md_compare_title": "# ⚡ Multi-Year Community Energy Comparison ({years})",
        "md_compare_overview": "## 1. Executive Comparison Overview",
        "md_compare_monthly": "## 2. Month-by-Month Consumption Comparison",
        "md_compare_cups": "## 3. Individual CUPS Evolution",
        "md_compare_charts": "## 4. Visual Monthly Trajectories by CUPS",
        "md_compare_insights": "## 5. Key Comparison Takeaways",
    },
    "es": {
        # App banner & overview
        "app_title": "⚡ ANALIZADOR DATADIS",
        "app_subtitle": "CLI de Inteligencia Energética para Comunidades de Propietarios",
        "overview_heading": "DESCRIPCIÓN GENERAL",
        "overview_text": (
            "Analiza el consumo horario de energía eléctrica exportado desde la plataforma DATADIS de España "
            "(https://datadis.es) para comunidades residenciales de vecinos.\n"
            "Detecta automáticamente dialectos CSV, agrupa los datos por año y mes, y calcula el porcentaje de reparto de cada CUPS."
        ),
        # Commands
        "available_commands": "COMANDOS DISPONIBLES",
        "cmd_name": "Comando",
        "cmd_desc": "Descripción",
        "cmd_summary_desc": "Recorrer directorios anuales, agregar consumo por año y mes, y mostrar tablas visuales de porcentajes.",
        "cmd_init_desc": "Configurar el idioma de salida de la aplicación (inglés o español) y preferencias persistentes.",
        "cmd_cleanup_desc": "Eliminar los informes generados y limpiar los archivos de la carpeta .output.",
        "cmd_help_desc": "Mostrar esta referencia de comandos, guía de estructura de datos y ejemplos.",
        "cmd_version_desc": "Mostrar la versión CalVer activa (AAAA.MM.NNN) y salir.",
        # Options
        "options_title": "OPCIONES PARA 'da summary'",
        "opt_name": "Opción",
        "opt_type": "Tipo",
        "opt_default": "Por defecto",
        "opt_desc": "Descripción",
        "opt_input_dir": "Directorio raíz que contiene las exportaciones CSV anualizadas de DATADIS.",
        "opt_year": "Filtrar el análisis de resumen a un año específico (ej. 2025).",
        "opt_view": "Modo de visualización: 'all' (anual + mensual), 'annual', o 'monthly' (desglose mensual completo por CUPS).",
        "opt_cups": "Filtrar resultados para un identificador CUPS específico.",
        "opt_lang": "Sobrescribir temporalmente el idioma para este comando ('en' o 'es').",
        # Data layout & examples
        "data_layout_title": "📁 Estructura de Datos",
        "data_layout_desc": (
            "Estructura de Entrada Esperada:\n"
            "  .input/\n"
            "    ├── 2025/\n"
            "    │   ├── ES0021000000000001AA_Consumo_....csv\n"
            "    │   └── ES0021000000000002BB_Consumo_....csv\n"
            "    └── 2026/\n"
            "        └── ...\n\n"
            "Las columnas estándar de DATADIS (cups, fecha, hora, consumo_kWh) y delimitadores (;, ,) se validan automáticamente."
        ),
        "quick_start_title": "🚀 Ejemplos de Inicio Rápido",
        "quick_start_col_cmd": "Comando / Ejemplo",
        "quick_start_col_desc": "Descripción",
        "quick_start_ex_init": "Configurar idioma de salida e inicializar espacio.",
        "quick_start_ex_summary": "Desglose comunitario completo (anual y mensual).",
        "quick_start_ex_year": "Inspeccionar específicamente el año 2025.",
        "quick_start_ex_monthly": "Mostrar porcentajes mensuales completos por CUPS.",
        "quick_start_ex_cups": "Seguir el consumo de un contador específico.",
        "quick_start_ex_compare": "Comparación multianual y tendencias de consumo.",
        "quick_start_ex_cleanup": "Limpiar informes generados de la carpeta .output.",
        "quick_start_ex_version": "Mostrar la versión CalVer activa de la aplicación.",
        "quick_start_text": (
            "$ da init --language es               # Configurar idioma de salida en español\n"
            "$ da summary                         # Desglose comunitario completo (anual y mensual)\n"
            "$ da summary --year 2025            # Inspeccionar específicamente el año 2025\n"
            "$ da summary --view monthly         # Mostrar porcentajes completos de cada CUPS por mes\n"
            "$ da summary --cups ES0021000000000001AA # Seguir el consumo de un contador específico\n"
            "$ da version                        # Mostrar la versión CalVer activa y salir\n"
        ),
        # Community overview card
        "overview_card_title": "🏢 Resumen Energético de la Comunidad de Propietarios",
        "total_community_consumption": "Consumo Total de la Comunidad:",
        "active_cups_meters": "Contadores CUPS Activos:",
        "csv_files_processed": "Archivos CSV Procesados:",
        "date_range": "Rango de Fechas:",
        "peak_month": "Mes de Máximo Consumo:",
        "total_hourly_readings": "Total de Lecturas Horarias:",
        "meters_count": "{count} contadores",
        "files_count": "{count} archivos",
        "hours_count": "{count:,} horas",
        # Annual table
        "annual_summary_title": "📅 Resumen Anual — Año {year}",
        "community_total_label": "Total Comunidad: {total}",
        "col_rank": "#",
        "col_cups": "CUPS",
        "col_consumption": "Consumo",
        "col_share": "% Cuota",
        "col_distribution": "Distribución",
        "col_total": "TOTAL",
        "annual_legend": "Leyenda: ★ Carga Principal Comunitaria | (0) Contador Inactivo (<1 kWh)",
        # Monthly timeline
        "monthly_timeline_title": "📊 Cronología Mensual de la Comunidad y Mayor Consumidor",
        "col_period": "Periodo",
        "col_community_total": "Total Comunidad",
        "col_top_cups": "CUPS Mayor Consumidor",
        "col_top_share": "% Mayor Consumo",
        # Detailed monthly breakdown
        "period_title": "📆 Periodo {period}",
        # CUPS Trajectory
        "cups_trajectory_title": "🔍 Trayectoria Mensual para el CUPS: {cups}",
        "col_cups_kwh": "kWh CUPS",
        "col_community_kwh": "kWh Comunidad",
        # Key insights
        "insights_title": "💡 Conclusiones y Observaciones Clave de la Comunidad",
        "dominant_consumer_insight": (
            "• [bold magenta]Consumidor Dominante de la Comunidad:[/] El CUPS [bold]{cups}[/bold] representa el "
            "[bold yellow]{pct:.2f}%[/bold yellow] de la electricidad comunitaria ({kwh}). En edificios residenciales, "
            "esto suele corresponder a servicios comunitarios (agua caliente central/climatización, ascensores o ventilación de garaje)."
        ),
        "zero_consumer_insight": (
            "• [dim white]Consumo Nulo o Despreciable:[/] {count} punto(s) de suministro registraron menos de 1 kWh: "
            "[dim]{cups}[/dim]."
        ),
        "seasonality_insight": (
            "• [cyan]Estacionalidad y Picos:[/] El pico de consumo comunitario se registró en [bold yellow]{peak_month}[/bold yellow] "
            "({peak_kwh}), mientras que el mínimo fue en [bold cyan]{lowest_month}[/bold cyan] ({lowest_kwh})."
        ),
        # Validation issues
        "validation_warnings_title": "⚠️  Avisos de Validación de Archivos de Entrada",
        "col_file": "Archivo",
        "col_status": "Estado",
        "col_issue": "Detalle de la Incidencia",
        # da init messages
        "init_title": "⚙️ Configuración Inicializada",
        "init_version_info": "Versión de DATADIS Analyzer: [bold cyan]{version}[/bold cyan]",
        "init_language_set": "Idioma de salida configurado correctamente a: [bold green]Español[/bold green].",
        "init_folders_created": "Carpetas de trabajo inicializadas: [cyan]{input_dir}/[/cyan] y [cyan]{output_dir}/[/cyan].",
        "init_persistence_note": "Esta preferencia se guarda en [cyan]{path}[/cyan] y se aplicará a los comandos siguientes.",
        "init_required_error": "DATADIS Analyzer no ha sido inicializado. Debe ejecutar 'da init' primero antes de utilizar cualquier otro comando.",
        "init_required_tip": "Ejecute 'da init' (o 'da init --language en|es') para configurar preferencias e inicializar carpetas de trabajo.",
        "app_version_label": "Versión de DATADIS Analyzer",
        "col_version": "Versión",
        # da cleanup messages
        "cleanup_title": "🧹 Limpieza de Carpeta de Salida",
        "cleanup_empty": "La carpeta de salida [cyan]{dir}[/cyan] ya está vacía. No hay archivos para eliminar.",
        "cleanup_confirm": "¿Eliminar {count} archivo(s) de [cyan]{dir}[/cyan]?",
        "cleanup_aborted": "Limpieza cancelada. No se eliminó ningún archivo.",
        "cleanup_success": "Se han eliminado [bold green]{count}[/bold green] archivo(s) correctamente de [cyan]{dir}[/cyan].",
        # Report export
        "report_generated": "Informe de resumen en Markdown guardado en: [cyan]{path}[/cyan]",
        # Markdown specific
        "md_doc_title": "# Informe Energético de la Comunidad de Propietarios (DATADIS)",
        "md_generated_at": "**Fecha de generación:** {datetime}",
        "md_section_overview": "## 1. Resumen Ejecutivo",
        "md_section_annual": "## 2. Consumo Anual y Porcentajes de Reparto por CUPS",
        "md_section_timeline": "## 3. Cronología Mensual Comunitaria y Mayores Contribuyentes",
        "md_section_monthly": "## 4. Desglose Mensual Detallado por CUPS",
        "md_section_insights": "## 5. Observaciones Clave de la Comunidad",
        # Compare command
        "cmd_compare_desc": "Comparar el consumo de energía eléctrica y el porcentaje de variación entre diferentes años.",
        "opt_compare_years": "Años a comparar (ej. -y 2024 -y 2025 o --years 2024,2025). Por defecto todos los disponibles.",
        "compare_overview_title": "⚡ Comparativa Energética Interanual de la Comunidad",
        "compare_years_label": "Años Comparados:",
        "compare_overall_change": "Variación Energética Total:",
        "compare_status_saving": "La comunidad redujo su consumo en [bold green]{diff_kwh}[/bold green] ([bold green]{pct}%[/bold green])",
        "compare_status_increase": "La comunidad aumentó su consumo en [bold red]{diff_kwh}[/bold red] ([bold red]+{pct}%[/bold red])",
        "compare_status_stable": "El consumo de la comunidad se mantuvo sin cambios ({diff_kwh})",
        "compare_max_decrease": "Mes con Mayor Reducción:",
        "compare_max_increase": "Mes con Mayor Incremento:",
        "compare_top_saver": "CUPS con Mayor Reducción:",
        "compare_top_increaser": "CUPS con Mayor Incremento:",
        "compare_monthly_title": "📅 Consumo Mensual y Variación Interanual de la Comunidad",
        "compare_month_col": "Mes",
        "compare_diff_col": "Dif. (kWh)",
        "compare_var_col": "Variación",
        "compare_trend_col": "Tendencia",
        "compare_trend_reduced": "▼ Reducción",
        "compare_trend_increased": "▲ Incremento",
        "compare_trend_equal": "— Estable",
        "compare_cups_title": "👥 Evolución Interanual por Punto de Suministro (CUPS)",
        "compare_cups_col": "CUPS",
        "no_data": "Sin datos",
        "incomplete_data": "Incompleto",
        "comparable_period_note": "Periodo comparable: {period} ({months} meses)",
        "comparable_total_label": "Total Comparable ({period})",
        "excluded_months_note": "{count} mes(es) excluido(s) por datos incompletos o ausentes ({months})",
        "charts_generated": "Se han generado {count} gráfico(s) comparativo(s) en: [cyan]{path}[/cyan]",
        "chart_cups_title": "CUPS: {cups}",
        "chart_subtitle": "Comparativa Mensual de Consumo Energético ({years})",
        "chart_month_axis": "Mes",
        "chart_kwh_axis": "Consumo (kWh)",
        "chart_community_title": "Consumo Total de la Comunidad",
        "chart_legend_total": "Total: {total}",
        "md_compare_title": "# ⚡ Comparativa Energética Interanual de la Comunidad ({years})",
        "md_compare_overview": "## 1. Resumen Ejecutivo de la Comparativa",
        "md_compare_monthly": "## 2. Comparativa de Consumo Mes a Mes",
        "md_compare_cups": "## 3. Evolución Individual por Punto de Suministro (CUPS)",
        "md_compare_charts": "## 4. Gráficos Comparativos Mensuales por CUPS",
        "md_compare_insights": "## 5. Conclusiones Clave de la Comparativa",
    },
}

MONTH_NAMES: dict[str, dict[int, str]] = {
    "en": {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    },
    "es": {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    },
}

MONTH_NAMES_SHORT: dict[str, dict[int, str]] = {
    "en": {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    },
    "es": {
        1: "Ene",
        2: "Feb",
        3: "Mar",
        4: "Abr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Ago",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dic",
    },
}


def get_month_name(month: int, lang: str | None = None, short: bool = False) -> str:
    """Retrieve localized month name.

    Args:
        month: Month number (1-12).
        lang: Target language ('en' or 'es').
        short: If True, returns 3-letter abbreviation.

    Returns:
        Formatted month name string.
    """
    selected_lang = (lang or get_language()).lower()
    norm_lang = "es" if selected_lang.startswith("es") else "en"
    mapping = MONTH_NAMES_SHORT if short else MONTH_NAMES
    return mapping[norm_lang].get(month, f"M{month:02d}")


def t(key: str, lang: str | None = None, **kwargs: Any) -> str:
    """Translate a given key into the target language with keyword formatting.

    Args:
        key: Unique string identifier for the message.
        lang: Language code ('en' or 'es'). If None, uses active configured language.
        **kwargs: Values to interpolate into the translated string template.

    Returns:
        Interpolated translated string.
    """
    selected_lang = (lang or get_language()).lower()
    if selected_lang not in TRANSLATIONS:
        selected_lang = "en"

    template = TRANSLATIONS[selected_lang].get(key)
    if template is None:
        # Fallback to English
        template = TRANSLATIONS["en"].get(key, key)

    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, ValueError):
            return template

    return template
