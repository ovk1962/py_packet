#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_TEST.py
#
#=======================================================================
import os, sys, math, time, sqlite3, logging
from datetime import datetime, timezone
import math
#from ipdb import set_trace as bp    # to set breakpoints just -> bp()
import PySimpleGUI as sg
#=======================================================================
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda s: sg.PopupError(s, no_titlebar = False, keep_on_top=True)
wrn_lmb = lambda s: sg.PopupOK(s,  background_color = 'Gold', no_titlebar = False, keep_on_top=True)
ok_lmb  = lambda st,s: sg.PopupOK(s,  title=st, background_color = 'LightGreen', no_titlebar = False, keep_on_top=True)
menu_def = [sg.Menu([
            ['TABLES', ['CFG_SOFT',    'CFG_PACK',    'DATA_FUT',    'DATA_PACK_RATIO',  '---',
                        'DATA_in_TXT', 'CLEAR_TABLES', '---', 'Exit',],]
                    ],
            tearoff=False, key='MENU') ]
#=======================================================================
class cnst():
    # cfg_soft
    titul, path_file_DATA, path_file_HIST, dt_start, path_file_TXT = range(5)
    head_cfg_soft  = ['name', 'val']
    # cfg_pck
    kNm, kKoef, kNul, kEma, kGo, kPos, kNeg = range(7)
    head_cfg_pack  = ['nm', 'koef', 'nul', 'ema', 'go', 'pos', 'neg']
    #
    head_data_fut  = ['P_code', 'Rest', 'Var_mrg', 'Open_prc', 'Last_prc',
                'Ask', 'Buy_qty', 'Bid', 'Sell_qty', 'Fut_go', 'Open_pos' ]
    sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos  = range(11)
    #
    head_DATA_PACK_RATIO = ['nm', 'koef', 'pos', 'neg', 'ratio']
    # arr_fut_a  arr_fut_t
    fAsk, fBid = range(2)
    # account
    aBal, aPrf, aGo, aDep = range(4)
    # arr_pck_a  arr_pck_t
    pAsk, pBid, pEMAf, pEMAf_r, pCnt_EMAf_r = range(5)

#=======================================================================
class Class_DB_SQLite():
    def __init__(self, path_db):
        self.path_db  = path_db

    def read_tbl(self, nm_tbl):
        print('=> _SQLite read_tbl ', nm_tbl)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- read  table   ---------------------------------
                cur.execute('SELECT * from ' + nm_tbl)
                arr = cur.fetchall()    # read LIST arr from TABLE nm_tbl
                lst_arr = []
                for item in arr: lst_arr.append(list(item))
        except Exception as ex:
            return [1, ex]
        #print('stop READ')
        return [0, lst_arr]

    def update_tbl(self, nm_tbl, buf_arr, val = ' VALUES(?,?)', p_append = False):
        print('=> _SQLite update_tbl ', nm_tbl)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- update table nm_tbl ---------------------------
                if p_append == False:
                    cur.execute('DELETE FROM ' + nm_tbl)
                cur.executemany('INSERT INTO ' + nm_tbl + val, buf_arr)
                conn.commit()
                #--- read  table   ---------------------------------
                cur.execute('SELECT * from ' + nm_tbl)
                arr = cur.fetchall()    # read LIST arr from TABLE nm_tbl
        except Exception as ex:
            return [1, ex]
        return [0, arr]
#=======================================================================
class Class_LOGGER():
    def __init__(self, path_log):
        #self.logger = logging.getLogger(__name__)
        self.logger = logging.getLogger('__main__')
        self.logger.setLevel(logging.INFO)
        # create a file handler
        self.handler = logging.FileHandler(path_log)
        self.handler.setLevel(logging.INFO)
        # create a logging format
        #self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)

        # add the handlers to the logger
        self.logger.addHandler(self.handler)
    #-------------------------------------------------------------------
    def wr_log_info(self, msg):
        self.logger.info(msg)
    #-------------------------------------------------------------------
    def wr_log_error(self, msg):
        self.logger.error(msg)
#=======================================================================
class Class_str_FUT_PCK(): # Class_str_FUT  Class_str_PCK  Class_cfg_PCK
    def __init__(self):
        self.ind_s, self.dt = 0, ''
        self.arr = []
    def __retr__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
    def __str__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
#=======================================================================
class Class_FUT():
    def __init__(self):
        self.sP_code, self.arr = '', []
    def __retr__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
    def __str__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
#=======================================================================
class Class_ACCOUNT():
    def __init__(self):
        self.ss = '        bal,      prf,      go,       dep'
        self.dt, self.arr  = '', []
    def __retr__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
    def __str__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
