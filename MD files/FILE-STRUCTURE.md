 # Coggy Flasher — file structure
Coggy flasher designed and developed by cognospace

Everything is served as static files from one folder. No build step, no server
code. It must be served over **HTTPS or localhost**, because Web Serial refuses
to run anywhere else.

## Top level

```
coggy-flasher/
├── index.html                  the whole app — markup, styles, catalogue, logic
├── assets/                     logos and icons
├── vendor/
│   └── esptool-js/
│       └── bundle.js           the flasher library, self-hosted
└── firmware/                   one folder per grade
```

## assets/

All five are referenced by name in `index.html`; a missing one shows a broken
image rather than breaking the page.

```
assets/
├── favicon-32.png              32×32   browser tab
├── coggy-icon.png              512×512 PWA / large favicon
├── coggy-icon-180.png          180×180 iOS home screen
├── cognospace-logo.png         header logo, light theme
└── cognospace-logo-dark.png    header logo, dark theme
```

## vendor/

```
vendor/
└── esptool-js/
    └── bundle.js
```

Get it with:

```bash
npm pack esptool-js@0.5.4
tar -xzf esptool-js-0.5.4.tgz
mkdir -p vendor/esptool-js
cp package/bundle.js vendor/esptool-js/bundle.js
```

If this file is absent the page still works — it falls back to jsdelivr, unpkg
and esm.sh — but you keep the slow first connect on a school network. Keep
`ESPTOOL_VERSION` in `index.html` matched to whatever you vendor here.

## firmware/

The path template lives in the catalogue block inside `index.html`:

```
/firmware/grade-{NN}/{CODE}/{table}/firmware.bin
```

`{table}` is substituted at flash time with the bench the teacher picked. All 86
activities are per-table, and all flash to offset **`0x0`** — so each
`firmware.bin` must be a **merged** image (bootloader + partition table +
app), not a bare application binary. See "Building the binaries" below.

```
firmware/
├── grade-03/                   Mechatronics · 10 activities
│   ├── CS-G03-A01/
│   │   ├── T1/firmware.bin
│   │   ├── T2/firmware.bin
│   │   ├── …
│   │   └── T15/firmware.bin
│   ├── CS-G03-A02/  … CS-G03-A05/
│   └── CS-G03-AI01/ … CS-G03-AI05/
├── grade-04/                   Mechatronics · 10
├── grade-05/                   Mechatronics · 10
├── grade-06/                   Mechatronics & AI · 10
├── grade-07/                   Mechatronics & AI · 10
├── grade-08/                   Robotics & IoT/Automation, AI · 15
├── grade-09/                   Advanced Robotics & IoT/Automation, AI · 15
└── grade-resources/            Educator Resources · 6  (CS-ER-A01 … A06)
```

Note the folder for the last group is `grade-resources`, not a number — the
catalogue's grade key is the literal string `resources`.

Codes follow `CS-G{NN}-A{nn}` for hardware activities and `CS-G{NN}-AI{nn}` for
the AI ones. Educator resources use `CS-ER-A{nn}`.

### Tables

Fifteen benches, defined in the `TABLES` list near the top of the script:

| | | | | |
|---|---|---|---|---|
| T1 Pi | T2 Newton | T3 Kalam | T4 Euler | T5 Einstein |
| T6 Hawking | T7 Curie | T8 Tesla | T9 Ramanujan | T10 Dhawan |
| T11 Bose | T12 Homi | T13 NA | T14 NA | T15 NA |

Rename freely — the `name` is cosmetic. The **`id` is the folder name on disk**
and must not change once builds exist. Delete a row to retire a bench; add one
with a matching folder to grow.

### Scale

86 activities × 15 tables = **1290** `firmware.bin` files at full coverage.
Nothing breaks with gaps: a missing file returns 404 and the flasher says which
folder is empty. Use "Check builds" in the app, or the script below, to see
what is outstanding.

## scaffold.py

Creates the whole tree and audits it. It parses the catalogue and `TABLES` out
of `index.html`, so it never drifts from the app.

```bash
python3 scaffold.py            # create every missing folder
python3 scaffold.py --check    # report only, create nothing
python3 scaffold.py --grade 8  # limit to one grade
```

Run it from the folder that holds `index.html`. Re-run it after adding an
activity or a bench.

## Building the binaries

Because the catalogue flashes everything at `0x0`, merge the three images
before copying them in. From an Arduino or ESP-IDF build:

```bash
esptool.py --chip esp32 merge_bin -o firmware.bin \
  --flash_mode dio --flash_freq 40m --flash_size 4MB \
  0x1000  bootloader.bin \
  0x8000  partitions.bin \
  0x10000 app.bin
```

The per-table difference is usually one constant in the sketch — a bench ID, a
Wi-Fi SSID, an MQTT topic — so a loop over the fifteen tables that recompiles
and drops the output into the right folder is worth writing once.

## Deploying

Any static host works. Whatever you use, make sure:

- `.bin` is served as a binary download, not as `text/html` on a 404 page — a
  soft-404 returning HTML will be flashed as firmware and brick the board.
  Nginx: `default_type application/octet-stream;` for `/firmware/`.
- No SPA catch-all rewrite over `/firmware/` — the flasher relies on a real 404
  to tell a teacher that a build is missing.
- HTTPS is on.

Builds are fetched with `cache: 'no-cache'`, so they revalidate and a fresh
upload is picked up on the next flash; an unchanged one comes back as a 304.
Serve `/firmware/` with ETags or Last-Modified so that actually works.
