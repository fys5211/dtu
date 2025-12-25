import ctypes
import os
import sys

# 配置虚拟串口的 COM 端口
COM_PORT1 = 'COM3'
COM_PORT2 = 'COM4'

# 尝试加载 vspdctl.dll
def try_load_vspd(dll_path):
    if not os.path.isfile(dll_path):
        print(f"Error: DLL not found at {dll_path}")
        return None

    try:
        lib = ctypes.WinDLL(dll_path)
        print(f"Loaded DLL: {dll_path}")
        return lib
    except Exception as e:
        print(f"Failed to load DLL {dll_path}: {e}")
        return None

# 删除虚拟串口对
def delete_virtual_com(lib, port1: str, port2: str):
    try:
        func = lib.DeletePair
    except AttributeError:
        print("DLL does not export DeletePair — can't delete pair")
        return False

    func.argtypes = [ctypes.c_char_p]
    func.restype = ctypes.c_bool

    print(f"Deleting COM pair: {port1}, {port2}...")
    # 删除 COM1
    res = func(port1.encode('ascii'))
    if res:
        print(f"Successfully deleted COM pair: {port1}")
    else:
        print(f"Failed to delete COM pair: {port1}")

    # 删除 COM2
    res = func(port2.encode('ascii'))
    if res:
        print(f"Successfully deleted COM pair: {port2}")
    else:
        print(f"Failed to delete COM pair: {port2}")
    return True

def main():
    dll_path = r"E:\Virtual Serial Port Driver 7.2\vspdctl.dll"  # 请改为你真实的 vspdctl.dll 路径
    lib = try_load_vspd(dll_path)
    if not lib:
        sys.exit(1)

    # 删除 COM3-COM4 对
    success = delete_virtual_com(lib, COM_PORT1, COM_PORT2)
    if success:
        print("Successfully deleted the COM pair.")
    else:
        print("Failed to delete COM pair.")

if __name__ == "__main__":
    main()
