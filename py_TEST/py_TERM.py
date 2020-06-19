#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pyTERM.py
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
menu_def = [sg.Menu([['TABLES',  ['CFG_SOFT', 'DATA_ACNT', '---',
                                  'DATA_FUT_FILE', 'DATA_HIST_FILE', '---',
                                  'Exit',],],
                     ['SERVICE', ['SAVE_HIST_FILE', 'CLR_HIST_TBL',],]],
                tearoff=False, key='-MENU-')]
#=======================================================================
class Class_CNST():
    # cfg_soft
    titul, path_file_DATA, path_file_HIST, dt_start, path_file_TXT = range(5)
    head_cfg_soft  = ['name', 'val']
    # account
    head_data_acnt = ['name', 'val']
    #
    head_data_fut  = ['P_code', 'Rest', 'Var_mrg', 'Open_prc', 'Last_prc',
                'Ask', 'Buy_qty', 'Bid', 'Sell_qty', 'Fut_go', 'Open_pos' ]
    sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos  = range(11)
    # hist_fut
    head_data_hst  = ['name', 'val']
    fAsk, fBid = range(2)
    # account
    aBal, aPrf, aGo, aDep = range(4)
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

    def update_2_tbl(self,
                    nm_tbl_1, buf_arr_1,
                    nm_tbl_2, buf_arr_2,
                    val1 = ' VALUES(?)', val2 = ' VALUES(?,?)'):
        print('=> _SQLite update_2_tbl ', nm_tbl_1, '   ', nm_tbl_2)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- update table nm_tbl ---------------------------
                cur.execute('DELETE FROM ' + nm_tbl_1)
                cur.execute('DELETE FROM ' + nm_tbl_2)
                cur.executemany('INSERT INTO ' + nm_tbl_1 + val1, buf_arr_1)
                cur.executemany('INSERT INTO ' + nm_tbl_2 + val2, buf_arr_2)
                conn.commit()
                #--- read  table   ---------------------------------
                #cur.execute('SELECT * from ' + nm_tbl_1)
                #arr = cur.fetchall()    # read LIST arr from TABLE nm_tbl
        except Exception as ex:
            return [1, ex]
        return [0, 'ok']
