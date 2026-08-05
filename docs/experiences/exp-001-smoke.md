# EXP-001 — smoke test local avec Ollama

Cette tranche branche le protocole EXP-001 sur un premier provider réel sans modifier le protocole pré-enregistré.

## Pré-requis

- Python 3.12+
- Ollama lancé localement sur `127.0.0.1:11434`
- un modèle déjà téléchargé

Aucune dépendance HTTP Python supplémentaire n'est nécessaire : le provider utilise la bibliothèque standard.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

## Premier smoke test

Commencer petit avant les 100 instances du protocole :

```bash
python scripts/run_exp001_smoke.py \
  --model qwen3:4b \
  --size 10 \
  --seed 1001 \
  --output results/exp001-smoke-10.jsonl
```

Puis, si l'exécution et le JSONL sont corrects :

```bash
python scripts/run_exp001_smoke.py \
  --model qwen3:4b \
  --size 100 \
  --seed 1001 \
  --output results/exp001-smoke-100.jsonl
```

Le modèle est volontairement un paramètre : aucun modèle particulier ne fait partie de l'hypothèse EXP-001.

## Ce que produit le runner

Pour chaque instance, le JSONL conserve notamment :

- les paramètres `(a,b,k,m)` ;
- la production primaire ;
- son exactitude, calculée uniquement à la frontière d'évaluation ;
- les trois répétitions et `score_R` ;
- les trois vues structurées ;
- le syndrome `[z_comm, z_offset, z_scale]` ;
- `score_E` ;
- les textes bruts, tokens et latences remontés par Ollama.

Le runner effectue 7 générations par instance : une production primaire partagée, trois répétitions pour R et trois vues pour E. Les deux détecteurs ont donc chacun le budget pré-enregistré de quatre productions en comptant la primaire commune.

## Important

Ce smoke test sert à vérifier le câblage réel, le parsing, le taux d'erreur obtenu et la qualité des traces. Il **ne constitue pas l'évaluation principale de H1**.

Si le taux d'erreur primaire est hors de la bande pilote prévue (5–40 %), on ajuste la difficulté sur un jeu pilote distinct avant de geler la configuration d'évaluation.
