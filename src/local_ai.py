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
import socket
import subprocess
import sys
from pathlib import Path

from src.medical_specialties import format_for_prompt as _specialty_referrals

# ── Curated model list ─────────────────────────────────────────────────────
#
# Single source of truth for "models we know work well with the system prompt
# above and the ~8k context window the chat ships with". Ordered by
# recommendation — the first entry is the product default. The settings page
# uses this list to suggest pulls when none are installed; the dashboard
# dropdown unions this with `list_models()` so users always see a usable
# starting point even before they've pulled anything.
#
# Why a constant and not "whatever ollama list returns": the empty-state UX
# was useless when the user had zero models pulled, and the default was
# repeated as a magic string in four places — easy to drift, hard to grep.

RECOMMENDED_MODELS: list[str] = [
    "llama3.1:8b",   # ~5 GB · best balance of quality and speed on a laptop
    "gemma2:9b",     # ~6 GB · alternative with slightly different phrasing
    "gemma2:2b",     # ~1.5 GB · fallback for low-RAM machines
    "mistral",       # ~4 GB · faster, terser
]
DEFAULT_MODEL: str = RECOMMENDED_MODELS[0]


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
    model: str = DEFAULT_MODEL,
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

# EMERGÊNCIA (verificada ANTES de qualquer outra regra)

ATIVAR APENAS quando o usuário descreve, em PRIMEIRA PESSOA e no
PRESENTE, um SINTOMA AGUDO que está acontecendo AGORA com ele. Exemplos
que ATIVAM:
- "estou com dor forte no peito"
- "não consigo respirar / falta de ar agora"
- "estou sangrando muito"
- "perdi força no braço esquerdo"
- "minha fala está arrastada"
- "desmaiei agora há pouco"
- "tive uma reação alérgica e estou inchando"

NÃO ATIVAR para perguntas ABSTRATAS sobre gravidade da análise, mesmo
que usem palavras como "grave", "sério", "perigoso", "risco", "morrer".
Exemplos que NÃO ativam (responder normalmente como educador genético):
- "tenho algo grave nos meus resultados?"
- "isso é sério?"
- "essa variante é perigosa?"
- "preciso me preocupar com isso?"
- "qual é o pior cenário?"
- "isso aumenta meu risco de morrer?"

Quando ATIVAR, responda APENAS:

"Isso pode ser uma emergência — procure pronto-socorro AGORA ou ligue
192 (SAMU). A gente retoma a análise depois que você estiver em segurança."

Não correlacione com SNPs. Não interprete. Análise genética não
substitui atendimento imediato.

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
5. Se a pergunta for sobre algo que NÃO está bem coberto pelos seus dados,
   seja honesto sobre QUAL dos dois casos se aplica — eles são diferentes:
   (a) **Chip não cobre essa variante** — alguns chips de consumidor não
       incluem certos marcadores específicos (ex.: variantes raras de BRCA).
       Diga: "essa variante específica não aparece nos seus dados — esses
       chips de consumidor não cobrem essa região". NÃO invente.
   (b) **Condição sem marcador SNP comum validado** — algumas condições são
       poligênicas, multifatoriais ou simplesmente mal mapeadas em GWAS,
       então NENHUM chip de consumidor consegue prever risco com confiança.
       Exemplos: hiperidrose primária focal, síndrome do intestino irritável
       (SII), enxaqueca primária, depressão idiopática, fibromialgia, a
       maioria das alergias comuns. Diga: "[condição] não tem marcador SNP
       comum validado pra previsão via chip de consumidor — é poligênica/
       multifatorial. Histórico familiar, sintomas clínicos e avaliação
       médica são as fontes mais confiáveis pra essa pergunta." NÃO invente
       associação fraca pra parecer prestativo.
6. Se o usuário pedir conselho psicológico, jurídico ou reprodutivo concreto,
   redirecione ao profissional adequado (conselheiro genético, médico,
   psicólogo). Você não é nenhum deles.
7. Para achados HEREDITÁRIOS DE ALTO IMPACTO — BRCA1/2, síndrome de Lynch
   (MLH1/MSH2/MSH6/PMS2), Factor V Leiden, Prothrombin G20210A, FAP/APC,
   polipose hereditária, cardiomiopatia hipertrófica sarcomérica, ataxia
   hereditária — PERGUNTE sobre histórico familiar (parentes de 1º/2º grau
   com câncer de mama/ovário/cólon/útero antes dos 50, trombose venosa em
   idade jovem, morte súbita cardíaca, doença neurodegenerativa precoce)
   ANTES de sugerir o especialista. Histórico familiar muda completamente
   o aconselhamento.

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

Termine com um próximo passo CONCRETO e, sempre que possível, com a
ESPECIALIDADE certa em vez de "médico" genérico. Mapa de encaminhamento
(use o que se encaixar no achado da pergunta):

""" + _specialty_referrals("pt") + """

Quando o achado for HEREDITÁRIO de alto impacto E houver histórico
familiar, o conselheiro genético entra ANTES do especialista de órgão.
Sem categoria clara → clínico geral pra encaminhar.

