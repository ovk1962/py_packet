#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_TABL.py
#
#=======================================================================
# TO DO
# 1. wndw_menu_HIST_FUT / wndw_menu_ACNT +++++++++++++++++++++++++++++++
# 2. write info from file HIST_FUT in file ***  ++++++++++++++++++++++++
# 3. clear file HIST_FUT (?) and tables hist_FUT/hist_PACK today +++++++
# 4. wndw_menu_SERV  ---------------------------------------------------
#=======================================================================
import os, sys, math, time, sqlite3, logging
from datetime import datetime, timezone
import math
#from ipdb import set_trace as bp    # to set breakpoints just -> bp()
import PySimpleGUI as sg
#=======================================================================
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st, background_color = 'Pink',       no_titlebar = False, keep_on_top=True)
wrn_lmb = lambda st,s: sg.PopupOK(s,    title=st, background_color = 'Gold',       no_titlebar = False, keep_on_top=True)
ok_lmb  = lambda st,s: sg.PopupOK(s,    title=st, background_color = 'LightGreen', no_titlebar = False, keep_on_top=True)
#
locationXY = (300, 50)
menu_def = [sg.Menu([['TABLES',  ['CFG_SOFT',        'CFG_PACK',       '---',
                                  'DATA_ACNT_TABL',  'DATA_FUT_TABL',  '---',
                                  'HIST_TABL_TODAY', 'HIST_TABL_ARCH', '---',
                                  'Exit',],],
                     ['SERVICE', ['APPEND_HIST_FILE', 'CLR_HIST_TBL',],]],
                tearoff=False, key='-MENU-')]
#=======================================================================
class Class_CNST():
    # cfg_soft
    titul, path_file_DATA, path_file_HIST, dt_start, path_file_TXT = range(5)
    head_cfg_soft  = ['name', 'val']
    # cfg_pck
    kNm, kKoef, kNul, kEma, kGo, kPos, kNeg = range(7)
    head_cfg_pack  = ['nm', 'koef', 'nul', 'ema', 'go', 'pos', 'neg', 'ratio']
    #
    # account
    head_data_acnt = ['name', 'val']
    #
    head_data_fut  = ['P_code', 'Rest', 'Var_mrg', 'Open_prc', 'Last_prc',
                'Ask', 'Buy_qty', 'Bid', 'Sell_qty', 'Fut_go', 'Open_pos' ]
    sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos  = range(11)
#=======================================================================
class Class_LGR():
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
class Class_FUT():
    def __init__(self):
        self.sP_code, self.arr = '', []
    def __retr__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
    def __str__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
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
class Class_ACNT():
    def __init__(self):
        self.ss = '        bal,      prf,      go,       dep'
        self.dt, self.arr  = '', []
    def __retr__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
    def __str__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
