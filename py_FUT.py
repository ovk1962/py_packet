#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_FUT.py
#
#  Copyright 2020 OVK <ovk.rus@gmail.com>
#
#=======================================================================
import os, sys, math, time, sqlite3, logging
from datetime import datetime, timezone
import math
from ipdb import set_trace as bp    # to set breakpoints just -> bp()
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
class Class_DB():
    def __init__(self, path_db):
        self.path_db = path_db
        self.table_db = []
        self.conn = ''
        self.cur  = ''
        # cfg_soft
        self.titul          = ''    # term ALFA
        self.path_file_DATA = ''    # c:\\str_log_ad_A7.txt
        self.path_file_HIST = ''    # c:\\hist_log_ad_A7.txt
        self.dt_start_sec   = 0     # 2017-01-01 00:00:00
        self.path_file_TXT  = ''    # c:\\hist_log_ALOR.txt
        #
        self.dt_file = 0        # curv stamptime data file path_file_DATA
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.ar_file = []       # list of strings from path_file_DATA
        self.hist_in_file = []  # list of strings from path_file_HIST
        #
        self.buf_file    = []               # data FUT from TXT file
        #self.dt_fut_file = []               # list of Class_FUT()
        #self.ac_fut_file = Class_ACCOUNT()  # obj Class_ACCOUNT()
        self.delay_tm = 8       # min period to get data for DB (10 sec)
        #
        self.dt_fut   = []               # list of Class_FUT()
        self.account  = Class_ACCOUNT()  # obj Class_ACCOUNT()
        #
        self.sec_10_00 = 36000      # seconds from 00:00 to 10:00
        self.sec_14_00 = 50410      # seconds from 00:00 to 14:00
        self.sec_14_05 = 50690      # seconds from 00:00 to 14:05
        #self.sec_18_45 = 67500      # seconds from 00:00 to 18:45
        self.sec_18_45 = 67500      # seconds from 00:00 to 18:45
        self.sec_19_05 = 68700      # seconds from 00:00 to 19:05
        self.sec_23_45 = 85500      # seconds from 00:00 to 23:45

    def prn_arr(self, name_arr, arr):
        print('len(' + name_arr + ')   => ' + str(len(arr)) + '\n' )
        if len(arr) > 4:
            for i in [0,1,2]: print(arr[i],'\n')
            print('+++++++++++++++++++++++++\n')
            for i in [-2,-1]: print(arr[i],'\n')
        else:
            for item in arr: print(item, '\n')

    def prn(self,
            p_cfg_SOFT  = False,
            p_ar_FILE   = False,
            p_hist_in_file = False,
            p_data_FUT  = False,
            ):
        s = ''
        try:
            if p_cfg_SOFT:
                frm = '{: <18}{: <55}'
                print(frm.format('titul',          self.titul))
                print(frm.format('dt_start',       self.dt_start))
                print(frm.format('dt_start_sec',   str(self.dt_start_sec)))
                print(frm.format('path_file_DATA', self.path_file_DATA))
                print(frm.format('path_file_HIST', self.path_file_HIST))
                print(frm.format('path_db_today',  self.path_db))

            if p_ar_FILE:
                for i in self.ar_file:   print(i)

            if p_data_FUT:
                print(self.account)
                for i in self.dt_fut:   print(i)

            if p_hist_in_file:
                self.prn_arr('hist_in_file', self.hist_in_file)

        except Exception as ex:
            r_prn = [1, 'op_archiv / ' + str(ex)]

        return [0, s]

    def op(self,
            rd_cfg_SOFT  = False,
            rd_term_FUT  = False,
            rd_term_HST  = False,
            ):
        r_op_today = []
        self.conn = sqlite3.connect(self.path_db)
        try:
            with self.conn:
                r_op_today = [0, 'ok']
                self.cur = self.conn.cursor()

                if rd_cfg_SOFT:
                    cfg = []
                    self.cur.execute('SELECT * from ' + 'cfg_SOFT')
                    cfg = self.cur.fetchall()    # read table name_tbl
                    #
                    for item in cfg:
                        if item[0] == 'titul'         : self.titul           = item[1]
                        if item[0] == 'path_file_DATA': self.path_file_DATA  = item[1]
                        if item[0] == 'path_file_HIST': self.path_file_HIST  = item[1]
                        if item[0] == 'dt_start'      : self.dt_start        = item[1]
                        if item[0] == 'path_file_TXT' : self.path_file_TXT   = item[1]

                    frm = '%Y-%m-%d %H:%M:%S'
                    self.dt_start_sec = \
                        int(datetime.strptime(self.dt_start, frm).replace(tzinfo=timezone.utc).timestamp())

                if rd_term_FUT:
                    #--- check file cntr.file_path_DATA ----------------------------
                    if not os.path.isfile(self.path_file_DATA):
                        err_msg = 'can not find file => ' + self.path_file_DATA
                        #cntr.log.wr_log_error(err_msg)
                        return [1, err_msg]
                    buf_stat = os.stat(self.path_file_DATA)
                    #
                    #--- check size of file ----------------------------------------
                    if buf_stat.st_size == 0:
                        err_msg = 'size DATA file is NULL'
                        #cntr.log.wr_log_error(err_msg)
                        return [2, err_msg]
                    #
                    #--- check time modificated of file ----------------------------
                    if int(buf_stat.st_mtime) == self.dt_file:
                        #str_dt_file = datetime.fromtimestamp(self.dt_file).strftime('%H:%M:%S')
                        return [3, 'FILE is not modificated ' + time.strftime("%M:%S", time.gmtime())]
                    else:
                        self.dt_file = int(buf_stat.st_mtime)
                    #--- read TERM file --------------------------------------------
                    buf_str = []
                    with open(self.path_file_DATA,"r") as fh:
                        buf_str = fh.read().splitlines()
                    #
                    #--- check size of list/file -----------------------------------
                    print('len(buf_str) = ', len(buf_str))
                    if len(buf_str) == 0:
                        err_msg = ' the size buf_str is NULL'
                        #cntr.log.wr_log_error(err_msg)
                        return [4, err_msg]
                    #
                    self.ar_file = []
                    self.ar_file = buf_str[:]
                    #
                    #--- update table 'data_FUT' -----------------------------------
                    self.cur.execute('DELETE FROM ' + 'data_FUT')
                    self.cur.executemany('INSERT INTO ' + 'data_FUT' + ' VALUES' + '(?)', ((j,) for j in buf_str))
                    self.conn.commit()
                    #
                    self.dt_fut = []
                    acc = self.account
                    for i, item in enumerate(buf_str):
                        lst = ''.join(item).replace(',','.').split('|')
                        del lst[-1]
                        #print('lst = > \n', lst)
                        if   i == 0:
                            acc.dt  = lst[0]
                        elif i == 1:
                            acc.arr = [float(j) for j in lst]
                        else:
                            b_fut = Class_FUT()
                            b_fut.sP_code = lst[0]
                            b_fut.arr     = [float(k) for k in lst[1:]]
                            self.dt_fut.append(b_fut)

                if rd_term_HST:
                    print('start rd_term_HST!  => ', str(len(self.hist_in_file)))
                    #--- check file cntr.file_path_DATA ----------------------------
                    if not os.path.isfile(self.path_file_HIST):
                        err_msg = 'can not find file => ' + self.path_file_HIST
                        #cntr.log.wr_log_error(err_msg)
                        return [1, err_msg]
                    buf_stat = os.stat(self.path_file_HIST)
                    #
                    #--- check size of file ----------------------------------------
                    if buf_stat.st_size == 0:
                        err_msg = 'size HIST file is NULL'
                        return [2, err_msg]
                    #
                    #--- read HIST file --------------------------------------------
                    buf_str = []
                    with open(self.path_file_HIST,"r") as fh:
                        buf_str = fh.read().splitlines()
                    #
                    #--- check size of list/file -----------------------------------
                    if len(buf_str) == 0:
                        err_msg = 'the size buf_str(HIST) is NULL '
                        return [3, err_msg]
                    #
                    #--- check MARKET time from 10:00 to 23:45 ---------------------
                    self.hist_in_file = []
                    for item in buf_str:
                        term_dt = item.split('|')[0]
                        dtt = datetime.strptime(str(term_dt), "%d.%m.%Y %H:%M:%S")
                        cur_time = dtt.second + 60 * dtt.minute + 60 * 60 * dtt.hour
                        if (
                            (cur_time > self.sec_10_00  and # from 10:00 to 14:00
                            cur_time < self.sec_14_00) or
                            (cur_time > self.sec_14_05  and # from 14:05 to 18:45
                            cur_time < self.sec_18_45) or
                            (cur_time > self.sec_19_05  and # from 19:05 to 23:45
                            cur_time < self.sec_23_45)):
                                self.hist_in_file.append(item)
                    print('finish rd_term_HST!  => ', str(len(self.hist_in_file)))


        except Exception as ex:
            r_op_today = [1, 'op_today / ' + str(ex)]

        return r_op_today
