# list_exports.py
import os
import sys

try:
    import pefile
except Exception:
    print("Missing dependency: pefile. Install with:\n    pip install pefile")
    sys.exit(1)

def list_exports(dll_path, out_path=None):
    if not os.path.isfile(dll_path):
        print(f"DLL not found: {dll_path}")
        return False
    pe = pefile.PE(dll_path)
    exports = []
    if not hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
        print("No export table found in DLL.")
        return False
    for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        name = exp.name.decode('utf-8', errors='replace') if exp.name else f"ordinal_{exp.ordinal}"
        exports.append((exp.ordinal, name))
    exports.sort()
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as f:
            for ordv, name in exports:
                f.write(f"{ordv:5d}  {name}\n")
    else:
        for ordv, name in exports:
            print(f"{ordv:5d}  {name}")
    print(f"Total exports: {len(exports)}")
    return True

if __name__ == "__main__":
    # 修改为你的 vspdctl.dll 路径
    dll_path = r"E:\Virtual Serial Port Driver 6.9\vspdctl.dll"
    out_file = r"E:\virtual_port_exports.txt"  # 输出文件（任选）
    ok = list_exports(dll_path, out_file)
    if ok:
        print(f"Exports written to: {out_file}")
    else:
        print("Failed to list exports.")
