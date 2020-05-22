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
clr = ['red', 'blue', 'green', 'black', 'coral', 'navy', 'teal', 'gray',  'brown', 'indigo', 'gold', 'purple',]
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
        #
        self.arr_pk_graph = []  # list of obj [Class_STR_PACK ... ]
        #self.pack_graph = 0
        #
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
def event_menu_win_GRAPH(ev, values, _gl, win):
    rq = [0,ev]
    graph = win.FindElement('graph')
    X_bot_left,  Y_bot_left  = 0, 0
    X_top_right, Y_top_right = graph.CanvasSize
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    print('ev =>     ', ev)
    print('values => ', values)
    #-------------------------------------------------------------------
    if ev == '__TIMEOUT__':
        print('event_menu_win_GRAPH ... __TIMEOUT__ ...')
        rep = _gl.db_tod.read_tbl('hist_PACK')
        _gl.arr_pck_t = []
        _gl.arr_pck_t = _gl.unpack_str_pck(rep[1])[1]

    #-------------------------------------------------------------------
    if ev in ['cmb_nm_pack',  'cmb_graph', 'REFRESH', '__TIMEOUT__'] :
        #--- fix number ticks in ARCHIV
        num_discr = 3
        if values['cmb_graph'] == 'GRAPH_slider' :
            num_discr = int(values['sld_graph']) * 520
        if values['cmb_graph'] == 'GRAPH_1_day' : num_discr = 1 * 520
        if values['cmb_graph'] == 'GRAPH_10_day': num_discr = 10 * 520
        if values['cmb_graph'] == 'GRAPH_20_day': num_discr = 20 * 520
        if values['cmb_graph'] == 'GRAPH_30_day': num_discr = 30 * 520
        if values['cmb_graph'] == 'GRAPH_all'   : num_discr = len(_gl.arr_pck_a)
        print('num_discr  = ', num_discr)

        #--- fix number packets in GRAPHik
        arr_num_pack = []
        for i, item in enumerate(_gl.cfg_pck.arr):
            if values['CB'+str(i)]:
                arr_num_pack.append(i)
        print('arr_num_pack = ', arr_num_pack)

        #--- fix list of FUNCTIONs for GRAPHik
        _gl.arr_pk_graph = []
        if len(_gl.arr_pck_a) > 0:
            for item in _gl.arr_pck_a[-num_discr:-1]:
                arr_bb = Class_str_PCK()
                arr_bb.ind_s, arr_bb.dt  = item.ind_s, item.dt
                for ktem in arr_num_pack:
                    arr_bb.arr.append(item.arr[ktem])
                _gl.arr_pk_graph.append(arr_bb)
        if len(_gl.arr_pck_t) > 0:
            for item in _gl.arr_pck_t:
                arr_bb = Class_str_PCK()
                arr_bb.ind_s, arr_bb.dt  = item.ind_s, item.dt
                for ktem in arr_num_pack:
                    arr_bb.arr.append(item.arr[ktem])
                _gl.arr_pk_graph.append(arr_bb)

        if len(_gl.arr_pk_graph) > 0:
            print('len(_gl.arr_pk_graph) = ', len(_gl.arr_pk_graph))
            print('arr_pk_graph[0]  = ', _gl.arr_pk_graph[0])
            print('arr_pk_graph[-1] = ', _gl.arr_pk_graph[-1])

        graph.Erase()
        # Draw axis X & LABELS
        step_X = int(X_top_right/10)
        k_gr_X = len(_gl.arr_pk_graph)/X_top_right
        gr_X = [item.dt for item in _gl.arr_pk_graph]
        for x in range(step_X, X_top_right, step_X):
            graph.DrawLine((x,Y_bot_left+25), (x, Y_top_right), color='lightgrey')
            i_gr_X = int(x*k_gr_X)
            graph.DrawText( gr_X[i_gr_X][0], (x,5),  color='black')
            graph.DrawText( gr_X[i_gr_X][1], (x,18), color='black')

        # Draw axis Y
        step_Y = int(Y_top_right/10)
        for y in range(step_Y, Y_top_right, step_Y):
            graph.DrawLine((X_bot_left + 30,y), (X_top_right, y), color='lightgrey')
            #graph.DrawText(str(y) , (15, y), color='black')

        pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
        gr_Y = []

        nul_index = num_discr - 10 - int(values['sld_null']) * 520
        nul_arr = [ int((prc[pAsk] + prc[pBid])/2) for prc in _gl.arr_pk_graph[nul_index].arr ]
        for item in _gl.arr_pk_graph:
            buf = [int((prc[pAsk] + prc[pBid])/2) - nul_arr[i] for i, prc in enumerate (item.arr)]
            for i, prc in enumerate (item.arr):
                buf.append( prc[EMAf_r] - nul_arr[i] )
            gr_Y.append(buf)
        print('gr_Y[0]  = ', gr_Y[0])
        print('gr_Y[-1] = ', gr_Y[-1])

        #
        k_max_Y =  max([max(item) for item in gr_Y])
        k_min_Y =  min([min(item) for item in gr_Y])
        k_gr_Y  = (k_max_Y - k_min_Y)/Y_top_right
        print('k_max_Y = ',k_max_Y)
        print('k_min_Y = ',k_min_Y)
        print('k_gr_Y  = ',k_gr_Y)

        for y in range(step_Y, Y_top_right, step_Y):
            cur_ASK  = int(y*k_gr_Y + k_min_Y)
            graph.DrawText(str(cur_ASK) , (18, y + 5), color='black')

        if values['cmb_graph'] == 'GRAPH_1_day' :
            for i, item in enumerate(gr_Y[1:]):
                prv_X = int((i - 1) / k_gr_X)
                cur_X = int((i - 0) / k_gr_X)
                for j, jtem in enumerate (item):
                    #cur_Y  = int((jtem   - k_min_Y) / k_gr_Y)
                    #graph.DrawPoint((cur_X, cur_Y), size=1, color=clr[j])
                    prv_Y = int((gr_Y[i-1][j] - k_min_Y) / k_gr_Y)
                    cur_Y = int((gr_Y[i][j]   - k_min_Y) / k_gr_Y)
                    graph.DrawLine((prv_X, prv_Y), (cur_X, cur_Y), width=1, color=clr[j])
        else:
            for i, item in enumerate(gr_Y[1:]):
                cur_X  = int((i - 0) / k_gr_X)
                for j, jtem in enumerate (item):
                    cur_Y  = int((jtem   - k_min_Y) / k_gr_Y)
                    graph.DrawPoint((cur_X, cur_Y), size=1, color=clr[j])

        # sg.PopupOK('\nDrawPoint *gr_Y* successfully !\n',
                    # background_color = 'LightGreen')

    #-------------------------------------------------------------------
    if ev == 'rd_hist_PACK_today'  :
        if 'OK' == sg.PopupOKCancel('\nRead table *hist_PACK*\n  from db_TODAY\n '):
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

                sg.PopupOK('\nRead table *hist_PACK* successfully !\n',
                            background_color = 'LightGreen')
    #-------------------------------------------------------------------
    if ev == 'rd_hist_PACK_arch'  :
        if 'OK' == sg.PopupOKCancel('\nRead table *hist_PACK*\n  from db_ARCH\n '):
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

                sg.PopupOK('\nRead table *hist_PACK* successfully !\n',
                            background_color = 'LightGreen')
    #-------------------------------------------------------------------
    if ev == 'read_cfg_PACK':
        print('read_cfg_PACK')
        _gl.prn_cfg_pack()
