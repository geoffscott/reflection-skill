# reflection-skill Development

This folder contains development artifacts for the reflection-skill. It's separate from the skill's user-facing definition (../SKILL.md).

## Files

- **DEVELOPMENT.md** — Implementation guide and design decisions
- **import-script.sh** — Main script for importing journal entries from an existing vault

## Quick Start

### Test the Import Script

1. Make a test vault with a few sample markdown files:
   ```bash
   mkdir -p /tmp/test-vault
   echo "Morning thought" > /tmp/test-vault/2026-03-06.md
   echo "Evening reflection" > /tmp/test-vault/2026-03-05.md
   ```

2. Run the import script:
   ```bash
   ./import-script.sh /tmp/test-vault
   ```

3. Check the results:
   ```bash
   ls -la ../entries/
   cat ../entries/2026-03-06.md
   ```

### Run Against Your Full Vault

Once tested, point it at your actual vault:

```bash
./import-script.sh /path/to/your/vault
```

The script will:
1. Scan all .md files
2. Parse dates from filenames or file creation time
3. Create entries in `reflection/entries/`
4. Generate `reflection/metadata.json` with import summary

## Next Steps

- [ ] Test with sample files
- [ ] Run full import on your vault
- [ ] Verify entry structure and metadata
- [ ] Review summary report
- [ ] Build lens framework (Phase 2)
