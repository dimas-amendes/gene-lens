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
import re
import socket
import subprocess
import sys
from pathlib import Path

# Ollama CLI emits ANSI cursor/erase control sequences when it detects (or
# guesses) a TTY. They survive subprocess.PIPE and leak into the chat as
# garbage like "[5D [K" or "[1D [K". This regex matches CSI sequences
# (ESC + '[' + optional params + a final byte) plus bare ESC[?…h variants.
_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07")


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from Ollama output.

    Ollama's CLI also rewrites partial lines with carriage returns, so a
    bare `\\r` means "discard everything since the previous newline" — we
    apply that semantics here so duplicated word fragments don't leak into
    the rendered chat bubble.
    """
    if not text:
        return text
    cleaned = _ANSI_ESCAPE_RE.sub("", text)
    if "\r" in cleaned:
        out_lines = []
        for line in cleaned.split("\n"):
            if "\r" in line:
                line = line.split("\r")[-1]
            out_lines.append(line)
        cleaned = "\n".join(out_lines)
    return cleaned


def _clean_env() -> dict:
    """Environment that tells Ollama (and anything it spawns) we're not a TTY,
    so it doesn't emit ANSI cursor/spinner control codes.

    Also pins COLUMNS/LINES to a giant value so Ollama's CLI doesn't
    soft-wrap mid-word and rewrite with `\\r` (which leaked partials like
    "CYP2C1\\nCYP2C19" into the rendered chat bubble)."""
    import os
    env = os.environ.copy()
    env["TERM"] = "dumb"
    env["NO_COLOR"] = "1"
    env["COLUMNS"] = "100000"
    env["LINES"] = "100000"
    return env


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


# ── System prompts ──────────────────────────────────────────────────────────
#
# These constants are the "constitution" the local model lives under for the
# whole chat session. Treat them as production code, not throwaway text —
# every line shapes how the model talks to people about their own DNA.
#
# Design choices baked in:
#
# 1. Educator framing, not clinician framing.
#    The model is a teacher; the user's doctor is the one who decides anything.
#    This keeps the product on the right side of "not a medical device".
#
# 2. Absolute prohibitions are listed first and in BLOCK CAPS so a small
#    8B-parameter model can latch onto them. Order matters — diagnostic
#    language ("you have") leads, prescription ("take X mg") second,
#    confident risk ("you are at risk") third.
#
# 3. Output format is specified explicitly. Without it, llama3.1:8b defaults
#    to wall-of-text or a 10-bullet list for every question. We want short
#    paragraphs with sparing use of bullets for "topics for your doctor"
#    style enumerations.
#
# 4. Refusal patterns are spelled out. If the user asks about a topic that
#    isn't in their analysis (e.g. "do I have a BRCA mutation" when the chip
#    didn't cover that variant), the model must say so explicitly rather than
#    confabulating.
#
# 5. rsID citation. When the model mentions a variant, it must use the
#    "rs1234" form so the frontend can render it as a clickable chip that
#    scrolls to the corresponding finding in the dashboard.
#
# 6. Cultural register. PT-BR version is tuned for Brazilian medical context
#    (SUS / convênio dynamics, "conselheiro genético" terminology). EN is
#    international.

SYSTEM_PROMPT_PT = """Você é um educador em genética conversando com alguém que rodou uma análise local de DNA com a ferramenta Gene Lens. O usuário vai fazer perguntas sobre a própria análise.

# REGRAS ABSOLUTAS (nunca quebre nenhuma)

1. NÃO diga "você tem [condição]", "você está em risco de", "você deve". Use:
   "este achado sugere conversar com um médico sobre X",
   "esta variante está associada a Y na literatura",
   "vale levar isso pra próxima consulta".
2. NÃO prescreva suplementos, doses, dietas ou medicamentos. Pode citar faixas
   estudadas na literatura ("estudos investigaram doses de 400-800 mg de Z"),
   mas sempre encerrando com "discuta com seu médico antes de qualquer ajuste".
