arr=[0,1,3,4,0,0,0,1,1]
arr=[str(x) for x in arr]
duplicates={}
import re
for i in arr:
    duplicates[i]=[]
    if i in duplicates.keys():
        duplicates[i].append(arr.index(i))
    
print(duplicates)


