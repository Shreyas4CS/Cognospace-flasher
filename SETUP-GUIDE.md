# Coggy Flasher — complete setup guide

From an empty machine to a working website with your firmware on it.
Written for Windows, with Mac and Linux paths noted where they differ.

Work through Parts 1 to 5 once. After that you only ever repeat Part 6.

---

# Part 1 — Install four things

### 1.1 Arduino IDE

Download from **arduino.cc/en/software**. Install with all defaults.

### 1.2 The ESP32 board package

The IDE does not know about ESP32 until you tell it.

1. Open the Arduino IDE.
2. **File ▸ Preferences**.
3. Find the box labelled *Additional Boards Manager URLs*. Paste this in:

   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```

4. Click OK.
5. **Tools ▸ Board ▸ Boards Manager**.
6. Type `esp32` in the search box.
7. Find **esp32 by Espressif Systems** and click Install. It is a large download — give it a few minutes.
8. Close and reopen the IDE.

To check it worked: **Tools ▸ Board** should now have an *esp32* section with entries like *ESP32 Dev Module*.

### 1.3 Python

Download from **python.org/downloads**.

On Windows, during installation there is a checkbox at the bottom of the first screen that says **"Add python.exe to PATH"**. Tick it. If you miss it, the next step will not work and you will have to reinstall.

On Mac, Python is usually already there.

To check: open Command Prompt (press Windows key, type `cmd`, Enter) and run:

```
python --version
```

You should see a version number. If you see "not recognised", Python is not on your PATH.

### 1.4 esptool

In the same Command Prompt:

```
pip install esptool
```

To check:

```
esptool version
```

You should see a version number. Note whether it starts with 4 or 5 — it changes one thing later.

### 1.5 Git

Download from **git-scm.com**. Install with all defaults.

To check:

```
git --version
```

### 1.6 USB driver (on every lab computer, not just yours)

Look at the small rectangular chip next to the USB socket on your Coggy:

- Says **CH340** or **CH9102** → search "CH341SER driver wch" and install it
- Says **CP2102** → search "CP210x VCP driver silabs" and install it

This is the one thing that still has to be installed on student machines. Do it once when you set up the lab and never again.

---

# Part 2 — Put the project folder on your machine

1. Download the project and unzip it.
2. Move the unzipped folder somewhere permanent. Not Downloads — it will get cleaned out. Use something like:

   ```
   C:\cognospace-flasher
   ```

   On Mac: `/Users/<you>/cognospace-flasher`

3. Open it and confirm you see:

   ```
   cognospace-flasher\
   ├── index.html
   ├── vercel.json
   ├── build.sh
   ├── SETUP-GUIDE.md
   ├── ESP32-WORKFLOW.md
   ├── assets\
   │   └── cognospace-logo.png
   └── firmware\
       ├── grade-03\
       ├── grade-04\
       ├── grade-05\
       ├── grade-06\
       ├── grade-07\
       ├── grade-08\
       └── grade-09\
   ```

4. Open `firmware\grade-03\` — you should see five folders named `CS-G03-A01` through `CS-G03-A05`.

**All 45 activity folders already exist.** You do not create them. You only put files into them.

If `assets\cognospace-logo.png` is missing, the logo on the website will show as broken text.

---

# Part 3 — Find `boot_app0.bin` (once, forever)

This small file is part of every merged ESP32 build. It ships with the board package you installed in 1.2, buried deep. Find it once, copy it somewhere easy, and reuse the same file for all 45 activities.

**Windows** — paste this into the File Explorer address bar:

```
%LOCALAPPDATA%\Arduino15\packages\esp32\hardware\esp32
```

**Mac** — in Finder press `Cmd+Shift+G` and paste:

```
~/Library/Arduino15/packages/esp32/hardware/esp32
```

**Linux**:

```
~/.arduino15/packages/esp32/hardware/esp32
```

Inside you will see one folder named after a version, like `3.0.7`. Open it, then open `tools`, then `partitions`. There is `boot_app0.bin`.

Copy that file to a new folder you make at:

```
C:\esp32-tools\boot_app0.bin
```

Done. You will point at this same path every time.

---

# Part 4 — GitHub and Vercel

### 4.1 Create the repository

1. Go to **github.com**, sign in, click the **+** at the top right, **New repository**.
2. Name it `cognospace-flasher`. Leave everything else alone. Click **Create repository**.
3. Leave that page open — you need the URL from it.

### 4.2 Push your folder to it

Open Command Prompt and run these one line at a time:

```bash
cd C:\cognospace-flasher
git init
git add .
git commit -m "Coggy Flasher"
git branch -M main
git remote add origin https://github.com/YOURNAME/cognospace-flasher.git
git push -u origin main
```

Replace `YOURNAME` with your GitHub username. It will ask you to sign in the first time.

Refresh the GitHub page — your files should be there.

### 4.3 Connect Vercel

1. Go to **vercel.com** and sign in **with GitHub**.
2. **Add New ▸ Project**.
3. Find `cognospace-flasher` in the list and click **Import**.
4. Framework Preset: choose **Other**.
5. Build Command: **leave empty**.
6. Output Directory: **leave empty**.
7. Click **Deploy**.

After a few seconds you get a URL like `cognospace-flasher.vercel.app`. Open it — the site is live.

It is served over HTTPS, which is what the flasher needs to talk to a board.

---

# Part 5 — Understand what a `.bin` is

Skip this if you already follow it, but it explains why the next part has an odd step.

Your `.ino` file is text — words a human wrote. The chip cannot read text. **Compiling** translates it into machine code. The Arduino IDE already does this every time you press upload.

The difference is that the ESP32 stores four separate things in four numbered slots in its memory:

```
slot 0x1000   bootloader        wakes the chip up
slot 0x8000   partition table   a map of what lives where
slot 0xe000   boot_app0         says which program to run
slot 0x10000  YOUR PROGRAM      the sketch you wrote
```

When you press upload in the IDE, it writes all four without telling you.

If the website sent only your program, a fresh board would have nothing in the first three slots — so nothing would wake it up and the board would appear dead.

So we **merge**: glue all four into one file with each piece at the right slot. That single file is what you put on the website, and it works on any board regardless of what was on it before.

---

# Part 6 — The loop: one sketch → one `.bin` in its folder

This is the part you repeat 45 times. The example uses **Class 7, Smart Watering System, code `CS-G07-A01`**.

### 6.1 Compile and keep the output

1. Open your sketch in the Arduino IDE.
2. **Tools ▸ Board ▸ esp32** → select the exact board you are using (usually *ESP32 Dev Module*).
3. **Sketch ▸ Export Compiled Binary**, or press `Ctrl + Alt + S`.

A progress bar runs and then nothing visible happens. That is normal — it wrote files quietly.

4. **Sketch ▸ Show Sketch Folder**. A window opens.
5. Go into `build`, then into the folder named after your board, e.g. `esp32.esp32.esp32`.

You should see something like:

```
SmartWatering.ino.bin
SmartWatering.ino.bootloader.bin
SmartWatering.ino.partitions.bin
SmartWatering.ino.map
```

### 6.2 Check for the shortcut first

**Look for a file ending in `.merged.bin`**, e.g. `SmartWatering.ino.merged.bin`.

Newer ESP32 board packages create this automatically, already glued together.

- **If it is there:** rename it to `firmware.bin` and skip straight to 6.4. No commands needed.
- **If it is not there:** carry on to 6.3.

### 6.3 Merge it yourself

Open Command Prompt and move into that build folder. Easiest way:

1. Type `cd ` (with a space after it), do not press Enter yet.
2. Drag the build folder from File Explorer onto the Command Prompt window. It pastes the full path.
3. Press Enter.

Now run this, replacing `SmartWatering` with your sketch name in all four places:

```
esptool --chip esp32 merge_bin -o firmware.bin --flash_mode dio --flash_freq 40m --flash_size 4MB 0x1000 SmartWatering.ino.bootloader.bin 0x8000 SmartWatering.ino.partitions.bin 0xe000 C:\esp32-tools\boot_app0.bin 0x10000 SmartWatering.ino.bin
```

In plain words that says: *take these four files, put each in the slot number written before it, save the result as `firmware.bin`.*

If esptool said version **5.x** earlier, change `merge_bin` to `merge-bin`.

If you are on an S3, C3 or C6 board, change `--chip esp32` to `--chip esp32s3` (or `esp32c3`, `esp32c6`) **and** change the first offset from `0x1000` to `0x0`. Those chips put the bootloader in a different slot.

When it finishes, `firmware.bin` is sitting in that same folder.

### 6.4 Put the file in its activity folder

Find the right folder using the table in Part 8. For `CS-G07-A01` it is:

```
C:\cognospace-flasher\firmware\grade-07\CS-G07-A01\
```

Copy `firmware.bin` into it. The folder now holds `.gitkeep` and `firmware.bin`.

**The name must be exactly `firmware.bin`.** Not `SmartWatering.bin`, not `firmware (1).bin`. The website is already looking for that exact name at that exact path.

While you are there, also copy your `.ino` in and rename it `source.ino`. A `.bin` is unreadable — six months from now when something misbehaves you will want the sketch that produced this exact file sitting next to it.

### 6.5 Test before you push

In Command Prompt:

```
cd C:\cognospace-flasher
npx serve .
```

It prints a local address, usually `http://localhost:3000`. Open that in **Chrome**.

