#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_QUIK_mon.py
#
#=======================================================================
import os, sys, math, time, sqlite3, logging
from datetime import datetime, timezone
import math
#from ipdb import set_trace as bp    # to set breakpoints just -> bp()
import PySimpleGUI as sg
#print(sg.__file__)
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
        except Exception as ex:
            return [1, ex]
        #print('stop READ')
        return [0, arr]

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
class Class_str_FUT():
    fAsk, fBid = range(2)
    def __init__(self):
        self.ind_s, self.dt, self.arr  = 0, '', []
    def __retr__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
    def __str__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
#=======================================================================
class Class_str_PCK():
    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
    def __init__(self):
        self.ind_s, self.dt, self.arr  = 0, '', []
    def __retr__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
    def __str__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
#=======================================================================
class Class_ACCOUNT():
    bal, prf, go, dep = range(4)
    def __init__(self):
        self.ss = '        bal,      prf,      go,       dep'
        self.dt, self.arr  = '', []
    def __retr__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
    def __str__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
#=======================================================================
class Class_FUT():
    sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos  = range(11)
    def __init__(self):
        self.sP_code, self.arr = '', []
    def __retr__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
    def __str__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
#=======================================================================
class Class_GL():
    def __init__(self):
        c_dir    = os.path.abspath(os.curdir)
        self.lg_file =    Class_LOGGER(c_dir + '\\LOG\\gl_LOG.log')
        self.db_arc  = Class_DB_SQLite(c_dir + '\\DB\\db_ARCH.sqlite')
        self.db_tod  = Class_DB_SQLite(c_dir + '\\DB\\db_TODAY.sqlite')
        # cfg_soft
        self.titul          = ''    # term ALFA
        self.path_file_DATA = ''    # c:\\str_log_ad_A7.txt
        self.path_file_HIST = ''    # c:\\hist_log_ad_A7.txt
        self.dt_start       = ''    # 2017-01-01 00:00:00
        self.dt_start_sec   = 0     # 2017-01-01 00:00:00
        self.path_file_TXT  = ''    # c:\\hist_log_ALOR.txt
        # cfg_pack
        self.nm   = []  # list NM   of packets
        self.koef = []  # list KOEF of packets
        self.nul  = []  # list NUL  of packets
        self.ema  = []  # list EMA  of packets
        #
        self.dt_start_sec = 0
        #
        self.dt_file = 0        # curv stamptime data file path_file_DATA
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.data_in_file = []  # ar_file   list of strings from path_file_DATA
        self.hist_in_file = []  # list of strings from path_file_HIST
        #
        self.dt_fut  = []               # list of Class_FUT()
        self.account = Class_ACCOUNT()  # obj Class_ACCOUNT()
        #
        #self.hst_fut_t = []
        self.arr_fut_t = []
        #self.hst_fut_a = []
        self.arr_fut_a = []
        #
        #self.hst_pck_t = []
        self.arr_pck_t = []
        #self.hst_pck_a = []
        self.arr_pck_a = []
        #
        self.time_1_min = 0
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

    def prn_cfg(self):
        frm = '{: <18}{: <55}'
        print(frm.format('titul',          self.titul))
        print(frm.format('dt_start',       self.dt_start))
        print(frm.format('dt_start_sec',   str(self.dt_start_sec)))
        print(frm.format('path_file_DATA', self.path_file_DATA))
        print(frm.format('path_file_HIST', self.path_file_HIST))
        print(frm.format('path_file_TXT',  self.path_file_TXT))

    def unpack_cfg_soft(self):
        print('=> _GL unpack_cfg_soft')
        try:
            cfg = self.db_tod.read_tbl('cfg_SOFT')
            if cfg[0] > 0: return cfg
            for item in cfg[1]:
                if item[0] == 'titul'         : self.titul           = item[1]
                if item[0] == 'path_file_DATA': self.path_file_DATA  = item[1]
                if item[0] == 'path_file_HIST': self.path_file_HIST  = item[1]
                if item[0] == 'dt_start'      : self.dt_start        = item[1]
                if item[0] == 'path_file_TXT' : self.path_file_TXT   = item[1]
            frm = '%Y-%m-%d %H:%M:%S'
            self.dt_start_sec = \
                int(datetime.strptime(self.dt_start, frm).replace(tzinfo=timezone.utc).timestamp())
            self.prn_cfg()
        except Exception as ex:
            return [1, ex]
        return [0, cfg]

    def unpack_cfg_pack(self):
        print('=> _GL unpack_cfg_pack ')
        try:
            cfg = self.db_tod.read_tbl('cfg_PACK')
            if cfg[0] > 0: return cfg
            self.nm   = []  # list NM   of packets
            self.koef = []  # list KOEF of packets
            self.nul  = []  # list NUL  of packets
            self.ema  = []
            for item in cfg[1]:
                self.nm.append(item[0])          # ['pckt0']
                arr_k    = item[1].split(',')
                arr_koef = []
                for item_k in arr_k:             # '0:2:SR' => [0, 32, 'SR']
                    buf_k = [int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')]
                    arr_koef.append(buf_k)
                self.koef.append(arr_koef)       #  [[0, 2, 'SR'],[9, -20, 'MX'], ...
                self.nul.append(int(item[2]))    #  [0]
                self.ema.append([int(e) for e in item[3].split(':')]) # [1111, 15]
            #-----------------------------------------------------------
            frm = '{: ^5}{: ^15}{}{}{}'
            print(frm.format('nm','nul','ema[]','        ','koef[]'))
            for i, item in enumerate(self.nm):
                print(frm.format(self.nm[i],
                            str(self.nul[i]),
                                self.ema[i], '   ',
                                self.koef[i]))
            #-----------------------------------------------------------
        except Exception as ex:
            return [1, ex]

        return [0, cfg]

    def pack_arr_cfg(self):
        print('=> _PACK pack_arr_cfg ')
        try:
            cfg_list = []
            for j, jtem in enumerate(self.nm):
                arr_koef = ''
                for ktem in self.koef[j]:
                    str_koef = ':'.join([str(f) for f in ktem])
                    arr_koef += str_koef + ','
                buf = [self.nm[j], arr_koef[:-1], str(self.nul[j]), ':'.join([str(f) for f in self.ema[j]])]
                cfg_list.append(buf)
            r_update = self.db_tod.update_tbl('cfg_PACK', cfg_list, val = ' VALUES(?,?,?,?)')
            if r_update[0] == 1:
                return [1, r_update[1]]

        except Exception as ex:
            return [1, ex]
        return [0, cfg_list]

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
            if not os.path.isfile(self.path_file_DATA):
                return [2, 'can not find file => path_file_DATA']
            buf_stat = os.stat(self.path_file_DATA)
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
            with open(self.path_file_DATA,"r") as fh:
                buf_str = fh.read().splitlines()
            #--- check size of list/file -------------------------------
            if len(buf_str) == 0:
                return [4, 'size buf_str is NULL']
            self.data_in_file = []
            self.data_in_file = buf_str[:]
            #for i in self.data_in_file:   print(i)
            #--- update table 'data_FUT' -------------------------------
            buf_arr = ((j,) for j in self.data_in_file)
            rep = self.db_tod.update_tbl('data_FUT', buf_arr, val = ' VALUES(?)')
            if rep[0] > 0: return rep
            #
            self.unpack_data_in_file()
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
            #--- check file self.path_file_HIST ------------------------
            if not os.path.isfile(self.path_file_HIST):
                return [2, 'can not find file => path_file_HIST']
            buf_stat = os.stat(self.path_file_HIST)
            #--- check size of file ------------------------------------
            if buf_stat.st_size == 0:
                return [3, 'size HIST file is NULL']
            #--- read HIST file ----------------------------------------
            buf_str = []
            with open(self.path_file_HIST,"r") as fh:
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
                with open(self.path_file_HIST, 'w') as file_HIST:
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
            rep = self.db_tod.update_tbl('hist_FUT', buf_list, val = ' VALUES(?,?)')
            if rep[0] > 0: return rep
            #--- update 'self.arr_fut_t' -------------------------------
            self.arr_fut_t = []
            self.arr_fut_t = self.unpack_str_fut(buf_list)[1]

        except Exception as ex:
            return [1, ex]
        return [0, 'ok']

    def unpack_data_in_file(self):
        print('=> _TERM unpack_data_in_file')
        try:
            self.dt_fut = []
            acc = self.account
            for i, item in enumerate(self.data_in_file):
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
        except Exception as ex:
            return [1, ex]
        return [0, 'ok']

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
                    s = Class_str_FUT()
                    s.ind_s = i_str[0]
                    s.dt    = i_str[1].split('|')[0].split(' ')
                    arr_buf = i_str[1].replace(',', '.').split('|')[1:-1]
                    fAsk, fBid = range(2)
                    for item in (zip(arr_buf[::2], arr_buf[1::2])):
                        s.arr.append([float(item[fAsk]), float(item[fBid])])
                    arr_fut.append(s)
                if len(arr_fut) % 100 == 0:  print(len(arr_fut), end='\r')
        except Exception as ex:
            return [1, ex]
        return [0, arr_fut]

    def unpack_str_pck(self, hist_pck):
        print('=> _PACK unpack_str_pck ', len(hist_pck))
        try:
            arr_pck = []
            for cnt, i_str in enumerate(hist_pck):
                buf = i_str[1].replace(',','.').split('|')
                del buf[-1]
                s = Class_str_PCK()
                s.ind_s = i_str[0]
                for cn, item in enumerate(buf):
                    if cn == 0 : s.dt = item.split(' ')[0:2]
                    ind_0 = 0 if cn != 0 else 2
                    s.arr.append([int(float(f)) for f in item.split(' ')[ind_0:]])
                arr_pck.append(s)
                if len(arr_pck) % 100 == 0:  print(len(arr_pck), end='\r')
                else:
                    pass
                if (len(arr_pck) == 0):
                    for item in self.nm:
                        arr_pck.append([])
        except Exception as ex:
            return [1, ex]
        return [0, arr_pck]

    def clc_ASK_BID(self, arr_FUT):
        print('=> _PACK clc_ASK_BID ', len(arr_FUT))
        try:
            #print('point 0')
            b_null = True if (self.nul[0] == 0) else False

            ''' init  table ARCHIV_PACK  --------------------'''
            arr_pk  = []  # list of Class_str_PCK()
            fAsk, fBid = range(2)
            #print('point 1')
            for idx, item in enumerate(arr_FUT): # change STRINGs
                if idx % 1000 == 0:  print(idx, end='\r')
                arr_bb = Class_str_PCK()
                arr_bb.ind_s, arr_bb.dt  = item.ind_s, item.dt
                for p, ptem in enumerate(self.nm):    # change PACKETs
                    ask_p, bid_p, arr_pp = 0, 0, [0, 0, 0, 0, 0]
                    for jdx, jtem in enumerate(self.koef[p]): # calc PACK
                        i_koef, k_koef = jtem[0], jtem[1]
                        if k_koef > 0 :
                            ask_p +=  k_koef * item.arr[i_koef][fAsk]
                            bid_p +=  k_koef * item.arr[i_koef][fBid]
                        if k_koef < 0 :
                            ask_p +=  k_koef * item.arr[i_koef][fBid]
                            bid_p +=  k_koef * item.arr[i_koef][fAsk]

                    if idx == 0 and b_null:
                        arr_pp = [0, 0, 0, 0, 0]
                        self.nul[p] = int((ask_p + bid_p)/2)
                        arr_bb.arr.append(arr_pp)
                        continue
                    arr_pp = [int(ask_p - self.nul[p]), int(bid_p - self.nul[p]), 0, 0, 0]
                    arr_bb.arr.append(arr_pp)
                arr_pk.append(arr_bb)

        except Exception as ex:
            return [1, ex]

        return [0, arr_pk]

    def clc_EMA(self, arr_pk, last_pk):
        print('=> _PACK clc_EMA ', len(arr_pk))
        b_null = True if (last_pk.ind_s == 0) else False
        try:

            koef_EMA, k_EMA_rnd = [], []
            for kdx, ktem in enumerate(self.nm):
                koef_EMA.append(round(2/(1+int(self.ema[kdx][0])),5))
                k_EMA_rnd.append(int(self.ema[kdx][1]))

            pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
            for idx, item in enumerate(arr_pk):
                if idx % 1000 == 0:  print(idx, end='\r')
                if idx == 0:
                    if not b_null:
                        arr_pk[0] = last_pk
                else:
                    for pdx, ptem in enumerate(item.arr):
                            cr = arr_pk[idx].arr[pdx]
                            pr = arr_pk[idx-1].arr[pdx]
                            cr[EMAf]  = round(pr[EMAf] + (int((ptem[pAsk] + ptem[pBid])/2) - pr[EMAf]) * koef_EMA[pdx], 1)
                            cr[EMAf_r]= k_EMA_rnd[pdx] * math.ceil(cr[EMAf] / k_EMA_rnd[pdx] )
                            if pr[EMAf_r] > cr[EMAf_r]:
                                cr[cnt_EMAf_r] = 0 if pr[cnt_EMAf_r] > 0 else pr[cnt_EMAf_r]-1
                            elif pr[EMAf_r] < cr[EMAf_r]:
                                cr[cnt_EMAf_r] = 0 if pr[cnt_EMAf_r] < 0 else pr[cnt_EMAf_r]+1
                            else:
                                cr[cnt_EMAf_r] = pr[cnt_EMAf_r]

        except Exception as ex:
            return [1, ex]

        return [0, arr_pk]

    def pack_arr_pck(self, arr_pk, db_pk, nm_tbl_pk):
        print('=> _PACK pack_arr_pck ', nm_tbl_pk, len(arr_pk))
        try:
            pck_list = []
            pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
            if len(arr_pk) > 0:
                for i_hist, item_hist in enumerate(arr_pk):
                    if i_hist % 1000 == 0:  print(str(i_hist), end='\r')
                    #bp()
                    buf_dt = item_hist.dt[0] + ' ' + item_hist.dt[1] + ' '
                    buf_s = ''
                    for i_pack, item_pack in enumerate(item_hist.arr):
                        buf_s += str(item_pack[pAsk]) + ' ' + str(item_pack[pBid])   + ' '
                        buf_s += str(item_pack[EMAf]) + ' ' + str(item_pack[EMAf_r]) + ' '
                        buf_s += str(item_pack[cnt_EMAf_r]) + '|'
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
            self.nul = [0 for i in range(len(self.nm))]
            r_clc = self.clc_ASK_BID(self.arr_fut_a)
            if r_clc[0] > 0:
                return [2, 'Did not CALC ASK_BID *hist_PACK*!']
            self.arr_pck_a = r_clc[1]
            self.pack_arr_cfg()
            r_pck = self.clc_EMA(self.arr_pck_a, Class_str_PCK())
            if r_pck[0] > 0:
                return [3, 'Did not CALC EMA *hist_PACK*!']
            self.arr_pck_a = r_pck[1]
            pck_a = self.pack_arr_pck(self.arr_pck_a, self.db_arc, 'hist_PACK')
            if pck_a[0] > 0:
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
            if self.rd_term_HST()[0] > 0:
                return [4, 'Problem of rd_term_HST!\n' + rd_term_HST()[1]]
            r_clc = self.clc_ASK_BID(self.arr_fut_t)
            if r_clc[0] > 0:
                return [5, 'Problem of clc_ASK_BID!\n' + r_clc[1]]
            self.arr_pck_t = r_clc[1]
            r_pck = self.clc_EMA(self.arr_pck_t, self.arr_pck_a[-1])
            if r_pck[0] > 0:
                return [6, 'Problem of clc_EMA!\n' + r_pck[1]]
            self.arr_pck_t = r_pck[1][1:]
            pck_t = self.pack_arr_pck(self.arr_pck_t, self.db_tod, 'hist_PACK')
            if pck_t[0] > 0:
                return [7, 'Problem of pack_arr_pck!\n' + pck_t[1]]
            #print(_gl.arr_pck_t[-1])

        except Exception as ex:
            return [1, ex]
        return [0, 'ok']

#=======================================================================
def event_menu_win_MAIN(ev, values, _gl, win):
    rq = [0,ev]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if ev == '__TIMEOUT__':
        print('event_menu_win_MAIN ... __TIMEOUT__ ...')
        r_rd = _gl.calc_arr_pck_today()
        if r_rd[0] > 0:
            win.FindElement('-inp_MAIN-').Update(r_rd[1])
        else:
            win.FindElement('-inp_MAIN-').Update(_gl.account.dt
            +'\nPROFIT = ' + str(_gl.account.arr[_gl.account.prf]))

    #-------------------------------------------------------------------
    if ev == 'rd_term_FUT'  :
        if 'OK' == sg.PopupOKCancel('\nRead file  *file_path_DATA*\n'):
            rep = _gl.rd_term_FUT()
            if rep[0] > 0 and rep[0] != 4: # ignore error "4"
                sg.PopupError('\nDid not read file!\n'
                                + rep[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)
            else:
                print(_gl.account)
                for i in _gl.dt_fut:   print(i)
                sg.PopupOK('\nRead *file_path_DATA* successfully !\n',
                            background_color = 'LightGreen')
    #-------------------------------------------------------------------
    if ev == 'rd_term_HST'  :
        if 'OK' == sg.PopupOKCancel('\nRead file  *path_file_HIST*\n'):
            rep = _gl.rd_term_HST()
            if rep[0] > 0:
                sg.PopupError('\nDid not read file!\n'
                                + rep[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)
            else:
                rq = _gl.prn_arr('arr_fut_t', _gl.arr_fut_t)
                sg.PopupOK('\nRead *path_file_HIST* successfully !\n',
                            background_color = 'LightGreen')
    #-------------------------------------------------------------------
    if ev == 'rd_db_FUT'  :
        if 'OK' == sg.PopupOKCancel('\nRead DB table  *data_FUT*\n'):
            rep = _gl.db_tod.read_tbl('data_FUT')
            if rep[0] > 0:
                sg.PopupError('\nDid not read table!\n'
                                + rep[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)
            else:
                _gl.data_in_file = rep[1][:]
                arr = _gl.unpack_data_in_file()
                print(_gl.account)
                for i in _gl.dt_fut:   print(i)
                sg.PopupOK('\nRead table *data_FUT* successfully !\n',
                            background_color = 'LightGreen')
    #-------------------------------------------------------------------
    if ev == 'rd_hist_FUT_today'  :
        if 'OK' == sg.PopupOKCancel('\nRead table *hist_FUT*\n  from db_TODAY\n '):
            rep = _gl.db_tod.read_tbl('hist_FUT')
            if rep[0] > 0:
                sg.PopupError('\nDid not read table!\n'
                                + rep[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)
            else:
                _gl.arr_fut_t = []
                _gl.arr_fut_t = _gl.unpack_str_fut(rep[1])[1]
                _gl.prn_arr('arr_fut_t', _gl.arr_fut_t)

                sg.PopupOK('\nRead table *hist_FUT* successfully !\n',
                            background_color = 'LightGreen')
    #-------------------------------------------------------------------
    if ev == 'rd_hist_PACK_today'  :
        if 'OK' == sg.PopupOKCancel('\nRead table *hist_PACK*\n  from db_TODAY\n '):
            rep = _gl.db_tod.read_tbl('hist_PACK')
            if rep[0] > 0:
                sg.PopupError('\nDid not read table!\n'
                                + rep[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)
            else:
                _gl.arr_pck_t = []
                _gl.arr_pck_t = _gl.unpack_str_pck(rep[1])[1]
                _gl.prn_arr('arr_pck_t', _gl.arr_pck_t)

                sg.PopupOK('\nRead table *hist_PACK* successfully !\n',
                            background_color = 'LightGreen')
    #-------------------------------------------------------------------
    if ev == 'rd_hist_FUT_arch'  :
        if 'OK' == sg.PopupOKCancel('\nRead table *hist_FUT*\n  from db_ARCH\n '):
            rep = _gl.db_arc.read_tbl('hist_FUT')
            if rep[0] > 0:
                sg.PopupError('\nDid not read table!\n'
                                + rep[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)
            else:
                _gl.arr_fut_a = []
                _gl.arr_fut_a = _gl.unpack_str_fut(rep[1])[1]
                _gl.prn_arr('arr_fut_a', _gl.arr_fut_a)

                sg.PopupOK('\nRead table *hist_FUT* successfully !\n',
                            background_color = 'LightGreen')
    #-------------------------------------------------------------------
    if ev == 'rd_hist_PACK_arch'  :
        if 'OK' == sg.PopupOKCancel('\nRead table *hist_PACK*\n  from db_ARCH\n '):
            rep = _gl.db_arc.read_tbl('hist_PACK')
            if rep[0] > 0:
                sg.PopupError('\nDid not read table!\n'
                                + rep[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)
            else:
                _gl.arr_pck_a = []
                _gl.arr_pck_a = _gl.unpack_str_pck(rep[1])[1]
                _gl.prn_arr('arr_pck_a', _gl.arr_pck_a)

                sg.PopupOK('\nRead table *hist_PACK* successfully !\n',
                            background_color = 'LightGreen')
    #-------------------------------------------------------------------
    if ev == 'calc_hst_PACK_a'  :
        if 'OK' == sg.PopupOKCancel('\nCalc table *hist_PACK*\n  from db_ARCH\n '):
            _gl.nul = [0 for i in range(len(_gl.nm))]
            r_clc = _gl.clc_ASK_BID(_gl.arr_fut_a)
            if r_clc[0] == 0:
                _gl.arr_pck_a = r_clc[1]
                sg.PopupOK('\nclc_ASK_BID *hist_PACK* successfully !\n',
                            background_color = 'LightGreen')
                _gl.pack_arr_cfg()
                sg.PopupOK('\nUpdate NUL *cfg_PACK* successfully !\n',
                            background_color = 'LightGreen')
                r_pck = _gl.clc_EMA(_gl.arr_pck_a, Class_str_PCK())
                if r_pck[0] == 0:
                    _gl.arr_pck_a = r_pck[1]
                    _gl.prn_arr('arr_pck_a', _gl.arr_pck_a)
                    sg.PopupOK('\nclc_EMA *hist_PACK* successfully !\n',
                                background_color = 'LightGreen')
                    pck_a = _gl.pack_arr_pck(_gl.arr_pck_a, _gl.db_arc, 'hist_PACK')
                    if pck_a[0] == 0:
                        sg.PopupOK('\nUpdate *hist_PACK* successfully !\n',
                                    background_color = 'LightGreen')
                    else:
                        sg.PopupError('\nDid not update *hist_PACK*!\n'
                                        + r_pck[1] + '\n',
                                        background_color = 'brown',
                                        no_titlebar = True)
                else:
                    sg.PopupError('\nDid not CALC EMA!\n'
                                    + r_pck[1] + '\n',
                                    background_color = 'brown',
                                    no_titlebar = True)
            else:
                sg.PopupError('\nDid not CALC ASK_BID!\n'
                                + r_clc[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)
    #-------------------------------------------------------------------
    if ev == 'calc_hst_PACK_t'  :
        if 'OK' == sg.PopupOKCancel('\nCalc table *hist_PACK*\n  from db_TODAY\n '):
            r_clc = _gl.calc_arr_pck_today()
            if r_clc[0] == 0:
                sg.PopupOK('\n calc_hst_PACK_t  successfully !\n',
                            background_color = 'LightGreen')
            else:
                sg.PopupError('\n calc_hst_PACK_t  problem !\n'
                                + r_clc[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)

    #-------------------------------------------------------------------
    print('rq = ', rq)
#=======================================================================
def event_menu_CFG_SOFT(_gl, win, ev = '-rd_cfg_SOFT-', values = [] ):
    rq = [0,ev]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if ev == '__TIMEOUT__':
        print('event_menu_CFG_SOFT ... __TIMEOUT__ ...')
    #-------------------------------------------------------------------
    if ev == '-rd_cfg_SOFT-':
        win.FindElement('-titul-'    ).Update(_gl.titul)
        win.FindElement('-path_DATA-').Update(_gl.path_file_DATA)
        win.FindElement('-path_HIST-').Update(_gl.path_file_HIST)
        win.FindElement('-dt_start-' ).Update(_gl.dt_start)
        win.FindElement('-path_TXT-' ).Update(_gl.path_file_TXT)
    #-------------------------------------------------------------------
    if ev == '-update_cfg_SOFT-':
        print('ev ... -update_cfg_SOFT- ...')
        if 'OK' == sg.PopupOKCancel('\n' + 'Update table *cfg_SOFT*' + '\n'):
            _gl.titul          = values['-titul-']
            _gl.path_file_DATA = values['-path_DATA-']
            _gl.path_file_HIST = values['-path_HIST-']
            _gl.dt_start       = values['-dt_start-']
            _gl.path_file_TXT  = values['-path_TXT-']

            cfg = []
            cfg.append(['titul',          _gl.titul])
            cfg.append(['path_file_DATA', _gl.path_file_DATA])
            cfg.append(['path_file_HIST', _gl.path_file_HIST])
            cfg.append(['dt_start',       _gl.dt_start])
            cfg.append(['path_file_TXT',  _gl.path_file_TXT])

            rq = _gl.db_tod.update_tbl('cfg_SOFT', cfg, val = ' VALUES(?,?)')
            if rq[0] > 0:
                sg.PopupError('\n' + 'Did not update cfg_SOFT!' + '\n'
                                + rep[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)
            else:
                sg.PopupOK('\nUpdated *cfg_SOFT* successfully !\n',
                            background_color = 'LightGreen')
    #-------------------------------------------------------------------
    print('rq = ', rq)
#=======================================================================
def event_menu_CFG_PACK(_gl, win, ev = '-rd_cfg_PACK-', val = {'-nm_pack-':0} ):
    rq = [0,ev]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if ev == '__TIMEOUT__':
        print('event_menu_CFG_PACK ... __TIMEOUT__ ...')
        print(val)
    #-------------------------------------------------------------------
    if ev == '-rd_cfg_PACK-':
        print('-nm_pack- = ', int(val['-nm_pack-']) )
        win.FindElement('-nm-').Update(_gl.nm[int(val['-nm_pack-'])])
        win.FindElement('-koef-').Update(_gl.koef[int(val['-nm_pack-'])])
        win.FindElement('-ema-').Update(_gl.ema[int(val['-nm_pack-'])])
    #-------------------------------------------------------------------
    if ev == '-update_cfg_PACK-':
        print('-update_cfg_PACK-')
    #-------------------------------------------------------------------
    print('rq = ', rq)
#=======================================================================
def event_menu_append_TODAY(_gl, win, ev = '-rd_cfg_SOFT-', val = [] ):
    rq = [0,ev]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if ev == '__TIMEOUT__':
        print('event_menu_append_TODAY ... __TIMEOUT__ ...')
        print(val)
    #-------------------------------------------------------------------
    if ev == '-rd_cfg_SOFT-':
        #win.FindElement('-path_DATA-').Update(_gl.path_file_DATA)
        win.FindElement('-path_TXT-' ).Update(_gl.path_file_TXT)
    #-------------------------------------------------------------------
    if ev == 'save_in_FILE':
        print('save_in_FILE ... save hist_FUT_today into file')
        if 'OK' == sg.PopupOKCancel('\n   Save data from table *hist_FUT_today*   ' +
                                      '\n      into file *path_file_TXT*   \n'):
            hst = _gl.db_tod.read_tbl('hist_FUT')
            if hst[0] > 0:
                print('problem read_tbl *hist_FUT* ... ', hst[1])
            else:
                hst_fut_t = hst[1]
                print('len(hist_FUT_today) = ', len(hst_fut_t))
                if len(hst_fut_t) > 0:
                    # change 2020-00-00 to  for name FILE
                    print(_gl.path_file_TXT)
                    buf_name = hst_fut_t[-1][1][6:10] + '-'
                    buf_name += hst_fut_t[-1][1][3:5] + '-'
                    buf_name += hst_fut_t[-1][1][0:2]
                    buf_name = _gl.path_file_TXT.split('***')[0] + buf_name + _gl.path_file_TXT.split('***')[1]
                    print(buf_name)
                    with open(buf_name, 'w') as file_HIST:
                        for item in hst_fut_t:
                            file_HIST.write(item[1]+'\n')
                else:
                    print('hist_FUT_today IS empty')
                    sg.PopupError('\n    Warning! \nTable *hist_FUT_today* IS empty!\n',
                                    background_color = 'grey',
                                    no_titlebar = True)
    #-------------------------------------------------------------------
    if ev == 'append_ARCH':
        print('append_ARCH ... read from file hist_FUT & append into DB ARCH')
        #--- read HIST file ---
        buf_hist_arch, buf_str, frm = [], [], '%d.%m.%Y %H:%M:%S'
        try:
            with open(val['-append_TODAY_in_ARCH-'],"r") as fh:
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
            sg.PopupError('\n' + str(ex) + '\n', background_color = 'brown', no_titlebar = True)
            return

        #--- prepaire 'buf_hist' for update table 'hist_fut'
        for item in buf_hist:
            dtt_cr = datetime.strptime(item.split('|')[0], frm)
            ind_sec = int(dtt_cr.replace(tzinfo=timezone.utc).timestamp())
            buf_hist_arch.append([ind_sec, item])

        rep = _gl.db_arc.update_tbl('hist_FUT', buf_hist_arch, val = ' VALUES(?,?)', p_append = True)
        if rep[0] > 0:
            print('problem update_tbl *hist_FUT* ARCH ... ', rep[1])
            sg.PopupError('\n' + rep[1] + '\n',
                            background_color = 'brown', no_titlebar = True)
        else:
            sg.PopupOK('\nOK, it was append data in table *hist_FUT* successfully !\n',
                        background_color = 'LightGreen')
    #-------------------------------------------------------------------

#=======================================================================
def main():
    _gl = Class_GL()
    _gl.unpack_cfg_soft()
    _gl.unpack_cfg_pack()
    # calc & write in DB hist_PACK for ARCH
    rep = _gl.db_arc.read_tbl('hist_FUT')
    if rep[0] > 0:
        sg.PopupError('\nDid not read table *hist_FUT*!\n'+ rep[1]
                        + '\n', background_color = 'brown',
                        no_titlebar = True)
    else:
        _gl.arr_fut_a = []
        _gl.arr_fut_a = _gl.unpack_str_fut(rep[1])[1]
        _gl.calc_arr_pck()
    #
    _gl.rd_term_FUT()
    _gl.rd_term_HST()
    #
    menu_def = [['MODE',
                    ['AUTO', 'Manual', '---',
                     'Exit',],],
                ['DIAG',
                    ['update_cfg_SOFT',   'update_cfg_PACK',   '---',
                     'append_TODAY_ARCH', '---',
                     'rd_term_FUT',       'rd_term_HST',       '---',
                     'rd_db_FUT',         '---',
                     'rd_hist_FUT_today', 'rd_hist_PACK_today','---',
                     'rd_hist_FUT_arch',  'rd_hist_PACK_arch', '---',
                     'calc_hst_PACK_a',   'calc_hst_PACK_t',   '---',],],
                ]
    #
    lay_MAIN = [ [sg.Menu(menu_def)                               ],
                [sg.Multiline(' ', size=(45, 1), do_not_clear=True, key='-inp_MAIN-')     ],
                [sg.Button('Exit')                                ]]
    #
    lay_cfg_SOFT = [ #[sg.Text('update_cfg_SOFT')],
                [sg.Text('titul',          size=(15, 1)), sg.Input('', do_not_clear=True, key='-titul-') ],
                [sg.Text('path_file_DATA', size=(15, 1)), sg.Input('', do_not_clear=True, key='-path_DATA-'), sg.FileBrowse()],
                [sg.Text('path_file_HIST', size=(15, 1)), sg.Input('', do_not_clear=True, key='-path_HIST-'), sg.FileBrowse()],
                [sg.Text('dt_start',       size=(15, 1)), sg.Input('', do_not_clear=True, key='-dt_start-')],
                [sg.Text('path_file_TXT',  size=(15, 1)), sg.Input('', do_not_clear=True, key='-path_TXT-'),  sg.FileBrowse()],
                [sg.Button('read cfg_SOFT',   key='-rd_cfg_SOFT-'),
                 sg.Button('update cfg_SOFT', key='-update_cfg_SOFT-'),
                 sg.Button('Close')],]
    #
    lay_cfg_PACK = [ #[sg.Text('update_cfg_PACK')],
                [sg.Slider(range=(0, len(_gl.nm)-1), orientation='h',    size=(23, 15),  default_value=0, key='-nm_pack-'),],
                [sg.Text('nm',   size=(4, 1)), sg.Input(_gl.nm[0],       size=(45, 1), do_not_clear=True, key='-nm-') ],
                [sg.Text('koef', size=(4, 1)), sg.Multiline(_gl.koef[0], size=(45, 1), do_not_clear=True, key='-koef-') ],
                [sg.Text('ema',  size=(4, 1)), sg.Input(_gl.ema[0],      size=(45, 1), do_not_clear=True, key='-ema-') ],
                [sg.Button('read cfg_PACK',   key='-rd_cfg_PACK-'),
                 sg.Button('update cfg_PACK', key='-update_cfg_PACK-'),
                 sg.Button('Close')],]
    #
    lay_append_TODAY = [
                [sg.Text('path_file_TXT',         size=(20, 1)), sg.Text('', size=(35, 1), key='-path_TXT-'), ],
                [sg.Button('save_in_FILE')],
                [sg.Text(45*' ', size=(45, 1))],
                [sg.Text('append_TODAY_in_ARCH',  size=(20, 1)), sg.Input('press FileBrowse', do_not_clear=True, key='-append_TODAY_in_ARCH-'),  sg.FileBrowse()],
                [sg.Button('append_ARCH'),  sg.Button('Close')],]
    #
    #sg.theme('DarkTeal12')   # Add a touch of color
    win_MAIN = sg.Window(_gl.titul, grab_anywhere=True).Layout(lay_MAIN).Finalize()
    win_MAIN_mode, win_MAIN_timeout = 'Manual', 36000
    #
    while True:
        #=== check 'Window MAIN' =======================================
        ev_MAIN, vals_MAIN = win_MAIN.Read(timeout = win_MAIN_timeout)
        print('ev_MAIN = ', ev_MAIN, '    vals_MAIN = ', vals_MAIN)
        if ev_MAIN in [None, 'Close', 'Exit']:
            win_MAIN.Close()
            break
        #---------------------------------------------------------------
        if ev_MAIN == 'AUTO'  :
            win_MAIN_timeout, win_MAIN_mode =  3000,   'AUTO'
        #---------------------------------------------------------------
        if ev_MAIN == 'Manual':
            win_MAIN_timeout, win_MAIN_mode = 36000, 'Manual'
        #--- ev_cfg_SOFT 'Window cfg_SOFT' -----------------------------
        event_menu_win_MAIN(ev_MAIN, vals_MAIN, _gl, win_MAIN)

        #=== open 'Window cfg_SOFT' ====================================
        if ev_MAIN == 'update_cfg_SOFT':
            win_MAIN.Hide()
            _gl.unpack_cfg_soft()
            win_cfg_SOFT = sg.Window('update_cfg_SOFT',
                    location=(450,25)).Layout(lay_cfg_SOFT[:]).Finalize()
            event_menu_CFG_SOFT(_gl, win_cfg_SOFT)
            while True:
                ev_cfg_SOFT, vals_cfg_SOFT = win_cfg_SOFT.Read(timeout=100)
                #if ev_cfg_SOFT is None or ev_cfg_SOFT == 'Close' or ev_cfg_SOFT == 'Exit':
                if ev_cfg_SOFT in [None, 'Close', 'Exit']:
                    win_MAIN.UnHide()
                    win_cfg_SOFT.Close()
                    break
                #--- ev_cfg_SOFT 'Window cfg_SOFT' -------------------------
                event_menu_CFG_SOFT(_gl, win_cfg_SOFT, ev_cfg_SOFT, vals_cfg_SOFT)
        #
        #=== open 'Window cfg_PACK' ====================================
        if ev_MAIN == 'update_cfg_PACK':
            win_MAIN.Hide()
            _gl.unpack_cfg_pack()
            win_cfg_PACK = sg.Window('update_cfg_PACK',
                    location=(150,200)).Layout(lay_cfg_PACK[:]).Finalize()
            event_menu_CFG_PACK(_gl, win_cfg_PACK)
            while True:
                ev_cfg_PACK, vals_cfg_PACK = win_cfg_PACK.Read(timeout=100)
                if ev_cfg_PACK in [None, 'Close', 'Exit']:
                    win_MAIN.UnHide()
                    win_cfg_PACK.Close()
                    break
                #--- ev_cfg_PACK 'Window win_cfg_PACK' -------------------------
                event_menu_CFG_PACK(_gl, win_cfg_PACK, ev_cfg_PACK, vals_cfg_PACK)
        #
        #=== open 'Window append_TODAY' ================================
        if ev_MAIN == 'append_TODAY_ARCH':
            win_MAIN.Hide()
            win_append_TODAY_ARCH = sg.Window('append TODAY in ARCH',
                    location=(250,350)).Layout(lay_append_TODAY[:]).Finalize()
            event_menu_append_TODAY(_gl, win_append_TODAY_ARCH)
            while True:
                ev_append_TODAY, vals_append_TODAY = win_append_TODAY_ARCH.Read(timeout=1000)
                if ev_append_TODAY in [None, 'Close', 'Exit']:
                    win_MAIN.UnHide()
                    win_append_TODAY_ARCH.Close()
                    break
                #--- ev_cfg_PACK 'Window win_cfg_PACK' -------------------------
                event_menu_append_TODAY(_gl, win_append_TODAY_ARCH, ev_append_TODAY, vals_append_TODAY)
        #
    return 0

if __name__ == '__main__':
    main()