#=======================================================================
#=======================================================================
def second_window():

    layout = [[sg.Text('The second form is small \nHere to show that opening a window using a window works')],
              [sg.OK()]]

    window = sg.Window('Second Form', layout)
    event, values = window.read()
    window.close()


def test_menus():

    sg.theme('LightGreen')
    sg.set_options(element_padding=(0, 0))

    # ------ Menu Definition ------ #
    menu_def = [['&File', ['&Open     Ctrl-O', '&Save       Ctrl-S', '&Properties', 'E&xit']],
                ['&Edit', ['&Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['&Toolbar', ['---', 'Command &1', 'Command &2',
                              '---', 'Command &3', 'Command &4']],
                ['&Help', '&About...'], ]

    right_click_menu = ['Unused', ['Right', '!&Click', '&Menu', 'E&xit', 'Properties']]

    # ------ GUI Defintion ------ #
    layout = [
        [sg.Menu(menu_def, tearoff=False, pad=(200, 1))],
        [sg.Text('Right click me for a right click menu example')],
        [sg.Output(size=(60, 20))],
        [sg.ButtonMenu('ButtonMenu',  right_click_menu, key='-BMENU-'), sg.Button('Plain Button')],
    ]

    window = sg.Window("Windows-like program",
                       layout,
                       default_element_size=(12, 1),
                       default_button_element_size=(12, 1),
                       right_click_menu=right_click_menu)

    # ------ Loop & Process button menu choices ------ #
    while True:
        event, values = window.read()
        if event in (None, 'Exit'):
            break
        print(event, values)
        # ------ Process menu choices ------ #
        if event == 'About...':
            window.disappear()
            sg.popup('About this program', 'Version 1.0',
                     'PySimpleGUI Version', sg.version,  grab_anywhere=True)
            window.reappear()
        elif event == 'Open':
            filename = sg.popup_get_file('file to open', no_window=True)
            print(filename)
        elif event == 'Properties':
            second_window()

    window.close()