#=======================================================================
class Class_GL():
    def __init__(self):
        c_dir    = os.path.abspath(os.curdir)
        self.lg_file =    Class_LOGGER(c_dir + '\\LOG\\gl_LOG.log')
        self.db_ARCHV = Class_DB_SQLite(c_dir + '\\DB\\db_ARCH.sqlite')
        self.db_TODAY = Class_DB_SQLite(c_dir + '\\DB\\db_TODAY.sqlite')
        #
        self.cfg_soft = [] # list of table 'cfg_SOFT'
        self.cfg_pck  = [] # list of table 'cfg_PACK' (unpack)
        self.dt_fut   = [] # list obj FUTs from table 'data_FUT'
        self.account = Class_ACCOUNT()  # obj Class_ACCOUNT()
        #
        self.arr_fut_t = []
        self.arr_fut_a = []
        self.arr_pck_t = []
        self.arr_pck_a = []
        #
        self.time_1_min = 0
        self.dt_start_sec = 0
        #
        self.dt_file = 0        # curv stamptime data file path_file_DATA
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.data_in_file = []  # ar_file   list of strings from path_file_DATA
        self.hist_in_file = []  # list of strings from path_file_HIST
        #
    def check_MARKET_time(self, term_dt):
        try:
            dtt = datetime.strptime(term_dt, "%d.%m.%Y %H:%M:%S")
            cur_time = dtt.second + 60 * dtt.minute + 60 * 60 * dtt.hour
            if (
                (cur_time > 35995  and # from 09:59:55 to 14:00:05
                cur_time < 50415) or   #
                (cur_time > 50685  and # from 14:04:55 to 18:45:05
                cur_time < 67505) or
                (cur_time > 68695  and # from 19:04:55 to 23:50:05
                cur_time < 85805)):
                    return True
        except Exception as ex:
            print('ERROR term_dt = ', term_dt)
        return False

    def prn_arr(self, name_arr, arr):
        print('len(' + name_arr + ')   => ' + str(len(arr)) + '\n' )
        if len(arr) > 4:
            for i in [0,1]: print(arr[i],'\n')
            print('+++++++++++++++++++++++++\n')
            for i in [-2,-1]: print(arr[i],'\n')
        else:
            for item in arr: print(item, '\n')

    def read_cfg_soft(self):
        print('=> _GL read_cfg_soft')
        try:
            tbl = self.db_TODAY.read_tbl('cfg_SOFT')
            if tbl[0] > 0: return tbl
            self.cfg_soft = tbl[1]
            # frm = '%Y-%m-%d %H:%M:%S'
            # self.dt_start_sec = \
                # int(datetime.strptime(self.dt_start, frm).replace(tzinfo=timezone.utc).timestamp())
            for item in self.cfg_soft: print(item)
            #ok_lmb('read_cfg_soft', self.cfg_soft)
        except Exception as ex:
            return [1, ex]
        return [0, tbl]

    def read_cfg_pack(self):
        print('=> _GL read_cfg_pack')
        try:
            tbl = self.db_TODAY.read_tbl('cfg_PACK')
            if tbl[0] > 0: return tbl
            self.cfg_pck = []
            for item in tbl[1]:
                arr_k    = item[cnst.kKoef].split(',')
                arr_koef, buf = [], []
                for item_k in arr_k:             # '0:2:SR' => [0, 32, 'SR']
                    arr_koef.append([int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')])
                buf = [item[cnst.kNm],
                        arr_koef,
                        int(item[cnst.kNul]),
                        [int(e) for e in item[cnst.kEma].split(':')],
                        int(item[cnst.kGo]),
                        int(item[cnst.kPos]),
                        int(item[cnst.kNeg])]
                while len(cnst.head_cfg_pack) > len(buf):
                    buf.append('')
                self.cfg_pck.append(buf)
            rep = self.calc_cfg_pack()
            if rep[0] > 0:
                return [1, rep[1]]
        except Exception as ex:
            return [1, ex]
        return [0, tbl]

    def calc_cfg_pack(self):
        print('=> _GL calc_cfg_pack')
        try:
            mtrx = []
            for item in self.dt_fut:
                mtrx.append([item.sP_code] + item.arr)
            # kNm, kKoef, kNul, kEma, kGo, kPos, kNeg = range(7)
            # kKoef => [0, 2, 'SR'] =>  list =>
            #           0 -index FUT   1 - number fut's  2 - name fut
            cfg_go_pos_neg = []
            for item in self.cfg_pck:
                pck_go, pck_pos, pck_neg = 0, 0, 0
                for pck in item[cnst.kKoef]:
                    prc = int((mtrx[pck[0]][cnst.sAsk] + mtrx[pck[0]][cnst.sBid])/2)
                    if pck[0] != 9:
                        pck_go += int(abs(pck[1]) * mtrx[pck[0]][cnst.sFut_go])
                    else:
                        pck_go += int(abs(pck[1]/10) * mtrx[pck[0]][cnst.sFut_go])
                    if pck[1] > 0:  pck_pos += int(prc * pck[1])
                    else:           pck_neg += int(prc * abs(pck[1]))
                cfg_go_pos_neg.append( [pck_go, pck_pos, pck_neg] )
            for i, item in enumerate(cfg_go_pos_neg):
                self.cfg_pck[i][-3:] = item

            rep = self.update_tbl_cfg_pack()
            if rep[0] > 0:
                return [1, rep[1]]
        except Exception as ex:
            print('calc_cfg_pack = ', ex)
            return [1, ex]
        return [0, 'ok']

    def update_tbl_cfg_pack(self):
        print('=> _GL update_tbl_cfg_pack ')
        try:
            cfg_lst,  cfg = [],  self.cfg_pck
            #  ['pack1', [[0, 3, 'SR'], [1, 2, 'GZ']], 7517, [1111, 150], 0, 0, 0]
            #  ['pack1', '0:3:SR,1:2:GZ', 7517, '1111:150', 0, 0, 0]
            for j in range(len(cfg)):
                str_koef = ''
                for ss in cfg[j][cnst.kKoef]:
                    str_koef += ':'.join((str(s) for s in ss)) + ','
                cfg_lst.append([cfg[j][cnst.kNm],       # kNm
                                str_koef[:-1],          # kKoef
                                cfg[j][cnst.kNul],      # kNul
                                ':'.join(str(s) for s in cfg[j][cnst.kEma]),
                                cfg[j][cnst.kGo],       # kGo
                                cfg[j][cnst.kPos],      # kPos
                                cfg[j][cnst.kNeg]       # kNeg
                                ])
            r_update = self.db_TODAY.update_tbl('cfg_PACK', cfg_lst, val = ' VALUES(?,?,?,?,?,?,?)')
            if r_update[0] == 1:
                print(r_update[1])
                return [1, r_update[1]]
        except Exception as ex:
            return [1, ex]
        return [0, cfg_lst]

    def rd_term_FUT(self):
        # read data FUT from file 'path_file_DATA'----------------------
        # check -
        #       file 'file_path_DATA'
        #       size of file
        #       time modificated of file
        #       size of TERM file
        # update table 'data_FUT' into DB 'db_FUT_tod'------------------
        print('=> _TERM rd_term_FUT')
        try:
            #--- check file self.file_path_DATA ------------------------
            path_data = self.cfg_soft[cnst.path_file_DATA][1]
            if not os.path.isfile(path_data):
                return [2, 'can not find file => path_file_DATA']
            buf_stat = os.stat(path_data)
            #--- check size of file ------------------------------------
            if buf_stat.st_size == 0:
                return [3, 'size DATA file is NULL']
            #--- check time modificated of file ------------------------
            if int(buf_stat.st_mtime) == self.dt_file:
                #str_dt_file = datetime.fromtimestamp(self.dt_file).strftime('%H:%M:%S')
                return [4, 'FILE is not modificated ' + time.strftime("%M:%S", time.gmtime())]
            else:
                self.dt_file = int(buf_stat.st_mtime)
            #--- read TERM file ----------------------------------------
            buf_str = []
            with open(path_data,"r") as fh:
                buf_str = fh.read().splitlines()
            #--- check size of list/file -------------------------------
            if len(buf_str) == 0:
                return [5, 'size buf_str is NULL']
            self.data_in_file = []
            self.data_in_file = buf_str[:]
            #for i in self.data_in_file:   print(i)
            #--- update table 'data_FUT' -------------------------------
            buf_arr = ((j,) for j in self.data_in_file)
            rep = self.db_TODAY.update_tbl('data_FUT', buf_arr, val = ' VALUES(?)')
            if rep[0] > 0: return rep
            #
            self.read_data_fut()
        except Exception as ex:
            return [1, ex]
        return [0, 'ok']

    def rd_term_HST(self):
        # read HIST from file 'path_file_HIST'--------------------------
        # check -
        #       file 'path_file_HIST'
        #       size of file
        #       read HIST file
        #       size of TERM file
        #       MARKET time
        # update table 'hist_FUT' into DB 'db_HIST_tod'-----------------
        # unpack table 'hist_FUT' into 'arr_fut_t'    ------------------
        print('=> _TERM rd_term_HST')
        try:
            path_hist = self.cfg_soft[cnst.path_file_HIST][1]
            #--- check file self.path_file_HIST ------------------------
            if not os.path.isfile(path_hist):
                return [2, 'can not find file => path_file_HIST']
            buf_stat = os.stat(path_hist)
            #--- check size of file ------------------------------------
            if buf_stat.st_size == 0:
                return [3, 'size HIST file is NULL']
            #--- read HIST file ----------------------------------------
            buf_str = []
            with open(path_hist,"r") as fh:
                buf_str = fh.read().splitlines()
            #--- check size of list/file -------------------------------
            if len(buf_str) == 0:
                return [4, 'the size buf_str(HIST) is NULL ']
            #--- check MARKET time from 10:00 to 23:45 -----------------
            self.hist_in_file = []
            error_MARKET_time = False
            for i, item in enumerate(buf_str):
                term_dt = item.split('|')[0]
                if self.check_MARKET_time(term_dt):
                    self.hist_in_file.append(item)
                else:
                    error_MARKET_time = True
                    print('error string is ',i)
            #--- repeir file 'path_file_HIST' --------------------------
            if error_MARKET_time:
                with open(path_hist, 'w') as file_HIST:
                    for item in self.hist_in_file:
                        file_HIST.write(item+'\n')
            #--- update table 'hist_FUT' -------------------------------
            buf_list =[]
            pAsk, pBid = range(2)
            if len(self.hist_in_file) > 0:
                frm = '%d.%m.%Y %H:%M:%S'
                for it in self.hist_in_file:
                    dtt = datetime.strptime(it.split('|')[0], frm)
                    ind_sec  = int(dtt.replace(tzinfo=timezone.utc).timestamp())
                    buf_list.append([ind_sec, it])
            rep = self.db_TODAY.update_tbl('hist_FUT', buf_list, val = ' VALUES(?,?)')
            if rep[0] > 0: return rep
            #--- update 'self.arr_fut_t' -------------------------------
            self.arr_fut_t = []
            self.arr_fut_t = self.unpack_str_fut(buf_list)[1]

        except Exception as ex:
            print('rd_term_HST\n' + str(ex))
            return [1, str(ex)]
        return [0, 'ok']

    def read_data_fut(self):
        print('=> _GL read_data_fut')
        try:
            tbl = self.db_TODAY.read_tbl('data_FUT')
            if tbl[0] > 0: return tbl
            #self.dt_fut = tbl[1]

            self.dt_fut = []
            acc = self.account
            for i, item in enumerate(tbl[1]):
                lst = ''.join(item).replace(',','.').split('|')
                del lst[-1]
                if   i == 0:
                    acc.dt  = lst[0]
                elif i == 1:
                    acc.arr = [float(j) for j in lst]
                else:
                    b_fut = Class_FUT()
                    b_fut.sP_code = lst[0]
                    b_fut.arr     = [float(k) for k in lst[1:]]
                    self.dt_fut.append(b_fut)
            #print(self.account)
            #for i in self.dt_fut:   print(i)

        except Exception as ex:
            return [1, ex]
        return [0, tbl]

    def unpack_str_fut(self, hist_fut):
        print('=> _PACK unpack_str_fut ', len(hist_fut))
        try:
            arr_fut = []
            for cnt, i_str in enumerate(hist_fut):
                mn_pr, mn_cr = '', ''
                if cnt == 0 :
                    mn_pr, mn_cr = '', '00'
                else:
                    mn_pr = hist_fut[cnt-1][1][14:16]
                    mn_cr = hist_fut[cnt-0][1][14:16]
                if mn_pr != mn_cr:
                    s = Class_str_FUT_PCK()
                    s.ind_s = i_str[0]
                    s.dt    = i_str[1].split('|')[0].split(' ')
                    arr_buf = i_str[1].replace(',', '.').split('|')[1:-1]
                    for item in (zip(arr_buf[::2], arr_buf[1::2])):
                        s.arr.append([float(item[cnst.fAsk]), float(item[cnst.fBid])])
                    arr_fut.append(s)
                if len(arr_fut) % 1000 == 0:  print(len(arr_fut), end='\r')
        except Exception as ex:
            return [1, ex]
        return [0, arr_fut]

    def clc_ASK_BID(self, arr_FUT):
        print('=> _PACK clc_ASK_BID ', len(arr_FUT))
        try:
            b_null = True if (self.cfg_pck[0][cnst.kNul] == 0) else False
            ''' init  table ARCHIV_PACK  --------------------'''
            arr_pk  = []  # list of Class_str_FUT_PCK()
            nm_pcks = len(self.cfg_pck)
            for idx, item in enumerate(arr_FUT): # change STRINGs
                if idx % 1000 == 0:  print(idx, end='\r')
                arr_bb = Class_str_FUT_PCK()
                arr_bb.ind_s, arr_bb.dt  = item.ind_s, item.dt
                for p in range(nm_pcks):        # change PACKETs
                    ask_p, bid_p, arr_pp = 0, 0, [0, 0, 0, 0, 0]
                    for jdx, jtem in enumerate(self.cfg_pck[p][cnst.kKoef]): # calc PACK
                        i_koef, k_koef = jtem[0], jtem[1]
                        if k_koef > 0 :
                            ask_p +=  k_koef * item.arr[i_koef][cnst.fAsk]
                            bid_p +=  k_koef * item.arr[i_koef][cnst.fBid]
                        if k_koef < 0 :
                            ask_p +=  k_koef * item.arr[i_koef][cnst.fBid]
                            bid_p +=  k_koef * item.arr[i_koef][cnst.fAsk]

                    if idx == 0 and b_null:
                        arr_pp = [0, 0, 0, 0, 0]
                        self.cfg_pck[p][cnst.kNul]= int((ask_p + bid_p)/2)
                        arr_bb.arr.append(arr_pp)
                        continue
                    arr_pp = [int(ask_p - self.cfg_pck[p][cnst.kNul]), int(bid_p - self.cfg_pck[p][cnst.kNul]), 0, 0, 0]
                    arr_bb.arr.append(arr_pp)
                arr_pk.append(arr_bb)

        except Exception as ex:
            return [1, ex]

        return [0, arr_pk]

    def clc_EMA(self, arr_pk, last_pk):
        print('=> _PACK clc_EMA ', len(arr_pk))
        b_null = True if (last_pk.ind_s == 0) else False
        try:
            nm_pcks = len(self.cfg_pck)
            koef_EMA, k_EMA_rnd = [], []
            for kdx in range(nm_pcks):
                k_ema = self.cfg_pck[kdx][cnst.kEma]
                koef_EMA.append(round(2/(1+int(k_ema[0])),5))
                k_EMA_rnd.append(int(k_ema[1]))
            for idx, item in enumerate(arr_pk):
                if idx % 1000 == 0:  print(idx, end='\r')
                if idx == 0:
                    if not b_null:
                        arr_pk[0] = last_pk
                else:
                    for pdx, ptem in enumerate(item.arr):
                        cr = arr_pk[idx].arr[pdx]
                        pr = arr_pk[idx-1].arr[pdx]
                        cr[cnst.pEMAf]  = round(pr[cnst.pEMAf] + (int((ptem[cnst.pAsk] + ptem[cnst.pBid])/2) - pr[cnst.pEMAf]) * koef_EMA[pdx], 1)
                        cr[cnst.pEMAf_r]= k_EMA_rnd[pdx] * math.ceil(cr[cnst.pEMAf] / k_EMA_rnd[pdx] )
                        if pr[cnst.pEMAf_r] > cr[cnst.pEMAf_r]:
                            cr[cnst.pCnt_EMAf_r] = 0 if pr[cnst.pCnt_EMAf_r] > 0 else pr[cnst.pCnt_EMAf_r]-1
                        elif pr[cnst.pEMAf_r] < cr[cnst.pEMAf_r]:
                            cr[cnst.pCnt_EMAf_r] = 0 if pr[cnst.pCnt_EMAf_r] < 0 else pr[cnst.pCnt_EMAf_r]+1
                        else:
                            cr[cnst.pCnt_EMAf_r] = pr[cnst.pCnt_EMAf_r]
        except Exception as ex:
            return [1, ex]

        return [0, arr_pk]

    def pack_arr_pck(self, arr_pk, db_pk, nm_tbl_pk):
        print('=> _PACK pack_arr_pck ', nm_tbl_pk, len(arr_pk))
        try:
            pck_list = []
            #pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
            if len(arr_pk) > 0:
                for i_hist, item_hist in enumerate(arr_pk):
                    if i_hist % 1000 == 0:  print(str(i_hist), end='\r')
                    #bp()
                    buf_dt = item_hist.dt[0] + ' ' + item_hist.dt[1] + ' '
                    buf_s = ''
                    for i_pack, item_pack in enumerate(item_hist.arr):
                        buf_s += str(item_pack[cnst.pAsk]) + ' ' + str(item_pack[cnst.pBid])   + ' '
                        buf_s += str(item_pack[cnst.pEMAf]) + ' ' + str(item_pack[cnst.pEMAf_r]) + ' '
                        buf_s += str(item_pack[cnst.pCnt_EMAf_r]) + '|'
                    pck_list.append((item_hist.ind_s, buf_dt + buf_s.replace('.', ',')))
            ''' rewrite data from table ARCHIV_PACK & PACK_TODAY & DATA ----'''
            r_update = db_pk.update_tbl(nm_tbl_pk, pck_list, val = ' VALUES(?,?)')
            if r_update[0] == 1:
                return [1, r_update[1]]

        except Exception as ex:
            return [1, ex]
        return [0, pck_list]

    def calc_arr_pck(self):
        print('=> _PACK calc_arr_pck ')
        try:
            for i in range(len(self.cfg_pck)):
                self.cfg_pck[i][cnst.kNul] = 0
            rep = self.clc_ASK_BID(self.arr_fut_a)
            if rep[0] > 0:
                return [2, 'Did not CALC ASK_BID *hist_PACK*!']
            self.arr_pck_a = rep[1]
            self.update_tbl_cfg_pack()
            self.read_cfg_pack()
            rep = self.clc_EMA(self.arr_pck_a, Class_str_FUT_PCK())
            if rep[0] > 0:
                return [3, 'Did not CALC EMA *hist_PACK*!']
            self.arr_pck_a = rep[1]
            rep = self.pack_arr_pck(self.arr_pck_a, self.db_ARCHV, 'hist_PACK')
            if rep[0] > 0:
                return [4, 'Did not update *hist_PACK*!']
        except Exception as ex:
            return [1, ex]
        return [0, 'ok']

    def calc_arr_pck_today(self):
        print('=> _PACK calc_arr_pck_today ')
        try:
            r_rd = self.rd_term_FUT()
            if r_rd[0] > 0:
                return [2, 'Did not rd_term_FUT *hist_FUT* today!\n' + r_rd[1]]
            dtt = datetime.strptime(self.account.dt, "%d.%m.%Y %H:%M:%S")
            if dtt.minute == self.time_1_min:
                return [3, 'Did not change time!']
            self.time_1_min = dtt.minute
            hst = self.rd_term_HST()
            if hst[0] > 0:
                return [4, 'Problem of rd_term_HST!\n' + hst[1]]
            #***
            r_clc = self.clc_ASK_BID(self.arr_fut_t)
            if r_clc[0] > 0:
                return [5, 'Problem of clc_ASK_BID!\n' + r_clc[1]]
            self.arr_pck_t = r_clc[1]

            r_pck = self.clc_EMA(self.arr_pck_t, self.arr_pck_a[-1])
            if r_pck[0] > 0:
                return [6, 'Problem of clc_EMA!\n' + r_pck[1]]
            self.arr_pck_t = r_pck[1][1:]
            pck_t = self.pack_arr_pck(self.arr_pck_t, self.db_TODAY, 'hist_PACK')
            if pck_t[0] > 0:
                return [7, 'Problem of pack_arr_pck!\n' + pck_t[1]]
        except Exception as ex:
            return [1, str(ex)]
        return [0, 'ok']
#=======================================================================
def open_CFG_SOFT(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    layout_CFG_SOFT =[  menu_def,
                        [sg.Table(
                            values   = _gl.cfg_soft,
                            num_rows = min(len(_gl.cfg_soft), 10),
                            headings = cnst.head_cfg_soft,
                            key      = '_CFG_SOFT_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'lightblue',
                            )],
                        [sg.Button(' EDIT ', key='-EDIT_CFG_SOFT-'),
                         sg.Button('SAVE',   key='-SAVE_CFG_SOFT-'),
                         sg.T(55*' '),
                         sg.Exit()]]
    wndw = sg.Window('CFG_SOFT', location=(50, 100)).Layout(layout_CFG_SOFT)
    return wndw
#=======================================================================
def open_CFG_PACK(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    rep = _gl.read_cfg_pack()
    layout_CFG_PACK =[  menu_def,
                        [sg.Table(
                            values   = _gl.cfg_pck,
                            num_rows = min(len(_gl.cfg_pck), 25),
                            headings = cnst.head_cfg_pack,
                            key      = '_CFG_PACK_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'coral',
                            )],
                        [sg.Button(' EDIT ', key='-EDIT_CFG_PACK-'),
                         sg.Button(' ADD  ', key='-ADD_CFG_PACK-' ),
                         sg.Button(' DEL  ', key='-DEL_CFG_PACK-' ),
                         sg.Button(' SAVE ', key='-SAVE_CFG_PACK-'),
                         sg.T(110*' '),
                         sg.Exit()]]
    wndw = sg.Window('CFG_PACK', location=(100, 150)).Layout(layout_CFG_PACK)
    return wndw
#=======================================================================
def open_DATA_FUT(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    mtrx = []
    for item in _gl.dt_fut:
        bf = []
        bf.append(item.sP_code)
        for jtem in item.arr:
            bf.append(jtem)
        mtrx.append(bf)
    layout_DATA_FUT =[  menu_def,
                        [sg.Table(
                            values   = mtrx,
                            num_rows = min(len(mtrx), 30),
                            headings = cnst.head_data_fut,
                            key      = '_DATA_FUT_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'lightsteelblue',
                            )],
                        [sg.Exit()]]
    wndw = sg.Window('DATA_FUT', location=(150, 200)).Layout(layout_DATA_FUT)
    return wndw
#=======================================================================
def open_DATA_PACK_RATIO(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    # ['nm', 'koef', 'pos', 'neg', 'ratio']
    mtrx = []
    for item in _gl.cfg_pck:
        mtrx.append([item[cnst.kNm],
                    item[cnst.kKoef],
                    item[cnst.kPos],
                    item[cnst.kNeg],
                    round(item[cnst.kPos]/item[cnst.kNeg],1) ])
    layout_DATA_PACK_RATIO =[  menu_def,
                        [sg.Table(
                            values   = mtrx,
                            num_rows = min(len(mtrx), 30),
                            headings = cnst.head_DATA_PACK_RATIO,
                            key      = '_DATA_PACK_RATIO_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'lightgreen',
                            )],
                        [sg.Exit()]]
    wndw = sg.Window('DATA_PACK_RATIO', location=(200, 250)).Layout(layout_DATA_PACK_RATIO)
    return wndw
#=======================================================================
def open_CLEAR_TABLES(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    # ['nm', 'start', 'end', 'lench']
    af, ap, tf, tp = _gl.arr_fut_a, _gl.arr_pck_a, _gl.arr_fut_t, _gl.arr_pck_t
    s1, s2, s3, s4 = [], [], [], []
    if len(tf) == 0:  s1 = ['TODAY_hist_FUT', 0, 0, 0]
    else: s1 = ['TODAY_hist_FUT', tf[0].dt, tf[-1].dt, len(tf)]
    if len(tp) == 0:  s2 = ['TODAY_hist_PCK', 0, 0, 0]
    else: s2 = ['TODAY_hist_PCK', tp[0].dt, tp[-1].dt, len(tp)]
    s3 = ['ARCH_hist_FUT ', af[0].dt, af[-1].dt, len(af)]
    if len(ap) == 0:  s4 = ['ARCH_hist_PCK', 0, 0, 0]
    else: s4 = ['ARCH_hist_PCK', ap[0].dt, ap[-1].dt, len(ap)]
    layout_CLEAR_TABLES =[  menu_def,
                        [sg.Table(
                            values   = [s1, s2, s3, s4],
                            num_rows = 4,
                            headings = ['nm', 'start', 'end', 'lench'],
                            key      = '_CLEAR_TABLES_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'lightgreen',
                            )],
                        [sg.Button('CLR_TODAY',    key='-CLR_TODAY-'),
                         sg.Button('CLR_ARC_PACK', key='-CLR_ARC_PACK-'),
                         sg.T(95*' '),
                         sg.Exit()]]
    wndw = sg.Window('CLEAR_TABLES', location=(250, 50)).Layout(layout_CLEAR_TABLES)
    return wndw
#=======================================================================
def open_DATA_in_TXT(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    layout_DATA_in_TXT =[  menu_def,
                        [sg.Table(
                            values   = _gl.cfg_soft[-2:],
                            num_rows = min(len(_gl.cfg_soft[-2:]), 10),
                            headings = cnst.head_cfg_soft,
                            key      = '_DATA_in_TXT_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'lightblue',
                            )],
                        [
                         sg.Button('SAVE',   key='-SAVE_DATA_in_TXT-'),
                         sg.Button('APPEND', key='-APPEND_TXT_in_ARCH-'),
                         sg.T(45*' '),
                         sg.Exit()]]
    wndw = sg.Window('DATA_in_TXT', location=(50, 100)).Layout(layout_DATA_in_TXT)
    return wndw
#=======================================================================
def event_menu_CFG_SOFT(ev, val, wndw, _gl):
    rq = [0,ev]
    #-------------------------------------------------------------------
    if ev == '-EDIT_CFG_SOFT-':
        print('-EDIT_CFG_SOFT-')
        if len(val['_CFG_SOFT_table_']) == 0:
            wrn_lmb('\n You MUST choise ROW !\n')
        else:
            slct = _gl.cfg_soft[val['_CFG_SOFT_table_'][0]]
            #
            slct_val = ['titul', 'path_file_DATA', 'path_file_HIST', 'path_file_TXT']
            if slct[0] in slct_val:
                for item in slct_val:
                    if item == slct[0]:
                        if item == 'titul':
                            txt = sg.PopupGetText(slct[0], default_text = slct[1])
                        else:
                            txt = sg.PopupGetFile( slct[1], title = slct[0])
                        if txt != None:
                            _gl.cfg_soft[val['_CFG_SOFT_table_'][0]] = (item, txt)
                            wndw.FindElement('_CFG_SOFT_table_').Update(_gl.cfg_soft)
            else:
                #sg.PopupError('\n' + slct[0] + '\nSorry, can not change\n', no_titlebar = True)
                err_lmb(s_lmb(slct[0]) + s_lmb('Sorry, can not change'))
    #-------------------------------------------------------------------
    if ev == '-SAVE_CFG_SOFT-':
        print('-SAVE_CFG_SOFT-')
        rq = _gl.db_TODAY.update_tbl('cfg_SOFT',
                                _gl.cfg_soft, val = ' VALUES(?,?)')
        if rq[0] > 0:
            err_lmb(s_lmb('Did not update cfg_SOFT!') + s_lmb(rep[1]))
        else:
            ok_lmb('event_menu_CFG_SOFT', s_lmb('Updated *cfg_SOFT* successfully !'))
    #-------------------------------------------------------------------
    print('rq = ', rq)
#=======================================================================
def event_menu_CFG_PACK(ev, val, wndw, _gl):
    rq = [0,ev]
    #-------------------------------------------------------------------
    if ev == '-EDIT_CFG_PACK-':
        print('-EDIT_CFG_PACK-')
        if len(val['_CFG_PACK_table_']) == 0:
            wrn_lmb('\n You MUST choise ROW !\n')
        else:
            slct = _gl.cfg_pck[val['_CFG_PACK_table_'][0]]
            chng = cnst.head_cfg_pack[:]
            for i, item in enumerate(slct):
                if i in [cnst.kNm, cnst.kKoef, cnst.kEma]:
                    pop_txt = item
                    if i == cnst.kKoef:
                        pop_txt = ''
                        for ss in item:
                            pop_txt += ':'.join((str(s) for s in ss)) + ','
                        pop_txt = pop_txt[:-1]
                    if i == cnst.kEma:
                        pop_txt = ':'.join(str(s) for s in item)
                    txt = sg.PopupGetText( cnst.head_cfg_pack[i], size=(55,1), default_text = pop_txt)
                    if (txt == None) or (txt == pop_txt): chng[i] = item
                    else:
                        if i == cnst.kNm:
                            chng[i] = txt
                        if i == cnst.kKoef:
                            arr_k    = txt.split(',')
                            arr_koef = []
                            for item_k in arr_k:
                                arr_koef.append([int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')])
                            chng[i] = arr_koef
                        if i == cnst.kNul or i == cnst.kGo or i == cnst.kPos or i == cnst.kNeg:
                            if txt.isdigit():   chng[i] = int(txt)
                            else:               chng[i] = item
                        if i == cnst.kEma:
                            chng[i] = [int(e) for e in txt.split(':')]
                else:
                    chng[i] = item
            _gl.cfg_pck[val['_CFG_PACK_table_'][0]] = chng
            wndw.FindElement('_CFG_PACK_table_').Update(_gl.cfg_pck)
    #-------------------------------------------------------------------
    if ev == '-ADD_CFG_PACK-':
        print('-ADD_CFG_PACK-')
        if len(val['_CFG_PACK_table_']) == 0:
            wrn_lmb('\n You MUST choise ROW !\n')
        else:
            slct = _gl.cfg_pck[val['_CFG_PACK_table_'][0]]
            _gl.cfg_pck.append(slct)
            print('append slct  ', slct)
            wndw.FindElement('_CFG_PACK_table_').Update(_gl.cfg_pck)
    #-------------------------------------------------------------------
    if ev == '-DEL_CFG_PACK-':
        print('-DEL_CFG_PACK-')
        if len(val['_CFG_PACK_table_']) == 0:
            wrn_lmb('\n You MUST choise ROW !\n')
        else:
            del _gl.cfg_pck[val['_CFG_PACK_table_'][0]]
            wndw.FindElement('_CFG_PACK_table_').Update(_gl.cfg_pck)
    #-------------------------------------------------------------------
    if ev == '-SAVE_CFG_PACK-':
        print('-SAVE_CFG_PACK-')
        rep = _gl.update_tbl_cfg_pack()
        if rep[0] > 0:
            err_lmb(s_lmb('Did not update cfg_PACK!') + s_lmb(rep[1]))
        else:
            ok_lmb('event_menu_CFG_PACK','Updated *cfg_PACK* successfully !')
#=======================================================================
def event_menu_DATA_in_TXT(ev, val, wndw, _gl):
    rq = [0,ev]
    # save hist TODAY from table in file TXT ---------------------------
    if ev == '-SAVE_DATA_in_TXT-':
        hst = _gl.db_TODAY.read_tbl('hist_FUT')
        if hst[0] > 0:
            err_lmb(s_lmb('Could not read table *hist_FUT*!') + s_lmb(hst[1]))
        else:
            hst_fut_t = hst[1]
            path = _gl.cfg_soft[cnst.path_file_TXT][1]
            txt = sg.PopupGetText( 'Save hist_FUT_today into file',
                                    size=(55,1),  default_text = path)
            if (txt != None):
                #
                # save hist_FUT_today into file ------------------------
                print('len(hist_FUT_today) = ', len(hst_fut_t))
                if len(hst_fut_t) > 0: # change 2020-00-00 to  for name FILE
                    h = hst_fut_t[-1][1]
                    y_m_d = h[6:10] + '-' + h[3:5] + '-' + h[0:2]
                    y_m_d = path.split('***')[0] + y_m_d + path.split('***')[1]
                    print(path+'\n'+y_m_d)
                    with open(y_m_d, 'w') as file_HIST:
                        for item in hst_fut_t:
                            file_HIST.write(item[1]+'\n')
                    #
                    # check print STRINGS for delay more then 1 minute
                    frm = "%d.%m.%Y %H:%M:%S"
                    str_buf = 'start = ' + hst_fut_t[0][1].split('|')[0]
                    print(str_buf)
                    for i, item in enumerate(hst_fut_t[2:]):
                        pr, cr = hst_fut_t[i-1][1], hst_fut_t[i-0][1]
                        dtp = datetime.strptime(str(pr.split('|')[0]), frm)
                        prv_time = dtp.second + 60 * dtp.minute + 60 * 60 * dtp.hour
                        dtc = datetime.strptime(str(cr.split('|')[0]), frm)
                        cur_time = dtc.second + 60 * dtc.minute + 60 * 60 * dtc.hour
                        if (cur_time - prv_time) > 60:
                            str_buf = 'delay = ' + pr.split('|')[0] + ' ... ' + cr.split('|')[0]
                            print(str_buf)
                    str_buf = 'last = ' + hst_fut_t[-1][1].split('|')[0]
                    print(str_buf)
                else:
                    err_lmb(s_lmb('Table *hist_FUT*!') + s_lmb('is EMPTY !!!'))
    #
    # append hist file from TXT in table -------------------------------
    if ev == '-APPEND_TXT_in_ARCH-':
        #--- read HIST file ---
        buf_hist_arch, buf_str, frm = [], [], '%d.%m.%Y %H:%M:%S'
        path_hist = sg.PopupGetFile( 'select TXT hist file',
                title = 'append hist file from TXT in table')
        if path_hist != None:
            try:
                with open(path_hist,"r") as fh:
                    buf_str = fh.read().splitlines()
                #--- create list 'buf_hist' HIST 1 minute 10.00 ... 18.45
                mn_pr, mn_cr, buf_hist = '', '00', []
                for cnt, item in enumerate(buf_str):
                    h_m_s = item.split('|')[0].split(' ')[1].split(':')
                    mn_cr = h_m_s[1]
                    if int(h_m_s[0]) < 10: continue
                    if int(h_m_s[0]) > 18: break
                    if mn_pr != mn_cr:
                        buf_hist.append(item)
                    mn_pr = mn_cr
            except Exception as ex:
                err_lmb(str(ex))
                return

            #--- prepaire 'buf_hist' for update table 'hist_fut'
            for item in buf_hist:
                dtt_cr = datetime.strptime(item.split('|')[0], frm)
                ind_sec = int(dtt_cr.replace(tzinfo=timezone.utc).timestamp())
                buf_hist_arch.append([ind_sec, item])

            rep = _gl.db_ARCHV.update_tbl('hist_FUT', buf_hist_arch, val = ' VALUES(?,?)', p_append = True)
            if rep[0] > 0:
                err_lmb('problem update_tbl *hist_FUT* ARCH ... ' + rep[1])
            else:
                ok_lmb('event_menu_DATA_in_TXT','OK, it was append data in table *hist_FUT* successfully !')
#=======================================================================
def event_menu_CLEAR_TABLES(ev, val, wndw, _gl):
    rq = [0,ev]
    # clear hist TODAY ---------------------------
    if ev == '-CLR_TODAY-':
        rep = _gl.db_TODAY.update_tbl('hist_PACK', [])
        if rep[0] == 0:
            ok_lmb('event_menu_CLEAR_TABLES','OK, clear table *hist_PACK* successfully !')
        else:
            err_lmb('Could not clear table *hist_PACK* !' + rep[1])
        rep = _gl.db_TODAY.update_tbl('hist_FUT', [])
        if rep[0] == 0:
            ok_lmb('event_menu_CLEAR_TABLES','OK, clear table *hist_FUT* successfully !')
        else:
            err_lmb('Could not clear table *hist_FUT* !' + rep[1])
        _gl.arr_fut_t, _gl.arr_pck_t = [], []

#=======================================================================
def main():
    sg.ChangeLookAndFeel('SystemDefault')
    _gl = Class_GL()
    #ok_lmb('main', 'You have init object (_gl) successfully !')
    while True:     # INIT  cycle  -------------------------------------
        rep = _gl.read_cfg_soft()
        if rep[0] > 0:
            err_lmb(s_lmb('Could not read table *cfg_soft*!') + s_lmb(rep[1]))
            return 0
        # else:
            # ok_lmb('main', s_lmb('Read table *cfg_soft* successfully !'))
            # os.system('cls')  # on windows
        #---------------------------------------------------------------
        rep = _gl.rd_term_FUT()
        if rep[0] > 0:
            err_lmb(s_lmb('Could not read term *data_file*!') + s_lmb(rep[1]))
            err_lmb(s_lmb('Lets try to read table *data_fut*!'))
            print('Could not read term *data_file*!')
        # else:
            # ok_lmb('main', s_lmb('Read term *data_file* successfully !'))
            # os.system('cls')  # on windows
        #---------------------------------------------------------------
        rep = _gl.read_data_fut()
        if rep[0] > 0:
            err_lmb(s_lmb('Could not read table *data_fut*!') + s_lmb(rep[1]))
        # else:
            # ok_lmb('main', s_lmb('Read term *data_file* successfully !'))
            # os.system('cls')  # on windows
        #---------------------------------------------------------------
        rep = _gl.read_cfg_pack()
        if rep[0] > 0:
            err_lmb(s_lmb('Could not read table *cfg_pack*!') + s_lmb(rep[1]))
            return 0
        # else:
            # ok_lmb('main', s_lmb('Read table *cfg_pack* successfully !'))
            # os.system('cls')  # on windows
        #---------------------------------------------------------------
        rep = _gl.db_ARCHV.read_tbl('hist_FUT')
        if rep[0] > 0:
            err_lmb(s_lmb('Could not read table *hist_FUT* from ARCH!') + s_lmb(rep[1]))
            return 0
        req = _gl.unpack_str_fut(rep[1])
        if req[0] > 0:
            err_lmb(s_lmb('Did not unpack table *hist_FUT* from ARCH!') + s_lmb(rep[1]))
            return 0
        _gl.arr_fut_a = req[1]
        # ok_lmb('main', s_lmb('Read table *data_fut* successfully !'))
        # os.system('cls')  # on windows
        #---------------------------------------------------------------
        rep = _gl.calc_arr_pck()
        if rep[0] > 0:
            err_lmb(s_lmb('Could not CALC *hist_FUT* from ARCH!') + s_lmb(rep[1]))
            return 0
        # ok_lmb('main', s_lmb('CALC & rewrite table *hist_PACK* from ARCH successfully !'))
        # os.system('cls')  # on windows
        #---------------------------------------------------------------
        rep = _gl.db_TODAY.read_tbl('hist_FUT')
        if rep[0] > 0:
            err_lmb(s_lmb('Could not read table *hist_FUT* from TODAY!') + s_lmb(rep[1]))
            return 0
        req = _gl.unpack_str_fut(rep[1])
        if req[0] > 0:
            err_lmb(s_lmb('Did not unpack table *hist_FUT* from TODAY!') + s_lmb(req[1]))
            return 0
        _gl.arr_fut_t = req[1]
        #ok_lmb('main', s_lmb('Read table *hist_FUT* from TODAY successfully !'))
        #os.system('cls')  # on windows
        #---------------------------------------------------------------
        #if len(_gl.arr_fut_t)  == 0: break
        _gl.dt_file = 0
        rep = _gl.calc_arr_pck_today()
        if rep[0] > 0:
            err_lmb(s_lmb('Problem calc_arr_pck_today  *hist_FUT* from TODAY!') + s_lmb(rep[1]))
            return 0
        #ok_lmb('main', s_lmb('Calc table *hist_FUT* from TODAY successfully !'))
        #os.system('cls')  # on windows

        break     # finish  init  --------------------------------------

    wndw = sg.Window('START').Layout([menu_def, [sg.Exit()]])
    wndw = open_CFG_SOFT(wndw, _gl)
    while True:     # MAIN cycle  --------------------------------------
        # for sg.Input must be => wndw.Read()  OR  timeout > 10000
        event, values = wndw.Read(timeout = 60000)
        print('event = ', event, '     values =', values)
        if event in (None, 'Exit'): break
        if event == '__TIMEOUT__':
            pass
        if event in ['CFG_SOFT', 'CFG_PACK', 'DATA_FUT', 'DATA_PACK_RATIO', 'DATA_in_TXT', 'CLEAR_TABLES']:
            if event == 'CFG_SOFT':
                wndw = open_CFG_SOFT(wndw, _gl)
            if event == 'CFG_PACK':
                wndw = open_CFG_PACK(wndw, _gl)
            if event == 'DATA_FUT':
                wndw = open_DATA_FUT(wndw, _gl)
            if event == 'DATA_PACK_RATIO':
                wndw = open_DATA_PACK_RATIO(wndw, _gl)
            if event == 'DATA_in_TXT':
                wndw = open_DATA_in_TXT(wndw, _gl)
            if event == 'CLEAR_TABLES':
                wndw = open_CLEAR_TABLES(wndw, _gl)
        event_menu_CFG_SOFT(event, values, wndw, _gl)
        event_menu_CFG_PACK(event, values, wndw, _gl)
        event_menu_DATA_in_TXT(event, values, wndw, _gl)
        event_menu_CLEAR_TABLES(event, values, wndw, _gl)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
