import glob
import tqdm
from conda_forge_tick.lazy_json_backends import dump, loads


all_nodes = glob.glob("./version_pr_info/**/*.json", recursive=True)

for node_path in tqdm.tqdm(all_nodes):
    with open(node_path, "r") as fp:
        attrs = loads(fp.read())

    new_ver = attrs.get("new_version", None)
    attempts = attrs.get("new_version_attempts", None)
    if (
        new_ver is not None
        and attempts is not None
        and attempts.get(new_ver, None) is not None
    ):
        attempts[new_ver] = 0
        with open(node_path, "w") as fp:
            dump(attrs, fp)
