"""
Motor de traducao offline para textos clinicos.

Pipeline:
1. Pre-processamento: substitui jargao medico por tokens (__MED_01__)
2. Traducao neural: argos-translate (en -> pt) no texto limpo
3. Pos-processamento: devolve os termos medicos traduzidos manualmente

Isso impede que o motor neural distorca terminologia clinica critica.
"""
import re
from pathlib import Path

# ── Dicionario estatico de jargao medico ──────────────────────────────────────
# Termos que traducao neural erra com frequencia.
# Formato: {termo_ingles_lower: traducao_pt_exata}

MEDICAL_TERMS = {
    # Pharmacogenomics
    "wild-type": "tipo selvagem",
    "wild type": "tipo selvagem",
    "poor metabolizer": "metabolizador lento",
    "poor metaboliser": "metabolizador lento",
    "intermediate metabolizer": "metabolizador intermediario",
    "intermediate metaboliser": "metabolizador intermediario",
    "extensive metabolizer": "metabolizador extensivo",
    "extensive metaboliser": "metabolizador extensivo",
    "rapid metabolizer": "metabolizador rapido",
    "rapid metaboliser": "metabolizador rapido",
    "ultrarapid metabolizer": "metabolizador ultrarapido",
    "ultrarapid metaboliser": "metabolizador ultrarapido",
    "normal metabolizer": "metabolizador normal",
    "normal metaboliser": "metabolizador normal",
    "normal function": "funcao normal",
    "decreased function": "funcao reduzida",
    "increased function": "funcao aumentada",
    "no function": "sem funcao",
    "loss of function": "perda de funcao",
    "gain of function": "ganho de funcao",
    "clearance": "depuracao",
    "half-life": "meia-vida",
    "bioavailability": "biodisponibilidade",
    "steady state": "estado estacionario",
    "steady-state": "estado estacionario",
    "trough concentration": "concentracao de vale",
    "peak concentration": "concentracao de pico",
    "area under the curve": "area sob a curva",
    "drug exposure": "exposicao ao farmaco",
    "drug-drug interaction": "interacao medicamentosa",
    "adverse event": "evento adverso",
    "adverse events": "eventos adversos",
    "adverse effect": "efeito adverso",
    "adverse effects": "efeitos adversos",
    "adverse drug reaction": "reacao adversa ao medicamento",
    "side effect": "efeito colateral",
    "side effects": "efeitos colaterais",
    "dose adjustment": "ajuste de dose",
    "dose reduction": "reducao de dose",
    "dose increase": "aumento de dose",
    "standard dose": "dose padrao",
    "loading dose": "dose de ataque",
    "maintenance dose": "dose de manutencao",
    "therapeutic range": "faixa terapeutica",
    "therapeutic window": "janela terapeutica",
    "over-anticoagulation": "anticoagulacao excessiva",
    "anticoagulation": "anticoagulacao",
    "bleeding risk": "risco de sangramento",
    "bleeding": "sangramento",
    "thromboembolism": "tromboembolismo",
    "thrombosis": "trombose",
    "myopathy": "miopatia",
    "rhabdomyolysis": "rabdomiolise",
    "hepatotoxicity": "hepatotoxicidade",
    "nephrotoxicity": "nefrotoxicidade",
    "neurotoxicity": "neurotoxicidade",
    "cardiotoxicity": "cardiotoxicidade",
    "ototoxicity": "ototoxicidade",
    "myelosuppression": "mielossupressao",
    "neutropenia": "neutropenia",
    "agranulocytosis": "agranulocitose",
    "hypersensitivity": "hipersensibilidade",
    "anaphylaxis": "anafilaxia",

    # Genetics
    "missense variant": "variante missense",
    "nonsense variant": "variante nonsense",
    "frameshift variant": "variante de deslocamento de leitura",
    "splice variant": "variante de splicing",
    "synonymous variant": "variante sinonima",
    "pathogenic": "patogenica",
    "likely pathogenic": "provavelmente patogenica",
    "benign": "benigna",
    "likely benign": "provavelmente benigna",
    "uncertain significance": "significancia incerta",
    "risk factor": "fator de risco",
    "risk allele": "alelo de risco",
    "protective": "protetor",
    "carrier": "portador",
    "homozygous": "homozigoto",
    "heterozygous": "heterozigoto",
    "hemizygous": "hemizigoto",
    "autosomal dominant": "autossomico dominante",
    "autosomal recessive": "autossomico recessivo",
    "x-linked": "ligado ao X",
    "penetrance": "penetrancia",
    "incomplete penetrance": "penetrancia incompleta",
    "expressivity": "expressividade",
    "genotype": "genotipo",
    "phenotype": "fenotipo",
    "haplotype": "haplotipo",
    "allele": "alelo",
    "alleles": "alelos",
    "polymorphism": "polimorfismo",

    # Clinical
    "clinical outcome": "desfecho clinico",
    "clinical outcomes": "desfechos clinicos",
    "treatment response": "resposta ao tratamento",
    "treatment failure": "falha terapeutica",
    "efficacy": "eficacia",
    "toxicity": "toxicidade",
    "tolerability": "tolerabilidade",
    "susceptibility": "suscetibilidade",
    "predisposition": "predisposicao",
    "prognosis": "prognostico",
    "prevalence": "prevalencia",
    "incidence": "incidencia",
    "mortality": "mortalidade",
    "morbidity": "morbidade",
    "remission": "remissao",
    "relapse": "recaida",
    "overall survival": "sobrevida global",
    "progression-free survival": "sobrevida livre de progressao",
    "disease-free survival": "sobrevida livre de doenca",

    # Body / conditions
    "as compared to": "em comparacao com",
    "may have": "pode(m) ter",
    "increased risk": "risco aumentado",
    "decreased risk": "risco reduzido",
    "higher risk": "risco mais alto",
    "lower risk": "risco mais baixo",
    "patients with": "pacientes com",
    "individuals with": "individuos com",
    "subjects with": "sujeitos com",
    "Other genetic and clinical factors": "Outros fatores geneticos e clinicos",
    "may also influence": "tambem podem influenciar",
}

