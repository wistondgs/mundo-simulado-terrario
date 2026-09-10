# Theory Ingestion

The source directory is external to Terrario. `build_theory_snapshot.py` copies
only structured derived artifacts into a content-addressed working snapshot.
Original files are never edited. The manifest records filename, SHA-256,
artifact version/type, original path, parser version and ingestion status.

CSV rows and Markdown tables retain their complete source fields and original
text. PDFs are outside the boundary. RAW concepts remain records even when a
canonical candidate exists. Rebuild with:

```bash
.venv/bin/python scripts/build_theory_snapshot.py \
  --source "/home/wis/Documentos/teoria de la inteligencia"
```
