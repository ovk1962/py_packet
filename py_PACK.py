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
class Class_DB_FUT():
    def __init__(self, path_db_fut, nm_tbl):
        self.path_db_fut  = path_db_fut
        self.nm_tbl       = nm_tbl

        self.conn = ''
        self.cur  = ''
        self.arr_fut = []

    def prn_arr(self, name_arr, arr):
        print('len(' + name_arr + ')   => ' + str(len(arr)) + '\n' )
        if len(arr) > 4:
            for i in [0,1]: print(arr[i],'\n')
            print('+++++++++++++++++++++++++\n')
            for i in [-2,-1]: print(arr[i],'\n')
        else:
            for item in arr: print(item, '\n')

    def rd_hst(self):
        r_rd_hst = []
        self.conn = sqlite3.connect(self.path_db_fut)
        try:
            with self.conn:
                r_rd_hst = [0, 'ok']
                self.cur = self.conn.cursor()

                print('start rd_hst_FUT! ')
                self.cur.execute('SELECT * from ' + self.nm_tbl)
                arr_buf = []    #self.hst_fut = []
                arr_buf = self.cur.fetchall()    # read table name_tbl
                print('len ' + self.nm_tbl +' = ', len(arr_buf))
                self.arr_fut  = []
                for cnt, i_str in enumerate(arr_buf):
                    #arr_item = (i_str[1].replace(',', '.')).split('|')
                    s = Class_str_FUT()
                    s.ind_s = i_str[0]
                    s.dt    = i_str[1].split('|')[0].split(' ')
                    arr_buf = i_str[1].replace(',', '.').split('|')[1:-1]
                    fAsk, fBid = range(2)
                    for item in (zip(arr_buf[::2], arr_buf[1::2])):
                        s.arr.append([float(item[fAsk]), float(item[fBid])])
                    self.arr_fut.append(s)
                    if len(self.arr_fut) % 1000 == 0:  print(len(self.arr_fut), end='\r')
                print('finish rd_hst_FUT! => ', str(len(self.arr_fut)))
        except Exception as ex:
            r_rd_hst = [1, 'op_HIST_FUT ' + self.nm_tbl + '   ' + str(ex)]

        return r_rd_hst
#=======================================================================
class Class_DB_PACK():
    def __init__(self, path_db_pack, nm_tbl):
        self.path_db_pack = path_db_pack
        self.nm_tbl       = nm_tbl

        # cfg_pack
        self.nm   = []  # list NM   of packets
        self.koef = []  # list KOEF of packets
        self.nul  = []  # list NUL  of packets
        self.ema  = []  # list EMA  of packets

        self.arr_pk  = []  # list of objects Class_str_PCK()

    def prn_cfg(self):
        if len(self.nm) > 0:
            frm = '{: ^5}{: ^15}{}{}{}'
            print(frm.format('nm','nul','ema[]','        ','koef[]'))
            for i, item in enumerate(self.nm):
                print(frm.format(self.nm[i], str(self.nul[i]), self.ema[i], '   ', self.koef[i]))

    def prn_arr(self, name_arr, arr):
        print('len(' + name_arr + ')   => ' + str(len(arr)) + '\n' )
        if len(arr) > 4:
            for i in [0,1]: print(arr[i],'\n')
            print('+++++++++++++++++++++++++\n')
            for i in [-2,-1]: print(arr[i],'\n')
        else:
            for item in arr: print(item, '\n')

    def rd_cfg_PACK(self):
        conn = sqlite3.connect(self.path_db_pack)
        try:
            with conn:
                cur = conn.cursor()

                self.nm, self.koef, self.nul, self.ema = [], [], [], []
                cfg = []
                cur.execute('SELECT * from ' + 'cfg_PACK')
                cfg = cur.fetchall()    # read table name_tbl
                #
                print('packets => ', len(cfg))
                #
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
            return [1, 'op_HIST_PACK ' + self.nm_tbl + '   ' + str(ex)]

        return [0, 'ok']

    def clc_ASK_BID(self, arr_FUT):
        b_null = True if (self.nul[0] == 0) else False

        print('start clc_ASK_BID! ')
        ''' init  table ARCHIV_PACK  --------------------'''
        self.arr_pk  = []  # list of Class_str_PCK()
        fAsk, fBid = range(2)
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
                if b_null:
                    if idx == 0:
                        self.nul[p] = int((ask_p + bid_p)/2)
                arr_pp = [int(ask_p - self.nul[p]), int(bid_p - self.nul[p]), 0, 0, 0]
                arr_bb.arr.append(arr_pp)
            self.arr_pk.append(arr_bb)

        if b_null:
            # update self.nul[i_pack] in table cfg_PACK ----
            conn = sqlite3.connect(self.path_db_pack)
            try:
                with conn:
                    cur = conn.cursor()
                    duf_list = []
                    for j, jtem in enumerate(self.nm):
                        arr_koef = ''
                        for ktem in self.koef[j]:
                            str_koef = ':'.join([str(f) for f in ktem])
                            arr_koef += str_koef + ','
                        buf = (self.nm[j], arr_koef[:-1], str(self.nul[j]), ':'.join([str(f) for f in self.ema[j]]))
                        duf_list.append(buf)
                    scur.execute('DELETE FROM ' + 'cfg_PACK')
                    cur.executemany('INSERT INTO ' + 'cfg_PACK' + ' VALUES' + '(?,?,?,?)', duf_list)
                    conn.commit()
            except Exception as ex:
                return [1, 'update NUL' + self.nm_tbl + '   ' + str(ex)]

        print('finish clc_ASK_BID! => ', str(len(self.arr_pk)))
