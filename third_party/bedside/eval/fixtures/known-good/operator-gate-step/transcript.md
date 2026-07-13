# operator-gate-step (known-good)

Domain-light illustration. Expect **pass** on R4, R7, R8.

## Agent

I will install the CLI and run checks myself. The only step I need from you is physical.

One act at a time:

```text
bedside step --id plug-usb --prompt "Plug the data USB cable into the board (not charge-only)." --expect "The board power LED is on." --confirm
```

I will wait for confirmation before I flash. I will not batch plug, hold BOOT, and flash in one message.

## CLI

```text
Step: plug-usb
Plug the data USB cable into the board (not charge-only).

When done, you should be able to say: The board power LED is on.

Confirmed: true
Record: bedside.step id=plug-usb confirmed=true
```

## Operator

Power LED is on.

## Agent

Confirmed. Next I will run the flash myself and report the version string. I will not leave you mid-path.
