# Labb Blocks

Official labb block collection (vendor: `lb`).

## Development

Start the block renderer:
```
poetry run labb block dev serve
```

Scaffold a new block:
```
poetry run labb block dev new crud/my-block
```

Validate all blocks:
```
poetry run labb block dev validate
```

Build the index:
```
poetry run labb block dev build
```

Refresh thumbnail baselines for both bundled themes:
```
poetry run python scripts/capture_thumbnails.py
```

Check the current previews against those baselines without overwriting them:
```
poetry run python scripts/capture_thumbnails.py --check
```