#=======================================================================
class Class_FUT():
    def __init__(self):
        self.sP_code, self.arr = '', []
    def __retr__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
    def __str__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
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
class Class_TRMN():
    #---------------------------  err_status  --------------------------
    err_try  = 128      #
    err_file = 1        # can not find file => path_file_DATA
    err_size = 2        # size DATA file is 0
    err_mdf_time  = 4   # FILE is not modificated
    err_file_size = 8   # FILE size is NULL
    #err_mrkt_time = 16  # size buf_str is NULL
    err_update_db = 32  #  can not update info in DB
    #-------------------------------------------------------------------
    def __init__(self):
        self.path_file_DATA = ''
        self.path_file_HIST = ''
        c_dir    = os.path.abspath(os.curdir)
        self.lg_file =    Class_LGR(c_dir + '\\LOG\\py_TERM.log')
        #
        self.dt_file = 0        # curv stamptime data file path_file_DATA
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.data_in_file = []  # list of strings from path_file_DATA
        self.hist_in_file = []  # list of strings from path_file_HIST
        #
        self.dt_fut      = []    # list of Class_FUT()
        #self.data_Class_str_FUT  = []    # list of Class_str_FUT()
        self.account = Class_ACNT()  # obj Class_ACCOUNT()
        #
        self.time_1_min = 0
        #
        self.err_status  = 0
        self.cnt_errors  = 0
    #-------------------------------------------------------------------
    def err_rd_term(self, err_pop = False, err_log = False):
        self.cnt_errors += 1
        if err_pop:
            err_lmb('err_rd_term',
                s_lmb(bin(self.err_status) + str(5*' ') + str(self.err_status)) +
                s_lmb('----------------------------------------------------') +
                s_lmb('0b001      1   # can not find file => path_file_DATA') +
                s_lmb('0b010      2   # size DATA file is 0                ') +
                s_lmb('0b100      4   # FILE is not modificated            ') +
                s_lmb('0b1000     8   # FILE size is NULL                  ') +
                s_lmb('0b100000   32  # can not update info in DB          ') +
                s_lmb('0b10000000 128 # error of TRY                       ')
                )
        if err_log:
            wr_log_error('err_rd_term => ' + str(self.err_status))
    #-------------------------------------------------------------------
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
    #-------------------------------------------------------------------
    def rd_term_FUT(self):
        # read data FUT from file 'path_file_DATA'----------------------
        print('=> _TERM rd_term_FUT')
        self.err_status  = 0
        try:
            #--- check file self.file_path_DATA ------------------------
            if not os.path.isfile(self.path_file_DATA):
                self.err_status += self.err_file
                return
            buf_stat = os.stat(self.path_file_DATA)
            #--- check size of file ------------------------------------
            if buf_stat.st_size == 0:
                self.err_status += self.err_size
                return
            #--- check time modificated of file ------------------------
            print('self.dt_file       ', self.dt_file)
            print('buf_stat.st_mtime  ', int(buf_stat.st_mtime))
            if int(buf_stat.st_mtime) == self.dt_file:
                #str_dt_file = datetime.fromtimestamp(self.dt_file).strftime('%H:%M:%S')
                self.err_status += self.err_mdf_time
                return
            else:
                self.dt_file = int(buf_stat.st_mtime)
            #--- read TERM file ----------------------------------------
            buf_str = []
            with open(self.path_file_DATA,"r") as fh:
                buf_str = fh.read().splitlines()
            #--- check size of list/file -------------------------------
            if len(buf_str) == 0:
                self.err_status += self.err_file_size
                return
            self.data_in_file = buf_str[:]
            #for i in self.data_in_file:   print(i)
            #
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
            self.err_status += self.err_try
        return
    #-------------------------------------------------------------------
    def rd_term_HST(self):
        # read HIST from file 'path_file_HIST'--------------------------
        print('=> _TERM rd_term_HST')
        self.err_status  = 0
        try:
            path_hist = self.path_file_HIST
            #--- check file self.path_file_HIST ------------------------
            if not os.path.isfile(path_hist):
                self.err_status += self.err_file # can not find path_file_HIST
                return
            buf_stat = os.stat(path_hist)
            #--- check size of file ------------------------------------
            if buf_stat.st_size == 0:
                self.err_status += self.err_size # size HIST file is NULL
                return
            #--- read HIST file ----------------------------------------
            buf_str = []
            with open(path_hist,"r") as fh:
                buf_str = fh.read().splitlines()
            #--- check size of list/file -------------------------------
            if len(buf_str) == 0:
                self.err_status += self.err_file_size # the size buf_str(HIST) is NULL
                return
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
            #
        except Exception as ex:
            print('rd_term_HST\n' + str(ex))
            self.err_status += self.err_try
        return
#=======================================================================
class Class_GLBL():
    def __init__(self):
        self.trm = Class_TRMN()
        c_dir    = os.path.abspath(os.curdir)
        self.db_ARCHV = Class_DB_SQLite(c_dir + '\\DB\\db_ARCH.sqlite')
        self.db_TODAY = Class_DB_SQLite(c_dir + '\\DB\\db_TODAY.sqlite')
        self.cfg_soft = [] # list of table 'cfg_SOFT'
        self.wndw_menu   = ''
        self.stastus_bar = ''
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
                err_lmb('read_cfg_soft', tbl[1])
                return [2, tbl[1]]
            self.cfg_soft = tbl[1]
            # frm = '%Y-%m-%d %H:%M:%S'
            # self.dt_start_sec = \
                # int(datetime.strptime(self.dt_start, frm).replace(tzinfo=timezone.utc).timestamp())
            for item in self.cfg_soft: print(item)
            self.trm.path_file_DATA = self.cfg_soft[Class_CNST.path_file_DATA][1]
            self.trm.path_file_HIST = self.cfg_soft[Class_CNST.path_file_HIST][1]
            #ok_lmb('read_cfg_soft', self.cfg_soft)
        except Exception as ex:
            err_lmb('read_cfg_soft', str(ex))
            return [1, ex]
        return [0, tbl[1]]
