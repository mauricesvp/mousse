"""
Utility script to merge the 'old' data.json with the 'new' ext_data.json.
Ideally we want to get all data using the XML parsing though.
"""

data = eval(open("data.json").read())
ext = eval(open("mousse/ext_data.json").read())

for x in ext:
    x["version"] = x["version"].replace("v", "")
    id = str(x["id"])
    for i, y in enumerate(data):
        if str(y["id"]) == id:
            data[i].update(x)
            break

with open("merged.json", "w+") as f:
    f.write(str(data))
