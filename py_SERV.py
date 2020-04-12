#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_SERV.py
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
class Class_SERV():
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
        self.hst_fut_t = []
        self.arr_fut_t = []
        self.hst_fut_a = []
        self.arr_fut_a = []
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
#=======================================================================
def event_menu(event, values, _gl):
    rq = [0,event]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if event == 'rd_cfg_SOFT'  :
        print('rd_cfg_SOFT ...')
        rq = _gl.unpack_cfg()
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
    if event == 'wr_HIST_file'  :
        print('wr_HIST_file ... save hist_FUT_today into file')
        if 'OK' == sg.popup_ok_cancel('\n   Save data from table *hist_FUT_today*   ' +
                                      '\n      into file *path_file_TXT*   \n'):
            hst = _gl.db_FUT_tod.read_tbl('hist_FUT_today')
            if hst[0] > 0:
                print('problem ...', hst[1])
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
                    sg.popup_error('\n    Warning! \nTable *hist_FUT_today* IS empty!\n',
                                    background_color = 'grey',
                                    no_titlebar = True)
    #-------------------------------------------------------------------
    if event == '-update_cfg_SOFT-':
        if 'OK' == sg.popup_ok_cancel('\n' + 'Update table *cfg_SOFT*' + '\n'):
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

            rq = _gl.db_FUT_tod.update_tbl('cfg_SOFT', cfg, val = ' VALUES(?,?)')
            if rq[0] > 0:
                sg.popup_error('\n' + 'Did not update cfg_SOFT!' + '\n'
                                + rep[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)
            else:
                sg.popup_ok('\nUpdated *cfg_SOFT* successfully !\n')
    #-------------------------------------------------------------------
    if event == 'del_HIST_tod':
        if 'OK' == sg.popup_ok_cancel('\nAre you sure to delete data in table *hist_FUT_today* ?\n'):
            try:
                conn = sqlite3.connect(os.path.abspath(os.curdir) + '\\DB\\db_fut_t.sqlite')
                with conn:
                    cur = conn.cursor()
                    #--- update table nm_tbl ---------------------------
                    cur.execute('DELETE FROM ' + 'hist_FUT_today')
                    conn.commit()
                    sg.popup_ok('\nOK, it was delete data in table *hist_FUT_today* successfully !\n')
            except Exception as ex:
                sg.popup_error('\n' + str(ex) + '\n', background_color = 'brown', no_titlebar = True)
        if 'OK' == sg.popup_ok_cancel('\nAre you sure to delete data in table *hist_PACK_today* ?\n'):
            try:
                conn = sqlite3.connect(os.path.abspath(os.curdir) + '\\DB\\db_pack_t.sqlite')
                with conn:
                    cur = conn.cursor()
                    #--- update table nm_tbl ---------------------------
                    cur.execute('DELETE FROM ' + 'hist_PACK_today')
                    conn.commit()
                    sg.popup_ok('\nOK, it was delete data in table *hist_PACK_today* successfully !\n')
            except Exception as ex:
                sg.popup_error('\n' + str(ex) + '\n', background_color = 'brown', no_titlebar = True)
    #---------------------------------------------------------------
    if event == '-check_HIST_file-':
        if 'OK' == sg.popup_ok_cancel('\n' +
            'check 1 minute interval in -path_check_HIST- ' +
            '\n' +
            '         please check PATH !'+
            '\n'):
            #--- read HIST file ---
            buf_str = []
            frm = '%d.%m.%Y %H:%M:%S'
            try:
                with open(values['-path_check_HIST-'],"r") as fh:
                    buf_str = fh.read().splitlines()
                    cr, pr, dtt_cr, dtt_pr = 0, 0, '', ''
                    for i, item in enumerate(buf_str):
                        dtt_pr = dtt_cr
                        dtt_cr = datetime.strptime(item.split('|')[0], frm)
                        ind_sec = int(dtt_cr.replace(tzinfo=timezone.utc).timestamp())
                        if i == 0:
                            cr, pr = ind_sec, 0
                        else:
                            pr = cr
                            cr = ind_sec
                        if cr - pr > 60:
                            print(dtt_pr, ' ... ', dtt_cr)
            except Exception as ex:
                sg.popup_error('\n' + str(ex) + '\n', background_color = 'brown', no_titlebar = True)
    #-------------------------------------------------------------------
    if event == 'load_HIST_arc':
        #--- read HIST file ---
        buf_str = []
        frm = '%d.%m.%Y %H:%M:%S'
        try:
            with open(values['-path_check_HIST-'],"r") as fh:
                buf_str = fh.read().splitlines()
            #--- create list 'buf_hist' HIST 1 minute 10.00 ... 18.45
            mn_pr, mn_cr, buf_hist = '', '00', []
            for cnt, item in enumerate(buf_str):
                mn_cr = item[14:16]
                #hr_cr = int(item[11:13])
                if int(item[11:13]) == 19: break
                if mn_pr != mn_cr:
                    buf_hist.append(item)
                mn_pr = mn_cr
        except Exception as ex:
            sg.popup_error('\n' + str(ex) + '\n', background_color = 'brown', no_titlebar = True)
            return
        #--- prepaire 'buf_hist' for update table 'hist_fut'
        buf_hist_arch, frm = [], '%d.%m.%Y %H:%M:%S'
        for item in buf_hist:
            dtt_cr = datetime.strptime(item.split('|')[0], frm)
            ind_sec = int(dtt_cr.replace(tzinfo=timezone.utc).timestamp())
            buf_hist_arch.append([ind_sec, item])
        for i in [0,1]: print(buf_hist_arch[i],'\n')
        print('+++++++++++++++++++++++++\n')
        for i in [-2,-1]: print(buf_hist_arch[i],'\n')
        print('len(buf_hist_arch) = ', len(buf_hist_arch))
        ''' append buf_hist_arch into table hist_FUT  ------'''
        path_db_FUT_arc = os.path.abspath(os.curdir) + '\\DB\\db_fut_a.sqlite'
        conn = sqlite3.connect(path_db_FUT_arc)
        try:
            with conn:
                cur = conn.cursor()
                #self.cur.execute('DELETE FROM ' + 'hist_FUT_today')
                cur.executemany('INSERT INTO ' + 'hist_FUT' + ' VALUES' + '(?,?)', buf_hist_arch)
                conn.commit()
                sg.popup_ok('\nOK, it was append data in table *hist_FUT* successfully !\n')
        except Exception as ex:
            sg.popup_error('\n' + str(ex) + '\n', background_color = 'brown', no_titlebar = True)
    #-------------------------------------------------------------------

    print('rq = ', rq)

#=======================================================================
def main():
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # wr_HIST_file    - write hist from table 'hist_FUT_today' in FILE
    # check_HIST_tod  - check 1 minute interval in hist_FUT_today
    # load_HIST_arc   - load 'hist_today' from FILE in table 'hist_FUT'
    # chn_CFG_tbl     - update info in table 'cfg_SOFT'
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    menu_def = [
        ['Mode',
            ['wr_HIST_file', 'load_HIST_arc', 'del_HIST_tod'],],
        ['READ',
            ['rd_cfg_SOFT',    '---', 'rd_HST_today',  'rd_HST_archiv', ],],
        ['PRINT',
            ['prn_cfg_SOFT',   '---', 'prn_hst_FUT_t', 'prn_arr_FUT_t', ],],
        ['Exit', 'Exit']
    ]
    while True:  # init db_TODAY ---------------------------------------
        #sg.theme('LightGreen')
        #sg.set_options(element_padding=(0, 0))

        _gl = Class_SERV()      # init db_TODAY ------------------------
        print('--- read table cfg_SOFT  --------------------------------')
        rq  = _gl.unpack_cfg()
        print('--- read table hist_FUT_today ---------------------------')
        hst = _gl.db_FUT_tod.read_tbl('hist_FUT_today')
        #
        stroki = []
        #

        break

    while True:  # init MENU -------------------------------------------
        def_txt, frm = [], '{: <10}  => {: ^15}\n'
        def_txt.append(frm.format('db_today' , '\\DB\\db_today.sqlite'))
        def_txt.append(frm.format('db_archv' , '\\DB\\db_archv.sqlite'))
        #===============================================================
        # Display data
        layout = [
                    [sg.Menu(menu_def, tearoff=False, key='menu_def')],
                    [sg.Text('path_check_HIST_file', size=(15, 1)), sg.Input('check_HIST_file', key='-path_check_HIST-'), sg.FileBrowse()],
                    [sg.Button('check_HIST_file', key='-check_HIST_file-')],
                    [sg.T(' ')],
                    [sg.Text('titul',          size=(15, 1)), sg.Input(_gl.titul, key='-titul-') ],
                    [sg.Text('path_file_DATA', size=(15, 1)), sg.Input(_gl.path_file_DATA, key='-path_DATA-'), sg.FileBrowse()],
                    [sg.Text('path_file_HIST', size=(15, 1)), sg.Input(_gl.path_file_HIST, key='-path_HIST-'), sg.FileBrowse()],
                    [sg.Text('dt_start',       size=(15, 1)), sg.Input(_gl.dt_start, key='-dt_start-')],
                    [sg.Text('path_file_TXT',  size=(15, 1)), sg.Input(_gl.path_file_TXT, key='-path_TXT-'),   sg.FileBrowse()],
                    [sg.Button('update cfg_SOFT', key='-update_cfg_SOFT-')],
                    [sg.T(' ')],
                    [sg.T('', size=(60,1), font='Helvetica 8', key='txt_status')],
                     #sg.Quit(auto_size_button=True)
                 ]
        sg.SetOptions(element_padding=(0,0))
        window = sg.Window('Titul SERV', grab_anywhere=True).Layout(layout).Finalize()
        #window.FindElement('txt_data').Update(''.join(def_txt))
        break

    frm = '%d.%m.%Y %H:%M:%S'
    stts  = 10*' ' + time.strftime(frm, time.localtime()) + '   event = none'
    window.FindElement('txt_status').Update(stts)

    while True:  # MAIN cycle ------------------------------------------
        stroki = []
        event, values = window.Read(timeout = 25000 )
        #---------------------------------------------------------------
        event_menu(event, values, _gl)
        #---------------------------------------------------------------
        if event is None or event == 'Quit' or event == 'Exit': break
        #---------------------------------------------------------------
        if event == '__TIMEOUT__':
            pass
        #---------------------------------------------------------------
        #window.FindElement('txt_data').Update('\n'.join(stroki))
        stts = 10*' ' + time.strftime(frm, time.localtime()) + 5*' ' + 'event = ' + event
        window.FindElement('txt_status').Update(stts)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
