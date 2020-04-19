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
class Class_str_PCK():
    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
    def __init__(self):
        self.ind_s, self.dt, self.arr  = 0, '', []
    def __retr__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
    def __str__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
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
        self.dt_start_sec   = 0     # 2017-01-01 00:00:00
        self.path_file_TXT  = ''    # c:\\hist_log_ALOR.txt

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
#=======================================================================
def main():
    _gl = Class_GL()
    _gl.unpack_cfg()

    menu_def = [['MODE',
                    ['AUTO', 'Manual', '---',
                     'Exit',],],
                ['DIAG',
                    ['rd_term_FUT',  'rd_term_HST',   '---',],],
                ]

    layout1 = [[sg.Menu(menu_def)                                   ],
              [sg.Input(do_not_clear=True, key='-INPUT_1-')         ],
              [sg.Text(text=' ', size=(15,1), key='-in_tab-')       ],
              [sg.Button('Launch 2'),
               sg.Button('Launch 3'),
               sg.Button('Exit')                                   ]]

    #sg.theme('DarkTeal12')   # Add a touch of color
    win1 = sg.Window(_gl.titul, grab_anywhere=True).Layout(layout1).Finalize()
    win2_active = False
    win3_active = False

    while True:
        #--- read 'Window 1' -------------------------------------------
        ev1, vals1 = win1.Read(timeout=100)
        #print('ev1 = ', ev1, '    vals1 = ', vals1)
        if ev1 is None or ev1 == 'Exit':
            break
        if ev1 == '__TIMEOUT__':
            win1.FindElement('-in_tab-').Update(vals1['-INPUT_1-'])

        #--- open 'Window 2' -------------------------------------------
        if not win2_active and ev1 == 'Launch 2':
            win2_active = True
            layout2 = [ [sg.Text('Window 2')],
                        [sg.Input(do_not_clear=True, key='-in_layout_2-')],
                        [sg.Button('Close')]]
            #win2 = sg.Window('Window 2', layout2)
            win2 = sg.Window('Window 2', grab_anywhere=True).Layout(layout2).Finalize()
        if win2_active:
            ev2, vals2 = win2.Read(timeout=100)
            #print('ev2 = ', ev2, '    vals2 = ', vals2)
            if ev2 is None or ev2 == 'Close' or ev2 == 'Exit':
                win2_active  = False
                win2.Close()
            if ev2 == '__TIMEOUT__':
                pass

        #--- open 'Window 3' -------------------------------------------
        if not win3_active and ev1 == 'Launch 3':
            win3_active = True
            layout3 = [ [sg.Text('Window 3')],
                        [sg.Input(do_not_clear=True, key='-in_layout_3-')],
                        [sg.Text(text=' ', size=(15,1))],
                        [sg.Button('Close')]]
            #win3 = sg.Window('Window 3', layout3)
            win3 = sg.Window('Window 3', grab_anywhere=True).Layout(layout3).Finalize()
        if win3_active:
            ev3, vals3 = win3.Read(timeout=100)
            #print('ev3 = ', ev3, '    vals3 = ', vals3)
            if ev3 is None or ev3 == 'Close' or ev3 == 'Exit':
                win3_active  = False
                win3.Close()
            if ev3 == '__TIMEOUT__':
                win3.FindElement('-in_layout_3-').Update(vals1['-INPUT_1-'])

    return 0

if __name__ == '__main__':
    main()
