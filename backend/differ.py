"""Create a nice diff for data.json"""
import json
import os
from subprocess import run

from git import Repo


print("> Starting ...")

print("> Checking if data.json has changed ...")
repo = Repo("..")
changed_files = repo.index.diff(None)
flag = 0
for file in changed_files:
    if file.a_path == "backend/data.json":
        flag = 1
        break
if not flag:
    exit("> data.json is up to date!")

print("> Copying data as backup ...")
run("cp data.json data.json.bk", shell=True)

print("> Renaming data.json ...")
os.rename("data.json", "new-data.json")

print("> Cecking out data.json ...")
run("git checkout -- data.json", shell=True)

new = eval(open("new-data.json").read())
old = eval(open("data.json").read())

print("> Converting to json ...")
new = json.dumps(new, indent=4)
old = json.dumps(old, indent=4)

print("> Saving to file ...")
open("new.json", "w+").write(str(new))
open("old.json", "w+").write(str(old))

print("> Creating diff ...")
run("diff new.json old.json > data.diff", shell=True)
print("> Diff saved to 'data.diff' ...")

print("> Deleting intermediaries ...")
run("rm new.json old.json", shell=True)

print("> Moving back data.json ...")
run("mv new-data.json data.json", shell=True)

print("> Done.")
