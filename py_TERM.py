#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_TERM.py
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
class Class_str_FUT():
    fAsk, fBid = range(2)
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
class Class_TERM():
    def __init__(self):
        c_dir    = os.path.abspath(os.curdir)
        self.lg_FILE    = Class_LOGGER(c_dir + '\\LOG\\pack_logger.log')
        self.db_FUT_arc = Class_DB_SQLite(c_dir + '\\DB\\db_fut_a.sqlite')
        self.db_FUT_tod = Class_DB_SQLite(c_dir + '\\DB\\db_fut_t.sqlite')
        # cfg_soft
        self.titul          = ''    # term ALFA
        self.path_file_DATA = ''    # c:\\str_log_ad_A7.txt
        self.path_file_HIST = ''    # c:\\hist_log_ad_A7.txt
        self.dt_start_sec   = 0     # 2017-01-01 00:00:00
        self.path_file_TXT  = ''    # c:\\hist_log_ALOR.txt
        #
        self.dt_file = 0        # curv stamptime data file path_file_DATA
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.data_in_file = []  # ar_file   list of strings from path_file_DATA
        self.hist_in_file = []  # list of strings from path_file_HIST
        #
        self.dt_fut  = []               # list of Class_FUT()
        self.account = Class_ACCOUNT()  # obj Class_ACCOUNT()
        #
        self.hst_fut_t = []
        #self.arr_fut_t = []
        self.hst_fut_a = []
        #self.arr_fut_a = []

    def prn_arr(self, name_arr, arr):
        print('len(' + name_arr + ')   => ' + str(len(arr)) + '\n' )
        if len(arr) > 4:
            for i in [0,1]: print(arr[i],'\n')
            print('+++++++++++++++++++++++++\n')
            for i in [-2,-1]: print(arr[i],'\n')
        else:
            for item in arr: print(item, '\n')

    def check_MARKET_time(self,term_dt):
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

    def prn_cfg(self):
        frm = '{: <18}{: <55}'
        print(frm.format('titul',          self.titul))
        print(frm.format('dt_start',       self.dt_start))
        print(frm.format('dt_start_sec',   str(self.dt_start_sec)))
        print(frm.format('path_file_DATA', self.path_file_DATA))
        print(frm.format('path_file_HIST', self.path_file_HIST))
        print(frm.format('path_file_TXT',  self.path_file_TXT))

    def unpack_cfg(self):
        print('=> _TERM unpack_cfg')
        try:
            cfg = self.db_FUT_tod.read_tbl('cfg_SOFT')
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
            rep = self.db_FUT_tod.update_tbl('data_FUT', buf_arr, val = ' VALUES(?)')
            if rep[0] > 0: return rep
            #
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
        # update table 'data_FUT' into DB 'db_FUT_tod'------------------
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
            #--- update table 'hist_FUT_today' -------------------------
            buf_list =[]
            pAsk, pBid = range(2)
            if len(self.hist_in_file) > 0:
                frm = '%d.%m.%Y %H:%M:%S'
                for it in self.hist_in_file:
                    dtt = datetime.strptime(it.split('|')[0], frm)
                    ind_sec  = int(dtt.replace(tzinfo=timezone.utc).timestamp())
                    buf_list.append([ind_sec, it])
            rep = self.db_FUT_tod.update_tbl('hist_FUT_today', buf_list, val = ' VALUES(?,?)')
            if rep[0] > 0: return rep

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
#=======================================================================
def event_menu(event, _gl):
    rq = [0,event]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if event == 'rd_term_FUT'  :
        print('rd_term_FUT ...')
        term_data = _gl.rd_term_FUT()
        if term_data[0] > 0:
            print(term_data[1])
        else:
            for i in _gl.data_in_file:   print(i)
    #-------------------------------------------------------------------
    if event == 'rd_term_HST'  :
        print('rd_term_HST ...')
        term_hist = _gl.rd_term_HST()
        if term_hist[0] > 0:
            print(term_hist[1])
        else:
            rq = _gl.prn_arr('hist_in_file', _gl.hist_in_file)
    #-------------------------------------------------------------------
    if event == 'prn_cfg_SOFT'  :
        print('prn_cfg_SOFT ...')
        rq = _gl.prn_cfg()
    #-------------------------------------------------------------------
    if event == 'prn_data_in_FILE'  :
        print('prn_data_in_FILE ...')
        for i in _gl.data_in_file:   print(i)
    #-------------------------------------------------------------------
    if event == 'prn_hist_in_FILE'  :
        print('prn_hist_in_FILE ...')
        rq = _gl.prn_arr('hist_in_file', _gl.hist_in_file)
    #-------------------------------------------------------------------
    if event == 'prn_data_FUT'  :
        print('prn_data_FUT ...')
        print(_gl.account)
        for i in _gl.dt_fut:   print(i)
    #-------------------------------------------------------------------

    print('rq = ', rq)
