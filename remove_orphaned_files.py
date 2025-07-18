import copy
import glob
import json
import subprocess

from conda_forge_tick.lazy_json_backends import get_sharded_path, LazyJson
from conda_forge_tick.git_utils import lazy_update_pr_json, github_client

GH = github_client()


def _is_pr_duplicated(node, number):
    repo = GH.get_repo("conda-forge/" + node)
    orig_pr = repo.get_pull(number)

    node = node.replace("-feedstock", "")
    with LazyJson(f"node_attrs/{node}.json") as lzj:
        with lzj["pr_info"] as pr_info:
            for pr in pr_info["PRed"]:
                if "PR" not in pr or "number" not in pr["PR"] or pr["PR"]["number"] is None:
                    continue
                _pr = repo.get_pull(int(pr["PR"]["number"]))
                if _pr.title == orig_pr.title:
                    if orig_pr.state == "open":
                        orig_pr.edit(state="closed")
                    return True

    return False


# clean out oprhaned PR json blobs
print("getting all pr json blobs", flush=True)
all_pr_json = glob.glob("./pr_json/**/*.json", recursive=True)
all_pr_json = set(
    "pr_json/" + pr_json.split("/")[-1]
    for pr_json in all_pr_json
)

print("getting only referenced pr json blobs", flush=True)
found_pr_json = set()
all_pr_info = glob.glob("./pr_info/**/*.json", recursive=True)
for pr_info in all_pr_info:
    with open(pr_info, "r") as fp:
        pri = json.load(fp)

    pred = pri.get("PRed", []) or []
    for _pr in pred:
        pr = _pr.get("PR", {}) or {}
        lzj = pr.get("__lazy_json__", None) or None
        if lzj:
            found_pr_json.add(lzj)

orphaned_pr_json = all_pr_json - found_pr_json
print(f"Found {len(orphaned_pr_json)} orphaned PR json blobs")

for pr_json in orphaned_pr_json:
    with LazyJson(pr_json) as lzj:
        pr_data = lazy_update_pr_json(copy.deepcopy(lzj.data))
        if pr_data is not None:
            if pr_data.get("state", None) == "closed":
                assert pr_data["id"] == int(pr_json.split("/")[-1].split(".")[0]), (
                    pr_data["id"],
                    pr_json,
                )
                print(
                    "can remove %s - last modified at %s" % (pr_json, pr_data["Last-Modified"]),
                    flush=True,
                )
                pth = get_sharded_path(pr_json)
                subprocess.run(["git", "rm", "-f", pth], check=True)
            else:
                repo = GH.get_repo("conda-forge/" + pr_data["base"]["repo"]["name"])
                if repo.archived:
                    print(
                        "can remove %s - repo is archived" % pr_json,
                        flush=True,
                    )
                    pth = get_sharded_path(pr_json)
                    subprocess.run(["git", "rm", "-f", pth], check=True)
                else:
                    if _is_pr_duplicated(pr_data["base"]["repo"]["name"], pr_data["number"]):
                        print(
                            "can remove %s - PR is duplicated so closing. "
                            "Run script again after a git pull to delete json." % pr_json,
                            flush=True,
                        )
                    else:
                        print("orphaned PR (%s): %s" % (pr_data["state"], pr_data["html_url"]), flush=True)
        else:
            print(f"could not load {pr_json}", flush=True)
