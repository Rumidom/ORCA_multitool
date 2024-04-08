# this is to be run on a PC/Github
import os


paths = []
exclude = ["./boot.py","./device_test.py"]
for root, dirs, files in os.walk("."):
    path = root.split(os.sep)
    for file in files:
        paths.append(os.path.basename(root)+"/"+file)
        
for path in exclude:
    paths.remove(path)

for path in paths:
    if path[-3:] != ".py":
        paths.remove(path)
        
print("Files to test:")
print(paths)
print("-------")

# check if all functions/methods have the correct number of arguments and self
functions = {}
methods = {}
classes = []
for filepath in paths:
    f = open(filepath, "r")
    lines = f.readlines()
    CurrentClass = None
    for line in lines:
        if line.strip()[:5] == "class":
            CurrentClass = line.strip()
            classes.append(line.strip())
        if line.strip()[:3] == "def":
            line = line.strip().replace("def ","").replace(":","")
            arguments = line.split("(")[-1].split(")")[0].split(",")
            if CurrentClass != None:
                methods[line] = (CurrentClass.replace("class ","").replace(":",""),len(arguments))
                if not "self" in line:
                    print("- {} in {} missing self".format(line,filepath))
            else:
                functions[line] = ((None,len(arguments)))

print("Found {} Functions, {} methods, {} Classes".format(len(functions.keys()),len(methods.keys()),len(classes)))


# check if defauts on pages/Config.py are sane
# check if page modules have correct formating:
#(self on all methods,a Run function,Input_Func has w)
# test control functions
# check if all components in page modules actually exist on components folder