Go to the flasher, pick Class 7, click Smart Watering System, plug in a Coggy, press Connect, then Flash. Watch the console.

Do not skip this. It is much easier to fix a problem now than in front of a class.

**Why not just double-click `index.html`?** Because browsers block the Web Serial API on `file://` addresses. It has to be served, either from `localhost` or from HTTPS.

### 6.6 Push it live

```
cd C:\cognospace-flasher
git add .
git commit -m "Add firmware for CS-G07-A01"
git push
```

Vercel sees the push and redeploys automatically. About twenty seconds later it is live on your URL.

---

# Part 7 — You do not edit `index.html`

For all 45 activities in your syllabus, the catalogue entry already exists and already points at the right path. Dropping `firmware.bin` into the folder is the entire job.

You only open `index.html` when you want to:

- add an activity that is not in your syllabus
- add a new class
- change an activity's name, description or component list
- bump a version number after rebuilding

In those cases, find the block near the bottom that starts with `<script type="application/json" id="catalog">` and edit the JSON there.

---

# Part 8 — Where every file goes

Each row tells you the exact folder for that activity code.

**Class 3** — `firmware/grade-03/`

| Code | Activity | Module | Drop the file here |
|---|---|---|---|
| `CS-G03-A01` | Traffic Signals | Mechatronics | `firmware/grade-03/CS-G03-A01/firmware.bin` |
| `CS-G03-A02` | Music LEDs | Mechatronics | `firmware/grade-03/CS-G03-A02/firmware.bin` |
| `CS-G03-A03` | Digital Dice | Mechatronics | `firmware/grade-03/CS-G03-A03/firmware.bin` |
| `CS-G03-A04` | 2 Way Switch | Mechatronics | `firmware/grade-03/CS-G03-A04/firmware.bin` |
| `CS-G03-A05` | Door Bell | Mechatronics | `firmware/grade-03/CS-G03-A05/firmware.bin` |