3. NÃO afirme diagnóstico. Testes de consumo (23andMe, AncestryDNA, Genera)
   têm ~40% de falso positivo para variantes clinicamente significativas
   (Tandy-Connor 2018) — toda variante "patogênica" aqui precisa de
   confirmação por sequenciamento clínico.
4. Doenças comuns (câncer, diabetes, Alzheimer, cardiovasculares, depressão)
   são poligênicas e dependem de ambiente. SNPs isolados NÃO preveem se a
   pessoa vai desenvolvê-las. Sempre lembre disso quando relevante.
5. Se a pergunta for sobre algo que NÃO aparece na análise (ex.: usuário
   pergunta sobre BRCA1 e o chip dele não cobre essa variante), diga
   explicitamente: "isso não aparece nos seus dados — esses chips não cobrem
   essa região / variante específica". NÃO invente.
6. Se o usuário pedir conselho psicológico, jurídico ou reprodutivo concreto,
   redirecione ao profissional adequado (conselheiro genético, médico,
   psicólogo). Você não é nenhum deles.

# FORMATO DE SAÍDA

- Responda em português brasileiro coloquial mas preciso. Sem "Olá!" ou
  "Que ótima pergunta!" — vá direto ao ponto.
- Comprimento: 3-6 parágrafos curtos no máximo. Se a pergunta for específica,
  responda em um único parágrafo.
- Use Markdown:
  - **negrito** para o ponto principal de cada parágrafo
  - listas com `-` apenas para "tópicos para o médico" ou enumerações reais
  - `código` para identificadores técnicos (rsIDs, genes)
- Cite rsIDs no formato "rs1234" (sem aspas no output, sem "rs#1234"). A
  interface renderiza esses identificadores como chips clicáveis que levam
  ao achado correspondente.
- Sempre que citar um gene, use o símbolo HUGO em maiúsculas (APOE, BRCA1,
  CYP2C19).

# QUANDO TERMINAR

Se a resposta envolve uma decisão de saúde, termine sugerindo um próximo
passo concreto: "vale levar isso na próxima consulta", "um exame de
[X] pode ajudar a esclarecer", "considere conversar com um conselheiro
genético se houver histórico familiar". Não termine com platitudes ("cada
caso é único") — termine com uma ação.
"""

SYSTEM_PROMPT_EN = """You are a genetics educator chatting with someone who ran a local DNA analysis using Gene Lens. The user will ask questions about their own analysis.

# ABSOLUTE RULES (never break any)

1. DO NOT say "you have [condition]", "you are at risk for", "you should".
   Use instead:
   "this finding suggests discussing X with your doctor",
   "this variant is associated with Y in the literature",
   "worth bringing this up at your next appointment".