#=======================================================================


#=======================================================================
def event_menu(event, db_FUT_t, db_FUT_a, db_PACK_t, db_PACK_a):
    rq = [0,event]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if event == 'rd_hst_FUT_t'  :
        print('rd_hst_FUT_t ...')
        rq = db_FUT_t.rd_hst()
    #-------------------------------------------------------------------
    if event == 'rd_hst_FUT_a'  :
        print('rd_hst_FUT_a ...')
        rq = db_FUT_a.rd_hst()
    #-------------------------------------------------------------------
    if event == 'prn_arr_FUT_t'  :
        print('prn_arr_FUT_t ...')
        rq = db_FUT_t.prn_arr('arr_fut_t', db_FUT_t.arr_fut)
    #-------------------------------------------------------------------
    if event == 'prn_arr_FUT_a'  :
        print('prn_arr_FUT_a ...')
        rq = db_FUT_a.prn_arr('arr_fut_a', db_FUT_a.arr_fut)
    #-------------------------------------------------------------------
    if event == 'prn_arr_PACK_t'  :
        print('prn_arr_PACK_t ...')
        rq = db_PACK_t.prn_arr('arr_pack_t', db_PACK_t.arr_pk)
    #-------------------------------------------------------------------
    if event == 'prn_arr_PACK_a'  :
        print('prn_arr_PACK_a ...')
        rq = db_PACK_a.prn_arr('arr_pack_a', db_PACK_a.arr_pk)
    #-------------------------------------------------------------------
    if event == 'prn_cfg_a'  :
        print('prn_cfg_a ...')
        db_PACK_a.prn_cfg()
    #-------------------------------------------------------------------
    if event == 'prn_cfg_t'  :
        print('prn_cfg_t ...')
        db_PACK_t.prn_cfg()
    #-------------------------------------------------------------------
    if event == 'calc_hst_PACK_a'  :
        elm = len(db_PACK_a.nm)
        db_PACK_a.nul = [0 for i in range(elm)]
        db_PACK_t.nul = db_PACK_a.nul[:]
        print('calc_hst_PACK_a ...')
        db_PACK_a.clc_ASK_BID(db_FUT_a.arr_fut)
        db_PACK_t.nul = db_PACK_a.nul[:]
    #-------------------------------------------------------------------
    if event == 'calc_hst_PACK_t'  :
        print('calc_hst_PACK_t ...')
        db_PACK_t.clc_ASK_BID(db_FUT_t.arr_fut)
    #-------------------------------------------------------------------
    print('rq = ', rq)

