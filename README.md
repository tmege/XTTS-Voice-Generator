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
xtts-env/bin/python3.11 xtts_app.py
```

### En double-clic (macOS .app)

Lancer `build_app.sh` pour générer le bundle :

```bash
bash build_app.sh
```

Ça crée `XTTS Voice Generator.app` — double-clic pour lancer. Glisser dans le Dock ou `/Applications` pour un accès rapide.

> **Note :** L'app utilise un launcher shell qui appelle directement `xtts-env/bin/python3.11` (pas PyInstaller). C'est beaucoup plus stable pour PyTorch/TTS sur macOS.

## Structure

```
.
├── xtts_app.py          # App principale (UI + backend TTS)
├── build_app.sh         # Génération du .app macOS (launcher)
├── xtts-env/            # Venv Python 3.11 (non versionné)
├── xtts_voices/         # Voix custom (fichiers audio de référence)
└── xtts_output/         # Fichiers .wav générés (par défaut)
```

## Known vulnerabilities

- **`torch.load(weights_only=False)`**: This app patches `torch.load` to disable the `weights_only` safety check at startup. This is required because XTTS v2 checkpoints rely on pickle-based serialization which is incompatible with `weights_only=True`. Loading a malicious model file could lead to arbitrary code execution. Only use trusted model sources.
- **`QThread.terminate()`**: The cancel button uses `QThread.terminate()` to stop generation, which is discouraged by Qt documentation as it can leave shared resources (mutexes, memory) in an inconsistent state. In practice this is low-risk since the thread only performs PyTorch inference, but it could theoretically cause instability.

## Notes

- Le patch `torch.load(weights_only=False)` est appliqué automatiquement au démarrage (requis par XTTS v2)
- Le premier lancement télécharge le modèle (~1.8 Go) dans `~/.local/share/tts/`
- La génération prend ~10-30s selon la longueur du texte (CPU)
