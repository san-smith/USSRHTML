'''

@author: Smith
'''

import USSRHTMLCore

f = open('./sample/index.txt','w')
f.write('\ягтр(\голова()\тело(Привет, Мир!))')
f.close()

f = open('./sample/index.txt')
line = f.readline()
print(line)
f.close()