#=======================================================================
def main():
    menu_def = [
        ['Mode',
            ['auto','manual', ],],
        ['READ',
            ['rd_term_FUT',  'rd_term_HST',   '---', ],],
        ['PRINT',
            ['prn_cfg_SOFT',   '---',
             'prn_data_in_FILE',   'prn_hist_in_FILE', '---',
             'prn_data_FUT',  '---',
             'prn_hst_FUT_t', 'prn_arr_FUT_t', ],],
        ['Exit', 'Exit']
    ]
    while True:  # init db_TODAY ---------------------------------------
        #sg.theme('LightGreen')
        #sg.set_options(element_padding=(0, 0))

        _gl = Class_TERM()      # init db_TODAY ------------------------
        #
        stroki = []
        #
        cfg = _gl.unpack_cfg()
        if cfg[0] > 0:
            stroki.append(cfg[1])
        #
        term_data = _gl.rd_term_FUT()
        if term_data[0] > 0:
            stroki.append(term_data[1])
        #
        term_hist = _gl.rd_term_HST()
        if term_hist[0] > 0:
            stroki.append(term_hist[1])
        #
        fut_data = _gl.unpack_data_in_file()
        if fut_data[0] > 0:
            stroki.append(fut_data[1])

        break

    while True:  # init MENU -------------------------------------------
        def_txt, frm = [], '{: <10}  => {: ^15}\n'
        def_txt.append(frm.format('db_today' , '\\DB\\db_today.sqlite'))
        def_txt.append(frm.format('db_archv' , '\\DB\\db_archv.sqlite'))
        #===============================================================
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
        window = sg.Window(_gl.titul, grab_anywhere=True).Layout(layout).Finalize()
        window.FindElement('txt_data').Update(''.join(def_txt))
        break

    tm_out, mode, frm = 360000, 'manual', '%d.%m.%Y %H:%M:%S'
    stts  = time.strftime(frm, time.localtime()) + '\n' + 'event = manual'
    window.FindElement('txt_status').Update(stts)

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
            term_data = _gl.rd_term_FUT()
            if term_data[0] > 0:
                stroki.append(term_data[1])
            else:
                fut_data = _gl.unpack_data_in_file()
                if fut_data[0] > 0:
                    stroki.append(fut_data[1])
                else:
                    term_hist = _gl.rd_term_HST()
                    if term_hist[0] > 0:
                        stroki.append(term_hist[1])
                    else:
                        #stroki.append('OK')
                        stroki.append('date FUT  => ' + _gl.account.dt)
                        stroki.append('last HIST => ' + _gl.hist_in_file[-1].split('|')[0])
                        stroki.append('len  HIST => ' + str(len(_gl.hist_in_file)))
                        stroki.append('PROFIT  => ' + str(_gl.account.arr[Class_ACCOUNT.prf]))
        #---------------------------------------------------------------
        window.FindElement('txt_data').Update('\n'.join(stroki))
        stts  = time.strftime(frm, time.localtime()) + '\n'
        stts += 'event = ' + event
        window.FindElement('txt_status').Update(stts)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