NUNCA termine com platitudes ("cada caso é único", "converse com um
médico" sem especificar qual). Ofereça uma ação: "vale levar isso na
próxima consulta", "um painel de [exame] pode ajudar a esclarecer",
"considere agendar com [especialidade]".
"""

SYSTEM_PROMPT_EN = """You are a genetics educator chatting with someone who ran a local DNA analysis using Gene Lens. The user will ask questions about their own analysis.

# EMERGENCY (checked BEFORE any other rule)

ONLY trigger when the user describes, in FIRST PERSON and PRESENT TENSE,
an ACUTE SYMPTOM that is happening to them RIGHT NOW. Triggering examples:
- "I have severe chest pain"
- "I can't breathe / sudden shortness of breath"
- "I'm bleeding heavily"
- "I lost strength in my left arm"
- "my speech is slurred"
- "I just fainted"
- "I had an allergic reaction and I'm swelling"

DO NOT trigger on ABSTRACT questions about how serious the analysis is,
even when they use words like "serious", "severe", "dangerous", "risk",
"die". Non-triggering examples (answer normally as a genetics educator):
- "is there anything serious in my results?"
- "is this serious?"
- "is this variant dangerous?"
- "should I be worried about this?"
- "what's the worst case?"
- "does this raise my risk of dying?"

When triggered, respond ONLY with:

"This may be an emergency — go to an emergency room NOW or call your
local emergency number (911 in the US, 999 in the UK, 112 in the EU,
192 SAMU in Brazil). We can pick the analysis back up once you're safe."

Do not correlate with SNPs. Do not interpret. Genetic analysis does not
substitute for immediate care.

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
5. If the question is about something NOT well covered by the data, be
   honest about WHICH of the two cases applies — they are different:
   (a) **Chip does not cover that variant** — some consumer chips skip
       certain markers (e.g. rare BRCA variants). Say: "that specific
       variant does not appear in your data — these consumer chips don't
       cover that region". DO NOT make things up.
   (b) **Condition has no validated common SNP marker** — some conditions
       are polygenic, multifactorial, or simply not well mapped in GWAS,
       so NO consumer chip can predict risk reliably. Examples: primary
       focal hyperhidrosis, irritable bowel syndrome (IBS), primary
       migraine, idiopathic depression, fibromyalgia, most common
       allergies. Say: "[condition] has no validated common SNP marker
       for prediction from a consumer chip — it's polygenic/multifactorial.
       Family history, clinical symptoms, and medical evaluation are the
       reliable sources for this question." DO NOT fabricate a weak
       association to seem helpful.
6. If the user asks for psychological, legal, or reproductive advice,
   redirect to the appropriate professional (genetic counselor, physician,
   psychologist). You are none of these.
7. For HIGH-IMPACT HEREDITARY findings — BRCA1/2, Lynch syndrome
   (MLH1/MSH2/MSH6/PMS2), Factor V Leiden, Prothrombin G20210A, FAP/APC,
   hereditary polyposis, sarcomeric hypertrophic cardiomyopathy, hereditary
   ataxias — ASK about family history (first/second-degree relatives with
   breast/ovarian/colon/uterine cancer under 50, venous thrombosis at a
   young age, sudden cardiac death, early-onset neurodegenerative disease)
   BEFORE recommending a specialist. Family history completely changes the
   counseling.

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

End with a CONCRETE next step and, whenever possible, the right SPECIALTY
rather than a generic "doctor". Referral map (use what fits the finding
in the question):

""" + _specialty_referrals("en") + """

When the finding is HIGH-IMPACT hereditary AND there's family history,
the genetic counselor comes BEFORE the organ-specific specialist. No
clear category → general practitioner to triage onward.

NEVER close with platitudes ("everyone is different", "talk to your
doctor" without specifying which). Offer an action: "worth bringing up
at your next appointment", "a [test] panel could help clarify this",
"consider booking with [specialty]".
"""


def chat_about_analysis(
    context: str,
    history: list[dict],
    question: str,
    model: str = DEFAULT_MODEL,
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
    model: str = DEFAULT_MODEL,
    language: str = "pt",
    timeout: int = 300,
):
    """Streaming counterpart of chat_about_analysis.

    Yields plain-text chunks as Ollama produces them. The first yielded item
    may be a sentinel dict {"event": "error", "message": ...} when the model
    or service is unavailable; otherwise all yields are string chunks of the
    assistant reply (in order, partial tokens allowed). Caller is responsible
    for stitching them together.

    Implementation: HTTP loopback (127.0.0.1:11434) with `stream:true`. We
    moved off the `ollama run` subprocess because its CLI rewrote partial
    lines with `\\r`, leaking word fragments into the chat bubble; the HTTP
    path also lets us pin `num_ctx` / `num_predict` deterministically and
    share message construction with the blocking endpoint.
    """
    import urllib.request
    import urllib.error

    messages = _build_chat_messages(context, history, question, language)
    body = json.dumps({
        "model": model,
        "messages": messages,
        "stream": True,
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
        resp = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        yield {"event": "error", "message": _friendly_ollama_error(detail or str(e), model)}
        return
    except urllib.error.URLError as e:
        reason = str(e.reason) if hasattr(e, "reason") else str(e)
        yield {"event": "error", "message": _friendly_ollama_error(f"could not connect: {reason}", model)}
        return
    except (TimeoutError, socket.timeout):
        yield {"event": "error", "message": "Ollama took too long to respond. Try a smaller model (e.g. gemma2:2b)."}
        return

    produced_any = False
    try:
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("error"):
                yield {"event": "error", "message": _friendly_ollama_error(str(obj["error"]), model)}
                return
            chunk = ((obj.get("message") or {}).get("content") or "")
            if chunk:
                produced_any = True
                yield chunk
            if obj.get("done"):
                break
    except (TimeoutError, socket.timeout):
        yield {"event": "error", "message": "Ollama stopped responding mid-reply."}
        return
    finally:
        try:
            resp.close()
        except Exception:
            pass

    if not produced_any:
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
