#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-.}"
ENV_FILE="${TARGET_DIR}/.env"
LOCAL_FILE="${TARGET_DIR}/.env.local"

if [[ ! -f "${LOCAL_FILE}" ]]; then
  echo "Error: ${LOCAL_FILE} not found."
  echo "Create ${LOCAL_FILE} first, then re-run."
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${LOCAL_FILE}" "${ENV_FILE}"
  echo "Created ${ENV_FILE} from ${LOCAL_FILE}."
  exit 0
fi

tmp_file="$(mktemp)"

awk -v local_file="${LOCAL_FILE}" '
BEGIN {
  FS="="
  while ((getline line < local_file) > 0) {
    if (line ~ /^[[:space:]]*#/ || line ~ /^[[:space:]]*$/) {
      continue
    }
    split(line, parts, "=")
    key = parts[1]
    sub(/^[[:space:]]+/, "", key)
    sub(/[[:space:]]+$/, "", key)
    if (key != "") {
      keys[key] = line
      order[++count] = key
    }
  }
  close(local_file)
  in_block = 0
}
{
  if ($0 ~ /^# === synced from \.env\.local ===$/) {
    in_block = 1
    next
  }
  if (in_block) {
    if ($0 ~ /^# === end synced from \.env\.local ===$/) {
      in_block = 0
    }
    next
  }

  line = $0
  if (line ~ /^[[:space:]]*#/ || line ~ /^[[:space:]]*$/) {
    print line
    next
  }

  split(line, parts, "=")
  key = parts[1]
  sub(/^[[:space:]]+/, "", key)
  sub(/[[:space:]]+$/, "", key)

  if (key in keys) {
    print "# (replaced by .env.local) " line
    next
  }

  print line
}
END {
  print ""
  print "# === synced from .env.local ==="
  for (i = 1; i <= count; i++) {
    key = order[i]
    print keys[key]
  }
  print "# === end synced from .env.local ==="
}
' "${ENV_FILE}" > "${tmp_file}"

mv "${tmp_file}" "${ENV_FILE}"
echo "Updated ${ENV_FILE} using ${LOCAL_FILE}."
