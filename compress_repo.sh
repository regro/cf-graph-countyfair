#!/usr/bin/env bash

echo "Compressing repo to only the local commits..."
git replace -f --graft $(git rev-list --max-parents=0 HEAD)
git filter-repo --force

echo -e "\nCleaning out the git database..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo -e "\nForce pushing upstream..."
git remote add origin https://github.com/regro/cf-graph-countyfair.git
git push origin --force --all
git push origin --force --tags

echo -e "\n\n"
echo "    ======================================================"
echo "    || Repo has been compressed and force pushed!       ||"
echo "    || **TURN GITHUB BRANCH PROTECTION RULES BACK ON ** ||"
echo "    ======================================================"
