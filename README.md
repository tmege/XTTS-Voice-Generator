# XTTS Voice Generator

App desktop macOS pour générer de l'audio avec clonage de voix via [XTTS v2](https://github.com/coqui-ai/TTS) (Coqui TTS).

## Fonctionnalités

- Synthèse vocale multilangue (fr, en, es, de, it, pt, etc.)
- 58 voix intégrées XTTS v2 sélectionnables dans un dropdown
- Clonage de voix à partir d'un fichier audio externe (.wav, .mp3)
- Lecture directe du fichier généré dans l'app
- Choix du dossier et nom de fichier de sortie
- Interface PyQt5, génération en arrière-plan (QThread)

## Architecture cible

Développé et testé sur **Mac Apple Silicon (M4)**. XTTS v2 et ses dépendances (PyTorch, Coqui TTS) ne sont pas nativement optimisés pour ARM / Apple Silicon, ce qui a nécessité plusieurs adaptations :

- **Python 3.11** obligatoire (certaines dépendances de Coqui TTS ne compilent pas sur 3.12+ avec ARM)
- **Patch `torch.load`** : PyTorch récent impose `weights_only=True` par défaut, ce qui casse le chargement des checkpoints XTTS v2 — on force `weights_only=False` au démarrage
- **Pas de CUDA** : la génération tourne sur CPU (MPS partiellement supporté mais instable avec XTTS) — compter ~10-30s par génération
- Les wheels PyTorch ARM64 sont utilisées automatiquement via pip, pas besoin de build custom

> Sur architecture Intel x86, ces adaptations restent compatibles mais le patch `torch.load` est le seul réellement nécessaire.

## Prérequis

- macOS 11+ (testé sur macOS 15 / Apple M4)
- Python 3.11 (pas 3.12+, incompatible avec certaines dépendances Coqui TTS)
- ~5 Go d'espace disque (modèle XTTS v2 + dépendances)

## Installation

```bash
# Créer le venv (Python 3.11 requis)
python3.11 -m venv xtts-env
source xtts-env/bin/activate

# Installer les dépendances
pip install TTS PyQt5

# Le modèle XTTS v2 se télécharge automatiquement au premier lancement (~1.8 Go)
```

## Utilisation

### Depuis le terminal

```bash
source xtts-env/bin/activate
python3 xtts_app.py
```

### En double-clic (macOS .app)

Lancer `build_app.sh` pour générer le bundle :

```bash
bash build_app.sh
```

Ça crée `XTTS Voice Generator.app` — double-clic pour lancer. Glisser dans le Dock ou `/Applications` pour un accès rapide.

## Structure

```
.
├── xtts_app.py          # App principale (UI + backend TTS)
├── build_app.sh         # Génération du .app macOS
├── xtts-env/            # Venv Python (non versionné)
└── xtts_output/         # Fichiers .wav générés (par défaut)
```

## Notes

- Le patch `torch.load(weights_only=False)` est appliqué automatiquement au démarrage (requis par XTTS v2)
- Le premier lancement télécharge le modèle (~1.8 Go) dans `~/.local/share/tts/`
- La génération prend ~10-30s selon la longueur du texte (CPU)
