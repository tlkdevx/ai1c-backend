import subprocess
import os

def parse_cf_file(file_path: str):
    # Папка для распаковки рядом с файлом
    outdir = os.path.join(os.path.dirname(file_path), 'cf_unpack')
    # Очищаем папку cf_unpack, если она уже есть
    if os.path.exists(outdir):
        for root, dirs, files in os.walk(outdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(outdir)

    exe_path = os.path.join(os.path.dirname(file_path), 'v8unpack.exe')
    try:
        subprocess.run([exe_path, '--unpack', file_path, outdir], check=True, capture_output=True)
    except Exception as e:
        return {"error": f"Ошибка запуска v8unpack: {e}"}
    result = {"objects": []}
    for root, dirs, files in os.walk(outdir):
        rel_root = os.path.relpath(root, outdir)
        for name in files:
            result["objects"].append({"type": "file", "path": os.path.join(rel_root, name)})
    return result
