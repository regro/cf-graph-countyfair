import glob
import subprocess

from conda_forge_tick.lazy_json_backends import load, dump
import tqdm


def _commit_and_push(done, itr, tot_itr):
    print(" ", flush=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-m", f"[{itr} of {tot_itr}] rewrite JSON blobs"], check=True)
    subprocess.run(["git", "push"], check=True)


print("globbing files...", flush=True)
all_fnames = glob.glob("**/*.json", recursive=True, include_hidden=True)
print(f"found {len(all_fnames)} files", flush=True)

modfac = 5000
itr = 0
tot_itr = len(all_fnames) // modfac + 1

done = set()
for fname in tqdm.tqdm(all_fnames, ncols=80):
    if fname.startswith(".git/"):
        continue

    if len(done) > 0 and len(done) % modfac == 0:
        itr += 1
        _commit_and_push(done, itr, tot_itr)
        done = set()

    with open(fname, "r") as f:
        data = load(f)
    with open(fname, "w") as f:
        dump(data, f)

    done.add(fname)

if done:
    itr += 1
    _commit_and_push(done, itr, tot_itr)
