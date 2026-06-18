#!/usr/bin/env bash
input=$(cat)

# ANSI codes
RESET=$'\033[0m'
REV=$'\033[7m'
YELLOW=$'\033[33m'
CYAN=$'\033[36m'
PURPLE=$'\033[35m'
GREEN=$'\033[32m'
RED=$'\033[31m'

# Reverse-video block: set color first, then reverse → color becomes background
# Usage: rev_block "$COLOR" "$text"
rev_block() {
  printf '%s%s %s %s' "$1" "$REV" "$2" "$RESET"
}

# Pick color by percentage threshold
pct_color() {
  local rounded
  rounded=$(printf '%.0f' "$1")
  if   [ "$rounded" -le 40 ]; then printf '%s' "$GREEN"
  elif [ "$rounded" -le 75 ]; then printf '%s' "$YELLOW"
  else                              printf '%s' "$RED"
  fi
}

project_dir=$(echo "$input" | jq -r '.workspace.project_dir // .workspace.current_dir' | sed "s|^$HOME|~|")
git_worktree=$(echo "$input" | jq -r '.workspace.git_worktree // .worktree.branch // empty')
if [ -z "$git_worktree" ]; then
  git_worktree=$(git -C "$(echo "$input" | jq -r '.workspace.project_dir // .workspace.current_dir')" branch --show-current 2>/dev/null || true)
fi
model=$(echo "$input" | jq -r '.model.display_name')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
five_hour=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
seven_day=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

SEP=" "

# Project dir — yellow reverse block
output="$(rev_block "$YELLOW" "⌂ ${project_dir}")"

# Git branch — cyan reverse block
if [ -n "$git_worktree" ]; then
  output="${output}${SEP}$(rev_block "$CYAN" "⎇ ${git_worktree}")"
fi

# Model — purple reverse block
output="${output}${SEP}$(rev_block "$PURPLE" "✦ ${model}")"

# Usage: CXxx% SNxx% WKxx% — uppercase labels, value colored by threshold
usage_part=""

if [ -n "$used_pct" ]; then
  c_val=$(printf '%.0f' "$used_pct")
  c_color=$(pct_color "$used_pct")
  usage_part="CX${c_color}${c_val}%${RESET}"
fi

if [ -n "$five_hour" ]; then
  s_val=$(printf '%.0f' "$five_hour")
  s_color=$(pct_color "$five_hour")
  s_str="SN${s_color}${s_val}%${RESET}"
  usage_part="${usage_part:+${usage_part} }${s_str}"
fi

if [ -n "$seven_day" ]; then
  w_val=$(printf '%.0f' "$seven_day")
  w_color=$(pct_color "$seven_day")
  w_str="WK${w_color}${w_val}%${RESET}"
  usage_part="${usage_part:+${usage_part} }${w_str}"
fi

if [ -n "$usage_part" ]; then
  output="${output}${SEP}${usage_part}"
fi

echo -e "${output}"
