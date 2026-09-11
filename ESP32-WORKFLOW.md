# CognoSpace Flasher — ESP32 workflow

Everything you need to go from an Arduino sketch on your laptop to an activity
a student can flash from the website.

---

## Part 1 — What to install (once per machine)

### On your machine (the one that builds firmware)

| # | Install | Why | Where |
|---|---|---|---|
| 1 | **Arduino IDE 2.x** | Compiles the sketch | arduino.cc/en/software |
| 2 | **ESP32 board package** | Adds ESP32 targets to the IDE | See below |
| 3 | **Python 3** | Needed for esptool | python.org (tick "Add to PATH" on Windows) |
| 4 | **esptool** | Merges the four ESP32 binaries into one file | `pip install esptool` |
| 5 | **Git** | Pushes to GitHub, which triggers Vercel | git-scm.com |
| 6 | **USB driver** | CH340 or CP2102, depending on your board | See step 1.3 |

### 1.1 Add the ESP32 board package

1. Arduino IDE → **File ▸ Preferences**
2. In *Additional Boards Manager URLs*, paste:
   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```
3. **Tools ▸ Board ▸ Boards Manager**, search `esp32`, install **esp32 by Espressif Systems**.
4. Restart the IDE. You now have ESP32 Dev Module, ESP32S3 Dev Module, and the rest.

### 1.2 Install esptool

```bash
pip install esptool
esptool version          # confirm it runs
```

On esptool 5.x the commands use hyphens (`merge-bin`); on 4.x they use underscores
(`merge_bin`). Check which you have with `esptool version` and use the matching form below.

### 1.3 USB driver

Look at the small chip next to the USB port on your board:

- **CH340 / CH9102** → download the CH34x driver from wch-ic.com
- **CP2102** → download the CP210x VCP driver from silabs.com
- **ESP32-S3 with native USB** → no driver needed

This driver has to be on **every lab computer**, not just yours. It is the one install
students' machines still need — the browser handles everything after that. Do it once
per machine when you set up the lab.

---

## Part 2 — Turning a sketch into a flashable `.bin`

### 2.1 Compile and export

1. Open your sketch in the Arduino IDE.
2. **Tools ▸ Board** → pick the exact board (ESP32 Dev Module, ESP32S3 Dev Module, …).
3. **Tools ▸ Partition Scheme** → note what it is set to. Keep it the same across
   rebuilds of the same activity, or the merged file will not line up.
4. **Sketch ▸ Export Compiled Binary** (`Ctrl + Alt + S`).

The IDE writes a `build/` folder inside your sketch folder:

```
MySketch/
├── MySketch.ino
└── build/esp32.esp32.esp32/
    ├── MySketch.ino.bin              ← your program
    ├── MySketch.ino.bootloader.bin   ← bootloader
    ├── MySketch.ino.partitions.bin   ← partition table
    └── MySketch.ino.map
```

### 2.2 Choose one of two approaches

**Approach A — merged file (recommended for classrooms)**

One file, flashed at `0x0`, contains everything. It works on a brand-new board, on a board
that was running something else, and on a board with a different partition scheme. Nothing
to get wrong at flash time.

**Approach B — app only**

Ship just `MySketch.ino.bin` at `0x10000`. Smaller and faster, but it only works if the board
already has a matching bootloader and partition table on it. Fine for re-flashing the same
set of school boards; risky on a board straight out of the box.

Use A unless you have a reason not to.

### 2.3 Making the merged file

You need one more file from the ESP32 core, `boot_app0.bin`. Find it at:

- **Windows** `C:\Users\<you>\AppData\Local\Arduino15\packages\esp32\hardware\esp32\<version>\tools\partitions\boot_app0.bin`
- **macOS** `~/Library/Arduino15/packages/esp32/hardware/esp32/<version>/tools/partitions/boot_app0.bin`
- **Linux** `~/.arduino15/packages/esp32/hardware/esp32/<version>/tools/partitions/boot_app0.bin`

Copy it somewhere convenient — you will reuse the same file for every build.

Then, from inside the `build/esp32.esp32.esp32/` folder:

```bash
esptool --chip esp32 merge_bin -o firmware.bin \
  --flash_mode dio --flash_freq 40m --flash_size 4MB \
  0x1000  MySketch.ino.bootloader.bin \
  0x8000  MySketch.ino.partitions.bin \
  0xe000  boot_app0.bin \
  0x10000 MySketch.ino.bin