#=======================================================================
def main():
    menu_def = [
        ['MODE', ['AUTO', 'Manual', '---', 'Exit',],],
        ['READ', [ 'read_cfg_PACK', 'rd_hist_PACK_arch',  'rd_hist_PACK_today',  ],],
        ['PRINT',[ 'prn_cfg_PCK',   'prn_arr_PCK_t',      'prn_arr_PCK_a',       ],],
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
            return 0
        else:
            if len(rep[1]) == 0:
                sg.PopupError('\ndb_ARCH table hist_PACK is EMPTY !\n',
                                background_color = 'brown',
                                no_titlebar = True)
                return 0
        #---------------------------------------------------------------
        _gl.arr_pck_a = []
        _gl.arr_pck_a = _gl.unpack_str_pck(rep[1])[1]
        #_gl.prn_arr('arr_pck_a', _gl.arr_pck_a)
        #
        # read db_TODAY table hist_PACK --------------------------------
        rep = _gl.db_tod.read_tbl('hist_PACK')
        if rep[0] > 0:
            sg.PopupError('\nDid not read table!\n'
                            + rep[1] + '\n',
                            background_color = 'brown',
                            no_titlebar = True)
            return 0
        #---------------------------------------------------------------
        _gl.arr_pck_t = []
        _gl.arr_pck_t = _gl.unpack_str_pck(rep[1])[1]
        break
    #
    obj_Graph = sg.Graph(canvas_size=(X_top_right, Y_top_right),
                 graph_bottom_left=(X_bot_left,  Y_bot_left ),
                 graph_top_right  =(X_top_right, Y_top_right),
                 background_color='white smoke', #'gray',
                 key='graph')
    obj_CheckBox = [[sg.Checkbox('P'+str(i), key='CB'+str(i))] for i in range(len(_gl.cfg_pck.arr))]
    #
    lay_GRAPH = [[sg.Menu(menu_def, tearoff=False, key='MENU') ],
                #[obj_Graph],
                [sg.Column(obj_CheckBox), obj_Graph],
                [sg.Slider(range=(1,15),
                         default_value=3,
                         size=(20,15),
                         orientation='horizontal',
                         font=('Helvetica', 10),
                         key='sld_graph'),
                 sg.Slider(range=(1,15),
                         default_value=1,
                         size=(20,15),
                         orientation='horizontal',
                         font=('Helvetica', 10),
                         key='sld_null'),
                         ],
                [sg.Combo(['GRAPH_slider', 'GRAPH_1_day', 'GRAPH_10_day', 'GRAPH_20_day', 'GRAPH_30_day', 'GRAPH_all' ],
                    default_value = 'GRAPH_slider',
                    enable_events =True,
                    auto_size_text=True,
                    key='cmb_graph'),
                    sg.T(10*' '),
                    sg.Button('REFRESH', auto_size_button=True),
                    sg.T(10*' '),
                    sg.Quit(auto_size_button=True)]]

    #sg.theme('DarkTeal12')   # Add a touch of color
    win_GRAPH = sg.Window('GRAFik').Layout(lay_GRAPH).Finalize()
    win_GRAPH_mode, win_GRAPH_timeout = 'Manual', 360000
    win_GRAPH.FindElement('CB0').Update(value=1)
    #
    while True:
        #=== check 'Window MAIN' =======================================
        ev_GRAPH, vals_GRAPH = win_GRAPH.Read(timeout = win_GRAPH_timeout)
        #---------------------------------------------------------------
        if ev_GRAPH in [None, 'Close', 'Exit', 'Quit']:
            win_GRAPH.Close()
            break
        #---------------------------------------------------------------
        if ev_GRAPH == 'AUTO'  :
            win_GRAPH_timeout, win_GRAPH_mode =  30000,   'AUTO'
        #---------------------------------------------------------------
        if ev_GRAPH == 'Manual':
            win_GRAPH_timeout, win_GRAPH_mode = 360000, 'Manual'
        #--- ev_cfg_SOFT 'Window cfg_SOFT' -----------------------------
        event_menu_win_GRAPH(ev_GRAPH, vals_GRAPH, _gl, win_GRAPH)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