#=======================================================================
def wndw_menu_DATA_FUT_FILE(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    if len(_gl.trm.dt_fut) == 0:
        mtrx = [['empty',0,0,0,0,0,0,0,0,0,0,],
                ['empty',0,0,0,0,0,0,0,0,0,0,]]
    else:
        mtrx = [([item.sP_code] + item.arr) for item in _gl.trm.dt_fut]
    layout_DATA_FUT_FILE =[  menu_def,
                        [sg.Table(
                            values   = mtrx,
                            num_rows = min(len(mtrx), 30),
                            headings = Class_CNST.head_data_fut,
                            key      = '_DATA_FUT_FILE_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'lightsteelblue',
                            )],
                        [sg.StatusBar(text= _gl.trm.account.dt + '  wait ...', size=(100,1), key='_st_fut_'), sg.Exit()]]
    wndw = sg.Window(_gl.cfg_soft[Class_CNST.titul][1]+' / DATA_FUT_FILE', location=locationXY).Layout(layout_DATA_FUT_FILE)
    _gl.wndw_menu   = 'DATA_FUT_FILE'
    return wndw
#=======================================================================
def wndw_menu_DATA_ACNT(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    mtrx = [['Date / Time  ',_gl.trm.account.dt,],
            ['BALANCE      ',str(_gl.trm.account.arr[0]),],
            ['PROFIT / LOSS',str(_gl.trm.account.arr[1]),],
            ['GO           ',str(_gl.trm.account.arr[2]),],
            ['DEPOSIT      ',str(_gl.trm.account.arr[3]),]]
    layout_DATA_ACNT =[  menu_def,
                        [sg.Text('0000.00', font= 'ANY 60', key='_txt_acnt_', justification = 'center')],
                        [sg.Table(
                            values   = mtrx,
                            num_rows = min(len(mtrx), 30),
                            headings = Class_CNST.head_data_acnt,
                            key      = '_DATA_ACNT_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'lavender',
                            )],
                        [sg.StatusBar(text= _gl.trm.account.dt + '  wait ...', size=(40,1), key='_st_acnt_'), sg.Exit()]]
    wndw = sg.Window(_gl.cfg_soft[Class_CNST.titul][1]+' / DATA_ACNT', location=locationXY).Layout(layout_DATA_ACNT)
    _gl.wndw_menu   = 'DATA_ACNT'
    return wndw
#=======================================================================
def wndw_menu_DATA_HIST_FILE(wndw, _gl):
    os.system('cls')  # on windows
    wndw.Close()
    mtrx = [['first' ,'-----------------------------------',],
            ['second','-----------------------------------',],
            ['------','-----------------------------------',],
            ['last'  ,'-----------------------------------',],
            ['lench' ,'-----------------------------------',]]
    mtrx_db = mtrx[:]
    if len(_gl.trm.hist_in_file) > 0:
        mtrx = [['first', _gl.trm.hist_in_file[0].split('|')[0],],
                ['second',_gl.trm.hist_in_file[1].split('|')[0],],
                ['------','-----------------------------------',],
                ['last' , _gl.trm.hist_in_file[-1].split('|')[0],],
                ['lench', len(_gl.trm.hist_in_file),]]

    layout_DATA_HIST_FILE =[  menu_def,
                        [sg.T('File HIST => ' + _gl.trm.path_file_HIST)],
                        [sg.Table(
                            values   = mtrx,
                            num_rows = min(len(mtrx), 30),
                            headings = Class_CNST.head_data_hst,
                            key      = '_DATA_HIST_FILE_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'darkgrey',
                            )],
                        [sg.T('Table hist_FUT => \DB\db_TODAY.sqlite')],
                        [sg.Table(
                            values   = mtrx_db,
                            num_rows = min(len(mtrx_db), 30),
                            headings = Class_CNST.head_data_hst,
                            key      = '_DATA_HIST_FILE_table_DB_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'darkgray',
                            )],
                        [sg.Button('CLR TABLE HIST_FUT',  key='-CLR_TBL_HIST_FUT-'),
                         sg.Button('READ TABLE HIST_FUT', key='-READ_TBL_HIST_FUT-')],
                        [sg.StatusBar(text= _gl.trm.account.dt + '  wait ...', size=(32,1), key='_st_hst_'), sg.Exit()]]
    wndw = sg.Window(_gl.cfg_soft[Class_CNST.titul][1]+' / DATA_HIST_FILE', location=locationXY).Layout(layout_DATA_HIST_FILE)
    _gl.wndw_menu   = 'DATA_HIST_FILE'
    return wndw
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
                        [sg.Button('___EDIT___', key='-EDIT_CFG_SOFT-'),
                         sg.Button('__SAVE__'  , key='-SAVE_HIST_FILE-')],
                        [sg.StatusBar(text= _gl.trm.account.dt + '  wait ...', size=(42,1), key='_st_soft_'),
                         sg.Exit()]]
    wndw = sg.Window(_gl.cfg_soft[Class_CNST.titul][1]+' / CFG_SOFT', location=locationXY).Layout(layout_CFG_SOFT)
    _gl.wndw_menu   = 'CFG_SOFT'
    return wndw
#=======================================================================
def event_menu_DATA_HIST_FILE(ev, val, wndw, _gl):
    rq = [0,ev]
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if ev == '-READ_TBL_HIST_FUT-':
        print('-READ_TBL_HIST_FUT-')
        print(val)
        rep = _gl.db_TODAY.read_tbl('hist_FUT')
        if rep[0] == 0:
            if len(rep[1]) > 1:
                mtrx_db = [['first', rep[1][0][1].split('|')[0],],
                           ['second',rep[1][1][1].split('|')[0],],
                           ['------','-----------------------------------',],
                           ['last' , rep[1][-1][1].split('|')[0],],
                           ['lench', len(rep[1]),]]
            else:
                mtrx_db = [['first', '',],
                           ['second','',],
                           ['------','-----------------------------------',],
                           ['last' , '',],
                           ['lench', len(rep[1]),]]
            wndw.FindElement('_DATA_HIST_FILE_table_DB_').Update(mtrx_db)
            ok_lmb(ev,'OK, read table *hist_FUT* successfully !')
        else:
            err_lmb(ev,'Could not read table *hist_FUT* !' + rep[1])
    #-------------------------------------------------------------------
    if ev == '-CLR_TBL_HIST_FUT-':
        print('-CLR_TBL_HIST_FUT-')
        print(val)
        rep = _gl.db_TODAY.update_tbl('hist_PACK', [])
        if rep[0] == 0:
            ok_lmb(ev,'OK, clear table *hist_PACK* successfully !')
        else:
            err_lmb(ev,'Could not clear table *hist_PACK* !' + rep[1])
        rep = _gl.db_TODAY.update_tbl('hist_FUT', [])
        if rep[0] == 0:
            ok_lmb(ev,'OK, clear table *hist_FUT* successfully !')
        else:
            err_lmb(ev,'Could not clear table *hist_FUT* !' + rep[1])
    #-------------------------------------------------------------------
    if len(_gl.trm.hist_in_file) > 2:
        mtrx = [['first',_gl.trm.hist_in_file[0].split('|')[0],],
                ['second',_gl.trm.hist_in_file[1].split('|')[0],],
                ['------','-----------------------------------',],
                ['last' ,_gl.trm.hist_in_file[-1].split('|')[0],],
                ['lench',len(_gl.trm.hist_in_file),]]
        wndw.FindElement('_DATA_HIST_FILE_table_').Update(mtrx)
    if _gl.trm.cnt_errors < 2:
        wndw.FindElement('_st_hst_').Update(_gl.stastus_bar, background_color = 'LightGreen')
    else:
        wndw.FindElement('_st_hst_').Update(_gl.stastus_bar, background_color = 'Pink')
#=======================================================================
def event_menu_DATA_FUT_FILE(ev, val, wndw, _gl):
    rq = [0,ev]
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    mtrx = [([item.sP_code] + item.arr) for item in _gl.trm.dt_fut]
    wndw.FindElement('_DATA_FUT_FILE_table_').Update(mtrx)
    if _gl.trm.cnt_errors < 2:
        wndw.FindElement('_st_fut_').Update(_gl.stastus_bar, background_color = 'LightGreen')
    else:
        wndw.FindElement('_st_fut_').Update(_gl.stastus_bar, background_color = 'Pink')
#=======================================================================
def event_menu_CFG_SOFT(ev, val, wndw, _gl):
    rq = [0,ev]
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    rep = _gl.read_cfg_soft()
    if rep[0] > 0:
        err_lmb('main', s_lmb('Could not read table *cfg_soft*!') + s_lmb(rep[1]))
        return
    #-------------------------------------------------------------------
    if ev == '-EDIT_CFG_SOFT-':
        print('-EDIT_CFG_SOFT-')
        print(val)
        if len(val['_CFG_SOFT_table_']) == 0:
            wrn_lmb(ev, s_lmb('You MUST choise ROW'))
        else:
            slct = _gl.cfg_soft[val['_CFG_SOFT_table_'][0]]
            #--- you can change ONLY parametrs from list 'slct_val'  ---------------
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
                            #---  update tale 'cfg_SOFT' -----------------------------
                            rq = _gl.db_TODAY.update_tbl('cfg_SOFT',
                                                    _gl.cfg_soft, val = ' VALUES(?,?)')
                            if rq[0] > 0:
                                err_lmb('event_menu_CFG_SOFT',
                                    s_lmb('Did not update cfg_SOFT!') + s_lmb(rep[1]))
                            else:
                                ok_lmb('event_menu_CFG_SOFT',
                                    s_lmb('Updated *cfg_SOFT* successfully !'))
            else:
                err_lmb(ev, s_lmb(slct[0]) + s_lmb('Sorry, can not change'))
    #-------------------------------------------------------------------
    if ev == '-SAVE_HIST_FILE-':
        print('-SAVE_HIST_FILE-')
        print(val)
        rep = _gl.db_TODAY.read_tbl('hist_FUT')
        if rep[0] > 0:
            err_lmb(ev, s_lmb('Could not read table *hist_FUT*!') + s_lmb(rep[1]))
        else:
            hst_fut_t = rep[1]
            path = _gl.cfg_soft[Class_CNST.path_file_TXT][1]
            txt = sg.PopupGetText( 'Save hist_FUT_today into file',
                        title=ev,  size=(55,1),  default_text = path)
            if (txt != None):
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
                    ok_lmb(ev, 'You have saved hist_FUT in file successfully !')
                else:
                    err_lmb(ev, s_lmb('Table *hist_FUT*!') + s_lmb('is EMPTY !!!'))
    #-------------------------------------------------------------------
    if _gl.trm.cnt_errors < 2:
        wndw.FindElement('_st_soft_').Update(_gl.stastus_bar, background_color = 'LightGreen')
    else:
        wndw.FindElement('_st_soft_').Update(_gl.stastus_bar, background_color = 'Pink')
#=======================================================================
def event_menu_DATA_ACNT(ev, val, wndw, _gl):
    rq = [0,ev]
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    mtrx = [['Date / Time  ',_gl.trm.account.dt,],
            ['BALANCE      ',str(_gl.trm.account.arr[Class_CNST.aBal]),],
            ['PROFIT / LOSS',str(_gl.trm.account.arr[Class_CNST.aPrf]),],
            ['GO           ',str(_gl.trm.account.arr[Class_CNST.aGo]),],
            ['DEPOSIT      ',str(_gl.trm.account.arr[Class_CNST.aDep]),]]
    wndw.FindElement('_DATA_ACNT_table_').Update(mtrx)
    if _gl.trm.cnt_errors < 2:
        wndw.FindElement('_st_acnt_').Update(_gl.stastus_bar, background_color = 'LightGreen')
    else:
        wndw.FindElement('_st_acnt_').Update(_gl.stastus_bar, background_color = 'Pink')
    prf = _gl.trm.account.arr[Class_CNST.aPrf]
    if prf > 0:
        wndw.FindElement('_txt_acnt_').Update(str(int(prf)), text_color = 'Green')
    else:
        wndw.FindElement('_txt_acnt_').Update(str(int(prf)), text_color = 'Red')

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
        #
        _gl.trm.rd_term_FUT()
        if _gl.trm.err_status > 0:
            err_lmb('main', s_lmb('Could not read term *data_file*!') + s_lmb(_gl.trm.err_status))
        else:
            #ok_lmb('main', s_lmb('Read term *data_file* successfully !'))
            os.system('cls')  # on windows
        #
        _gl.trm.rd_term_HST()
        if _gl.trm.err_status > 0:
            err_lmb('main', s_lmb('Could not read term *hist_file*!') + s_lmb(_gl.trm.err_status))
        else:
            #ok_lmb('main', s_lmb('Read term *hist_file* successfully !'))
            os.system('cls')  # on windows
        break
    #
    wndw = sg.Window('START').Layout([menu_def, [sg.Exit()]])
    wndw = wndw_menu_DATA_ACNT(wndw, _gl)
    #
    while True:     # MAIN cycle  --------------------------------------
        # for sg.Input must be => wndw.Read()  OR  timeout > 10000
        evn, val = wndw.Read(timeout = 3000)
        print('----------------------------------------------')
        print('evn = ', evn, '     val =', val)
        if evn in (None, 'Exit'): break
        #
        if evn == '__TIMEOUT__':
            try:
                #--- Read file DATA  ---------------------------------------
                _gl.trm.rd_term_FUT()
                _gl.stastus_bar = _gl.trm.account.dt + 3*' '
                if _gl.trm.err_status > 0:
                    _gl.stastus_bar += 'Error DATA - ' + str(_gl.trm.err_status)
                    _gl.trm.err_rd_term()
                else:
                    _gl.trm.cnt_errors = 0
                    _gl.stastus_bar += 'Got new DATA'
                #--- Read file HIST  ---------------------------------------
                dtt = datetime.strptime(_gl.trm.account.dt, "%d.%m.%Y %H:%M:%S")
                if dtt.minute == _gl.trm.time_1_min:
                    _gl.stastus_bar += '     Did not read HIST, it is not time'
                else:
                    _gl.trm.time_1_min = dtt.minute
                    _gl.trm.rd_term_HST()
                    if _gl.trm.err_status > 0:
                        _gl.stastus_bar += '     Error HIST - ' + str(_gl.trm.err_status)
                        _gl.trm.err_rd_term()
                    else:
                        _gl.stastus_bar += '     Got new HIST'
                #--- If is not errors READ files then:  --------------------
                #        update tables 'data_FUT' & 'hist_FUT'
                if _gl.trm.err_status == 0:
                    buf_arr_1, buf_arr_2 = [], []
                    frm = '%d.%m.%Y %H:%M:%S'
                    #
                    buf_arr_1 = ((j,) for j in _gl.trm.data_in_file)
                    if len(_gl.trm.hist_in_file) > 0:
                        for it in _gl.trm.hist_in_file:
                            dtt = datetime.strptime(it.split('|')[0], frm)
                            ind_sec  = int(dtt.replace(tzinfo=timezone.utc).timestamp())
                            buf_arr_2.append([ind_sec, it])
                    #
                    rep = _gl.db_TODAY.update_2_tbl('data_FUT', buf_arr_1, 'hist_FUT', buf_arr_2)
                    if rep[0] > 0:
                        _gl.trm.err_rd_term('main', rep[1], err_log = True)
                        #err_lmb('main', s_lmb('Could not update tables ') + s_lmb(rep[1]))
                    #
            except Exception as ex:
                _gl.trm.err_rd_term('main', str(ex), err_log = True)

            #print('_gl.wndw_menu = ', _gl.wndw_menu)
        if _gl.wndw_menu == 'CFG_SOFT':
            event_menu_CFG_SOFT(evn, val, wndw, _gl)
        elif _gl.wndw_menu == 'DATA_FUT_FILE':
            event_menu_DATA_FUT_FILE(evn, val, wndw, _gl)
        elif _gl.wndw_menu == 'DATA_HIST_FILE':
            event_menu_DATA_HIST_FILE(evn, val, wndw, _gl)
        elif _gl.wndw_menu == 'DATA_ACNT':
            event_menu_DATA_ACNT(evn, val, wndw, _gl)
        else:      pass
        #
        if evn == 'CFG_SOFT':
            wndw = wndw_menu_CFG_SOFT(wndw, _gl)
        elif evn == 'DATA_FUT_FILE':
            wndw = wndw_menu_DATA_FUT_FILE(wndw, _gl)
        elif evn == 'DATA_HIST_FILE':
            wndw = wndw_menu_DATA_HIST_FILE(wndw, _gl)
        elif evn == 'DATA_ACNT':
            wndw = wndw_menu_DATA_ACNT(wndw, _gl)

        else:      pass


    #ok_lmb('titul', 'message')
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