# Sort by length descending to match longer phrases first
_SORTED_TERMS = sorted(MEDICAL_TERMS.items(), key=lambda x: -len(x[0]))


class MedicalTranslator:
    """Translates clinical text from English to Portuguese with medical term preservation."""

    def __init__(self):
        self._argos_available = False
        self._argos_translator = None
        self._init_argos()

    def _init_argos(self):
        """Initialize argos-translate with en->pt model."""
        try:
            import argostranslate.package
            import argostranslate.translate

            # Check if en->pt is installed
            installed = argostranslate.translate.get_installed_languages()
            en = next((l for l in installed if l.code == "en"), None)
            pt = next((l for l in installed if l.code == "pt"), None)

            if en and pt:
                self._argos_translator = en.get_translation(pt)
                self._argos_available = True
                return

            # Try to install en->pt package
            argostranslate.package.update_package_index()
            available = argostranslate.package.get_available_packages()
            pkg = next((p for p in available if p.from_code == "en" and p.to_code == "pt"), None)
            if pkg:
                print("  Baixando modelo de traducao en->pt (~100MB)...")
                argostranslate.package.install_from_path(pkg.download())
                installed = argostranslate.translate.get_installed_languages()
                en = next((l for l in installed if l.code == "en"), None)
                pt = next((l for l in installed if l.code == "pt"), None)
                if en and pt:
                    self._argos_translator = en.get_translation(pt)
                    self._argos_available = True

        except ImportError:
            pass
        except Exception as e:
            print(f"  [AVISO] argos-translate nao disponivel: {e}")

    def translate(self, text: str) -> str:
        """Translate clinical English text to Portuguese.

        Pipeline:
        1. Replace medical terms with tokens
        2. Neural translate the clean text
        3. Restore medical terms with PT translations
        """
        if not text or not text.strip():
            return text

        # Step 1: Tokenize medical terms
        tokens = {}
        processed = text
        token_id = 0

        for term_en, term_pt in _SORTED_TERMS:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(term_en), re.IGNORECASE)
            matches = list(pattern.finditer(processed))
            for match in reversed(matches):  # reverse to preserve positions
                token = f"XMED{token_id:03d}X"
                tokens[token] = term_pt
                processed = processed[:match.start()] + token + processed[match.end():]
                token_id += 1

        # Step 2: Neural translation (if available)
        if self._argos_available and self._argos_translator:
            try:
                translated = self._argos_translator.translate(processed)
            except Exception:
                translated = processed
        else:
            # Fallback: just return with medical terms translated
            translated = processed

        # Step 3: Restore medical terms — try exact and fuzzy (argos may add spaces)
        for token, term_pt in tokens.items():
            # Exact match
            if token in translated:
                translated = translated.replace(token, term_pt)
            else:
                # Fuzzy: argos may insert spaces around token
                fuzzy = re.compile(r'\s*'.join(list(token)), re.IGNORECASE)
                translated = fuzzy.sub(term_pt, translated, count=1)

        return translated

    def translate_batch(self, texts: list) -> list:
        """Translate a list of texts."""
        return [self.translate(t) for t in texts]

    @property
    def is_neural_available(self) -> bool:
        return self._argos_available


# Singleton
_translator = None

def get_translator() -> MedicalTranslator:
    global _translator
    if _translator is None:
        _translator = MedicalTranslator()
    return _translator


def translate_medical(text: str) -> str:
    """Convenience function to translate a single medical text."""
    return get_translator().translate(text)
