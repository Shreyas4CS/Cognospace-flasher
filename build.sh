#!/usr/bin/env bash
# CognoSpace Flasher — merge Arduino IDE ESP32 output into one flashable file.
#
# Run this from inside the sketch's build folder, e.g.
#   ~/Arduino/ServoDial/build/esp32.esp32.esp32/
#
# usage: ./build.sh <chip> <sketch-name> <path-to-boot_app0.bin>
#   ./build.sh esp32   ServoDial    ~/esp32-tools/boot_app0.bin
#   ./build.sh esp32s3 FaceGate     ~/esp32-tools/boot_app0.bin
#
# Output: firmware.bin — flash it at offset 0x0.

set -euo pipefail

CHIP=${1:-}
NAME=${2:-}
BOOTAPP=${3:-}

if [[ -z "$CHIP" || -z "$NAME" || -z "$BOOTAPP" ]]; then
  echo "usage: $0 <chip> <sketch-name> <path-to-boot_app0.bin>"
  echo "  chip: esp32 | esp32s2 | esp32s3 | esp32c3 | esp32c6"
  exit 1
fi

# S3, C3 and C6 put the bootloader at 0x0; ESP32 and S2 put it at 0x1000.
case "$CHIP" in
  esp32|esp32s2) BLOFF=0x1000 ;;
  esp32s3|esp32c3|esp32c6) BLOFF=0x0 ;;
  *) echo "Unknown chip: $CHIP"; exit 1 ;;
esac

for f in "${NAME}.ino.bootloader.bin" "${NAME}.ino.partitions.bin" "${NAME}.ino.bin"; do
  [[ -f "$f" ]] || { echo "Missing $f — did you run Sketch > Export Compiled Binary?"; exit 1; }
done
[[ -f "$BOOTAPP" ]] || { echo "Missing boot_app0.bin at $BOOTAPP"; exit 1; }

# esptool 5.x uses merge-bin, 4.x uses merge_bin
if esptool merge-bin --help >/dev/null 2>&1; then CMD=merge-bin; else CMD=merge_bin; fi

esptool --chip "$CHIP" "$CMD" -o firmware.bin \
  --flash_mode dio --flash_freq 40m --flash_size 4MB \
  "$BLOFF"  "${NAME}.ino.bootloader.bin" \
  0x8000    "${NAME}.ino.partitions.bin" \
  0xe000    "$BOOTAPP" \
  0x10000   "${NAME}.ino.bin"

echo
echo "Wrote firmware.bin ($(du -h firmware.bin | cut -f1)) — flash this at offset 0x0"
echo "Catalogue entry:  \"parts\": [{ \"file\": \"/firmware/grade-XX/CS-GXX-AXX/firmware.bin\", \"offset\": \"0x0\" }]"
