lst_1 = ['Model = K80+I', 'partition = 010010', '-lnL = 1348.3477', 'K = 51', 
         'kappa = 1.5150 (ti/tv = 0.7575)', 'gamma shape = 0.1190']

for num, i in enumerate(lst_1):
    lst_1[num] = i.translate(None, ' \r\n)')
    if '(ti/tv' in i:
        tmp = (lst_1.pop(num)).split('(')
        lst_1.insert(num, tmp[0])
        lst_1.append(tmp[1])

print lst_1