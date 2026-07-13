# Install / update

1. Host gate green: `python -m pytest -q`
2. Agent/operator: `silico doctor` then `silico inspect`
3. **Only after you confirm** writing the board:

```text
silico deploy firmware/version.py firmware/main.py --port COMx --yes --verify --expect-name GCU --expect-version 0.0.1
```

Replace names/versions with your product `firmware/version.py`.