#=======================================================================
class Class_GLBL():
    def __init__(self):
        c_dir    = os.path.abspath(os.curdir)
        self.lg_file  = Class_LGR      (c_dir + '\\LOG\\py_TABL.log')
        self.db_ARCHV = Class_DB_SQLite(c_dir + '\\DB\\db_ARCH.sqlite')
        self.db_TODAY = Class_DB_SQLite(c_dir + '\\DB\\db_TODAY.sqlite')
        self.cfg_soft = [] # list of table 'cfg_SOFT'
        #
        self.wndw_menu   = ''
        self.stastus_bar = ''
        #
        self.cfg_soft = []          # list of table 'cfg_SOFT'
        self.cfg_pck  = []          # list of table 'cfg_PACK' (unpack)
        self.dt_fut   = []          # list obj FUTs from table 'data_FUT'
        self.account  = Class_ACNT()# obj Class_ACNT()
        #
        self.arr_fut_t = []
        self.arr_fut_a = []
        self.arr_pck_t = []
        self.arr_pck_a = []
        #
        self.dt_db_TODAY = 0     # time modificated of file db_TODAY (seconds)
        #
        self.err_status  = 0
        #self.cnt_errors  = 0
    #-------------------------------------------------------------------
    def err_DB(self, err_pop = False, err_log = False):
        #self.cnt_errors += 1
        if err_pop:
            err_lmb('err_rd_term',
                s_lmb(bin(self.err_status) + str(5*' ') + str(self.err_status)) )
        if err_log:
            wr_log_error('err_rd_term => ' + str(self.err_status))
    #-------------------------------------------------------------------
    def prn_arr(self, name_arr, arr):
        print('len(' + name_arr + ')   => ' + str(len(arr)) + '\n' )
        if len(arr) > 4:
            for i in [0,1]: print(arr[i],'\n')
            print('+++++++++++++++++++++++++\n')
            for i in [-2,-1]: print(arr[i],'\n')
        else:
            for item in arr: print(item, '\n')
    #-------------------------------------------------------------------
    def read_cfg_soft(self):
        print('=> _GLBL read_cfg_soft')
        try:
            tbl = self.db_TODAY.read_tbl('cfg_SOFT')
            if tbl[0] > 0:
                self.err_status = 'read_cfg_soft   ' + s_lmb(tbl[1])
                self.err_DB(err_pop = True, err_log = True)
                return [2, tbl[1]]
            self.cfg_soft = tbl[1]
            #for item in self.cfg_soft: print(item)
        except Exception as ex:
            err_lmb('read_cfg_soft', str(ex))
            return [1, ex]
        return [0, tbl[1]]
    #-------------------------------------------------------------------
    def read_data_FUT(self):
        print('=> _GL read_data_FUT')
        try:
            tbl = self.db_TODAY.read_tbl('data_FUT')
            if tbl[0] > 0:
                self.err_status = 'read_data_FUT   ' + s_lmb(tbl[1])
                self.err_DB(err_log = True)
                return [2, tbl[1]]

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
            # print(self.account)
            # for i in self.dt_fut:   print(i)

        except Exception as ex:
            self.err_status = 'read_data_FUT / try  ' + s_lmb(ex)
            self.err_DB(err_log = True)
            return [1, ex]
        return [0, tbl[1]]
    #-------------------------------------------------------------------
    def read_cfg_PACK(self):
        print('=> _GL read_cfg_PACK')
        try:
            tbl = self.db_TODAY.read_tbl('cfg_PACK')
            if tbl[0] > 0:
                self.err_status = 'read_cfg_PACK   ' + s_lmb(tbl[1])
                self.err_DB(err_log = True)
                return [2, tbl[1]]
            self.cfg_pck = []
            for item in tbl[1]:
                arr_k    = item[Class_CNST.kKoef].split(',')
                arr_koef, buf = [], []
                for item_k in arr_k:             # '0:2:SR' => [0, 32, 'SR']
                    arr_koef.append([int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')])
                buf = [item[Class_CNST.kNm],
                        arr_koef,
                        int(item[Class_CNST.kNul]),
                        [int(e) for e in item[Class_CNST.kEma].split(':')],
                        int(item[Class_CNST.kGo]),
                        int(item[Class_CNST.kPos]),
                        int(item[Class_CNST.kNeg])]
                while len(Class_CNST.head_cfg_pack)-1 > len(buf):
                    buf.append('')
                self.cfg_pck.append(buf)

            # for item in self.cfg_pck: print(item)
            # ok_lmb('read_cfg_PACK', '1 cfg_pck')

            # rep = self.calc_cfg_pack()
            # if rep[0] > 0:
                # self.err_status = 'read_cfg_PACK calc_cfg_pack   ' + s_lmb(rep[1])
                # self.err_DB(err_log = True)
                # return [3, rep[1]]

            # for item in self.cfg_pck: print(item)
            # ok_lmb('read_cfg_PACK', '2 cfg_pck')

        except Exception as ex:
            self.err_status = 'read_cfg_PACK / try  ' + s_lmb(ex)
            self.err_DB(err_log = True)
            return [1, ex]

        # for item in tbl[1]: print(item)
        # ok_lmb('read_cfg_PACK', '3 tbl[1]')

        return [0, tbl[1]]
    #-------------------------------------------------------------------
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
                for pck in item[Class_CNST.kKoef]:
                    prc = int((mtrx[pck[0]][Class_CNST.sAsk] + mtrx[pck[0]][Class_CNST.sBid])/2)
                    if pck[0] != 9:
                        pck_go += int(abs(pck[1]) * mtrx[pck[0]][Class_CNST.sFut_go])
                    else:
                        pck_go += int(abs(pck[1]/10) * mtrx[pck[0]][Class_CNST.sFut_go])
                    if pck[1] > 0:  pck_pos += int(prc * pck[1])
                    else:           pck_neg += int(prc * abs(pck[1]))
                cfg_go_pos_neg.append( [pck_go, pck_pos, pck_neg] )
            for i, item in enumerate(cfg_go_pos_neg):
                self.cfg_pck[i][-3:] = item
            #
            rep = self.update_tbl_cfg_pack()
            if rep[0] > 0:
                self.err_status = 'calc_cfg_pack   ' + s_lmb(rep[1])
                self.err_DB(err_log = True)
                return [2, rep[1]]

        except Exception as ex:
            self.err_status = 'calc_cfg_pack / try  ' + s_lmb(ex)
            self.err_DB(err_log = True)
            return [1, ex]
        return [0, 'ok']
    #-------------------------------------------------------------------
    def update_tbl_cfg_pack(self):
        print('=> _GL update_tbl_cfg_pack ')
        try:
            cfg_lst, cfg = [], self.cfg_pck
            #  ['pack1', [[0, 3, 'SR'], [1, 2, 'GZ']], 7517, [1111, 150], 0, 0, 0]
            #  ['pack1', '0:3:SR,1:2:GZ', 7517, '1111:150', 0, 0, 0]
            for j in range(len(cfg)):
                str_koef = ''
                for ss in cfg[j][Class_CNST.kKoef]:
                    str_koef += ':'.join((str(s) for s in ss)) + ','
                cfg_lst.append([cfg[j][Class_CNST.kNm],       # kNm
                                str_koef[:-1],          # kKoef
                                cfg[j][Class_CNST.kNul],      # kNul
                                ':'.join(str(s) for s in cfg[j][Class_CNST.kEma]),
                                cfg[j][Class_CNST.kGo],       # kGo
                                cfg[j][Class_CNST.kPos],      # kPos
                                cfg[j][Class_CNST.kNeg]       # kNeg
                                ])
            rep = self.db_TODAY.update_tbl('cfg_PACK', cfg_lst, val = ' VALUES(?,?,?,?,?,?,?)')
            if rep[0] > 0:
                self.err_status = 'update_tbl_cfg_pack   ' + s_lmb(rep[1])
                self.err_DB(err_log = True)
                return [2, rep[1]]
        except Exception as ex:
            self.err_status = 'update_tbl_cfg_pack / try  ' + s_lmb(ex)
            self.err_DB(err_log = True)
            return [1, ex]
        return [0, cfg_lst]

    def unpack_str_fut(self, hist_fut):
        print('=> _GL unpack_str_fut ', len(hist_fut))
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
            self.err_status = 'unpack_str_fut / try  ' + s_lmb(ex)
            self.err_DB(err_log = True)
            return [1, ex]

        return [0, arr_fut]
#=======================================================================
def wndw_menu_CFG_SOFT(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    layout_CFG_SOFT =[  menu_def,
                        [sg.Table(
                            values   = _gl.cfg_soft,
                            num_rows = min(len(_gl.cfg_soft), 10),
                            headings = Class_CNST.head_cfg_soft,
                            key      = '_CFG_SOFT_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'thistle',
                            )],
                        [sg.StatusBar(text= _gl.account.dt + '  wait ...', size=(42,1), key='_st_bar_'),
                         sg.Exit()]]
    wndw = sg.Window('DB_TABL / CFG_SOFT', location=locationXY).Layout(layout_CFG_SOFT)
    _gl.wndw_menu   = 'CFG_SOFT'
    return wndw
#=======================================================================
def wndw_menu_CFG_PACK(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    mtrx = []
    for item in _gl.cfg_pck:
        ratio = str(round(item[Class_CNST.kPos]/item[Class_CNST.kNeg],2))
        mtrx.append(item + [ratio])
    layout_CFG_PACK =[  menu_def,
                        [sg.Table(
                            values   = mtrx,
                            num_rows = min(len(mtrx), 30),
                            headings = Class_CNST.head_cfg_pack,
                            key      = '_CFG_PACK_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'coral',
                            )],
                        [sg.StatusBar(text= _gl.account.dt + '  wait ...', size=(42,1), key='_st_bar_'),
                         sg.Exit()]]
    wndw = sg.Window('DB_TABL / CFG_PACK', location=locationXY).Layout(layout_CFG_PACK)
    _gl.wndw_menu   = 'CFG_PACK'
    return wndw
#=======================================================================
def wndw_menu_DATA_ACNT_TABL(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    mtrx = [['Date / Time  ',_gl.account.dt,],
            ['BALANCE      ',str(_gl.account.arr[0]),],
            ['PROFIT / LOSS',str(_gl.account.arr[1]),],
            ['GO           ',str(_gl.account.arr[2]),],
            ['DEPOSIT      ',str(_gl.account.arr[3]),]]
    layout_DATA_ACNT_TABL =[  menu_def,
                        #[sg.Text('0000.00', font= 'ANY 60', key='_txt_acnt_')],
                        [sg.Table(
                            values   = mtrx,
                            num_rows = min(len(mtrx), 30),
                            headings = Class_CNST.head_data_acnt,
                            key      = '_DATA_ACNT_TABL_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'lavender',
                            )],
                        [sg.StatusBar(text= _gl.account.dt + '  wait ...', size=(40,1), key='_st_bar_'), sg.Exit()]]
    wndw = sg.Window('DB_TABL / DATA_ACNT_TABL', location=locationXY).Layout(layout_DATA_ACNT_TABL)
    _gl.wndw_menu   = 'DATA_ACNT_TABL'
    return wndw
#=======================================================================
def wndw_menu_DATA_FUT_TABL(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    if len(_gl.dt_fut) == 0:
        mtrx = [['empty',0,0,0,0,0,0,0,0,0,0,],
                ['empty',0,0,0,0,0,0,0,0,0,0,]]
    else:
        mtrx = [([item.sP_code] + item.arr) for item in _gl.dt_fut]
    layout_DATA_FUT_TABL =[  menu_def,
                        [sg.Table(
                            values   = mtrx,
                            num_rows = min(len(mtrx), 30),
                            headings = Class_CNST.head_data_fut,
                            key      = '_DATA_FUT_TABL_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'lightsteelblue',
                            )],
                        [sg.StatusBar(text= _gl.account.dt + '  wait ...', size=(100,1), key='_st_bar_'), sg.Exit()]]
    wndw = sg.Window('DB_TABL / DATA_FUT_TABL', location=locationXY).Layout(layout_DATA_FUT_TABL)
    _gl.wndw_menu   = 'DATA_FUT_TABL'
    return wndw
#=======================================================================
def event_menu_CFG_SOFT(ev, val, wndw, _gl):
    rq = [0,ev]
    #os.system('cls')  # on windows
    #-------------------------------------------------------------------
    rep = _gl.read_cfg_soft()
    if rep[0] > 0:
        err_lmb('main', s_lmb('Could not read table *cfg_soft*!') + s_lmb(rep[1]))
        return
    #-------------------------------------------------------------------
    wndw.FindElement('_CFG_SOFT_table_').Update(_gl.cfg_soft)
    if 'wait' in _gl.stastus_bar:
        wndw.FindElement('_st_bar_').Update(_gl.stastus_bar, background_color = 'Gold')
    else:
        wndw.FindElement('_st_bar_').Update(_gl.stastus_bar, background_color = 'LightGreen')
#=======================================================================
def event_menu_CFG_PACK(ev, val, wndw, _gl):
    rq = [0,ev]
    #os.system('cls')  # on windows
    #-------------------------------------------------------------------
    rep = _gl.read_cfg_PACK()
    if rep[0] > 0:
        err_lmb('event_menu_CFG_PACK', s_lmb('Could not read table *cfg_PACK*!') + s_lmb(rep[1]))
        return
    #-------------------------------------------------------------------
    # You must calc_cfg_pack After EDIT/CHANGE parametrs PACKET
    #-------------------------------------------------------------------
    mtrx = []
    for item in _gl.cfg_pck:
        ratio = str(round(item[Class_CNST.kPos]/item[Class_CNST.kNeg],2))
        mtrx.append(item + [ratio])
    wndw.FindElement('_CFG_PACK_table_').Update(mtrx)
    #-------------------------------------------------------------------
    if 'wait' in _gl.stastus_bar:
        wndw.FindElement('_st_bar_').Update(_gl.stastus_bar, background_color = 'Gold')
    else:
        wndw.FindElement('_st_bar_').Update(_gl.stastus_bar, background_color = 'LightGreen')
#=======================================================================
def event_menu_DATA_ACNT_TABL(ev, val, wndw, _gl):
    rq = [0,ev]
    #os.system('cls')  # on windows
    #-------------------------------------------------------------------
    mtrx = [['Date / Time  ',_gl.account.dt,],
            ['BALANCE      ',str(_gl.account.arr[0]),],
            ['PROFIT / LOSS',str(_gl.account.arr[1]),],
            ['GO           ',str(_gl.account.arr[2]),],
            ['DEPOSIT      ',str(_gl.account.arr[3]),]]
    wndw.FindElement('_DATA_ACNT_TABL_table_').Update(mtrx)
    if 'wait' in _gl.stastus_bar:
        wndw.FindElement('_st_bar_').Update(_gl.stastus_bar, background_color = 'Gold')
    else:
        wndw.FindElement('_st_bar_').Update(_gl.stastus_bar, background_color = 'LightGreen')
#=======================================================================
def event_menu_DATA_FUT_TABL(ev, val, wndw, _gl):
    rq = [0,ev]
    #os.system('cls')  # on windows
    #-------------------------------------------------------------------
    mtrx = [([item.sP_code] + item.arr) for item in _gl.dt_fut]
    wndw.FindElement('_DATA_FUT_TABL_table_').Update(mtrx)
    if 'wait' in _gl.stastus_bar:
        wndw.FindElement('_st_bar_').Update(_gl.stastus_bar, background_color = 'Gold')
    else:
        wndw.FindElement('_st_bar_').Update(_gl.stastus_bar, background_color = 'LightGreen')
#=======================================================================
def main():
    # init -------------------------------------------------------------
    while True:     # INIT cycle  --------------------------------------
        sg.ChangeLookAndFeel('SystemDefault')
        _gl = Class_GLBL()
        #
        rep = _gl.read_cfg_soft()
        if rep[0] > 0:
            err_lmb('main', s_lmb('Could not read table *cfg_soft*!') + s_lmb(rep[1]))
            return 0
        else:
            # ok_lmb('main', s_lmb('Read table *cfg_soft* successfully !'))
            os.system('cls')  # on windows
        #
        rep = _gl.read_data_FUT()
        if rep[0] > 0:
            err_lmb('main', s_lmb('Could not read table *data_FUT*!') + s_lmb(rep[1]))
            return 0
        else:
            # ok_lmb('main', s_lmb('Read table *data_FUT* successfully !'))
            os.system('cls')  # on windows
        #
        rep = _gl.read_cfg_PACK()
        if rep[0] > 0:
            err_lmb('main', s_lmb('Could not read table *cfg_PACK*!') + s_lmb(rep[1]))
            return 0
        else:
            rep = _gl.calc_cfg_pack()
            if rep[0] > 0:
                err_lmb('main', s_lmb('Could not calc table *cfg_PACK*!') + s_lmb(rep[1]))
                return 0
            # ok_lmb('main', s_lmb('Read table *cfg_PACK* successfully !'))
            os.system('cls')  # on windows


        break
    #
    wndw = sg.Window('START').Layout([menu_def, [sg.Exit()]])
    wndw = wndw_menu_CFG_PACK(wndw, _gl)
    #
    while True:     # MAIN cycle  --------------------------------------
        # for sg.Input must be => wndw.Read()  OR  timeout > 10000
        evn, val = wndw.Read(timeout = 3500)
        os.system('cls')  # on windows
        print('----------------------------------------------')
        print('evn = ', evn, '     val =', val)
        if evn in (None, 'Exit'): break
        #
        if evn == '__TIMEOUT__':
            #--- Read time modificated of file db_TODAY ----------------
            buf_stat = os.stat(os.path.abspath(os.curdir) +
                                            '\\DB\\db_TODAY.sqlite')
            #--- check time modificated of file ------------------------
            if int(buf_stat.st_mtime) > _gl.dt_db_TODAY:
                #ok_lmb('main', s_lmb('new time !'))
                _gl.dt_db_TODAY = int(buf_stat.st_mtime)
                rep = _gl.read_data_FUT()
                if rep[0] > 0:
                    _gl.stastus_bar = _gl.account.dt + 3*' ' + 'error ...'
                else:
                    _gl.stastus_bar = _gl.account.dt + 3*' ' + 'Got new DATA'
            else:
                _gl.stastus_bar = _gl.account.dt + 3*' ' + 'wait ...'

        if _gl.wndw_menu == 'CFG_SOFT':
            event_menu_CFG_SOFT(evn, val, wndw, _gl)
        elif _gl.wndw_menu == 'CFG_PACK':
            print('_gl.stastus_bar', _gl.stastus_bar)
            event_menu_CFG_PACK(evn, val, wndw, _gl)
        elif _gl.wndw_menu == 'DATA_ACNT_TABL':
            event_menu_DATA_ACNT_TABL(evn, val, wndw, _gl)
        elif _gl.wndw_menu == 'DATA_FUT_TABL':
            event_menu_DATA_FUT_TABL(evn, val, wndw, _gl)
        else:      pass
        #
        if evn == 'CFG_SOFT':
            wndw = wndw_menu_CFG_SOFT(wndw, _gl)
        elif evn == 'CFG_PACK':
            wndw = wndw_menu_CFG_PACK(wndw, _gl)
        elif evn == 'DATA_ACNT_TABL':
            wndw = wndw_menu_DATA_ACNT_TABL(wndw, _gl)
        elif evn == 'DATA_FUT_TABL':
            wndw = wndw_menu_DATA_FUT_TABL(wndw, _gl)
        else:      pass
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
