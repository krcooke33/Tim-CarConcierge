#!/usr/bin/env bash
# resize-images.sh — Web-optimize source photos from img_original/ into img/.
#
# IMPORTANT: This script always runs `-auto-orient` BEFORE stripping metadata.
# Without that step, JPEGs with EXIF orientation flags (e.g. shot in portrait
# on a phone, or sideways/upside-down) silently render rotated in browsers
# once the EXIF tag is removed. That bug bit the Mercedes 450SL gallery photo
# (Task #13) and prompted Task #29 to formalize the pipeline.
#
# Behavior:
#   - Auto-orient (rotate pixels per EXIF Orientation tag), then strip metadata
#   - Resize to fit within MAX_DIM on the long side (no upscaling)
#   - Progressive JPEG, quality 82, Q chroma subsampling 4:2:0
#   - Idempotent: safe to re-run any time. Output overwrites in place.
#
# Sections processed:
#   - img_original/gallery/*.jpg      → img/gallery/        (max 1920px long side)
#   - img_original/inventory/*/*.jpg  → img/inventory/*/    (max 1920px long side)
#
# Hero and Tim portrait images are NOT auto-regenerated here because the
# served versions in img/hero/ and img/tim/ are not 1:1 derived from
# img_original/ (different sources, different aspect ratios — see Task #31
# for the home hero history). Re-add per-folder loops here only when an
# original is actually a 1:1 source for the served file.
#
# Usage:
#   ./scripts/resize-images.sh                       # process all
#   ./scripts/resize-images.sh gallery/foo.jpg ...   # process specific files

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_ROOT="${ROOT}/img_original"
DST_ROOT="${ROOT}/img"
MAX_DIM="${MAX_DIM:-1920}"
QUALITY="${QUALITY:-82}"

if ! command -v magick >/dev/null 2>&1; then
  echo "error: ImageMagick 'magick' is required but not on PATH" >&2
  exit 1
fi

resize_one() {
  local rel="$1"               # e.g. "gallery/mercedes-450sl.jpg"
  local src="${SRC_ROOT}/${rel}"
  local dst="${DST_ROOT}/${rel}"

  if [[ ! -f "$src" ]]; then
    echo "skip (no source): $rel"
    return 0
  fi

  mkdir -p "$(dirname "$dst")"

  # auto-orient FIRST, then strip, then resize, then re-encode
  magick "$src" \
    -auto-orient \
    -strip \
    -resize "${MAX_DIM}x${MAX_DIM}>" \
    -interlace Plane \
    -sampling-factor 4:2:0 \
    -quality "$QUALITY" \
    "$dst"

  local in_size out_size dims
  in_size=$(stat -c%s "$src")
  out_size=$(stat -c%s "$dst")
  dims=$(magick identify -format '%wx%h' "$dst")
  printf '  %-48s  %s  %s → %s bytes\n' "$rel" "$dims" "$in_size" "$out_size"
}

echo "Resizing into ${DST_ROOT} (max ${MAX_DIM}px, q${QUALITY})…"

if [[ $# -gt 0 ]]; then
  for rel in "$@"; do
    resize_one "$rel"
  done
  exit 0
fi

# Default: re-process gallery + inventory subdirs from canonical sources.
shopt -s nullglob
for src in "${SRC_ROOT}"/gallery/*.jpg "${SRC_ROOT}"/gallery/*.jpeg; do
  rel="${src#${SRC_ROOT}/}"
  resize_one "$rel"
done

for dir in "${SRC_ROOT}"/inventory/*/; do
  for src in "${dir}"*.jpg "${dir}"*.jpeg; do
    rel="${src#${SRC_ROOT}/}"
    resize_one "$rel"
  done
done

echo "Done."
