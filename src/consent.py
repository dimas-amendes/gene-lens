"""
Consent / Terms acceptance — required before first use.

Stores acceptance flag in ~/.genetics_consent so it persists across sessions.
The user must explicitly acknowledge the limitations of consumer genotyping.
"""
from pathlib import Path

CONSENT_FILE = Path.home() / ".genetics_consent"

TERMS_TEXT = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    TERMOS DE USO / TERMS OF USE                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  Este software NAO e um dispositivo medico (SaMD).                     ║
║  This software is NOT a medical device (SaMD).                         ║
║                                                                        ║
║  Finalidade exclusivamente EDUCACIONAL e de AUTOCONHECIMENTO.          ║
║  For EDUCATIONAL and SELF-KNOWLEDGE purposes only.                     ║
║                                                                        ║
║  FATOS IMPORTANTES / IMPORTANT FACTS:                                  ║
║                                                                        ║
║  - Testes de genotipagem de consumo (23andMe, Genera, AncestryDNA)     ║
║    possuem taxa de falso positivo de aproximadamente 40% para           ║
║    variantes clinicamente significativas.                               ║
║    (Tandy-Connor et al., Genetics in Medicine, 2018)                   ║
║                                                                        ║
║  - Os resultados NAO substituem exames medicos, diagnosticos           ║
║    clinicos, laudos geneticos ou aconselhamento genetico.              ║
║                                                                        ║
║  - NUNCA altere medicamentos, dietas ou tratamentos baseado            ║
║    nestes resultados sem consultar um medico.                          ║
║                                                                        ║
║  - O autor/mantenedor NAO se responsabiliza por decisoes               ║
║    clinicas, sofrimento psicologico (ansiedade induzida por            ║
║    falsos positivos) ou quaisquer danos causados pelo uso              ║
║    deste software.                                                     ║
║                                                                        ║
║  Para aconselhamento genetico profissional:                            ║
║  https://findageneticcounselor.nsgc.org                                ║
║                                                                        ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

ACCEPT_PROMPT = (
    'Digite "Y" para aceitar / Type "Y" to accept: '
)


def is_consent_given() -> bool:
    """Check if user has already accepted terms."""
    return CONSENT_FILE.exists()


def require_consent():
    """Show terms and require acceptance. Exits if declined."""
    if is_consent_given():
        return

    print(TERMS_TEXT)
    try:
        answer = input(ACCEPT_PROMPT).strip().upper()
    except (EOFError, KeyboardInterrupt):
        print("\nTermos nao aceitos. Saindo.")
        raise SystemExit(1)

    if answer != "Y":
        print("\nTermos nao aceitos. Saindo. / Terms not accepted. Exiting.")
        raise SystemExit(1)

    # Save consent
    CONSENT_FILE.write_text(
        "consent_accepted=true\n"
        "This file records that the user accepted the terms of use.\n"
        "Delete this file to be prompted again.\n"
    )
    print("\nTermos aceitos. / Terms accepted.\n")


def require_consent_web():
    """For Flask: check consent, return True if accepted, False if not."""
    return is_consent_given()