**Class 4** — `firmware/grade-04/`

| Code | Activity | Module | Drop the file here |
|---|---|---|---|
| `CS-G04-A01` | Timer & Stopwatch | Mechatronics | `firmware/grade-04/CS-G04-A01/firmware.bin` |
| `CS-G04-A02` | Digital Measuring Tape | Mechatronics | `firmware/grade-04/CS-G04-A02/firmware.bin` |
| `CS-G04-A03` | Rain Detection | Mechatronics | `firmware/grade-04/CS-G04-A03/firmware.bin` |
| `CS-G04-A04` | Cognojump Game | Mechatronics | `firmware/grade-04/CS-G04-A04/firmware.bin` |
| `CS-G04-A05` | Weather Station | Mechatronics | `firmware/grade-04/CS-G04-A05/firmware.bin` |

**Class 5** — `firmware/grade-05/`

| Code | Activity | Module | Drop the file here |
|---|---|---|---|
| `CS-G05-A01` | Automatic Gate | Mechatronics | `firmware/grade-05/CS-G05-A01/firmware.bin` |
| `CS-G05-A02` | Soil Moisture Test | Mechatronics | `firmware/grade-05/CS-G05-A02/firmware.bin` |
| `CS-G05-A03` | Motor Speed Control | Mechatronics | `firmware/grade-05/CS-G05-A03/firmware.bin` |
| `CS-G05-A04` | Calculator using OLED | Mechatronics | `firmware/grade-05/CS-G05-A04/firmware.bin` |
| `CS-G05-A05` | Smart Fan | Mechatronics | `firmware/grade-05/CS-G05-A05/firmware.bin` |

**Class 6** — `firmware/grade-06/`

| Code | Activity | Module | Drop the file here |
|---|---|---|---|
| `CS-G06-A01` | Automatic Rain Hanger | Mechatronics | `firmware/grade-06/CS-G06-A01/firmware.bin` |
| `CS-G06-A02` | Secure Home | Mechatronics | `firmware/grade-06/CS-G06-A02/firmware.bin` |
| `CS-G06-A03` | Smart Light | Mechatronics | `firmware/grade-06/CS-G06-A03/firmware.bin` |
| `CS-G06-A04` | Wireless Notice Board | Mechatronics | `firmware/grade-06/CS-G06-A04/firmware.bin` |
| `CS-G06-A05` | Visitor Counter | Mechatronics | `firmware/grade-06/CS-G06-A05/firmware.bin` |

**Class 7** — `firmware/grade-07/`

| Code | Activity | Module | Drop the file here |
|---|---|---|---|
| `CS-G07-A01` | Smart Watering System | Mechatronics | `firmware/grade-07/CS-G07-A01/firmware.bin` |
| `CS-G07-A02` | Automatic Railway Gate | Mechatronics | `firmware/grade-07/CS-G07-A02/firmware.bin` |
| `CS-G07-A03` | Morse Code Flasher | Mechatronics | `firmware/grade-07/CS-G07-A03/firmware.bin` |
| `CS-G07-A04` | Smart Parking System | Mechatronics | `firmware/grade-07/CS-G07-A04/firmware.bin` |
| `CS-G07-A05` | ADAS Car | Mechatronics | `firmware/grade-07/CS-G07-A05/firmware.bin` |

