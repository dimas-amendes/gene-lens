#!/usr/bin/env python3
"""
Gene Lens — Privacy-First Local Genome Analysis

Usage:
    python main.py analyze <genome_file>              # Full analysis
    python main.py analyze <genome_file> --name "Jo"  # With subject name
    python main.py analyze <genome_file> --ai          # + Local AI interpretation
    python main.py analyze <genome_file> --ai --model gemma2:9b  # Custom model
    python main.py download                            # Download databases
    python main.py privacy-check                       # Verify privacy setup
    python main.py formats                             # Show supported formats

Privacy guarantees:
- Network is BLOCKED during analysis (socket patched)
- No system metadata in reports (no hostname, username, paths)
- Secure file deletion available for temporary data
- All AI runs locally via Ollama (optional)
"""
import argparse
import sys
import time
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

from config import DATA_DIR, OUTPUT_DIR, CLINVAR_TSV, PHARMGKB_ANNOTATIONS, PHARMGKB_ALLELES


def cmd_analyze(args):
    """Run full genetic analysis pipeline with network blocked."""
    from src.consent import require_consent
    require_consent()

    from src.privacy import NetworkBlocker, ensure_directories, check_input_permissions
    from src.parsers import load_genome
    from src.databases import load_clinvar, load_pharmgkb
    from src.analyzer import analyze_lifestyle, analyze_disease_risk
    from src.reports import generate_genetic_report, generate_disease_report, generate_protocol

    genome_path = Path(args.genome)
    if not genome_path.exists():
        print(f"[ERROR] Genome file not found: {genome_path}")
        sys.exit(1)

    ensure_directories()

    print()
    print("=" * 60)
    print("  GENE LENS (Privacidade Local)")
    print("=" * 60)

    # Privacy checks
    print("\n[PRIVACIDADE]")
    check_input_permissions(genome_path)
    print("  Acesso a rede: BLOQUEADO durante analise")
    print("  Transmissao de dados: NENHUMA")
    print("  Metadados dos relatorios: sanitizados (sem info do sistema)")

    # Block network for the entire analysis
    with NetworkBlocker():
        t0 = time.time()

        # 1. Load genome
        print(f"\n[1/5] Carregando genoma...")
        genome_by_rsid, genome_by_position, fmt = load_genome(genome_path)
        print(f"  Formato detectado: {fmt}")
        print(f"  SNPs carregados: {len(genome_by_rsid):,}")

        # 2. Load databases
        print(f"\n[2/5] Carregando bancos de dados de referencia...")
        clinvar = load_clinvar()
        pharmgkb = load_pharmgkb()

        # 3. Analyze
        print(f"\n[3/5] Analisando variantes de estilo de vida/saude...")
        health_results = analyze_lifestyle(genome_by_rsid, pharmgkb)
        print(f"  Achados de estilo de vida: {len(health_results['findings'])}")
        print(f"  Interacoes droga-gene: {len(health_results['pharmgkb_findings'])}")

        print(f"\n[4/5] Analisando risco de doencas (ClinVar)...")
        disease_findings, disease_stats = analyze_disease_risk(genome_by_position, clinvar)
        if disease_findings:
            print(f"  Variantes patogenicas: {disease_stats['pathogenic_count']}")
            print(f"  Provavelmente patogenicas: {disease_stats['likely_pathogenic_count']}")
            print(f"  Fatores de risco: {len(disease_findings['risk_factor'])}")

        # 4. Generate reports
        print(f"\n[5/5] Gerando relatorios...")
        name = args.name

        report_1 = OUTPUT_DIR / "GENETIC_HEALTH_REPORT.md"
        generate_genetic_report(health_results, report_1, name)
        print(f"  -> {report_1.name}")

        report_2 = OUTPUT_DIR / "DISEASE_RISK_REPORT.md"
        if disease_findings:
            generate_disease_report(disease_findings, disease_stats, len(genome_by_rsid), report_2, name)
            print(f"  -> {report_2.name}")

        report_3 = OUTPUT_DIR / "ACTIONABLE_HEALTH_PROTOCOL.md"
        generate_protocol(health_results, disease_findings, report_3, name)
        print(f"  -> {report_3.name}")

        elapsed = time.time() - t0
        print(f"\n  Analise concluida em {elapsed:.1f}s")

    # AI interpretation (outside network block since Ollama is local)
    if args.ai:
        from src.local_ai import interpret_reports, save_interpretation

        report_paths = [report_1]
        if disease_findings:
            report_paths.append(report_2)
        report_paths.append(report_3)

        model = args.model or "llama3.1:8b"
        language = args.lang or "pt-BR"

        interpretation = interpret_reports(report_paths, model=model, language=language)
        ai_path = OUTPUT_DIR / "AI_INTERPRETATION.md"
        save_interpretation(interpretation, ai_path)
        print(f"  -> {ai_path.name}")

    print()
    print("=" * 60)
    print(f"  Relatorios salvos em: {OUTPUT_DIR}")
    print("  NENHUM dado foi transmitido. Analise 100% local.")
    print()
    print("  LEMBRETE: Estes sao resultados preliminares de exploracao")
    print("  baseados em genotipagem de consumo (~40% de taxa de falso")
    print("  positivo para variantes clinicamente significativas).")
    print("  Confirme qualquer achado preocupante com um conselheiro")
    print("  genetico ou medico.")
    print("  https://findageneticcounselor.nsgc.org")
    print("=" * 60)
    print()


