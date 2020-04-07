#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_PACK.py
#
#  Copyright 2020 OVK <ovk.rus@gmail.com>
#
#=======================================================================
import os, sys, math, time, sqlite3, logging
from datetime import datetime, timezone
import math
#from ipdb import set_trace as bp    # to set breakpoints just -> bp()
import PySimpleGUI as sg
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

    def update_tbl(self, nm_tbl, buf_arr, val = ' VALUES(?,?)'):
        print('=> _SQLite update_tbl ', nm_tbl)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- update table nm_tbl ---------------------------
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
class Class_str_PCK():
    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
    def __init__(self):
        self.ind_s, self.dt, self.arr  = 0, '', []
    def __retr__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
    def __str__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
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
class Class_PACK():
    def __init__(self):
        c_dir    = os.path.abspath(os.curdir)
        self.lg_FILE    = Class_LOGGER(c_dir + '\\LOG\\pack_logger.log')
        self.db_FUT_arc = Class_DB_SQLite(c_dir + '\\DB\\db_fut_a.sqlite')
        self.db_FUT_tod = Class_DB_SQLite(c_dir + '\\DB\\db_fut_t.sqlite')
        self.db_PCK_arc = Class_DB_SQLite(c_dir + '\\DB\\db_pack_a.sqlite')
        self.db_PCK_tod = Class_DB_SQLite(c_dir + '\\DB\\db_pack_t.sqlite')
        # cfg_pack
        self.nm   = []  # list NM   of packets
        self.koef = []  # list KOEF of packets
        self.nul  = []  # list NUL  of packets
        self.ema  = []  # list EMA  of packets
        #
        self.hst_fut_t = []
        self.arr_fut_t = []
        self.hst_fut_a = []
        self.arr_fut_a = []
        #
        self.hst_pck_t = []
        self.arr_pck_t = []
        self.hst_pck_a = []
        self.arr_pck_a = []
        #
        self.dt_file = 0
        #
        self.lg_FILE.wr_log_info('START')

    def prn_arr(self, name_arr, arr):
        print('len(' + name_arr + ')   => ' + str(len(arr)) + '\n' )
        if len(arr) > 4:
            for i in [0,1]: print(arr[i],'\n')
            print('+++++++++++++++++++++++++\n')
            for i in [-2,-1]: print(arr[i],'\n')
        else:
            for item in arr: print(item, '\n')

    def prn_cfg(self):
        #-----------------------------------------------------------
        frm = '{: ^5}{: ^15}{}{}{}'
        print(frm.format('nm','nul','ema[]','        ','koef[]'))
        for i, item in enumerate(self.nm):
            print(frm.format(self.nm[i],
                        str(self.nul[i]),
                            self.ema[i], '   ',
                            self.koef[i]))

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
            #self.arr_pk_t  = []
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

    def unpack_str_cfg(self, cfg):
        print('=> _PACK unpack_str_cfg ', len(cfg))
        try:
            self.nm   = []  # list NM   of packets
            self.koef = []  # list KOEF of packets
            self.nul  = []  # list NUL  of packets
            self.ema  = []
            for item in cfg:
                self.nm.append(item[0])          # ['pckt0']
                arr_k    = item[1].split(',')
                arr_koef = []
                for item_k in arr_k:             # '0:2:SR' => [0, 32, 'SR']
                    buf_k = [int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')]
                    arr_koef.append(buf_k)
                self.koef.append(arr_koef)       #  [[0, 2, 'SR'],[9, -20, 'MX'], ...
                self.nul.append(int(item[2]))    #  [0]
                self.ema.append([int(e) for e in item[3].split(':')]) # [1111, 15]
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
            r_update = self.db_PCK_arc.update_tbl('cfg_PACK', cfg_list, val = ' VALUES(?,?,?,?)')
            if r_update[0] == 1:
                return [1, r_update[1]]

        except Exception as ex:
            return [1, ex]
        return [0, cfg_list]

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

    def clc_PACK_arc(self):
        print('=> _PACK clc_PACK_arc ')
        cfg = self.db_PCK_arc.read_tbl('cfg_PACK')
        if cfg[0] > 0: return cfg
        arr = self.unpack_str_cfg(cfg[1])
        hst = self.db_FUT_arc.read_tbl('hist_FUT')
        if hst[0] > 0: return hst
        self.hst_fut_a = hst[1][:]
        arr = self.unpack_str_fut(self.hst_fut_a)
        if arr[0] > 0: return arr
        self.arr_fut_a = arr[1][:]
        self.nul = [0 for i in range(len(self.nm))]
        r_clc = self.clc_ASK_BID(self.arr_fut_a)
        if r_clc[0] > 0: return r_clc
        self.arr_pck_a = r_clc[1]
        r_pck = self.clc_EMA(self.arr_pck_a, Class_str_PCK())
        if r_pck[0] > 0: return r_pck
        self.arr_pck_a = r_pck[1]
        pck_a = self.pack_arr_pck(self.arr_pck_a, self.db_PCK_arc, 'hist_PACK')
        if pck_a[0] > 0: return pck_a
        return [0, 'update hst_PACK ok!']

    def clc_PACK_tod(self):
        print('=> _PACK clc_PACK_tod ')
        hst = self.db_FUT_tod.read_tbl('hist_FUT_today')
        if hst[0] > 0: return hst
        self.hst_fut_t = hst[1][:]
        arr = self.unpack_str_fut(hst[1])
        if arr[0] > 0: return arr
        self.arr_fut_t = arr[1][:]
        r_clc = self.clc_ASK_BID(self.arr_fut_t)
        if r_clc[0] > 0: return r_clc
        self.arr_pck_t = r_clc[1]
        r_clc = self.clc_EMA(self.arr_pck_t, self.arr_pck_a[-1])
        if r_clc[0] > 0: return r_clc
        self.arr_pck_t = r_clc[1][1:]
        pck_t = self.pack_arr_pck(self.arr_pck_t, self.db_PCK_tod, 'hist_PACK_today')
        if pck_t[0] > 0: return pck_t
        return [0, 'update hst_PACK_today ok!']

    def check_time_changed(self):
        path_fut_today = os.path.abspath(os.curdir) + '\\DB\\db_fut_t.sqlite'
        #--- check file cntr.file_path_DATA ----------------------------
        if not os.path.isfile(path_fut_today):
            err_msg = 'can not find file => ' + path_fut_today
            return [1, err_msg]
        buf_stat = os.stat(path_fut_today)
        #
        #--- check time modificated of file ----------------------------
        if int(buf_stat.st_mtime) == self.dt_file:
            #str_dt_file = datetime.fromtimestamp(self.dt_file).strftime('%H:%M:%S')
            return [2, 'FILE is not modificated ' + time.strftime("%M:%S", time.gmtime())]
        else:
            self.dt_file = int(buf_stat.st_mtime)
        return [0, 'ok']
#=======================================================================
def event_menu(event, _gl):
    rq = [0,event]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if event == 'rd_hst_FUT_a'  :   #   _gl.hst_fut_a   _gl.arr_fut_a
        hst = _gl.db_FUT_arc.read_tbl('hist_FUT')
        if hst[0] == 0:
            _gl.hst_fut_a = hst[1][:]
            arr = _gl.unpack_str_fut(hst[1])
            if arr[0] == 0:
                _gl.arr_fut_a = arr[1][:]
    #-------------------------------------------------------------------
    if event == 'rd_hst_FUT_t'  :   #   _gl.hst_fut_t   _gl.arr_fut_t
        hst = _gl.db_FUT_tod.read_tbl('hist_FUT_today')
        if hst[0] == 0:
            _gl.hst_fut_t = hst[1][:]
            arr = _gl.unpack_str_fut(hst[1])
            if arr[0] == 0:
                _gl.arr_fut_t = arr[1][:]
    #-------------------------------------------------------------------
    if event == 'rd_hst_PACK_a'  :   #   _gl.hst_pck_a   _gl.arr_pck_a
        hst = _gl.db_PCK_arc.read_tbl('hist_PACK')
        if hst[0] == 0:
            _gl.hst_pck_a = hst[1][:]
            arr = _gl.unpack_str_pck(hst[1])
            if arr[0] == 0:
                _gl.arr_pck_a = arr[1][:]
                _gl.prn_arr('arr_pck_a', arr[1],)
    #-------------------------------------------------------------------
    if event == 'rd_hst_PACK_t'  :   #   _gl.hst_pck_t   _gl.arr_pck_t
        hst = _gl.db_PCK_tod.read_tbl('hist_PACK_today')
        if hst[0] == 0:
            _gl.hst_pck_t = hst[1][:]
            arr = _gl.unpack_str_pck(hst[1])
            if arr[0] == 0:
                _gl.arr_pck_t = arr[1][:]
                _gl.prn_arr('arr_pck_t', arr[1],)
    #-------------------------------------------------------------------
    if event == 'rd_cfg_PACK_a'  :
        cfg = _gl.db_PCK_arc.read_tbl('cfg_PACK')
        if cfg[0] == 0:
            arr = _gl.unpack_str_cfg(cfg[1])
    #-------------------------------------------------------------------
    if event == 'wr_cfg_PACK_a'  :
        cfg = _gl.pack_arr_cfg()
        if cfg[0] == 0:
            print('update CFG ok!')
    #-------------------------------------------------------------------
    if event == 'calc_hst_PACK_a'  :
        _gl.nul = [0 for i in range(len(_gl.nm))]
        print('calc_hst_PACK_a ...')
        r_clc = _gl.clc_ASK_BID(_gl.arr_fut_a)
        if r_clc[0] == 0:
            _gl.arr_pck_a = r_clc[1]
            print('start EMA')
            r_pck = _gl.clc_EMA(_gl.arr_pck_a, Class_str_PCK())
            if r_pck[0] == 0:
                _gl.arr_pck_a = r_pck[1]
    #-------------------------------------------------------------------
    if event == 'calc_hst_PACK_t'  :
        print('calc_hst_PACK_t ...')
        r_clc = _gl.clc_ASK_BID(_gl.arr_fut_t)
        if r_clc[0] == 0:
            _gl.arr_pck_t = r_clc[1]
            print('start EMA')
            r_clc = _gl.clc_EMA(_gl.arr_pck_t, _gl.arr_pck_a[-1])
            if r_clc[0] == 0:
                _gl.arr_pck_t = r_clc[1][1:]
    #-------------------------------------------------------------------
    if event == 'wr_hst_PACK_a'  :
        print('wr_hst_PACK_a ...')
        pck_a = _gl.pack_arr_pck(_gl.arr_pck_a, _gl.db_PCK_arc, 'hist_PACK')
        if pck_a[0] == 0:
            print('update hst_PACK ok!')
    #-------------------------------------------------------------------
    if event == 'wr_hst_PACK_t'  :
        print('wr_hst_PACK_t ...')
        pck_t = _gl.pack_arr_pck(_gl.arr_pck_t, _gl.db_PCK_tod, 'hist_PACK_today')
        if pck_t[0] == 0:
            print('update hst_PACK_today ok!')
    #-------------------------------------------------------------------
    if event == 'CALC_PACK_a'  :
        arr = _gl.clc_PACK_arc()
        if arr[0] > 0: return arr
        print('CALC_PACK_a ok!')
    #-------------------------------------------------------------------
    if event == 'CALC_PACK_t'  :
        arr = _gl.clc_PACK_tod()
        if arr[0] > 0: return arr
        print('CALC_PACK_t ok!')
    #-------------------------------------------------------------------
    if event == 'prn_cfg_a'  :
        _gl.prn_cfg()
    #-------------------------------------------------------------------
    if event == 'prn_hst_FUT_t'  :
        _gl.prn_arr('hist_fut_t', _gl.hst_fut_t)
    #-------------------------------------------------------------------
    if event == 'prn_arr_FUT_t'  :
        _gl.prn_arr('arr_fut_t', _gl.arr_fut_t)
    #-------------------------------------------------------------------
    if event == 'prn_hst_FUT_a'  :
        _gl.prn_arr('hist_fut_a', _gl.hst_fut_a)
    #-------------------------------------------------------------------
    if event == 'prn_arr_FUT_a'  :
        _gl.prn_arr('arr_fut_a', _gl.arr_fut_a)
    #-------------------------------------------------------------------
    if event == 'prn_hst_PCK_t'  :
        _gl.prn_arr('hist_pck_t', _gl.hst_pck_t)
    #-------------------------------------------------------------------
    if event == 'prn_arr_PCK_t'  :
        _gl.prn_arr('arr_pck_t', _gl.arr_pck_t)
    #-------------------------------------------------------------------
    if event == 'prn_hst_PCK_a'  :
        _gl.prn_arr('hist_pck_a', _gl.hst_pck_a)
    #-------------------------------------------------------------------
    if event == 'prn_arr_PCK_a'  :
        _gl.prn_arr('arr_pck_a', _gl.arr_pck_a)
    #-------------------------------------------------------------------

    print('rq = ', rq)

#=======================================================================
def main():
    menu_def = [
        ['Mode',
            ['auto','manual', ],],
        ['DEBUG',
            ['rd_cfg_PACK_a',   'wr_cfg_PACK_a',    '---',
             'rd_hst_FUT_a',    'rd_hst_FUT_t',     '---',
             'rd_hst_PACK_a',   'rd_hst_PACK_t',    '---',
             'calc_hst_PACK_a', 'calc_hst_PACK_t',  '---',
             'wr_hst_PACK_a',   'wr_hst_PACK_t',    '---',
             'CALC_PACK_a',     'CALC_PACK_t',      '---',  ],],
        ['PRINT',
            ['prn_cfg_a',  '---',
             'prn_hst_FUT_t', 'prn_arr_FUT_t', 'prn_hst_FUT_a', 'prn_arr_FUT_a',  '---',
             'prn_hst_PCK_t', 'prn_arr_PCK_t', 'prn_hst_PCK_a', 'prn_arr_PCK_a', ],],
        ['Exit', 'Exit']
    ]
    _gl = Class_PACK()      # init db_TODAY ----------------------------
    arr = _gl.clc_PACK_arc()
    if arr[0] > 0:
        stroki.append(arr[1])
    while True:  # init MENU -------------------------------------------
        def_txt, frm = [], '{: <10}  => {: ^15}\n'
        def_txt.append(frm.format('db_FUT_tod' , '\\DB\\db_fut_t.sqlite'))
        def_txt.append(frm.format('db_FUT_arc' , '\\DB\\db_fut_a.sqlite'))
        def_txt.append(frm.format('db_PCK_tod' , '\\DB\\db_pack_t.sqlite'))
        def_txt.append(frm.format('db_PCK_arc' , '\\DB\\db_pack_a.sqlite'))
        #=======================================================================
        # Display data
        layout = [
                    [sg.Menu(menu_def, tearoff=False, key='menu_def')],
                    [sg.Multiline( default_text=''.join(def_txt),
                        size=(50, 5), key='txt_data', autoscroll=False, focus=False),],
                    [sg.T('',size=(60,2), font='Helvetica 8', key='txt_status'),
                     #sg.Quit(auto_size_button=True)
                     ],
                 ]
        sg.SetOptions(element_padding=(0,0))
        window = sg.Window('Titul PACK', grab_anywhere=True).Layout(layout).Finalize()
        window.FindElement('txt_data').Update(''.join(def_txt))
        break

    tm_out, mode, frm = 360000, 'manual', '%d.%m.%Y %H:%M:%S'
    stts  = time.strftime(frm, time.localtime()) + '\n' + 'event = manual'
    window.FindElement('txt_status').Update(stts)

    win_CFG_active = False
    while True:  # MAIN cycle ------------------------------------------
        stroki = []
        event, values = window.Read(timeout = tm_out )
        #---------------------------------------------------------------
        event_menu(event, _gl)
        #---------------------------------------------------------------
        if event is None or event == 'Quit' or event == 'Exit': break
        #---------------------------------------------------------------
        if event == 'auto'   :    tm_out, mode =  2500,   'auto'
        #---------------------------------------------------------------
        if event == 'manual' :    tm_out, mode = 360000, 'manual'
        #---------------------------------------------------------------
        if event == '__TIMEOUT__':
            r = _gl.check_time_changed()
            if r[0] == 0:
                stroki.append('New date FUT today')
                arr = _gl.clc_PACK_tod()
                if arr[0] > 0:
                    print(arr)
                    #stroki.append(arr)
            else:
                print(r)
                #stroki.append(r[1])
        #---------------------------------------------------------------
        window.FindElement('txt_data').Update('\n'.join(stroki))
        stts  = time.strftime(frm, time.localtime()) + '\n'
        stts += 'event = ' + event
        window.FindElement('txt_status').Update(stts)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
