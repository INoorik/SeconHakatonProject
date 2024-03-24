flag = input()

mask = ''.join(chr(ord(flag[i])^i) for i in range(len(flag)))

print(mask)