def main():
    while True:  # init db_TODAY ---------------------------------------
        sg.theme('LightGreen')
        sg.set_options(element_padding=(0, 0))
        c_dir    = os.path.abspath(os.curdir)
        db_TODAY = Class_DB(c_dir + '\\DB\\db_today.sqlite')
        #db_ARCHV = Class_term_TODAY(c_dir + '\\DB\\db_archv.sqlite')
        lg_FILE  = Class_LOGGER(    c_dir + '\\LOG\\fut_logger.log')
        lg_FILE.wr_log_info('START')
        rq = db_TODAY.op(
                        rd_cfg_SOFT  = True,
                        rd_term_FUT  = True,
                        rd_term_HST  = True,
                        )
        if rq[0] != 0 : #prn_rq('INIT rd_cfg_SOFT TODAY', rq)
            print('INIT = > ', rq[1])
        else:
            print('INIT cfg_term_data_hist TODAY = > ', rq)

        # rq = db_TODAY.prn(
                        # p_cfg_SOFT  = True,
                        # p_ar_FILE = True,
                        # p_data_FUT = True,
                        # p_hist_in_file = True,

                        # )
        # if rq[0] != 0 :
            # print('print INIT = > ', rq[1])

        break

    while True:  # init MENU -------------------------------------------
        def_txt, frm = [], '{: <10}  => {: ^15}\n'
        def_txt.append(frm.format('db_today' , '\\DB\\db_today.sqlite'))
        #=======================================================================
        menu_def = [
            ['Mode',
                ['auto','manual','auto_TEST','cnrt_TXT_HIST', ], ],
            ['READ  today',
                ['rd_term_FUT',  'rd_term_HST',   '---',
                'rd_cfg_PACK',   'rd_data_FUT',   '---',
                'rd_hst_FUT_t',  'rd_hst_PCK_t',  '---',
                'rd_hst_FUT',    'rd_hst_PCK'],],
            ['WRITE today',
                ['wr_cfg_PACK',  'wr_data_FUT',   '---', 'wr_hist_FUT_t', 'wr hist_FUT',  '---', 'wr_hst_PCK_t', 'wr_hst_PCK'],],
            ['CALC',
                ['ASK_BID', 'EMA_f', '---', 'ASK_BID_t', 'EMA_f_t', '---', 'cnt', '---', 'update_arr_PK', 'update_arr_PK_t'] ,],
            ['PRINT today',
                ['prn_cfg_SOFT', 'prn_cfg_PACK', 'prn_cfg_ALARM',   '---',
                'prn_ar_FILE',   'prn_hist_in_FILE', '---',
                'prn_data_FUT',  '---',
                'prn_hst_FUT_t', 'prn_arr_FUT_t', 'prn_arr_PK_t',   '---',
                'prn_arr_FUT',   'prn_arr_PK'],],
            ['Plot', 'win2_active'],
            ['Exit', 'Exit']
        ]
        #=======================================================================
        # Display data
        layout = [
                    [sg.Menu(menu_def, tearoff=False, key='menu_def')],
                    [sg.Multiline( default_text=''.join(def_txt),
                        size=(50, 5), key='txt_data', autoscroll=False, focus=False),],
                    [sg.T('',size=(60,2), font='Helvetica 8', key='txt_status'), sg.Quit(auto_size_button=True)],
                 ]
        sg.SetOptions(element_padding=(0,0))
        window = sg.Window('Test db_today', grab_anywhere=True).Layout(layout).Finalize()
        window.FindElement('txt_data').Update(''.join(def_txt))
        break

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