2. DO NOT prescribe supplements, doses, diets, or medications. You may cite
   ranges studied in the literature ("studies have investigated doses of
   400-800 mg of Z"), always ending with "discuss with your doctor before
   making any change".
3. DO NOT state a diagnosis. Consumer genotyping (23andMe, AncestryDNA,
   MyHeritage) has a ~40% false-positive rate for clinically significant
   variants (Tandy-Connor 2018) — every "pathogenic" variant here needs
   clinical sequencing to confirm.
4. Common diseases (cancer, diabetes, Alzheimer's, cardiovascular,
   depression) are polygenic and environment-dependent. Individual SNPs
   CANNOT predict whether someone will develop them. Always remind the user
   when relevant.
5. If the question is about something NOT in the analysis (e.g. user asks
   about BRCA1 when their chip didn't cover that variant), say so
   explicitly: "that does not appear in your data — these chips don't cover
   that specific region / variant". DO NOT make things up.
6. If the user asks for psychological, legal, or reproductive advice,
   redirect to the appropriate professional (genetic counselor, physician,
   psychologist). You are none of these.

# OUTPUT FORMAT

- Respond in English, plain but precise. No "Hi there!" or "Great question!"
  — get to the point.
- Length: 3-6 short paragraphs maximum. If the question is specific, answer
  in a single paragraph.
- Use Markdown:
  - **bold** for the main point of each paragraph
  - lists with `-` only for "topics for your doctor" or real enumerations
  - `code` for technical identifiers (rsIDs, genes)
- Cite rsIDs in the form "rs1234" (no quotes in the output, no "rs#1234").
  The frontend renders these as clickable chips that jump to the
  corresponding finding.
- When citing a gene, use the official HUGO symbol in caps (APOE, BRCA1,
  CYP2C19).

# HOW TO END

If the answer involves a health decision, end with a concrete next step:
"worth bringing up at your next appointment", "a [X] lab could help clarify
this", "consider talking to a genetic counselor if you have a family
history". Don't close with platitudes ("everyone is different") — close
with an action.
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

    Talks to the local Ollama daemon over loopback (127.0.0.1:11434) instead
    of spawning `ollama run`. The CLI is a thin client to the same daemon —
    going direct avoids its terminal rendering (soft-wrap mid-word, ANSI
    spinners) that smuggled word fragments like "CYP2C1\\nCYP2C19" into the
    chat bubble, and lets us pin num_ctx / num_predict explicitly so replies
    aren't truncated mid-thought.
    """
    import urllib.request
    import urllib.error

    messages = _build_chat_messages(context, history, question, language)
    body = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_ctx": 8192,
            "num_predict": 2048,
            "temperature": 0.3,
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        return False, _friendly_ollama_error(detail or str(e), model)
    except urllib.error.URLError as e:
        reason = str(e.reason) if hasattr(e, "reason") else str(e)
        return False, _friendly_ollama_error(f"could not connect: {reason}", model)
    except (TimeoutError, socket.timeout):
        return False, "Ollama took too long to respond. Try a smaller model (e.g. gemma2:2b)."

    answer = ((payload.get("message") or {}).get("content") or "").strip()
    if not answer:
        return False, "The model produced an empty response. Try rephrasing your question."
    return True, answer


def _build_chat_messages(context: str, history: list, question: str, language: str) -> list[dict]:
    """Build the messages array for Ollama's /api/chat endpoint."""
    system_prompt = SYSTEM_PROMPT_PT if language == "pt" else SYSTEM_PROMPT_EN

    MAX_CONTEXT_CHARS = 20000
    ctx = (context or "").strip()
    if len(ctx) > MAX_CONTEXT_CHARS:
        ctx = ctx[:MAX_CONTEXT_CHARS] + (
            f"\n\n[... analysis truncated: {len(ctx) - MAX_CONTEXT_CHARS} "
            "characters omitted to fit the model's context window. "
            "Ask about specific findings to get more detail.]"
        )

    messages = [{
        "role": "system",
        "content": (
            system_prompt
            + "\n\n---- USER'S ANALYSIS (read-only context) ----\n"
            + ctx
            + "\n---- END OF ANALYSIS ----"
        ),
    }]
    for turn in history[-8:]:
        role = "user" if turn.get("role") == "user" else "assistant"
        content = (turn.get("content") or "").strip()
        if content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": question.strip()})
    return messages


def chat_about_analysis_stream(
    context: str,
    history: list[dict],
    question: str,
    model: str = "llama3.1:8b",
    language: str = "pt",
):
    """Streaming counterpart of chat_about_analysis.

    Yields plain-text chunks as Ollama produces them. The first yielded item
    may be a sentinel dict {"event": "error", "message": ...} when the model
    or service is unavailable; otherwise all yields are string chunks of the
    assistant reply (in order, partial tokens allowed). Caller is responsible
    for stitching them together.

    Implementation note: uses subprocess.Popen + line iteration on stdout
    instead of the Ollama HTTP API, so we don't introduce a new dependency
    and the NetworkBlocker (when active for analysis) doesn't interfere.
    """
    if not is_ollama_available():
        yield {"event": "error", "message": (
            "Ollama is not available on this machine. Install it from "
            "https://ollama.com and pull a model (e.g. `ollama pull llama3.1:8b`)."
        )}
        return

    prompt = _build_chat_prompt(context, history, question, language)

    try:
        proc = subprocess.Popen(
            ["ollama", "run", model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # line buffered
            env=_clean_env(),
        )
    except FileNotFoundError:
        yield {"event": "error", "message": "Ollama binary not found. Install it from https://ollama.com."}
        return

    # Feed the full prompt then close stdin so Ollama starts generating.
    try:
        proc.stdin.write(prompt)
        proc.stdin.close()
    except BrokenPipeError:
        # Process died before we could send the prompt — most likely the model isn't pulled.
        stderr = (proc.stderr.read() or "") if proc.stderr else ""
        yield {"event": "error", "message": _friendly_ollama_error(stderr, model)}
        return

    produced_any = False
    try:
        while True:
            raw = proc.stdout.read(64) if proc.stdout else ""
            if not raw:
                break
            chunk = _strip_ansi(raw)
            if not chunk:
                continue  # whole chunk was control codes, swallow it
            produced_any = True
            yield chunk
    finally:
        proc.wait(timeout=2)

    if proc.returncode != 0:
        stderr = (proc.stderr.read() or "") if proc.stderr else ""
        # If we already streamed text the caller can ignore this — but we still
        # surface the diagnostic so the UI can append a banner.
        yield {"event": "error", "message": _friendly_ollama_error(stderr, model)}
    elif not produced_any:
        yield {"event": "error", "message": "The model produced an empty response. Try rephrasing your question."}


def estimate_tokens(text: str) -> int:
    """Rough token count for sizing prompts vs. context window.

    Uses the conventional rule of thumb (~4 chars per token for English/PT
    on Llama-family tokenizers). This is an estimate — exact counts depend
    on the tokenizer and the script. Good enough for "will this fit" UI hints.
    """
    if not text:
        return 0
    return max(1, len(text) // 4)


def estimate_prompt_tokens(context: str, history: list, question: str, language: str = "pt") -> dict:
    """Token estimate broken down by section, so the UI can show what's
    eating the budget."""
    sys_prompt = SYSTEM_PROMPT_PT if language == "pt" else SYSTEM_PROMPT_EN
    history_text = "\n".join(t.get("content", "") for t in history[-8:])
    return {
        "system": estimate_tokens(sys_prompt),
        "context": estimate_tokens(context),
        "history": estimate_tokens(history_text),
        "question": estimate_tokens(question),
        "total": estimate_tokens(sys_prompt) + estimate_tokens(context)
                 + estimate_tokens(history_text) + estimate_tokens(question),
    }


def _build_chat_prompt(context: str, history: list, question: str, language: str) -> str:
    """Shared prompt construction used by both blocking and streaming chat."""
    system_prompt = SYSTEM_PROMPT_PT if language == "pt" else SYSTEM_PROMPT_EN

    MAX_CONTEXT_CHARS = 20000
    context = context.strip()
    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS] + (
            f"\n\n[... analysis truncated: {len(context) - MAX_CONTEXT_CHARS} "
            "characters omitted to fit the model's context window. "
            "Ask about specific findings to get more detail.]"
        )

    transcript_lines = [
        system_prompt,
        "",
        "---- USER'S ANALYSIS (read-only context) ----",
        context,
        "---- END OF ANALYSIS ----",
        "",
    ]
    for turn in history[-8:]:
        role = "USER" if turn.get("role") == "user" else "ASSISTANT"
        transcript_lines.append(f"{role}: {turn.get('content', '').strip()}")
    transcript_lines.append(f"USER: {question.strip()}")
    transcript_lines.append("ASSISTANT:")
    return "\n".join(transcript_lines)


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
