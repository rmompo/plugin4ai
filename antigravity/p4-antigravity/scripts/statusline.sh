#!/usr/bin/env bash
# =============================================================================
# statusline.sh — p4-antigravity plugin
# Antigravity CLI custom statusline renderer.
#
# Receives JSON via stdin:
#   {
#     "cwd": "/path/to/project",
#     "conversation_id": "...",
#     "model": { "id": "...", "display_name": "Gemini 3.5 Flash" },
#     "product": "antigravity-cli",
#     "context_window": { "used_percentage": 42.5 },
#     "rate_limits": {
#       "five_hour": { "used_percentage": 10.0 },
#       "seven_day":  { "used_percentage": 88.0 }
#     }
#   }
#
# Output format:
#   " ⌂ ~/project "  " ⎇ main "  " ✦ Gemini 3.5 Flash "  CX12% SN5% WK88%
# =============================================================================

input=$(cat)

# -----------------------------------------------------------------------------
# ANSI escape helpers
# -----------------------------------------------------------------------------
RESET=$'\033[0m'

# Segment background colors — standard (non-bright) codes, same as p4-claudecode
YELLOW=$'\033[33m'    # Segment 1: directory
CYAN=$'\033[36m'      # Segment 2: git branch
PURPLE=$'\033[35m'    # Segment 3: model

# Percentage value colors
GREEN=$'\033[32m'
RED=$'\033[31m'

# -----------------------------------------------------------------------------
# seg_block COLOR TEXT
#   Renders a colored segment using reverse video, matching p4-claudecode style.
#   COLOR is a standard foreground code (30-37); reverse swaps it to background.
# -----------------------------------------------------------------------------
seg_block() {
  local color="$1"
  local text="$2"
  printf '%s%s %s %s' "$color" $'\033[7m' "$text" "$RESET"
}

# -----------------------------------------------------------------------------
# pct_color FLOAT
#   Prints the ANSI color code for a given usage percentage.
#   green  : x <= 50
#   yellow : 50 < x <= 75
#   red    : x > 75
# -----------------------------------------------------------------------------
pct_color() {
  local rounded
  rounded=$(printf '%.0f' "$1" 2>/dev/null) || rounded=0
  if   [ "$rounded" -le 40 ]; then printf '%s' "$GREEN"
  elif [ "$rounded" -le 75 ]; then printf '%s' "$YELLOW"
  else                              printf '%s' "$RED"
  fi
}

# -----------------------------------------------------------------------------
# Parse payload fields
# -----------------------------------------------------------------------------
# Use python3 for reliable JSON parsing (jq may not be available)
_py_get() {
  python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    keys = '$1'.split('.')
    val = d
    for k in keys:
        val = val[k]
    print(val if val is not None else '')
except:
    print('')
" <<< "$input" 2>/dev/null
}

cwd=$(_py_get "cwd")
model=$(_py_get "model.display_name")
used_pct=$(_py_get "context_window.used_percentage")
five_hour=$(_py_get "rate_limits.five_hour.used_percentage")
seven_day=$(_py_get "rate_limits.seven_day.used_percentage")

# Abbreviate home directory (portable: use sed to replace literal $HOME path)
_home="${HOME:-/root}"
project_dir=$(echo "$cwd" | sed "s|^${_home}|~|")

# Git branch (fallback to "no-git")
git_branch=$(git -C "$cwd" branch --show-current 2>/dev/null)
[ -z "$git_branch" ] && git_branch="no-git"

# Default model label if empty
[ -z "$model" ] && model="unknown"

SEP=" "

# -----------------------------------------------------------------------------
# Build output
# -----------------------------------------------------------------------------

# Segment 1: ⌂ pwd — yellow background
output="$(seg_block "$YELLOW" "⌂ ${project_dir}")"

# Segment 2: ⎇ branch — cyan background
output="${output}${SEP}$(seg_block "$CYAN" "⎇ ${git_branch}")"

# Segment 3: ✦ model — purple background
output="${output}${SEP}$(seg_block "$PURPLE" "✦ ${model}")"

# Segment 4: CXxx% SNxx% WKxx% — labels normal, values colored by threshold
# Each metric is only rendered if the CLI provides its value.
usage_part=""

if [ -n "$used_pct" ] && [ "$used_pct" != "None" ]; then
  c_val=$(printf '%.0f' "$used_pct")
  c_color=$(pct_color "$used_pct")
  usage_part="CX${c_color}${c_val}%${RESET}"
fi

if [ -n "$five_hour" ] && [ "$five_hour" != "None" ]; then
  s_val=$(printf '%.0f' "$five_hour")
  s_color=$(pct_color "$five_hour")
  s_str="SN${s_color}${s_val}%${RESET}"
  usage_part="${usage_part:+${usage_part} }${s_str}"
fi

if [ -n "$seven_day" ] && [ "$seven_day" != "None" ]; then
  w_val=$(printf '%.0f' "$seven_day")
  w_color=$(pct_color "$seven_day")
  w_str="WK${w_color}${w_val}%${RESET}"
  usage_part="${usage_part:+${usage_part} }${w_str}"
fi

if [ -n "$usage_part" ]; then
  output="${output}${SEP}${usage_part}"
fi

echo -e "${output}"
