"""Command-line interface entry point for DATADIS Analyzer."""

from pathlib import Path

import typer

from src.config import (
    CONFIG_FILE_PATH,
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    ensure_directories,
    get_language,
    load_config,
    normalize_language_code,
    set_language,
)
from src.i18n import t
from src.ingestion.loader import DatadisLoader
from src.ingestion.schema import DatadisError
from src.presentation.console import console
from src.presentation.export import cleanup_output_directory, export_markdown_summary
from src.presentation.views import (
    render_annual_tables,
    render_cleanup_result,
    render_community_overview,
    render_cups_trajectory,
    render_detailed_monthly_breakdown,
    render_export_success,
    render_help,
    render_init_success,
    render_key_insights,
    render_monthly_overview,
    render_validation_issues,
)
from src.processing.aggregator import DataAggregator

app = typer.Typer(
    help="DATADIS Analyzer: CLI tool to analyze Spanish residential community energy consumption.",
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def default_callback(ctx: typer.Context) -> None:
    """Default entrypoint. Renders custom formatted help if no subcommand is passed."""
    if ctx.invoked_subcommand is None:
        render_help(lang=get_language())


@app.command(name="help")
def help_cmd(
    lang: str | None = typer.Option(
        None,
        "--lang",
        "-l",
        help="Language for help output ('en' or 'es').",
    ),
) -> None:
    """Display comprehensive command reference, expected folder structure, and examples."""
    effective_lang = lang or get_language()
    render_help(lang=effective_lang)


@app.command(name="init")
def init_cmd(
    language: str | None = typer.Option(
        None,
        "--language",
        "-l",
        help="Select output language: 'en' (English) or 'es' (Spanish).",
    ),
) -> None:
    """Initialize application settings and choose persistent output language (English or Spanish)."""
    selected = language
    if not selected:
        selected = typer.prompt(
            "Select output language / Seleccione idioma de salida [en/es]",
            default="en",
        )

    try:
        lang_code = set_language(selected)
    except ValueError as exc:
        console.print(f"\n[bold red]Error:[/bold red] {exc}\n")
        raise typer.Exit(code=1) from exc

    input_dir, output_dir = ensure_directories()

    render_init_success(
        lang_code=lang_code,
        config_path=CONFIG_FILE_PATH,
        input_dir=input_dir,
        output_dir=output_dir,
        lang=lang_code,
    )


@app.command(name="cleanup")
def cleanup_cmd(
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory containing reports to remove (default: ./.output).",
        exists=False,
        file_okay=False,
        dir_okay=True,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without interactive confirmation prompt.",
    ),
    lang: str | None = typer.Option(
        None,
        "--lang",
        "-l",
        help="Language for output messages ('en' or 'es').",
    ),
) -> None:
    """Remove generated reports and clear files from the .output directory."""
    effective_lang = lang or get_language()
    cfg = load_config()
    target_output_dir = output_dir or Path(cfg.output_dir or DEFAULT_OUTPUT_DIR)

    if not target_output_dir.exists() or not any(target_output_dir.iterdir()):
        render_cleanup_result([], output_dir=target_output_dir, lang=effective_lang)
        return

    existing_items = list(target_output_dir.iterdir())
    if not force:
        confirmed = typer.confirm(
            t(
                "cleanup_confirm",
                lang=effective_lang,
                count=len(existing_items),
                dir=str(target_output_dir),
            ),
            default=False,
        )
        if not confirmed:
            console.print(f"\n[yellow]{t('cleanup_aborted', lang=effective_lang)}[/yellow]\n")
            raise typer.Exit(code=0)

    removed = cleanup_output_directory(target_output_dir)
    render_cleanup_result(removed, output_dir=target_output_dir, lang=effective_lang)


@app.command(name="clean", hidden=True)
def clean_alias(
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory containing reports to remove (default: ./.output).",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without interactive confirmation prompt.",
    ),
    lang: str | None = typer.Option(
        None,
        "--lang",
        "-l",
        help="Language for output messages ('en' or 'es').",
    ),
) -> None:
    """Alias for 'cleanup'."""
    cleanup_cmd(output_dir=output_dir, force=force, lang=lang)


