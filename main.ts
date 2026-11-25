// Entry for make.fun's news-image-20261125: ship the page this repository holds.
//
// The picture is drawn by render.py from stories.py (the 25 November 2026 scan of our own
// wire feeds) and committed as entry.png. This program is what the sandbox runs: it reads the
// committed bytes, walks every PNG chunk to prove the file is whole, checks it against the
// competition's gate, and writes the same bytes to /output/entry.png.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const here = new URL(".", import.meta.url).pathname;
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const png = readFileSync(join(here, "entry.png"));

// 1. signature
const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!png.subarray(0, 8).equals(sig)) throw new Error("entry.png is not a PNG");

// 2. every chunk, end to end: length, type, data, CRC -- and an IEND at the last byte
let at = 8;
let first = true;
let sawIdat = false;
let sawIend = false;
while (at + 12 <= png.length) {
  const len = png.readUInt32BE(at);
  const type = png.subarray(at + 4, at + 8).toString("latin1");
  const data = png.subarray(at + 8, at + 8 + len);
  const crc = png.readUInt32BE(at + 8 + len);
  if (crc !== crc32(png.subarray(at + 4, at + 8 + len))) throw new Error(`bad CRC in ${type}`);
  if (first) {
    if (type !== "IHDR") throw new Error("the first chunk is not IHDR");
    first = false;
  }
  if (type === "IDAT") sawIdat = true;
  if (type === "IEND") {
    sawIend = true;
    if (at + 12 + len !== png.length) throw new Error("bytes after IEND");
    break;
  }
  at += 12 + len;
}
if (!sawIdat || !sawIend) throw new Error("missing IDAT or IEND");

// 3. the gate's own limits
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);
const depth = png[24];
const colourType = png[25];
if (width !== 1024 || height !== 1024) throw new Error(`image is ${width}x${height}, needs 1024x1024`);
if (png.length > 1048576) throw new Error(`image is ${png.length} bytes, cap is 1048576`);
if (depth !== 8 || colourType !== 2) throw new Error(`unexpected PNG depth/colour type ${depth}/${colourType}`);

// 4. write, then read back so the sandbox proves the same bytes landed
mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
writeFileSync(target, png);
const back = readFileSync(target);
if (!back.equals(png)) throw new Error("written bytes differ from the committed image");
console.log(`wrote ${target}: ${back.length} bytes, ${width}x${height}, ${depth}-bit type ${colourType}`);

function crc32(buf: Buffer): number {
  let c: number;
  const table: number[] = [];
  for (let n = 0; n < 256; n++) {
    c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  let crc = 0xffffffff;
  for (const b of buf) crc = table[(crc ^ b) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}
