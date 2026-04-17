from __future__ import annotations

import struct
import sys
import zipfile
from pathlib import Path


PT_LOAD = 1
MIN_PAGE_ALIGN = 16 * 1024


def iter_program_headers(data: bytes):
    if data[:4] != b"\x7fELF":
        return None

    elf_class = data[4]
    endian = "<" if data[5] == 1 else ">"

    if elf_class == 2:
        e_phoff = struct.unpack_from(endian + "Q", data, 32)[0]
        e_phentsize = struct.unpack_from(endian + "H", data, 54)[0]
        e_phnum = struct.unpack_from(endian + "H", data, 56)[0]
        headers = []
        for i in range(e_phnum):
            off = e_phoff + i * e_phentsize
            header = struct.unpack_from(endian + "IIQQQQQQ", data, off)
            p_type, _p_flags, p_offset, p_vaddr, _p_paddr, p_filesz, p_memsz, p_align = header
            headers.append((p_type, p_offset, p_vaddr, p_filesz, p_memsz, p_align))
        return headers

    if elf_class == 1:
        e_phoff = struct.unpack_from(endian + "I", data, 28)[0]
        e_phentsize = struct.unpack_from(endian + "H", data, 42)[0]
        e_phnum = struct.unpack_from(endian + "H", data, 44)[0]
        headers = []
        for i in range(e_phnum):
            off = e_phoff + i * e_phentsize
            header = struct.unpack_from(endian + "IIIIIIII", data, off)
            p_type, p_offset, p_vaddr, _p_paddr, p_filesz, p_memsz, _p_flags, p_align = header
            headers.append((p_type, p_offset, p_vaddr, p_filesz, p_memsz, p_align))
        return headers

    return None


def zip_data_offset(bundle_path: Path, info: zipfile.ZipInfo) -> int:
    with bundle_path.open("rb") as fp:
        fp.seek(info.header_offset)
        header = fp.read(30)
    name_len = int.from_bytes(header[26:28], "little")
    extra_len = int.from_bytes(header[28:30], "little")
    return info.header_offset + 30 + name_len + extra_len


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: verify_page_sizes.py <apk-or-aab>", file=sys.stderr)
        return 2

    bundle_path = Path(sys.argv[1])
    if not bundle_path.exists():
        print(f"Archive not found: {bundle_path}", file=sys.stderr)
        return 2

    failures: list[str] = []
    checked = 0
    skipped_non_elf = 0

    with zipfile.ZipFile(bundle_path) as zf:
        for info in zf.infolist():
            if not info.filename.endswith(".so"):
                continue

            data = zf.read(info.filename)
            headers = iter_program_headers(data)
            if headers is None:
                skipped_non_elf += 1
                continue

            checked += 1
            load_aligns = [p_align for p_type, *_rest, p_align in headers if p_type == PT_LOAD]
            if not load_aligns:
                failures.append(f"{info.filename}: ELF has no PT_LOAD segments")
                continue

            bad_aligns = [hex(align) for align in load_aligns if align < MIN_PAGE_ALIGN]
            if bad_aligns:
                failures.append(
                    f"{info.filename}: PT_LOAD alignments below 16 KB: {', '.join(bad_aligns)}"
                )

            if info.compress_type == zipfile.ZIP_STORED:
                offset = zip_data_offset(bundle_path, info)
                if offset % MIN_PAGE_ALIGN != 0:
                    failures.append(
                        f"{info.filename}: uncompressed ZIP entry offset {offset} is not 16 KB aligned"
                    )

    print(
        f"Checked {checked} ELF shared libraries in {bundle_path.name}; "
        f"skipped {skipped_non_elf} non-ELF .so payloads."
    )
    if failures:
        print("16 KB page-size verification failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("16 KB page-size verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
