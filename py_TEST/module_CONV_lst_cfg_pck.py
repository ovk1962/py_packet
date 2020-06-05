#-----------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      OVK
#
# Created:     27.05.2020
# Copyright:   (c) OVK 2020
# Licence:     <your licence>
#-----------------------------------------------------------------------
import PySimpleGUI as sg
#=======================================================================
class Class_FUT():
    a, b, c = 1, 2, 3
    def __init__(self):
        self.sP_code, self.arr = '', []
    def __retr__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
    def __str__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
    def prn_cnst(self):
        print('a, b, c => ', self.a, self.b, self.c)

class cnst:
    head_data_fut  = ['P_code', 'Rest', 'Var_mrg', 'Open_prc', 'Last_prc',
                'Ask', 'Buy_qty', 'Bid', 'Sell_qty', 'Fut_go', 'Open_pos' ]
    sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos  = range(11)
    # cfg_pck
    kNm, kKoef, kNul, kEma, kGo = range(5)
    head_cfg_pack  = ['nm', 'koef', 'nul', 'ema', 'go']

arr_fut_DATA = [
    '26.05.2020 20:58:20|',
    '932097.57|-1262.11|350787.33|580048.13|',
    'SRM0|-11|-264|0|19497|19494|1105|19497|754|3981,09|285378|0|',
    'GZM0|-1|5|0|19744|19742|668|19752|532|4036,24|167874|0|',
    'LKM0|0|0|0|55015|54950|276|55015|166|11220,34|29718|0|',
    'RNM0|0|0|0|36226|36223|198|36248|138|7688,57|12400|0|',
    'VBM0|-2|-22|0|3539|3538|682|3540|638|720,96|169378|0|',
    'HYM0|0|0|0|6924|6920|255|6924|89|1413,82|11602|0|',
    'GMM0|0|0|0|222671|222382|125|222759|95|45316,59|11690|0|',
    'SPM0|0|0|0|17820|17815|140|17829|182|3629,78|43462|0|',
    'RIM0|0|0|0|122160|122160|1368|122170|970|28305,77|401420|0|',
    'MMM0|-7|-226,5|0|2755,6|2754,2|329|2755,35|212|3556,81|48476|0|']

def read_fut_DATA():
    try:
        dt_fut = []
        for i, item in enumerate(arr_fut_DATA):
            lst = ''.join(item).replace(',','.').split('|')
            del lst[-1]
            if   i == 0:
                pass
            elif i == 1:
                pass
            else:
                b_fut = Class_FUT()
                b_fut.sP_code = lst[0]
                b_fut.arr     = [float(k) for k in lst[1:]]
                dt_fut.append(b_fut)
        #print(self.account)
        #for i in self.dt_fut:   print(i)

    except Exception as ex:
        return [1, ex]
    return [0, dt_fut]

def main():
    b_fut = Class_FUT()
    b_fut.prn_cnst()

    a_byte = b'\xff'  # 255
    i = ord(a_byte)   # Get the integer value of the byte

    bin = "{0:b}".format(i) # binary: 11111111
    hex = "{0:x}".format(i) # hexadecimal: ff
    oct = "{0:o}".format(i) # octal: 377

    print(bin)
    print(hex)
    print(oct)

    req = read_fut_DATA()
    #for item in req[1]: print(item)
    data_fut = req[1]
    matr = [([item.sP_code] + item.arr) for item in data_fut]
    #print(matr)

    mtrx = []
    for item in data_fut:
        bf = []
        bf.append(item.sP_code)
        for jtem in item.arr:
            bf.append(jtem)
        mtrx.append(bf)
    print(mtrx)

    lst_cfg_pck = ['p22', '0:-3:SR,1:2:GZ', 46, '3333:100',111]
    cfg_pck     = ['p22', [[0,-3,'SR'],[9,20,'MX']], 46, [3333,100], 111]

    pck_go, pck_pos, pck_neg = 0, 0, 0
    for pck in cfg_pck[cnst.kKoef]:
        if pck[0] != 9:
            pck_go += abs(pck[1]) * mtrx[pck[0]][cnst.sFut_go]
            prc = int(1*(mtrx[pck[0]][cnst.sAsk] + mtrx[pck[0]][cnst.sBid])/2)
        else:
            pck_go += abs(pck[1]/10) * mtrx[pck[0]][cnst.sFut_go]
            prc = int(10*(mtrx[pck[0]][cnst.sAsk] + mtrx[pck[0]][cnst.sBid])/2)
        if pck[1] > 0:  pck_pos += prc
        else:           pck_neg += prc

    print('pck_go  = ', pck_go)
    print('pck_pos = ', pck_pos)
    print('pck_neg = ', pck_neg)
    print('rat pos/neg = ', round( pck_neg/pck_pos, 2))

    slct = cfg_pck
    #print('slct = ', slct)
    chng = cnst.head_cfg_pack[:]
    for i, item in enumerate(slct):
        pop_txt = item
        if i == cnst.kKoef:
            pop_txt = ''
            for ss in item:
                pop_txt += ':'.join((str(s) for s in ss)) + ','
            pop_txt = pop_txt[:-1]
        if i == cnst.kEma:
            pop_txt = ':'.join(str(s) for s in item)

##        txt = sg.PopupGetText( cnst.head_cfg_pack[i], size=(55,1), default_text = pop_txt)
##
##        print('txt = ', txt, '   pop_txt = ', pop_txt)
##        if (txt == None) or (txt == pop_txt): chng[i] = item
##        else:
##            if i == cnst.kNm:
##                chng[i] = txt
##            if i == cnst.kKoef:
##                arr_k    = txt.split(',')
##                arr_koef = []
##                for item_k in arr_k:
##                    arr_koef.append([int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')])
##                chng[i] = arr_koef
##            if i == cnst.kNul or i == cnst.kGo:
##                if txt.isdigit():   chng[i] = int(txt)
##                else:               chng[i] = item
##            if i == cnst.kEma:
##                chng[i] = [int(e) for e in txt.split(':')]
##
##        print('chng  =  ', chng)



if __name__ == '__main__':
    main()
