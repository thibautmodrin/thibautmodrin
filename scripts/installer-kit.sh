#!/usr/bin/env bash
#
# Installe le kit de collaboration (AGENTS.md, règles, commandes, garde-fous) dans un autre dépôt.
#
#   ./scripts/installer-kit.sh /chemin/vers/projet             installe sans rien écraser
#   ./scripts/installer-kit.sh /chemin/vers/projet --dry-run   montre ce qui serait fait
#   ./scripts/installer-kit.sh /chemin/vers/projet --force     écrase, en gardant une copie .bak
#   ./scripts/installer-kit.sh /chemin/vers/projet --avec-docs installe aussi docs/assistant/
#
set -euo pipefail

SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CIBLE=""
DRY_RUN=0
FORCE=0
AVEC_DOCS=0

for argument in "$@"; do
  case "$argument" in
    --dry-run)   DRY_RUN=1 ;;
    --force)     FORCE=1 ;;
    --avec-docs) AVEC_DOCS=1 ;;
    -h|--help)   sed -n '3,8p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*)          echo "Option inconnue : $argument" >&2; exit 2 ;;
    *)           CIBLE="$argument" ;;
  esac
done

if [[ -z "$CIBLE" ]]; then
  echo "Usage : $0 /chemin/vers/projet [--dry-run] [--force] [--avec-docs]" >&2
  exit 2
fi

if [[ ! -d "$CIBLE" ]]; then
  echo "Cible introuvable : $CIBLE" >&2
  exit 1
fi

CIBLE="$(cd "$CIBLE" && pwd)"

if [[ "$CIBLE" == "$SOURCE" ]]; then
  echo "La cible est le dépôt source. Rien à faire." >&2
  exit 1
fi

if [[ ! -d "$CIBLE/.git" ]]; then
  echo "Attention : $CIBLE n'est pas un dépôt git. Les fichiers installés ne seront pas versionnés."
fi

installes=0
ignores=0
ecrases=0

# copier <chemin relatif source> <chemin relatif cible>
copier() {
  local relatif_source="$1"
  local relatif_cible="${2:-$1}"
  local origine="$SOURCE/$relatif_source"
  local destination="$CIBLE/$relatif_cible"

  if [[ ! -e "$origine" ]]; then
    echo "  absent du kit, ignoré : $relatif_source"
    return
  fi

  if [[ -e "$destination" ]]; then
    if [[ "$FORCE" -eq 0 ]]; then
      echo "  existe déjà, conservé : $relatif_cible"
      ignores=$((ignores + 1))
      return
    fi
    if [[ "$DRY_RUN" -eq 0 ]]; then
      cp -a "$destination" "$destination.bak"
    fi
    echo "  écrasé (copie dans $relatif_cible.bak) : $relatif_cible"
    ecrases=$((ecrases + 1))
  else
    echo "  installé : $relatif_cible"
    installes=$((installes + 1))
  fi

  if [[ "$DRY_RUN" -eq 0 ]]; then
    mkdir -p "$(dirname "$destination")"
    cp -a "$origine" "$destination"
  fi
}

echo "Kit  : $SOURCE"
echo "Cible: $CIBLE"
[[ "$DRY_RUN" -eq 1 ]] && echo "Mode : simulation, aucun fichier ne sera écrit"
echo

echo "Contrat et règles"
if [[ -e "$CIBLE/AGENTS.md" && "$FORCE" -eq 0 ]]; then
  # Un AGENTS.md existant peut contenir des consignes propres au projet : on le laisse en place et
  # on dépose le contrat à côté, à fusionner à la main.
  copier "AGENTS.md" "AGENTS.kit.md"
  echo "  AGENTS.md existant conservé — fusionner depuis AGENTS.kit.md, puis supprimer ce dernier"
else
  copier "AGENTS.md"
fi
copier ".cursor/rules"

echo "Commandes"
copier ".cursor/commands"

echo "Garde-fous"
copier ".cursor/hooks.json"
copier ".cursor/hooks/garde-actions.py"
copier ".cursor/permissions.json"
copier "docs/assistant/modeles/cursorignore" ".cursorignore"

if [[ "$AVEC_DOCS" -eq 1 ]]; then
  echo "Documentation"
  copier "docs/assistant"
fi

if [[ "$DRY_RUN" -eq 0 ]]; then
  chmod +x "$CIBLE/.cursor/hooks/garde-actions.py" 2>/dev/null || true

  # Le journal des décisions du garde-fou ne doit pas être versionné.
  if [[ -f "$CIBLE/.gitignore" ]] && ! grep -qF ".cursor/hooks/journal.log" "$CIBLE/.gitignore"; then
    printf '\n# Journal du garde-fou Cursor\n.cursor/hooks/journal.log\n' >> "$CIBLE/.gitignore"
    echo "  ajouté à .gitignore : .cursor/hooks/journal.log"
  fi
fi

echo
echo "Bilan : $installes installé(s), $ignores conservé(s), $ecrases écrasé(s)."
echo
echo "À faire à la main :"
echo "  1. Vérifier le garde-fou   : python3 .cursor/hooks/garde-actions.py --autotest"
echo "  2. Adapter le périmètre    : .cursor/rules/10-perimetre-competences.mdc"
echo "  3. Adapter les globs        : .cursor/rules/*.mdc, selon l'arborescence du projet"
echo "  4. Régler les approbations : Settings > Agents > Approvals & Execution (Auto-review)"
echo "  5. Recharger la fenêtre Cursor pour activer les hooks"

if [[ "$ignores" -gt 0 && "$FORCE" -eq 0 ]]; then
  echo
  echo "Des fichiers existants ont été conservés. Les comparer avant d'utiliser --force :"
  echo "  diff -ru $SOURCE/.cursor $CIBLE/.cursor"
fi
