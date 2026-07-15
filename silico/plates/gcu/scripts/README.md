# scripts/

Thin wrappers around the **silico** CLI. Prefer:

```text
silico doctor
silico wait-device
silico inspect --port COMx
# only after operator confirms overwrite:
silico deploy --port COMx --yes --verify   # no file args: uses silico.toml [deploy].core, cannot drift from the manifest (tig/silico#47)
```
