#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_GRAFik.py
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
class Class_cfg_PCK():
    nm, koef, nul, ema = range(4)
    def __init__(self):
        self.arr  = []
    def __retr__(self):
        return 'arr={}'.format(str(self.arr))
    def __str__(self):
        return 'arr={}'.format(str(self.arr))
#=======================================================================
class Class_GL():
    def __init__(self):
        c_dir    = os.path.abspath(os.curdir)
        self.lg_file =    Class_LOGGER(c_dir + '\\LOG\\gl_GRAF.log')
        self.db_arc  = Class_DB_SQLite(c_dir + '\\DB\\db_ARCH.sqlite')
        self.db_tod  = Class_DB_SQLite(c_dir + '\\DB\\db_TODAY.sqlite')
        #
        self.cfg_pck = Class_cfg_PCK()
        #
        self.dt_start_sec = 0
        #
        self.arr_pck_t = []
        self.arr_pck_a = []

    def prn_arr(self, name_arr, arr):
        print('len(' + name_arr + ')   => ' + str(len(arr)) + '\n' )
        if len(arr) > 4:
            for i in [0,1]: print(arr[i],'\n')
            print('+++++++++++++++++++++++++\n')
            for i in [-2,-1]: print(arr[i],'\n')
        else:
            for item in arr: print(item, '\n')

    def prn_cfg_pack(self):
        frm = '{:-^5}{:-^35}{:-^5}{:-^10}'
        print(frm.format('nm','koef[]','nul','ema[]','        '))
        for item in self.cfg_pck.arr:
            print(item)

    def read_cfg_pack(self):
        print('=> _GL read_cfg_pack ')
        try:
            cfg = self.db_tod.read_tbl('cfg_PACK')
            if cfg[0] > 0: return cfg
            c = self.cfg_pck
            c.arr = []
            for item in cfg[1]:
                arr_k    = item[1].split(',')
                arr_koef = []
                for item_k in arr_k:             # '0:2:SR' => [0, 32, 'SR']
                    arr_koef.append([int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')])
                #buf = [item[0], arr_koef, int(item[2]), [int(e) for e in item[3].split(':')]]
                #nm, koef, nul, ema = range(4)
                buf = [item[c.nm], arr_koef, int(item[c.nul]), [int(e) for e in item[c.ema].split(':')]]
                c.arr.append(buf)
            #for item in c.arr:
            #    print(item)

        except Exception as ex:
            return [1, ex]

        return [0, cfg]

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
#=======================================================================
def main():
    menu_def = [
        ['READ', [ 'rd_cfg_PACK_a', 'rd_arr_PACK_a',  'rd_arrPACK_t',  ],],
        ['PRINT',[ 'prn_cfg_PCK',   'prn_arr_PCK_t',  'prn_arr_PCK_a', ],],
        ['Exit', 'Exit']
    ]
    _gl = Class_GL()      # init db_TODAY ------------------------------

    while True:
        X_bot_left,  Y_bot_left  = 0,    0
        X_top_right, Y_top_right = 1040, 500
        #
        rep = _gl.read_cfg_pack()
        #
        if rep[0] > 0:
            sg.PopupError('\n Could not read_cfg_pack table *cfg_PACK*! \n'+ rep[1]
            + '\n', background_color = 'brown',no_titlebar = True)
            return 0
        #
        # read db_ARCH table hist_PACK ---------------------------------
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
        #
        # read db_TODAY table hist_PACK --------------------------------
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
        break
        #
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
