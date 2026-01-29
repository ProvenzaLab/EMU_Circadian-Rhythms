from pathlib import Path
from collections import defaultdict

def find_duplicate_filenames(root):
    files_by_name = defaultdict(list)

    for p in Path(root).rglob("*"):
        if p.is_file():
            files_by_name[p.name].append(p)

    return {name: paths for name, paths in files_by_name.items() if len(paths) > 1}


dups = find_duplicate_filenames("/path/to/folder")

def delete_duplicate_filenames(root, dry_run=True):
    dups = find_duplicate_filenames(root)

    for name, paths in dups.items():
        # keep first path (sorted for determinism)
        paths = sorted(paths)
        keep = paths[0]
        to_delete = paths[1:]

        for p in to_delete:
            if dry_run:
                print(f"Would delete: {p}")
            else:
                p.unlink()
                print(f"Deleted: {p}")

# dry run first!
delete_duplicate_filenames("foundation_model_prep", dry_run=False)