**Class 8** — `firmware/grade-08/`

| Code | Activity | Module | Drop the file here |
|---|---|---|---|
| `CS-G08-A01` | Basics of Robotics | Mechatronics | `firmware/grade-08/CS-G08-A01/firmware.bin` |
| `CS-G08-A02` | Gripper | Mechatronics | `firmware/grade-08/CS-G08-A02/firmware.bin` |
| `CS-G08-A03` | Human Following Robot | Mechatronics | `firmware/grade-08/CS-G08-A03/firmware.bin` |
| `CS-G08-A04` | Bluetooth Controlled Robot | Mechatronics | `firmware/grade-08/CS-G08-A04/firmware.bin` |
| `CS-G08-A05` | Perseverance Rover - Bluetooth | Mechatronics | `firmware/grade-08/CS-G08-A05/firmware.bin` |
| `CS-G08-A06` | Introduction to Automation/IoT | IoT/Automation | `firmware/grade-08/CS-G08-A06/firmware.bin` |
| `CS-G08-A07` | Home Automation | IoT/Automation | `firmware/grade-08/CS-G08-A07/firmware.bin` |
| `CS-G08-A08` | Automatic Street Lights | IoT/Automation | `firmware/grade-08/CS-G08-A08/firmware.bin` |
| `CS-G08-A09` | Sensor Integration to Thingspeak | IoT/Automation | `firmware/grade-08/CS-G08-A09/firmware.bin` |
| `CS-G08-A10` | Weather Monitoring using Webserver | IoT/Automation | `firmware/grade-08/CS-G08-A10/firmware.bin` |

**Class 9** — `firmware/grade-09/`

| Code | Activity | Module | Drop the file here |
|---|---|---|---|
| `CS-G09-A01` | Basics of Robotics | Mechatronics | `firmware/grade-09/CS-G09-A01/firmware.bin` |
| `CS-G09-A02` | Obstacle Avoiding Robot | Mechatronics | `firmware/grade-09/CS-G09-A02/firmware.bin` |
| `CS-G09-A03` | Edge Avoiding Robot | Mechatronics | `firmware/grade-09/CS-G09-A03/firmware.bin` |
| `CS-G09-A04` | Robotic Arm | Mechatronics | `firmware/grade-09/CS-G09-A04/firmware.bin` |
| `CS-G09-A05` | Perseverance Rover - Wifi | Mechatronics | `firmware/grade-09/CS-G09-A05/firmware.bin` |
| `CS-G09-A06` | Introduction to Automation/IoT | IoT/Automation | `firmware/grade-09/CS-G09-A06/firmware.bin` |
| `CS-G09-A07` | Home Monitoring using Webserver | IoT/Automation | `firmware/grade-09/CS-G09-A07/firmware.bin` |
| `CS-G09-A08` | Weather Station using Thingspeak | IoT/Automation | `firmware/grade-09/CS-G09-A08/firmware.bin` |
| `CS-G09-A09` | Smart Agriculture Monitoring | IoT/Automation | `firmware/grade-09/CS-G09-A09/firmware.bin` |
| `CS-G09-A10` | WiFi-Rover | IoT/Automation | `firmware/grade-09/CS-G09-A10/firmware.bin` |

---

# Part 9 — When things go wrong

**`esptool` is not recognised**
Python was installed without "Add to PATH", or `pip install esptool` was not run. Reinstall Python with the box ticked, then run `pip install esptool` again.

**`Sketch ▸ Export Compiled Binary` is greyed out**
No board is selected. Pick one under Tools ▸ Board first.

**The build folder has no `.bootloader.bin`**
You selected an Arduino board rather than an ESP32 board. Change the board and export again.

**The site shows the activity card but the console says the file was not found**
Either `firmware.bin` is not in that folder, or it is named something else, or you have not pushed yet. Check all three in that order.

**The board flashes with no errors, then does nothing**
Almost always a wrong offset. If you merged the file, the catalogue entry must say `"offset": "0x0"` — which is what all 45 entries already say. If you used the app-only `.bin` instead of a merged one, it must say `0x10000`.

**Connect fails or the port list is empty**
Try a different USB cable first — charge-only cables are the most common cause by a wide margin. Then check the CH340 or CP2102 driver.

**Flashing starts, then fails partway**
Hold the BOOT button on the board while pressing Connect. Some boards need it. A shorter cable also helps.

**The whole shelf is empty**
A JSON syntax error in the catalogue, usually a comma left after the last item in a list. Only relevant if you edited `index.html`.
