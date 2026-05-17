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


SYSTEM_PROMPT_PT = """Voce e um educador em genetica conversando com alguem que rodou uma analise local de DNA com a ferramenta Gene Lens. O usuario fara perguntas sobre a propria analise.

REGRAS ABSOLUTAS:
- NUNCA diga "voce tem", "voce esta em risco" ou "voce deve" — use "este achado sugere conversar com um medico sobre X"
- NUNCA prescreva suplementos, doses, dietas ou medicamentos — sempre encaminhe ao profissional
- NUNCA afirme diagnostico — testes de consumo tem ~40% de falso positivo para variantes clinicamente significativas
- SEMPRE lembre que doencas comuns sao poligenicas e nao podem ser previstas por SNPs isolados
- SE a pergunta for sobre topico ausente nos dados, diga claramente "isso nao aparece na sua analise"
- Responda em portugues brasileiro, conciso (3-6 paragrafos no maximo)
"""

SYSTEM_PROMPT_EN = """You are a genetics educator chatting with someone who ran a local DNA analysis using Gene Lens. The user will ask questions about their own analysis.

ABSOLUTE RULES:
- NEVER say "you have", "you are at risk for", or "you should" — instead "this finding suggests discussing X with your doctor"
- NEVER prescribe supplements, doses, diets, or medications — always defer to a healthcare professional
- NEVER state a diagnosis — consumer genotyping has a ~40% false-positive rate for clinically significant variants
- ALWAYS remind that common diseases are polygenic and cannot be predicted by individual SNPs
- IF the question is about a topic absent from the data, clearly say "that does not appear in your analysis"
- Respond in English, concise (3-6 short paragraphs max)
"""


def chat_about_analysis(
    context: str,
    history: list[dict],
    question: str,
    model: str = "llama3.1:8b",
    language: str = "pt",
    timeout: int = 120,
) -> tuple[bool, str]:
    """Ask a question about a previously generated analysis.

    Returns (ok, text). On failure, text holds a user-facing error message.
    """
    if not is_ollama_available():
        return False, (
            "Ollama is not available on this machine. Install it from "
            "https://ollama.com and pull a model (e.g. `ollama pull llama3.1:8b`)."
        )

    system_prompt = SYSTEM_PROMPT_PT if language == "pt" else SYSTEM_PROMPT_EN

    # Bound the analysis context so it never blows past the typical 8 GB
    # consumer model's effective context window (~6k tokens ≈ 24k chars).
    # Reserve ~4k chars for system prompt + history + reply. Anything past
    # this is truncated with a visible marker so the model knows it's seeing
    # a subset and won't fabricate details about the cut content.
    MAX_CONTEXT_CHARS = 20000
    context = context.strip()
    truncated_note = ""
    if len(context) > MAX_CONTEXT_CHARS:
        kept = context[:MAX_CONTEXT_CHARS]
        truncated_note = (
            f"\n\n[... analysis truncated: {len(context) - MAX_CONTEXT_CHARS} "
            "characters omitted to fit the model's context window. "
            "Ask about specific findings to get more detail.]"
        )
        context = kept + truncated_note

    # Build a single prompt: system + analysis context + chat transcript + new question.
    # Ollama CLI doesn't expose role-based messages, so we serialize manually with
    # explicit ROLE: markers — small models follow this well enough for our use case.
    transcript_lines = [
        system_prompt,
        "",
        "---- USER'S ANALYSIS (read-only context) ----",
        context,
        "---- END OF ANALYSIS ----",
        "",
    ]
    for turn in history[-8:]:  # keep last 8 turns so the prompt stays bounded
        role = "USER" if turn.get("role") == "user" else "ASSISTANT"
        transcript_lines.append(f"{role}: {turn.get('content', '').strip()}")
    transcript_lines.append(f"USER: {question.strip()}")
    transcript_lines.append("ASSISTANT:")
    prompt = "\n".join(transcript_lines)

    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, "Ollama took too long to respond. Try a smaller model (e.g. gemma2:2b)."
    except FileNotFoundError:
        return False, "Ollama binary not found. Install it from https://ollama.com."

    if result.returncode != 0:
        return False, _friendly_ollama_error(result.stderr or "", model)

    answer = result.stdout.strip()
    if not answer:
        return False, "The model produced an empty response. Try rephrasing your question."
    return True, answer


def _friendly_ollama_error(stderr: str, model: str) -> str:
    """Translate raw Ollama stderr into actionable messages for the UI."""
    low = stderr.lower()
    if "model" in low and ("not found" in low or "manifest" in low or "pulling manifest" in low):
        return (
            f"The model `{model}` isn't downloaded yet. Open a terminal and run:\n\n"
            f"`ollama pull {model}`\n\n"
            f"It's a one-time download (typically 2–8 GB). After it finishes, ask again."
        )
    if "connection refused" in low or "could not connect" in low:
        return (
            "Ollama is installed but the background service isn't running. "
            "Start it with `ollama serve` in a terminal, or just launch the Ollama app."
        )
    if "out of memory" in low or "cuda out of memory" in low:
        return (
            f"Your machine ran out of memory loading `{model}`. Try a smaller model "
            "(e.g. `ollama pull gemma2:2b`) and select it from the dropdown."
        )
    # Fall back to the raw stderr, trimmed.
    cleaned = stderr.strip()
    if cleaned:
        return cleaned[:600]
    return "Ollama returned a non-zero exit code without details."


def save_interpretation(interpretation: str, output_path: Path):
    """Save AI interpretation to a separate file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# AI Health Interpretation\n\n")
        f.write("*Generated locally using Ollama — no data sent to external servers.*\n\n")
        f.write("---\n\n")
        f.write(interpretation)
        f.write("\n\n---\n\n")
        f.write("**This is NOT medical advice. Consult a healthcare professional.**\n")
