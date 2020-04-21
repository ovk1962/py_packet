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
        self.dt_start       = ''    # 2017-01-01 00:00:00
        self.dt_start_sec   = 0     # 2017-01-01 00:00:00
        self.path_file_TXT  = ''    # c:\\hist_log_ALOR.txt
        # cfg_pack
        self.nm   = []  # list NM   of packets
        self.koef = []  # list KOEF of packets
        self.nul  = []  # list NUL  of packets
        self.ema  = []  # list EMA  of packets
        #

    def prn_cfg(self):
        frm = '{: <18}{: <55}'
        print(frm.format('titul',          self.titul))
        print(frm.format('dt_start',       self.dt_start))
        print(frm.format('dt_start_sec',   str(self.dt_start_sec)))
        print(frm.format('path_file_DATA', self.path_file_DATA))
        print(frm.format('path_file_HIST', self.path_file_HIST))
        print(frm.format('path_file_TXT',  self.path_file_TXT))

    def unpack_cfg_soft(self):
        print('=> _GL unpack_cfg_soft')
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

    def unpack_cfg_pack(self):
        print('=> _GL unpack_cfg_pack ')
        try:
            cfg = self.db_tod.read_tbl('cfg_PACK')
            if cfg[0] > 0: return cfg
            self.nm   = []  # list NM   of packets
            self.koef = []  # list KOEF of packets
            self.nul  = []  # list NUL  of packets
            self.ema  = []
            for item in cfg[1]:
                self.nm.append(item[0])          # ['pckt0']
                arr_k    = item[1].split(',')
                arr_koef = []
                for item_k in arr_k:             # '0:2:SR' => [0, 32, 'SR']
                    buf_k = [int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')]
                    arr_koef.append(buf_k)
                self.koef.append(arr_koef)       #  [[0, 2, 'SR'],[9, -20, 'MX'], ...
                self.nul.append(int(item[2]))    #  [0]
                self.ema.append([int(e) for e in item[3].split(':')]) # [1111, 15]
            #-----------------------------------------------------------
            frm = '{: ^5}{: ^15}{}{}{}'
            print(frm.format('nm','nul','ema[]','        ','koef[]'))
            for i, item in enumerate(self.nm):
                print(frm.format(self.nm[i],
                            str(self.nul[i]),
                                self.ema[i], '   ',
                                self.koef[i]))
            #-----------------------------------------------------------
        except Exception as ex:
            return [1, ex]

        return [0, cfg]
#=======================================================================
def event_menu_win_MAIN(ev, values, _gl, win):
    rq = [0,ev]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if ev == '__TIMEOUT__':
        print('ev ... __TIMEOUT__ ...')
    #-------------------------------------------------------------------

    #-------------------------------------------------------------------
    print('rq = ', rq)
#=======================================================================
def event_menu_CFG_SOFT(ev, values, _gl, win):
    rq = [0,ev]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if ev == '__TIMEOUT__':
        print('ev ... __TIMEOUT__ ...')
    #-------------------------------------------------------------------
    if ev == '-update_cfg_SOFT-':
        print('ev ... -update_cfg_SOFT- ...')
        if 'OK' == sg.PopupOKCancel('\n' + 'Update table *cfg_SOFT*' + '\n'):
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

            rq = _gl.db_tod.update_tbl('cfg_SOFT', cfg, val = ' VALUES(?,?)')
            if rq[0] > 0:
                sg.PopupError('\n' + 'Did not update cfg_SOFT!' + '\n'
                                + rep[1] + '\n',
                                background_color = 'brown',
                                no_titlebar = True)
            else:
                sg.PopupOK('\nUpdated *cfg_SOFT* successfully !\n')
    #-------------------------------------------------------------------
    print('rq = ', rq)
#=======================================================================
def event_menu_CFG_PACK(ev, val, _gl, win):
    rq = [0,ev]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    #-------------------------------------------------------------------
    if ev == '__TIMEOUT__':
        print('__TIMEOUT__')
    #-------------------------------------------------------------------
    if ev == '-rd_cfg_PACK-':
        print('-nm_pack- = ', int(val['-nm_pack-']) )
        win.FindElement('-nm-').Update(_gl.nm[int(val['-nm_pack-'])])
        win.FindElement('-koef-').Update(_gl.koef[int(val['-nm_pack-'])])
        win.FindElement('-ema-').Update(_gl.ema[int(val['-nm_pack-'])])
    #-------------------------------------------------------------------
    if ev == '-update_cfg_PACK-':
        print('-update_cfg_PACK-')
    #-------------------------------------------------------------------
    print('rq = ', rq)
#=======================================================================
def main():
    _gl = Class_GL()
    _gl.unpack_cfg_soft()
    _gl.unpack_cfg_pack()

    menu_def = [['MODE',
                    ['AUTO', 'Manual', '---',
                     'Exit',],],
                ['DIAG',
                    ['update_cfg_SOFT',  'update_cfg_PACK',  '---',
                     'rd_term_FUT',      'rd_term_HST',      '---',],],
                ]

    lay_MAIN = [ [sg.Menu(menu_def)                               ],
                [sg.Multiline(' ', size=(45, 1), do_not_clear=True, key='-INPUT_1-')     ],
                [sg.Button('Exit')                                ]]

    lay_cfg_SOFT = [ #[sg.Text('update_cfg_SOFT')],
                [sg.Text('titul',          size=(15, 1)), sg.Input(_gl.titul,           do_not_clear=True, key='-titul-') ],
                [sg.Text('path_file_DATA', size=(15, 1)), sg.Input(_gl.path_file_DATA,  do_not_clear=True, key='-path_DATA-'), sg.FileBrowse()],
                [sg.Text('path_file_HIST', size=(15, 1)), sg.Input(_gl.path_file_HIST,  do_not_clear=True, key='-path_HIST-'), sg.FileBrowse()],
                [sg.Text('dt_start',       size=(15, 1)), sg.Input(_gl.dt_start,        do_not_clear=True, key='-dt_start-')],
                [sg.Text('path_file_TXT',  size=(15, 1)), sg.Input(_gl.path_file_TXT,   do_not_clear=True, key='-path_TXT-'),   sg.FileBrowse()],
                [sg.Button('update cfg_SOFT', key='-update_cfg_SOFT-'), sg.Button('Close')],]

    lay_cfg_PACK = [ #[sg.Text('update_cfg_PACK')],
                [sg.Button('read cfg_PACK', key='-rd_cfg_PACK-'),
                 sg.Slider(range=(0, len(_gl.nm)-1), orientation='h',    size=(23, 15), default_value=0, key='-nm_pack-'),],
                [sg.Text('nm',   size=(4, 1)), sg.Input(_gl.nm[0],       size=(45, 1), do_not_clear=True, key='-nm-') ],
                [sg.Text('koef', size=(4, 1)), sg.Multiline(_gl.koef[0], size=(45, 1), do_not_clear=True, key='-koef-') ],
                [sg.Text('ema',  size=(4, 1)), sg.Input(_gl.ema[0],      size=(45, 1), do_not_clear=True, key='-ema-') ],
                [sg.Button('update cfg_PACK', key='-update_cfg_PACK-'), sg.Button('Close')],]

    #sg.theme('DarkTeal12')   # Add a touch of color
    win_MAIN = sg.Window(_gl.titul, grab_anywhere=True).Layout(lay_MAIN).Finalize()
    cfg_SOFT_active = False
    cfg_PACK_active = False

    while True:
        #--- check 'Window MAIN' ---------------------------------------
        ev_MAIN, vals_MAIN = win_MAIN.Read(timeout=500)
        print('ev_MAIN = ', ev_MAIN, '    vals_MAIN = ', vals_MAIN)
        if ev_MAIN is None or ev_MAIN == 'Exit':
            break
        #--- ev_cfg_SOFT 'Window cfg_SOFT' -------------------------
        event_menu_win_MAIN(ev_MAIN, vals_MAIN, _gl, win_MAIN)

        #--- open 'Window cfg_SOFT' ------------------------------------
        if ev_MAIN == 'update_cfg_SOFT' and not cfg_SOFT_active:
            cfg_SOFT_active = True
            win_cfg_SOFT = sg.Window('update_cfg_SOFT', location=(25,25)).Layout(lay_cfg_SOFT[:]).Finalize()
        #--- check 'win_cfg_SOFT' --------------------------------------
        if cfg_SOFT_active:
            ev_cfg_SOFT, vals_cfg_SOFT = win_cfg_SOFT.Read(timeout=100)
            #print('ev_cfg_SOFT = ', ev_cfg_SOFT, '    vals_cfg_SOFT = ', vals_cfg_SOFT)
            if ev_cfg_SOFT is None or ev_cfg_SOFT == 'Close' or ev_cfg_SOFT == 'Exit':
                cfg_SOFT_active  = False
                win_cfg_SOFT.Close()
            #--- ev_cfg_SOFT 'Window cfg_SOFT' -------------------------
            event_menu_CFG_SOFT(ev_cfg_SOFT, vals_cfg_SOFT, _gl, win_cfg_SOFT)

        #--- open 'Window cfg_PACK' ------------------------------------
        if ev_MAIN == 'update_cfg_PACK' and not cfg_PACK_active:
            cfg_PACK_active = True
            win_cfg_PACK = sg.Window('update_cfg_PACK', location=(150,200)).Layout(lay_cfg_PACK[:]).Finalize()
        #--- check 'Window 3' ------------------------------------------
        if cfg_PACK_active:
            ev_cfg_PACK, vals_cfg_PACK = win_cfg_PACK.Read(timeout=100)
            #print('ev_cfg_PACK = ', ev_cfg_PACK, '    vals_cfg_PACK = ', vals_cfg_PACK)
            if ev_cfg_PACK is None or ev_cfg_PACK == 'Close' or ev_cfg_PACK == 'Exit':
                cfg_PACK_active  = False
                win_cfg_PACK.Close()
            #--- ev_cfg_PACK 'Window win_cfg_PACK' ---------------------
            event_menu_CFG_PACK(ev_cfg_PACK, vals_cfg_PACK, _gl, win_cfg_PACK)


    return 0

if __name__ == '__main__':
    main()