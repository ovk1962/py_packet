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
            p_hst_FUT_t = False,
            p_arr_FUT_t = False,
            p_arr_fut   = False,
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

            if p_hst_FUT_t:
                self.prn_arr('hst_fut_t', self.hst_fut_t)

            if p_arr_FUT_t:
                self.prn_arr('arr_fut_t', self.arr_fut_t)

            if p_arr_fut:
                self.prn_arr('arr_fut', self.arr_fut)

        except Exception as ex:
            r_prn = [1, 'op_archiv / ' + str(ex)]

        return [0, s]

    def op(self,
            rd_cfg_SOFT  = False,
            wr_cfg_SOFT  = False,

            update_data_FUT = False,
            update_data_HST = False,

            rd_term_FUT  = False,
            rd_term_HST  = False,

            wr_data_FUT  = False,
            rd_data_FUT  = False,

            rd_hst_FUT   = False,

            wr_hist_FUT_t = False,
            rd_hst_FUT_t  = False,

            upload_HST  = False,

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

                if wr_cfg_SOFT:
                    cfg = []
                    cfg.append(['titul',          self.titul])
                    cfg.append(['path_file_DATA', self.path_file_DATA])
                    cfg.append(['path_file_HIST', self.path_file_HIST])
                    cfg.append(['dt_start',       self.dt_start])
                    cfg.append(['path_file_TXT',  self.path_file_TXT])
                    self.cur.execute('DELETE FROM ' + 'cfg_SOFT')
                    self.cur.executemany('INSERT INTO ' + 'cfg_SOFT' + ' VALUES' + '(?,?)', cfg)
                    self.conn.commit()

                if update_data_FUT:
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

                if update_data_HST:
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
                    #--- update table 'hist_FUT_today' ------------------------------
                    buf_list =[]
                    pAsk, pBid = range(2)
                    if len(self.hist_in_file) > 0:
                        for it in self.hist_in_file:
                            dtt = datetime.strptime(it.split('|')[0], '%d.%m.%Y %H:%M:%S')
                            ind_sec  = int(dtt.replace(tzinfo=timezone.utc).timestamp())
                            buf_list.append([ind_sec, it])

                    ''' rewrite data from table hist_FUT_today ------'''
                    self.cur.execute('DELETE FROM ' + 'hist_FUT_today')
                    self.cur.executemany('INSERT INTO ' + 'hist_FUT_today' + ' VALUES' + '(?,?)', buf_list)
                    self.conn.commit()

                if rd_term_FUT:
                    print('start rd_term_FUT!  => ', str(len(self.ar_file)))
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
                    print('finish rd_term_FUT!  => ', str(len(self.ar_file)))

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

                if wr_data_FUT:
                    print('start wr_data_FUT! ')
                    self.dt_fut = []
                    acc = self.account
                    for i, item in enumerate(list(self.ar_file)):
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
                    self.cur.execute('DELETE FROM ' + 'data_FUT')
                    self.cur.executemany('INSERT INTO ' + 'data_FUT' + ' VALUES' + '(?)', ((jtem,) for jtem in self.ar_file))
                    self.conn.commit()
                    print('finish wr_data_FUT!  => ', str(len(self.ar_file)))

                if rd_data_FUT:
                    print('start rd_data_FUT! ')
                    data = []
                    self.cur.execute('SELECT * from ' + 'data_FUT')
                    data = self.cur.fetchall()    # read table name_tbl
                    #
                    self.dt_fut = []
                    acc = self.account
                    for i, item in enumerate(list(data)):
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
                    print('finish rd_data_FUT! => ', str(len(self.dt_fut)))

                if rd_hst_FUT_t:
                    print('start rd_hst_FUT_t! ')
                    self.cur.execute('SELECT * from ' + 'hist_FUT_today')
                    self.hst_fut_t = []
                    self.hst_fut_t = self.cur.fetchall()    # read table name_tbl
                    print('len(hist_FUT_today) = ', len(self.hst_fut_t))
                    self.arr_fut_t  = []
                    for cnt, i_str in enumerate(self.hst_fut_t):
                        mn_pr, mn_cr = '', ''
                        if cnt == 0 :
                            mn_pr, mn_cr = '', '00'
                        else:
                            mn_pr = self.hst_fut_t[cnt-1][1][14:16]
                            mn_cr = self.hst_fut_t[cnt-0][1][14:16]
                        if mn_pr != mn_cr:
                            s = Class_str_FUT()
                            s.ind_s = i_str[0]
                            s.dt    = i_str[1].split('|')[0].split(' ')
                            arr_buf = i_str[1].replace(',', '.').split('|')[1:-1]
                            fAsk, fBid = range(2)
                            for item in (zip(arr_buf[::2], arr_buf[1::2])):
                                s.arr.append([float(item[fAsk]), float(item[fBid])])
                            self.arr_fut_t.append(s)
                        if len(self.arr_fut_t) % 100 == 0:  print(len(self.arr_fut_t), end='\r')
                    print('finish rd_hst_FUT_t => !', str(len(self.arr_fut_t)))

                if upload_HST:
                    print('len(self.hst_fut_t) = ', len(self.hst_fut_t))
                    if len(self.hst_fut_t) > 0:
                        # change 2020-00-00 to  for name FILE
                        print(self.path_file_HIST)
                        buf_name = self.hst_fut_t[-1][1][6:10] + '-'
                        buf_name += self.hst_fut_t[-1][1][3:5] + '-'
                        buf_name += self.hst_fut_t[-1][1][0:2]
                        #buf_name = 'c:\\' + buf_name + '_hist_log_ALFA.txt'
                        buf_name = self.path_file_TXT.split('*')[0] + buf_name + self.path_file_TXT.split('*')[1]
                        print(buf_name)
                        with open(buf_name, 'w') as file_HIST:
                            for item in self.hst_fut_t:
                                file_HIST.write(item[1]+'\n')
                    else:
                        print('self.hst_fut_t IS empty')

        except Exception as ex:
            r_op_today = [1, 'op_today / ' + str(ex)]

        return r_op_today
#=======================================================================


#=======================================================================
def event_menu(event, db_TODAY):
    rq = [0,event]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if event == 'rd_term_FUT'  :
        print('rd_term_FUT ...')
        rq = db_TODAY.op(rd_term_FUT = True)
    #-------------------------------------------------------------------
    if event == 'rd_term_HST'  :
        print('rd_term_HST ...')
        rq = db_TODAY.op(rd_term_HST = True)
    #-------------------------------------------------------------------
    if event == 'rd_data_FUT'  :
        print('rd_data_FUT ...')
        rq = db_TODAY.op(rd_data_FUT = True)
    #-------------------------------------------------------------------
    if event == 'rd_hst_FUT_t'  :
        print('rd_hst_FUT_t ...')
        rq = db_TODAY.op(rd_hst_FUT_t = True)
    #-------------------------------------------------------------------
    if event == 'update_data_FUT'  :
        print('update_data_FUT ...')
        db_TODAY.dt_file = 0
        rq = db_TODAY.op(update_data_FUT = True)
    #-------------------------------------------------------------------
    if event == 'update_data_HST'  :
        print('update_data_HST ...')
        db_TODAY.dt_file = 0
        rq = db_TODAY.op(update_data_HST = True,  rd_hst_FUT_t = True)
    #-------------------------------------------------------------------
    if event == 'prn_cfg_SOFT'  :
        print('prn_cfg_SOFT ...')
        rq = db_TODAY.prn(p_cfg_SOFT = True)
    #-------------------------------------------------------------------
    if event == 'prn_ar_FILE'  :
        print('prn_ar_FILE ...')
        rq = db_TODAY.prn(p_ar_FILE = True)
    #-------------------------------------------------------------------
    if event == 'prn_hist_in_FILE'  :
        print('prn_hist_in_FILE ...')
        rq = db_TODAY.prn(p_hist_in_file = True)
    #-------------------------------------------------------------------
    if event == 'prn_data_FUT'  :
        print('prn_data_FUT ...')
        rq = db_TODAY.prn(p_data_FUT = True)
    #-------------------------------------------------------------------
    if event == 'prn_hst_FUT_t'  :
        print('prn_hst_FUT_t ...')
        rq = db_TODAY.prn(p_hst_FUT_t = True)
    #-------------------------------------------------------------------
    if event == 'prn_arr_FUT_t'  :
        print('prn_arr_FUT_t ...')
        rq = db_TODAY.prn(p_arr_FUT_t = True)
    #-------------------------------------------------------------------
    if event == 'upload_HST'  :
        print('upload_HST ...')
        rq = db_TODAY.op(upload_HST = True)
    #-------------------------------------------------------------------
    if event == 'update_cfg_SOFT'  :
        print('update_cfg_SOFT ...')
        rq = db_TODAY.op(rd_cfg_SOFT = True)


    print('rq = ', rq)
#=======================================================================
def main():
    while True:  # init db_TODAY ---------------------------------------
        #sg.theme('LightGreen')
        #sg.set_options(element_padding=(0, 0))
        c_dir    = os.path.abspath(os.curdir)
        db_TODAY = Class_DB(c_dir + '\\DB\\db_today.sqlite')
        #db_ARCHV = Class_term_TODAY(c_dir + '\\DB\\db_archv.sqlite')
        lg_FILE  = Class_LOGGER(    c_dir + '\\LOG\\fut_logger.log')
        lg_FILE.wr_log_info('START')
        rq = db_TODAY.op(
                        rd_cfg_SOFT     = True,
                        update_data_FUT = True,
                        update_data_HST = True,
                        rd_hst_FUT_t    = True,
                        )
        if rq[0] != 0 : #prn_rq('INIT rd_cfg_SOFT TODAY', rq)
            print('INIT = > ', rq[1])
        else:
            print('INIT cfg_term_data_hist TODAY = > ', rq)

        break

    while True:  # init MENU -------------------------------------------
        def_txt, frm = [], '{: <10}  => {: ^15}\n'
        def_txt.append(frm.format('db_today' , '\\DB\\db_today.sqlite'))
        #=======================================================================
        menu_def = [
            ['Mode',
                ['auto','manual','upload_HST',], ],
            ['READ',
                ['rd_term_FUT',  'rd_term_HST',   '---',
                 'rd_data_FUT',  'rd_hst_FUT_t',  ],],
            ['UPDATE',
                ['update_cfg_SOFT',  'update_data_FUT', 'update_data_HST',],],
            ['PRINT',
                ['prn_cfg_SOFT',   '---',
                 'prn_ar_FILE',   'prn_hist_in_FILE', '---',
                 'prn_data_FUT',  '---',
                 'prn_hst_FUT_t', 'prn_arr_FUT_t', ],],
            ['Exit', 'Exit']
        ]
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
        window = sg.Window(db_TODAY.titul, grab_anywhere=True).Layout(layout).Finalize()
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
        event_menu(event, db_TODAY)
        #---------------------------------------------------------------
        if event is None or event == 'Quit' or event == 'Exit': break
        #---------------------------------------------------------------
        if event == 'auto'   :    tm_out, mode =  2500,   'auto'
        #---------------------------------------------------------------
        if event == 'manual' :    tm_out, mode = 360000, 'manual'
        #---------------------------------------------------------------
        if event == '__TIMEOUT__':
            rq = db_TODAY.op(
                        update_data_FUT  = True,
                        update_data_HST  = True,
                        )
            if rq[0] == 0:
                #stroki.append('OK')
                stroki.append('date FUT  => ' + db_TODAY.account.dt)
                stroki.append('last HIST => ' + db_TODAY.hist_in_file[-1].split('|')[0])
                stroki.append('len  HIST => ' + str(len(db_TODAY.hist_in_file)))
            else:
                stroki.append(rq[1])
            stroki.append('PROFIT  => ' + str(db_TODAY.account.arr[Class_ACCOUNT.prf]))
        #---------------------------------------------------------------
        if event == 'update_cfg_SOFT' and not win_CFG_active:
            win_CFG_active = True
            window.Hide()

            d = db_TODAY
            layout2 = [
                        [sg.Text('titul',          size=(15, 1)), sg.Input(d.titul, key='-titul-') ],
                        [sg.Text('path_file_DATA', size=(15, 1)), sg.Input(d.path_file_DATA, key='-path_DATA-'), sg.FileBrowse()],
                        [sg.Text('path_file_HIST', size=(15, 1)), sg.Input(d.path_file_HIST, key='-path_HIST-'), sg.FileBrowse()],
                        [sg.Text('dt_start',       size=(15, 1)), sg.Input(d.dt_start, key='-dt_start-')],
                        [sg.Text('path_file_TXT',  size=(15, 1)), sg.Input(d.path_file_TXT, key='-path_TXT-'),   sg.FileBrowse()],
                        [sg.OK(),  sg.T(' '), sg.Cancel()]
                       ]
            win_CFG = sg.Window('Update TABLE cfg_SOFT').Layout(layout2)
            win_CFG.Finalize()
            while True:
                ev_win_CFG, vals_win_CFG = win_CFG.Read()
                print(ev_win_CFG, vals_win_CFG)
                #-------------------------------------------------------
                if ev_win_CFG is None or ev_win_CFG == 'Cancel':
                    win_CFG.Close()
                    win_CFG_active = False
                    window.UnHide()
                    break
                #-------------------------------------------------------
                if ev_win_CFG == 'OK':
                    db_TODAY.titul          = vals_win_CFG['-titul-']
                    db_TODAY.path_file_DATA = vals_win_CFG['-path_DATA-']
                    db_TODAY.path_file_HIST = vals_win_CFG['-path_HIST-']
                    db_TODAY.dt_start       = vals_win_CFG['-dt_start-']
                    db_TODAY.path_file_TXT  = vals_win_CFG['-path_TXT-']

                    print(db_TODAY.titul)
                    print(db_TODAY.path_file_DATA)
                    print(db_TODAY.path_file_HIST)
                    print(db_TODAY.dt_start)
                    print(db_TODAY.path_file_TXT)

                    rq = db_TODAY.op(wr_cfg_SOFT = True)
                    print('rq = ', rq)
        #---------------------------------------------------------------
        window.FindElement('txt_data').Update('\n'.join(stroki))
        stts  = time.strftime(frm, time.localtime()) + '\n'
        stts += 'event = ' + event
        window.FindElement('txt_status').Update(stts)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