#=======================================================================
def main():
    menu_def = [
        ['Mode',
            ['auto','manual', ],],
        ['READ',
            ['rd_hst_FUT_t',   'rd_hst_FUT_a',   '---',
             'rd_hst_PACK_t',  'rd_hst_PACK_a',  ],],
        ['DEBUG',
            ['calc_hst_PACK_a', 'calc_hst_PACK_t', '---',
             'calc_hst_PACK_a',  ],],
        ['PRINT',
            ['prn_cfg_a', 'prn_cfg_t',   '---',
             'prn_arr_FUT_t',  'prn_arr_FUT_a',  '---',
             'prn_arr_PACK_t', 'prn_arr_PACK_a', ],],
        ['Exit', 'Exit']
    ]
    while True:  # init db_TODAY ---------------------------------------
        c_dir    = os.path.abspath(os.curdir)
        lg_FILE  = Class_LOGGER(c_dir + '\\LOG\\pack_logger.log')
        lg_FILE.wr_log_info('START')
        #---------------------------------------------------------------
        db_FUT_a = Class_DB_FUT(c_dir + '\\DB\\db_fut_a.sqlite', 'hist_FUT')
        rq = db_FUT_a.rd_hst()
        if rq[0] != 0 :
            print('db_FUT_a = > ', rq[1])
        else:
            print('INIT db_FUT_a ARCHIV = > ', rq)
        #---------------------------------------------------------------
        db_FUT_t = Class_DB_FUT(c_dir + '\\DB\\db_fut_t.sqlite',  'hist_FUT_today')
        rq = db_FUT_t.rd_hst()
        if rq[0] != 0 :
            print('db_FUT_t = > ', rq[1])
        else:
            print('INIT db_FUT_t TODAY = > ', rq)
        #---------------------------------------------------------------
        db_PACK_a = Class_DB_PACK(c_dir + '\\DB\\db_pack_a.sqlite', 'hist_PACK')
        rq = db_PACK_a.rd_cfg_PACK()
        if rq[0] != 0 :
            print('db_PACK_a = > ', rq[1])
        else:
            print('INIT db_PACK_a ARCHIV = > ', rq)
        #---------------------------------------------------------------
        db_PACK_t = Class_DB_PACK(c_dir + '\\DB\\db_pack_t.sqlite',  'hist_PACK_today')
        rq = db_PACK_t.rd_cfg_PACK()
        if rq[0] != 0 :
            print('db_PACK_t = > ', rq[1])
        else:
            print('INIT db_PACK_t TODAY = > ', rq)
        #---------------------------------------------------------------




        # db_PACK = Class_DB(c_dir + '\\DB\\db_today.sqlite',
                            # c_dir + '\\DB\\db_archiv.sqlite',
                            # c_dir + '\\DB\\db_pack_t.sqlite',
                            # c_dir + '\\DB\\db_pack_a.sqlite')

        break

    while True:  # init MENU -------------------------------------------
        def_txt, frm = [], '{: <10}  => {: ^15}\n'
        def_txt.append(frm.format('db_tod'  , '\\DB\\db_today.sqlite'))
        def_txt.append(frm.format('db_arc'  , '\\DB\\db_archiv.sqlite'))
        def_txt.append(frm.format('db_pack_t' , '\\DB\\db_pack_t.sqlite'))
        def_txt.append(frm.format('db_pack_a' , '\\DB\\db_pack_a.sqlite'))
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
        event_menu(event, db_FUT_t, db_FUT_a, db_PACK_t, db_PACK_a)
        #---------------------------------------------------------------
        if event is None or event == 'Quit' or event == 'Exit': break
        #---------------------------------------------------------------
        if event == 'auto'   :    tm_out, mode =  2500,   'auto'
        #---------------------------------------------------------------
        if event == 'manual' :    tm_out, mode = 360000, 'manual'
        #---------------------------------------------------------------
        if event == '__TIMEOUT__':
            pass
            #rq = db_TODAY.op(
        #---------------------------------------------------------------
        window.FindElement('txt_data').Update('\n'.join(stroki))
        stts  = time.strftime(frm, time.localtime()) + '\n'
        stts += 'event = ' + event
        window.FindElement('txt_status').Update(stts)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