def cmd_download(args):
    """Download reference databases."""
    import download_databases
    download_databases.main()


def cmd_privacy_check(args):
    """Verify privacy setup."""
    from src.privacy import NetworkBlocker

    print()
    print("=" * 60)
    print("  PRIVACY CHECK")
    print("=" * 60)

    # Check .gitignore
    gitignore = Path(__file__).parent / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        has_input = "input/" in content
        has_output = "output/" in content
        has_data = "data/*.tsv" in content
        print(f"\n  .gitignore:")
        print(f"    input/ ignored:  {'YES' if has_input else 'NO — ADD IT!'}")
        print(f"    output/ ignored: {'YES' if has_output else 'NO — ADD IT!'}")
        print(f"    data/ ignored:   {'YES' if has_data else 'NO — ADD IT!'}")
    else:
        print("\n  [WARNING] No .gitignore found! Genetic data could be committed!")

    # Check network blocking
    print(f"\n  Network blocking:")
    try:
        with NetworkBlocker():
            import socket
            try:
                socket.socket()
                print("    [FAIL] Network not blocked!")
            except ConnectionError:
                print("    [OK] Network successfully blocked during analysis")
    except Exception as e:
        print(f"    [ERROR] {e}")

    # Check databases
    print(f"\n  Databases:")
    print(f"    ClinVar:  {'FOUND' if CLINVAR_TSV.exists() else 'NOT FOUND — run: python main.py download'}")
    print(f"    PharmGKB: {'FOUND' if PHARMGKB_ANNOTATIONS.exists() else 'NOT FOUND'}")

    # Check Ollama
    print(f"\n  Local AI (Ollama):")
    try:
        from src.local_ai import is_ollama_available, list_models
        if is_ollama_available():
            models = list_models()
            print(f"    [OK] Ollama available with {len(models)} model(s)")
            for m in models[:5]:
                print(f"      - {m}")
        else:
            print("    [NOT INSTALLED] Install from https://ollama.ai")
    except Exception:
        print("    [NOT INSTALLED] Install from https://ollama.ai")

    print()


def cmd_formats(args):
    """Show supported DNA file formats."""
    print()
    print("Supported DNA raw data formats:")
    print()
    print("  23andMe      4 columns: rsid, chromosome, position, genotype")
    print("  AncestryDNA  5 columns: rsid, chromosome, position, allele1, allele2")
    print("  MyHeritage   CSV with RSID, CHROMOSOME, POSITION, RESULT columns")
    print("  Generic      Tab-separated with rsid in first column")
    print()
    print("Format is auto-detected from file headers.")
    print("Place your raw data file in the input/ directory.")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Gene Lens — Privacy-First Local Genome Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py analyze input/my_dna.txt
  python main.py analyze input/my_dna.txt --name "John" --ai
  python main.py web                          # Dashboard local
  python main.py download
  python main.py privacy-check
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze genome file")
    p_analyze.add_argument("genome", type=str, help="Path to raw DNA file")
    p_analyze.add_argument("--name", "-n", type=str, default=None, help="Subject name for reports")
    p_analyze.add_argument("--ai", action="store_true", help="Run local AI interpretation (requires Ollama)")
    p_analyze.add_argument("--model", type=str, default=None, help="Ollama model (default: llama3.1:8b)")
    p_analyze.add_argument("--lang", type=str, default="en", choices=["pt-BR", "en"], help="Report language")

    # download
    p_download = subparsers.add_parser("download", help="Download reference databases")

    # privacy-check
    p_privacy = subparsers.add_parser("privacy-check", help="Verify privacy setup")

    # web
    p_web = subparsers.add_parser("web", help="Start local dashboard")
    p_web.add_argument("--port", type=int, default=5000, help="Port (default: 5000)")
    p_web.add_argument(
        "--lang", type=str, default="en", choices=["en", "pt", "pt-BR"],
        help="Console/log language (default: en). UI language is per-user via cookie.",
    )

    # formats
    p_formats = subparsers.add_parser("formats", help="Show supported DNA formats")

    args = parser.parse_args()

    if args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "download":
        cmd_download(args)
    elif args.command == "web":
        from dashboard import run_dashboard
        run_dashboard(port=args.port, lang=args.lang)
    elif args.command == "privacy-check":
        cmd_privacy_check(args)
    elif args.command == "formats":
        cmd_formats(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
