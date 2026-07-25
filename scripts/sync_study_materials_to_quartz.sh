#!/usr/bin/env bash
# Sync study_materials/ vault into quartz/content/ for website publishing.
# Run this after editing study_materials/ and before building the Quartz site.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT_DIR/study_materials"
DEST="$ROOT_DIR/quartz/content"

echo "Syncing study_materials -> quartz/content ..."
rm -rf "$DEST"
mkdir -p "$DEST"
cp -r "$SRC"/* "$DEST/"

# Create a homepage for the website if not present
if [ ! -f "$DEST/index.md" ]; then
  cat > "$DEST/index.md" <<'EOF'
---
title: InterruptLLM Study Curriculum
---

# Welcome

This is a beginner-friendly, step-by-step curriculum for understanding the paper **"InterruptLLM: A Preemptive Scheduling Framework for Low-Latency Multi-Tenant LLM Inference."**

Start here: [[00-curriculum-overview]]
EOF
fi

echo "Done. Files copied: $(find "$DEST" -type f | wc -l)"
