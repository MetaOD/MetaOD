# let's dedup for the delta debugging style augmentation outputs 

# search for the following patterns and dedup
# [LOG] percentage  0.2527015466697146
# finish with :  (171, 169) (202, 210)

s = set([])
with open("t1") as f:
    lines = f.readlines()

    for i in range(0,len(lines)):
        if "random" in lines[i]:
            title = lines[i].split(":")[1].strip()
        if i == 0:
            continue

        ll = lines[i-1]
        l = lines[i]
        if "percentage" in ll:
            assert "finish" in l
            items = l.split("(")
            k1 = items[1].split(")")[0]
            k2 = items[2].split(")")[0]
            if k1 == k2:
                # skip
                continue
            else:
                # print (title + k1)
                s.add((title+k1))

print (len(s))