@app.command(name="summary")
def summary_cmd(
    input_dir: Path = typer.Option(
        DEFAULT_INPUT_DIR,
        "--input-dir",
        "-i",
        help="Root directory containing annualized DATADIS CSV exports (default: ./.input).",
        exists=False,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory where markdown reports will be stored (default: ./.output).",
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
    ),
    year: int | None = typer.Option(
        None,
        "--year",
        "-y",
        help="Filter analysis to a specific year (e.g. 2025).",
    ),
    view: str = typer.Option(
        "all",
        "--view",
        "-v",
        help="Output view mode: 'all' (annual + monthly summary), 'annual', or 'monthly' (full monthly CUPS breakdown).",
    ),
    cups: str | None = typer.Option(
        None,
        "--cups",
        "-c",
        help="Filter display to a single CUPS code.",
    ),
    lang: str | None = typer.Option(
        None,
        "--lang",
        "-l",
        help="Temporary language override for this command ('en' or 'es').",
    ),
) -> None:
    """Aggregate community consumption by year and month, display visual tables, and export report to .output/."""
    effective_lang = lang or get_language()
    try:
        effective_lang = normalize_language_code(effective_lang)
    except ValueError:
        effective_lang = "en"

    cfg = load_config()
    target_output_dir = output_dir or Path(cfg.output_dir or DEFAULT_OUTPUT_DIR)

    normalized_view = view.lower().strip()
    if normalized_view not in ("all", "annual", "monthly"):
        console.print(
            f"[bold red]Invalid view mode '{view}'.[/bold red] Expected one of: 'all', 'annual', 'monthly'."
        )
        raise typer.Exit(code=1)

    loader = DatadisLoader()

    loading_msg = (
        "[bold cyan]Descubriendo y validando archivos DATADIS...[/bold cyan]"
        if effective_lang == "es"
        else "[bold cyan]Discovering and validating DATADIS export files...[/bold cyan]"
    )
    agg_msg = (
        "[bold cyan]Agregando consumo y calculando porcentajes de reparto...[/bold cyan]"
        if effective_lang == "es"
        else "[bold cyan]Aggregating energy consumption and calculating community shares...[/bold cyan]"
    )

    try:
        with console.status(loading_msg):
            df, validation_results = loader.load_all(base_dir=input_dir, year=year)

        with console.status(agg_msg):
            summary = DataAggregator.aggregate_community(df)

    except DatadisError as err:
        console.print(f"\n[bold red]Error:[/bold red] {err}\n")
        raise typer.Exit(code=1) from err
    except Exception as exc:
        console.print(f"\n[bold red]Unexpected processing error:[/bold red] {exc}\n")
        raise typer.Exit(code=1) from exc

    # Validate CUPS if filter supplied
    if cups and cups not in summary.cups_list:
        not_found_msg = (
            f"El CUPS '{cups}' no fue encontrado en el conjunto de datos."
            if effective_lang == "es"
            else f"CUPS '{cups}' was not found in the loaded dataset."
        )
        avail_msg = "CUPS disponibles:" if effective_lang == "es" else "Available CUPS in dataset:"
        console.print(
            f"\n[bold red]Error:[/bold red] {not_found_msg}\n[dim]{avail_msg}[/dim] {', '.join(summary.cups_list)}\n"
        )
        raise typer.Exit(code=1)

    # 1. Validation warnings (if any files were skipped or corrupted)
    render_validation_issues(validation_results, lang=effective_lang)

    # 2. High-level community overview card
    valid_file_count = len([v for v in validation_results if v.is_valid])
    render_community_overview(summary, file_count=valid_file_count, lang=effective_lang)

    # 3. Dedicated CUPS trajectory if single CUPS is filtered
    if cups:
        render_cups_trajectory(
            summary=summary, target_cups=cups, filter_year=year, lang=effective_lang
        )
        render_key_insights(summary, lang=effective_lang)
    else:
        # 4. Annual consumption and CUPS shares
        if normalized_view in ("all", "annual"):
            render_annual_tables(
                summary=summary,
                filter_cups=cups,
                filter_year=year,
                lang=effective_lang,
            )

        # 5. Monthly timeline overview
        if normalized_view in ("all", "monthly"):
            render_monthly_overview(
                summary=summary,
                filter_cups=cups,
                filter_year=year,
                lang=effective_lang,
            )

        # 6. Detailed monthly CUPS breakdown with percentage shares
        if normalized_view in ("all", "monthly"):
            render_detailed_monthly_breakdown(
                summary=summary,
                filter_cups=cups,
                filter_year=year,
                lang=effective_lang,
            )

        # 7. Analytical community key insights
        render_key_insights(summary, lang=effective_lang)

    # 8. Export markdown summary report into .output/
    report_file = export_markdown_summary(
        summary=summary,
        output_dir=target_output_dir,
        lang=effective_lang,
        year_filter=year,
        cups_filter=cups,
        view_mode=normalized_view,
    )
    render_export_success(report_file, lang=effective_lang)


def main() -> None:
    """Main CLI entrypoint registered in pyproject.toml."""
    app()


if __name__ == "__main__":
    main()
