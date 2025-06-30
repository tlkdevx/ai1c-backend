import subprocess
import os

def parse_cf_file(file_path: str):
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

    def build_tree(start_path):
        tree = {}
        for root, dirs, files in os.walk(start_path):
            rel_path = os.path.relpath(root, start_path)
            node = tree
            if rel_path != ".":
                for part in rel_path.split(os.sep):
                    node = node.setdefault(part, {})
            for d in dirs:
                node[d] = {}
            for f in files:
                node[f] = None
        return tree

    result = build_tree(outdir)
    return result
