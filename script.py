import glob,json
files=glob.glob('*.json')
print(files)
merged=[]
files.pop()
for file in files:
    with open(file,'r') as file:
        merged.append(file.read())
print(merged)
with open('units3.json','w') as outputfile:
    json.dump(merged,outputfile,indent=4)
    
