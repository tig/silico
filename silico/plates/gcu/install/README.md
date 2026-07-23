# Install / update

1. Host gate green: `python -m pytest -q`
2. Agent/operator: `silico doctor` then `silico inspect --port COMx`
3. Confirm device identity with the operator
4. **Only after the operator confirms** writing the board:

```text
silico deploy firmware/version.py firmware/main.py --port COMx --yes --verify --expect-name GCU --expect-version 0.0.1
```

Replace names/versions with the product `firmware/version.py`. Always pass explicit `--port`.

**Good on metal (XIAO RP2040):** user **green** LED blinks (~0.25 s). That is not the red power LED (always on). Green is active-low on GPIO16.