```

That produces a single `firmware.bin` that flashes at offset `0x0`.

### 2.4 Offsets differ by chip

The bootloader does **not** sit at `0x1000` on every ESP32. Get this wrong and the board
will not boot.

| Chip | `--chip` flag | Bootloader offset | Partitions | boot_app0 | App |
|---|---|---|---|---|---|
| ESP32 | `esp32` | `0x1000` | `0x8000` | `0xe000` | `0x10000` |
| ESP32-S2 | `esp32s2` | `0x1000` | `0x8000` | `0xe000` | `0x10000` |
| ESP32-S3 | `esp32s3` | **`0x0`** | `0x8000` | `0xe000` | `0x10000` |
| ESP32-C3 | `esp32c3` | **`0x0`** | `0x8000` | `0xe000` | `0x10000` |
| ESP32-C6 | `esp32c6` | **`0x0`** | `0x8000` | `0xe000` | `0x10000` |
| ESP8266 | `esp8266` | — single file — | | | `0x0` |

The merged output always flashes at `0x0`, whichever chip it was built for.

### 2.5 A script to save you the typing

Save this as `build.sh` in the repo root and run it from inside a `build/` folder:

```bash
#!/usr/bin/env bash
# usage: ./build.sh <chip> <sketch-name> <boot_app0-path>
# example: ./build.sh esp32 LineFollower ~/esp32-tools/boot_app0.bin
set -e
CHIP=${1:-esp32}
NAME=$2
BOOTAPP=$3

case "$CHIP" in
  esp32|esp32s2) BLOFF=0x1000 ;;
  *)             BLOFF=0x0    ;;
esac

esptool --chip "$CHIP" merge_bin -o firmware.bin \
  --flash_mode dio --flash_freq 40m --flash_size 4MB \
  $BLOFF  "${NAME}.ino.bootloader.bin" \
  0x8000  "${NAME}.ino.partitions.bin" \
  0xe000  "$BOOTAPP" \
  0x10000 "${NAME}.ino.bin"

echo "Wrote firmware.bin — flash this at 0x0"
```

Make it executable once: `chmod +x build.sh`.

---

## Part 3 — Folder structure and how to keep it tidy

### 3.1 The shape

```
cognospace-flasher/
├── index.html                    everything: page, styles, script, catalogue
├── vercel.json
├── build.sh
├── assets/
│   └── cognospace-logo.png
└── firmware/
    ├── grade-05/
    │   └── CS-G05-A01/
    │       ├── firmware.hex
    │       ├── source.ino        the sketch that produced it
    │       └── notes.md          wiring, pins, what to expect
    ├── grade-06/
    ├── grade-07/
    │   └── CS-G07-A02/
    │       ├── firmware.bin
    │       ├── source.ino
    │       └── notes.md
    ├── grade-08/
    ├── grade-09/
    └── grade-10/
```

### 3.2 The four rules that keep it from rotting

**One folder per activity, named after the code.** The folder name, the `code` in the
catalogue, and the code on the student worksheet are always the same string. If you can
read the folder name you know exactly which activity it is, without opening anything.

**The binary is always called `firmware.bin` or `firmware.hex`.** Identity lives in the
folder name, not the filename. This means every catalogue path looks the same shape and
you never mistype one.

**Keep `source.ino` next to the binary.** A `.bin` is not readable. Six months from now,
when a student asks why the robot turns left too early, you want the sketch that produced
that exact binary sitting right there. This is the single habit that saves the most time.

**Codes are permanent.** Once a code is printed on a worksheet it never changes meaning.
Rebuilt the firmware? Bump `version` in the catalogue. Activity moved to a different grade?
Retire the old code and issue a new one — do not reuse it.

### 3.3 The code format

```
CS - G07 - A02
│    │     └─ activity number within that grade, two digits
│    └─────── grade, two digits
└──────────── organisation prefix
```

Keep a simple rule for numbering: activities are numbered in the order they are taught,
and gaps are fine. If A03 is retired, A04 stays A04. Do not renumber.

### 3.4 What `notes.md` should hold

Two minutes of writing here saves a lab session later:

```markdown
# CS-G07-A02 — Line Follower

Board: ESP32 Dev Module
Partition scheme: Default 4MB with spiffs

