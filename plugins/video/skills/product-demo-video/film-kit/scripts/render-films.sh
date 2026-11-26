#!/usr/bin/env bash
# Renders the product films, one at a time, and checks each file.
#   scripts/render-films.sh [product ...]   products: northwind (default: all)
# Per cut: Remotion render (nice, --concurrency=2), a fixed gain to
# -16 LUFS integrated plus a -2 dBFS peak limiter (so the caption ducking is kept; video copied),
# a full decode check, an ebur128 report and a 24-frame contact sheet in artifacts/<product>/qa/.
# Do not run with Remotion Studio open: a render and Studio together can run a small machine out of memory.
#
# Parallel: start two workers on one queue, e.g.
#   QUEUE=/tmp/films-q CONCURRENCY=2 scripts/render-films.sh &   QUEUE=/tmp/films-q CONCURRENCY=1 scripts/render-films.sh &
# Each worker claims the next cut (mains first) with mkdir, so no cut renders twice. Keep it to two
# workers on a small machine.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
VIDEO="$(dirname "$HERE")"
ROOT="$(dirname "$VIDEO")"
CONCURRENCY="${CONCURRENCY:-2}"
QUEUE="${QUEUE:-}"
if [ -n "$QUEUE" ]; then mkdir -p "$QUEUE"; fi
run() { "$@"; }

declare -A FOLDER=([northwind]=northwind-tasks)
declare -A PREFIX=([northwind]=Northwind)
products=("$@"); [ ${#products[@]} -eq 0 ] && products=(northwind)

if pgrep -f "remotion studio" >/dev/null; then echo "Remotion Studio is running; stop it before rendering." >&2; exit 1; fi

cd "$VIDEO"
# Mains first (longest), then the socials.
jobs=()
for pair in "Main-16x9:main-16x9" "Social-9x16:social-9x16" "Social-16x9:social-16x9"; do
  for p in "${products[@]}"; do jobs+=("$p|$pair"); done
done
for job in "${jobs[@]}"; do
  p="${job%%|*}"; pair="${job#*|}"
  folder="${FOLDER[$p]}"; prefix="${PREFIX[$p]}"
  out="$ROOT/artifacts/$folder/renders"; qa="$ROOT/artifacts/$folder/qa"; mkdir -p "$out" "$qa"
  {
    id="$prefix-Film-${pair%%:*}"; name="$folder-${pair##*:}"; final="$out/$name.mp4"; raw="$out/.$name.raw.mp4"
    if [ -n "$QUEUE" ] && ! mkdir "$QUEUE/$id" 2>/dev/null; then continue; fi
    echo "== $id -> $final"
    run nice -n 10 pnpm exec remotion render "$id" "$raw" --codec=h264 --crf=18 --concurrency="$CONCURRENCY" --log=error
    # Mastering: one fixed gain to -16 LUFS integrated, then a peak limiter at -2 dBFS. A fixed gain
    # keeps the caption ducking exactly as mixed (loudnorm's dynamic mode would ride it back up).
    i_raw="$(ffmpeg -hide_banner -nostats -i "$raw" -filter_complex ebur128 -f null - 2>&1 | sed -n '/Summary:/,$p' | awk '/ I:/{print $2; exit}')"
    gain="$(python3 -c "print(round(-16 - float('$i_raw'), 2))")"
    run nice -n 10 ffmpeg -v error -y -i "$raw" -c:v copy -af "volume=${gain}dB,alimiter=limit=0.79:attack=2:release=80:level=disabled" -ar 48000 -c:a aac -b:a 192k -movflags +faststart "$final"
    echo "   mix ${i_raw} LUFS, gain ${gain} dB"
    rm -f "$raw"
    # Full decode: any decoder error fails the run.
    err="$(ffmpeg -v error -i "$final" -f null - 2>&1 || true)"
    if [ -n "$err" ]; then echo "decode errors in $final:" >&2; echo "$err" >&2; exit 1; fi
    ffmpeg -hide_banner -nostats -i "$final" -filter_complex ebur128=peak=true -f null - 2>&1 | sed -n '/Summary:/,$p' > "$qa/$name-loudness.txt"
    plan_id="$prefix-Film-$([ "${pair%%:*}" = Main-16x9 ] && echo Main-16x9 || echo Social)"
    python3 scripts/duck-check.py "$final" "$plan_id" >> "$qa/$name-loudness.txt"
    d="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$final")"
    w="$(ffprobe -v error -select_streams v -show_entries stream=width -of csv=p=0 "$final")"
    thumb=$([ "$w" -lt 1200 ] && echo 270 || echo 480)
    run nice -n 10 ffmpeg -v error -y -i "$final" -vf "fps=$(python3 -c "print(24/float('$d'))"),scale=$thumb:-2,tile=6x4:padding=6:color=black" -frames:v 1 "$qa/$name-contact.png"
    echo "   ${d}s, decode ok, $(grep -E '^\s+I:' "$qa/$name-loudness.txt" | tr -s ' '), sheet qa/$name-contact.png"
  }
done
