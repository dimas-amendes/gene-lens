<!-- Please write this PR in English. See CONTRIBUTING.md for details. -->

## What does this PR do?
Brief description of the changes.

## Related Issue
Closes #

## Type of Change
- [ ] Bug fix
- [ ] New feature / analysis panel
- [ ] Documentation update
- [ ] Refactoring (no behavior change)
- [ ] Translation / i18n

## Checklist

### Required
- [ ] I tested locally with `sample/sample_genome.csv`
- [ ] No real genetic data is included in this PR
- [ ] No API keys, tokens, or credentials are included
- [ ] I agree that my contributions are licensed under AGPLv3

### Language & Scope
- [ ] Does NOT introduce diagnostic wording ("you have", "you are at risk", "recommended dose", "you should take")
- [ ] Uses exploratory language ("associated with", "may indicate", "discuss with your physician")
- [ ] Maintains the educational/self-knowledge scope of the project

### For new analysis panels
- [ ] SNPs are well-validated in peer-reviewed literature (cite sources)
- [ ] Evidence quality is documented (replicated GWAS, clinical guideline, etc.)
- [ ] Added corresponding i18n strings in both PT-BR and EN
- [ ] Added SNPs to `sample/sample_genome.csv` for testing
- [ ] Follows the sex-aware routing pattern if condition is sex-dependent

### Privacy
- [ ] Does NOT modify `src/privacy.py` NetworkBlocker behavior
- [ ] Does NOT add external network calls during analysis
- [ ] Does NOT log or transmit genetic data

## How to Test
Steps for the maintainer to verify:
1.
2.
