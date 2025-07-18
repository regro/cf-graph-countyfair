from conda_forge_tick.utils import get_sharded_path
import os
import tqdm
import shutil

NEW_LOC = "../cf-graph-countyfair"

# make the new location
os.makedirs(NEW_LOC, exist_ok=True)

# mappings
print("moving mappings", flush=True)
os.makedirs(NEW_LOC + "/mappings", exist_ok=True)
os.system("cp -r mappings " + NEW_LOC + "/.")

# other files/dirs
print("moving other files", flush=True)
for item in [
    ".github",
    ".gitignore",
    "License",
    "README.md",
    "all_feedstocks.json",
    "example.ipynb",
    "graph.json",
    "ranked_hubs_authorities.json",
    "reset_version_attempts.py",
    "shard_files.py",
    "test_load_graph.py",
]:
    os.system(f"cp -r {item} {NEW_LOC}/")

# do status
print("moving status data", flush=True)
top_list = [
    "version_status.json",
    "total_status.json",
    "closed_status.json",
    "regular_status.json",
    "longterm_status.json",
]
skip_list = ["pr_state.csv"]
os.makedirs(f"{NEW_LOC}/status/migration_json", exist_ok=True)
os.makedirs(f"{NEW_LOC}/status/migration_svg", exist_ok=True)
fnames = os.listdir("./status")
not_moved = 0
for fname in tqdm.tqdm(fnames, desc="status", ncols=80):
    if fname in top_list:
        shutil.copy2(f"./status/{fname}", f"{NEW_LOC}/status/.")
    elif fname.endswith(".json"):
        shutil.copy2(
            f"./status/{fname}",
            f"{NEW_LOC}/status/migration_json/.",
        )
    elif fname.endswith(".svg"):
        shutil.copy2(
            f"./status/{fname}",
            f"{NEW_LOC}/status/migration_svg/.",
        )
    elif fname in skip_list:
        continue
    else:
        not_moved += 1
        print(fname)

assert not_moved == 0

# now move the sharded files
print("moving graph data", flush=True)
for dr in [
    "versions",
    "version_pr_info",
    "pr_json",
    "pr_info",
    "node_attrs",
    "audits/depfinder",
    "audits/grayskull",
]:
    fnames = os.listdir(dr)
    os.makedirs(
        os.path.join(NEW_LOC, dr),
        exist_ok=True
    )
    for fname in tqdm.tqdm(fnames, desc=dr, ncols=80):
        pth = os.path.join(dr, fname)
        sharded_pth = get_sharded_path(pth)
        dst = os.path.join(NEW_LOC, sharded_pth)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            shutil.copy2(pth, dst)
        except Exception:
            print(fname, pth, sharded_pth, dst)
