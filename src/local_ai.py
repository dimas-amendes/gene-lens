"""
Local AI interpretation via Ollama — 100% offline, zero data leakage.

Ollama runs LLMs locally (Llama 3, Mistral, Gemma, etc.).
This module reads the generated reports and produces a human-friendly
interpretation without sending any data to external servers.

Requirements:
- Ollama installed: https://ollama.ai
- A model pulled: ollama pull llama3.1:8b (or gemma2:9b, mistral, etc.)
"""
import json
import subprocess
import sys
from pathlib import Path


def is_ollama_available() -> bool:
    """Check if Ollama is installed and running."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def list_models() -> list[str]:
    """List available Ollama models."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []
        lines = result.stdout.strip().split("\n")
        models = []
        for line in lines[1:]:  # skip header
            parts = line.split()
            if parts:
                models.append(parts[0])
        return models
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def interpret_reports(
    report_paths: list[Path],
    model: str = "llama3.1:8b",
    language: str = "pt-BR",
) -> str:
    """Send reports to local Ollama for human-friendly interpretation.

    This uses the Ollama CLI directly — no HTTP, no network.
    The model runs entirely on your machine.
    """
    if not is_ollama_available():
        return (
            "\n[AI Interpretation unavailable]\n"
            "Install Ollama (https://ollama.ai) and pull a model:\n"
            "  ollama pull llama3.1:8b\n"
            "Then re-run with: python main.py analyze <file> --ai\n"
        )

    # Read reports
    combined = ""
    for path in report_paths:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            # Truncate if too long for context window
            if len(content) > 12000:
                content = content[:12000] + "\n\n[...truncated for model context window...]"
            combined += f"\n\n{'='*60}\n{path.name}\n{'='*60}\n\n{content}"

    lang_instruction = ""
    if language == "pt-BR":
        lang_instruction = "Responda em português brasileiro."
    elif language == "en":
        lang_instruction = "Respond in English."

    prompt = f"""You are helping someone understand a preliminary genetic exploration report.
{lang_instruction}

CRITICAL CONTEXT: This data comes from consumer-grade genotyping (like 23andMe), NOT
clinical sequencing. Published research shows a ~40% false-positive rate for clinically
significant variants in this type of data. All findings are PRELIMINARY and UNCONFIRMED.

Based on the genetic analysis below, provide:

1. **Plain-Language Summary** (3-5 most notable signals — emphasize these are unconfirmed)
2. **Questions to Ask Your Doctor** (specific topics to bring up at next appointment)
3. **Drug Interactions Worth Mentioning** (to share with prescribing physicians — NOT to self-adjust)
4. **Lab Tests to Request** (which tests might help confirm or rule out genetic signals)

IMPORTANT RULES:
- Never say "you have" or "you are at risk for" — say "this signal suggests discussing X with your doctor"
- Never prescribe supplements, doses, or dietary changes — frame as "topics to explore with a professional"
- Always remind that consumer genotyping is not clinical-grade and findings need confirmation
- Be clear that common diseases are polygenic and cannot be predicted by individual SNPs

--- GENETIC REPORTS ---
{combined}
--- END REPORTS ---"""

    print(f"\n  Running local AI interpretation with {model}...")
    print("  (This may take 1-3 minutes depending on your hardware)\n")

    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=300,  # 5 min max
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"[AI Error] {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "[AI Timeout] Model took too long. Try a smaller model: ollama pull gemma2:2b"
    except FileNotFoundError:
        return "[AI Error] Ollama not found. Install from https://ollama.ai"


def save_interpretation(interpretation: str, output_path: Path):
    """Save AI interpretation to a separate file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# AI Health Interpretation\n\n")
        f.write("*Generated locally using Ollama — no data sent to external servers.*\n\n")
        f.write("---\n\n")
        f.write(interpretation)
        f.write("\n\n---\n\n")
        f.write("**This is NOT medical advice. Consult a healthcare professional.**\n")