## Wiring
IR left   -> GPIO 34
IR right  -> GPIO 35
L298N IN1 -> GPIO 26
...

## Expected behaviour
Both IR LEDs light. Robot follows a 2cm black line on white.
Serial at 115200 prints the raw sensor pair ten times a second.

## Known gotchas
GPIO 34/35 are input-only — do not move the IR sensors to other pins
without checking.
```

---

## Part 4 — Adding an ESP32 activity, end to end

Say you are adding **Servo Dial** as activity 3 of grade 7.

**Step 1 — Compile**

Arduino IDE, board set, **Sketch ▸ Export Compiled Binary**.

**Step 2 — Merge**

```bash
cd ~/Arduino/ServoDial/build/esp32.esp32.esp32
~/cognospace-flasher/build.sh esp32 ServoDial ~/esp32-tools/boot_app0.bin
```

**Step 3 — Make the folder and move the files in**

```bash
cd ~/cognospace-flasher
mkdir -p firmware/grade-07/CS-G07-A03
cp ~/Arduino/ServoDial/build/esp32.esp32.esp32/firmware.bin firmware/grade-07/CS-G07-A03/
cp ~/Arduino/ServoDial/ServoDial.ino firmware/grade-07/CS-G07-A03/source.ino
```

Write `notes.md` while the wiring is still fresh in your head.

**Step 4 — Add one entry to the catalogue**

Open `index.html`, scroll to the `<script type="application/json" id="catalog">` block,
find grade 7, and add to its `activities` array:

```json
{
  "code": "CS-G07-A03",
  "name": "Servo Dial",
  "category": "Actuators",
  "board": "esp32",
  "version": "1.0.0",
  "description": "A potentiometer drives a servo through 0 to 180 degrees.",
  "components": ["SG90 servo", "10k potentiometer"],
  "parts": [
    { "file": "/firmware/grade-07/CS-G07-A03/firmware.bin", "offset": "0x0" }
  ]
}
```

Note the offset is `0x0` because it is a merged file. If you went with app-only, use
`0x10000` and point at `MySketch.ino.bin`.

Watch the commas — a stray or missing one makes the whole catalogue fail to parse, and
the shelf will come up empty. Paste the block into jsonlint.com if you are unsure.

**Step 5 — Test it locally before pushing**

```bash
cd ~/cognospace-flasher
npx serve .
```

Open `http://localhost:3000`, connect a real board, flash it. Web Serial refuses to run
from a `file://` URL, so opening the HTML directly will not work.

**Step 6 — Push**

```bash
git add firmware/grade-07/CS-G07-A03 index.html
git commit -m "Add CS-G07-A03 Servo Dial"
git push
```

Vercel rebuilds in about twenty seconds. The firmware and the page are served with
`must-revalidate`, so students get the new build without a hard refresh.

---

## Part 5 — Adding a new grade

Append to the `grades` array in the catalogue block:

```json
{
  "grade": 11,
  "title": "Capstone Builds",
  "activities": []
}
```

Then `mkdir -p firmware/grade-11`. The grade rail, the filters, the counts on the landing
page and the search all regenerate from that one block — nothing else to edit.

---

## Part 6 — Before a lab session

- [ ] CH340 / CP2102 driver installed on every machine in the room
- [ ] Chrome or Edge on every machine (Firefox and Safari cannot flash)
- [ ] The site opens over HTTPS, not a local file
- [ ] You have flashed the activity onto one board yourself, today
- [ ] The activity code is written on the board or the worksheet

---

## Troubleshooting

**"No board connected" and the port list is empty**
The USB driver is missing, or the cable is charge-only. Swap the cable first — it is the
cause more often than the driver.

**Connects, then fails partway through writing**
Hold the BOOT button while pressing Connect on boards without auto-reset circuitry. Some
cheap ESP32 clones need this. Also try a shorter cable; long cables drop packets at 921600.

**Flashes fine but the board does nothing afterwards**
Almost always the wrong bootloader offset for the chip. Check the table in 2.4 — S3, C3
and C6 use `0x0`, not `0x1000`.

**The shelf is empty and the console says the catalogue did not load**
JSON syntax error in the catalogue block. Check for a trailing comma after the last item
in an array.

**A board that worked last term will not take a merged file**
Tick "Erase the whole flash first" in the flasher, then try again. This clears leftover
partition data from whatever it was running before.
