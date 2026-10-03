"""Internationalization (i18n) module supporting English and Spanish localization."""

from typing import Any, Optional

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
        "cmd_help_desc": "Display this comprehensive command reference, input structure guidelines, and examples.",
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
        "quick_start_text": (
            "$ da init --language es               # Configure output language to Spanish\n"
            "$ da summary                         # Complete annual & monthly community breakdown\n"
            "$ da summary --year 2025            # Inspect year 2025 specifically\n"
            "$ da summary --view monthly         # Show full CUPS percentage shares for each month\n"
            "$ da summary --cups ES0021000000000001AA # Track consumption for one specific meter\n"
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
        "init_language_set": "Output language successfully configured to: [bold green]English[/bold green].",
        "init_persistence_note": "This preference is persisted in [cyan]{path}[/cyan] and will apply to all subsequent commands.",
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
        "cmd_help_desc": "Mostrar esta referencia de comandos, guía de estructura de datos y ejemplos.",
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
        "quick_start_text": (
            "$ da init --language es               # Configurar idioma de salida en español\n"
            "$ da summary                         # Desglose comunitario completo (anual y mensual)\n"
            "$ da summary --year 2025            # Inspeccionar específicamente el año 2025\n"
            "$ da summary --view monthly         # Mostrar porcentajes completos de cada CUPS por mes\n"
            "$ da summary --cups ES0021000000000001AA # Seguir el consumo de un contador específico\n"
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
        "init_language_set": "Idioma de salida configurado correctamente a: [bold green]Español[/bold green].",
        "init_persistence_note": "Esta preferencia se guarda en [cyan]{path}[/cyan] y se aplicará a los comandos siguientes.",
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
    },
}


def t(key: str, lang: Optional[str] = None, **kwargs: Any) -> str:
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
