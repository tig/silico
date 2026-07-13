# scripts/

Thin wrappers around the **silico** CLI. Prefer:

```text
silico doctor
silico wait-device
silico inspect --port COMx
# only after operator confirms overwrite:
silico deploy firmware/version.py firmware/main.py --port COMx --yes --verify
```
