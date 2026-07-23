# Install / update (C plate)

Host gate:

```text
cmake -S host -B build/host
cmake --build build/host --target host_test
```

Deploy (after operator confirms board identity):

```text
silico deploy --port COMx --yes --verify
```

Requires ESP-IDF (`idf.py` or `IDF_PATH`). First flash and app update use the same image path.
