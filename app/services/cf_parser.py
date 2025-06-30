import subprocess
import os

TYPICAL_GROUPS = [
    "Catalogs",
    "Documents",
    "CommonModules",
    "Subsystems",
    "Constants",
    "DocumentJournals",
    "Enums",
    "BusinessProcesses",
    "Tasks",
    "InformationRegisters",
    "AccumulationRegisters",
    "ChartOfAccounts",
    "ChartOfCalculationTypes",
    "ExchangePlans",
    "EventSubscriptions",
    "ScheduledJobs",
    "Reports",
    "DataProcessors",
    "Settings",
    "Roles",
    "Templates",
    "Languages"
]

def parse_cf_file(file_path: str):
    outdir = os.path.join(os.path.dirname(file_path), 'cf_unpack')
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

    # Группировка файлов по типу
    grouped = {g: {} for g in TYPICAL_GROUPS}
    grouped['Other'] = {}

    stats = {g: 0 for g in TYPICAL_GROUPS}
    stats['Other'] = 0

    for root, dirs, files in os.walk(outdir):
        rel_root = os.path.relpath(root, outdir)
        if rel_root == ".":
            continue
        group = rel_root.split(os.sep)[0]
        if group not in grouped:
            group = "Other"
        node = grouped[group]
        parts = rel_root.split(os.sep)[1:]
        for part in parts:
            node = node.setdefault(part, {})
        for f in files:
            node[f] = None
            stats[group] += 1

    for f in os.listdir(outdir):
        if os.path.isfile(os.path.join(outdir, f)):
            grouped['Other'][f] = None
            stats['Other'] += 1

    # Простейшая попытка определить версию платформы (если есть файл version.data)
    version = None
    version_path = os.path.join(outdir, "version.data")
    if os.path.exists(version_path):
        try:
            with open(version_path, "rb") as vf:
                v = vf.read()
                version = str(v)
        except Exception:
            version = None

    return {
        "structure": grouped,
        "stats": stats,
        "version_guess": version
    }
