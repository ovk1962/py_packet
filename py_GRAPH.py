#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_GRAPH.py
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
class Class_str_PCK():
    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
    def __init__(self):
        self.ind_s, self.dt, self.arr  = 0, '', []
    def __retr__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
    def __str__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
#=======================================================================
class Class_PACK():
    def __init__(self):
        c_dir    = os.path.abspath(os.curdir)
        self.lg_FILE    = Class_LOGGER(c_dir + '\\LOG\\pack_logger.log')
        self.db_PCK_arc = Class_DB_SQLite(c_dir + '\\DB\\db_pack_a.sqlite')
        self.db_PCK_tod = Class_DB_SQLite(c_dir + '\\DB\\db_pack_t.sqlite')
        # cfg_pack
        self.nm   = []  # list NM   of packets
        self.koef = []  # list KOEF of packets
        self.nul  = []  # list NUL  of packets
        self.ema  = []  # list EMA  of packets
        #
        #
        self.hst_pck_t = []
        self.arr_pck_t = []
        self.hst_pck_a = []
        self.arr_pck_a = []
        #
        self.arr_pk_graph = []  # list of obj [Class_STR_PACK ... ]
        self.pack_graph = 0
        #

    def prn_arr(self, name_arr, arr):
        print('len(' + name_arr + ')   => ' + str(len(arr)) + '\n' )
        if len(arr) > 4:
            for i in [0,1]: print(arr[i],'\n')
            print('+++++++++++++++++++++++++\n')
            for i in [-2,-1]: print(arr[i],'\n')
        else:
            for item in arr: print(item, '\n')

    def prn_cfg(self):
        #-----------------------------------------------------------
        frm = '{: ^5}{: ^15}{}{}{}'
        print(frm.format('nm','nul','ema[]','        ','koef[]'))
        for i, item in enumerate(self.nm):
            print(frm.format(self.nm[i],
                        str(self.nul[i]),
                            self.ema[i], '   ',
                            self.koef[i]))

    def unpack_str_pck(self, hist_pck):
        print('=> _PACK unpack_str_pck ', len(hist_pck))
        try:
            arr_pck = []
            #self.arr_pk_t  = []
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

    def unpack_str_cfg(self, cfg):
        print('=> _PACK unpack_str_cfg ', len(cfg))
        try:
            self.nm   = []  # list NM   of packets
            self.koef = []  # list KOEF of packets
            self.nul  = []  # list NUL  of packets
            self.ema  = []
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
            return [1, ex]
        return [0, cfg]

    def get_pk_graph(self):
        print('start get_pk_graph for PACK => ', self.pack_graph)
        self.arr_pk_graph = []
        if len(self.arr_pck_a) > 0:
            for item in self.arr_pck_a:
                arr_bb = Class_str_PCK()
                arr_bb.ind_s, arr_bb.dt  = item.ind_s, item.dt
                arr_bb.arr.append(item.arr[0])
                arr_bb.arr.append(item.arr[self.pack_graph])
                self.arr_pk_graph.append(arr_bb)
        if len(self.arr_pck_t) > 0:
            for item in self.arr_pck_t:
                arr_bb = Class_str_PCK()
                arr_bb.ind_s, arr_bb.dt  = item.ind_s, item.dt
                arr_bb.arr.append(item.arr[0])
                arr_bb.arr.append(item.arr[self.pack_graph])
                self.arr_pk_graph.append(arr_bb)
        if len(self.arr_pk_graph) > 0:
            print('arr_pk_graph[-1] = ', self.arr_pk_graph[-1])

#=======================================================================
def event_menu_2(ev2, vals2, _gl, win2):
    rq = [0, ev2]
    graph = win2.FindElement('graph')
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    X_bot_left,  Y_bot_left  = 0, 0
    X_top_right, Y_top_right = graph.CanvasSize
    #-------------------------------------------------------------------
    if ev2 in ('inc_PACK', 'dec_PACK', 'refresh' ):
        if ev2 == 'inc_PACK':
            _gl.pack_graph = (_gl.pack_graph + 1) % len(_gl.nm)
        if ev2 == 'dec_PACK':
            if (_gl.pack_graph - 1) < 0:
                _gl.pack_graph = len(_gl.nm) - 1
            else:
                _gl.pack_graph = _gl.pack_graph - 1

        if ev2 in ('inc_PACK', 'dec_PACK'):
            str_pck = _gl.nm[_gl.pack_graph] + '___'
            koef_pckt = _gl.koef[_gl.pack_graph]
            for i, item in enumerate(koef_pckt):
                str_pck +='_'.join(str(x) for x in koef_pckt[i]) + '___'
            win2.FindElement('name_pckt').Update(str_pck)
            #win2.FindElement('btn_graph').Update('choice & press button GRAPH ...')

        rq = _gl.get_pk_graph()
        num_discr = 0
        buf_arr   = []
        if vals2['cmb_graph'] == 'GRAPH_1_day' : num_discr = 1  * 520
        if vals2['cmb_graph'] == 'GRAPH_5_day' : num_discr = 5  * 520
        if vals2['cmb_graph'] == 'GRAPH_10_day': num_discr= 10 * 520
        if vals2['cmb_graph'] == 'GRAPH_all'   : num_discr = len(_gl.arr_pk_graph)
        #win2.FindElement('btn_graph').Update(ev2)

        buf_arr = _gl.arr_pk_graph[-num_discr:-1]
        print('num_discr  = ', num_discr)
        print('buf_arr[0] = ', buf_arr[0])
        print('buf_arr[-1] = ', buf_arr[-1])
        gr_X, gr_Y0, gr_ASK, gr_BID, gr_EMAf, gr_EMAf_r, gr_cnt_EMAf_r = [],[],[],[],[],[],[]
        pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
        for item in buf_arr:
            gr_X.append(item.dt)
            gr_Y0.append(item.arr[0][EMAf])
            gr_ASK.append(item.arr[1][pAsk])
            gr_BID.append(item.arr[1][pBid])
            gr_EMAf.append(item.arr[1][EMAf])
            gr_EMAf_r.append(item.arr[1][EMAf_r])
            gr_cnt_EMAf_r.append(item.arr[1][cnt_EMAf_r])

        print('gr_X[-1] = ', gr_X[-1])

        graph.Erase()
        # Draw axis X
        step_X = int(X_top_right/10)
        for x in range(step_X, X_top_right, step_X):
            graph.DrawLine((x,Y_bot_left+25), (x, Y_top_right), color='lightgrey')

        # Draw axis Y
        step_Y = int(Y_top_right/10)
        for y in range(step_Y, Y_top_right, step_Y):
            graph.DrawLine((X_bot_left + 30,y), (X_top_right, y), color='lightgrey')
            #graph.DrawText(str(y) , (15, y), color='black')

        # Calc X for Graph
        k_gr_X = num_discr/X_top_right
        print('k_gr_X = ', k_gr_X)

        # Draw LABELS of axis X
        for x in range(step_X, X_top_right, step_X):
            i_gr_X = int(x*k_gr_X)
            graph.DrawText( gr_X[i_gr_X][0], (x,5),  color='black')
            graph.DrawText( gr_X[i_gr_X][1], (x,18), color='black')

        # Draw Graph Y
        k_gr_Y0  = (max(gr_Y0) - min(gr_Y0))/Y_top_right
        k_min_Y0 =  min(gr_Y0)

        k_max_Y1 = max(max(gr_ASK),max(gr_BID),max(gr_EMAf),max(gr_EMAf_r) )
        k_max_Y1 = int(math.ceil(k_max_Y1 / 1000.0)) * 1000
        k_min_Y1 = min(min(gr_ASK),min(gr_BID),min(gr_EMAf),min(gr_EMAf_r) )
        k_min_Y1 = int(math.ceil(k_min_Y1 / 1000.0)) * 1000 - 1000
        k_gr_Y1  = (k_max_Y1 - k_min_Y1)/Y_top_right

        # Draw LABELS of axis Y1
        step_Y = int(Y_top_right/10)
        for y in range(step_Y, Y_top_right, step_Y):
            cur_ASK  = int(y*k_gr_Y1 + k_min_Y1)
            graph.DrawText(str(cur_ASK) , (18, y + 5), color='black')
        print('k_max_Y1  = ', k_max_Y1)
        print('k_min_Y1  = ', k_min_Y1)
        #print('num_discr = ',  num_discr)
        #print('k_gr_Y1   = ', k_gr_Y1 )

        if max(gr_cnt_EMAf_r) == min(gr_cnt_EMAf_r):
            k_gr_Y2  = (max(gr_cnt_EMAf_r) + min(gr_cnt_EMAf_r))/Y_top_right
        else:
            k_gr_Y2  = (max(gr_cnt_EMAf_r) - min(gr_cnt_EMAf_r))/Y_top_right
        if k_gr_Y2 == 0:
            k_gr_Y2 = 1
        k_min_Y2 =  min(gr_cnt_EMAf_r)
        print('max(gr_cnt_EMAf_r)  = ', max(gr_cnt_EMAf_r))
        print('k_min_Y2  = ', k_min_Y2)
        print('num_discr = ', num_discr)
        print('k_gr_Y2   = ', k_gr_Y2 )

        for i, item in enumerate(gr_Y0):
            if i > 0:
                prev_X = int((i - 1) / k_gr_X)
                cur_X  = int((i - 0) / k_gr_X)

                prev_Y0 = int((gr_Y0[i-1] - k_min_Y0) / k_gr_Y0)
                cur_Y0  = int((gr_Y0[i]   - k_min_Y0) / k_gr_Y0)
                graph.DrawLine((prev_X, prev_Y0), (cur_X, cur_Y0),      width=3, color='red')

                prev_ASK = int((gr_ASK[i-1] - k_min_Y1) / k_gr_Y1)
                cur_ASK  = int((gr_ASK[i]   - k_min_Y1) / k_gr_Y1)
                graph.DrawLine((prev_X, prev_ASK), (cur_X, cur_ASK),    width=1, color='green')

                prev_BID = int((gr_BID[i-1] - k_min_Y1) / k_gr_Y1)
                cur_BID  = int((gr_BID[i]   - k_min_Y1) / k_gr_Y1)
                graph.DrawLine((prev_X, prev_BID), (cur_X, cur_BID),    width=1, color='green')

                prev_EMAf = int((gr_EMAf[i-1] - k_min_Y1) / k_gr_Y1)
                cur_YEMAf = int((gr_EMAf[i]   - k_min_Y1) / k_gr_Y1)
                graph.DrawLine((prev_X, prev_EMAf), (cur_X, cur_YEMAf), width=1, color='blue')

                prev_EMAf_r = int((gr_EMAf_r[i-1] - k_min_Y1) / k_gr_Y1)
                cur_YEMAf_r = int((gr_EMAf_r[i]   - k_min_Y1) / k_gr_Y1)
                graph.DrawLine((prev_X, prev_EMAf_r), (cur_X, cur_YEMAf_r), width=3, color='blue')

                prev_Y2 = int((gr_cnt_EMAf_r[i-1] - k_min_Y2) / k_gr_Y2)
                cur_Y2  = int((gr_cnt_EMAf_r[i]   - k_min_Y2) / k_gr_Y2)
                graph.DrawLine((prev_X, prev_Y2), (cur_X, cur_Y2),      width=3, color='brown')

    #-------------------------------------------------------------------
    if ev2 == 'rd_cfg_PACK_a'  :
        cfg = _gl.db_PCK_arc.read_tbl('cfg_PACK')
        if cfg[0] == 0:
            arr = _gl.unpack_str_cfg(cfg[1])
    #-------------------------------------------------------------------
    if ev2 == 'rd_arr_PACK_a'  :   #   _gl.hst_pck_a   _gl.arr_pck_a
        hst = _gl.db_PCK_arc.read_tbl('hist_PACK')
        if hst[0] == 0:
            _gl.hst_pck_a = hst[1][:]
            arr = _gl.unpack_str_pck(hst[1])
            if arr[0] == 0:
                _gl.arr_pck_a = arr[1][:]
                _gl.prn_arr('arr_pck_a', arr[1],)
    #-------------------------------------------------------------------
    if ev2 == 'rd_arrPACK_t'  :   #   _gl.hst_pck_t   _gl.arr_pck_t
        hst = _gl.db_PCK_tod.read_tbl('hist_PACK_today')
        if hst[0] == 0:
            _gl.hst_pck_t = hst[1][:]
            arr = _gl.unpack_str_pck(hst[1])
            if arr[0] == 0:
                _gl.arr_pck_t = arr[1][:]
                _gl.prn_arr('arr_pck_t', arr[1],)
    #-------------------------------------------------------------------
    if ev2 == 'prn_cfg_PCK_t'  :
        _gl.prn_cfg()
    #-------------------------------------------------------------------
    if ev2 == 'prn_arr_PCK_a'  :
        _gl.prn_arr('arr_pck_a', _gl.arr_pck_a)
    #-------------------------------------------------------------------
    if ev2 == 'prn_arr_PCK_t'  :
        _gl.prn_arr('arr_pck_t', _gl.arr_pck_t)
    #-------------------------------------------------------------------

    #-------------------------------------------------------------------
    print('rq = ', rq)
    print(ev2)
    print(vals2)

    return
#=======================================================================
def main():
    menu_def = [
        ['READ', [ 'rd_cfg_PACK_a', 'rd_arr_PACK_a',  'rd_arrPACK_t',  ],],
        ['PRINT',[ 'prn_cfg_PCK_t', 'prn_arr_PCK_t',  'prn_arr_PCK_a', ],],
        ['Exit', 'Exit']
    ]
    _gl = Class_PACK()      # init db_TODAY ------------------------

    X_bot_left,  Y_bot_left  = 0,    0
    X_top_right, Y_top_right = 1040, 500

    layout = [
                [sg.Menu(menu_def, tearoff=False, key='menu_def')],
                [sg.T(110*'_', size=(110,1), key='name_pckt')],
                #[sg.T(110*' ', size=(110,1), key='btn_graph')],
                [sg.Graph(canvas_size=(X_top_right, Y_top_right),
                    graph_bottom_left=(X_bot_left,  Y_bot_left ),
                    graph_top_right  =(X_top_right, Y_top_right),
                    background_color='white',
                    key='graph')],

                [sg.Button('dec_PACK'),  sg.T(' '),
                 sg.Button('inc_PACK'),  sg.T(' '),
                 sg.Button('refresh'),   sg.T(10*' '),
                 sg.Combo(['GRAPH_1_day', 'GRAPH_5_day', 'GRAPH_10_day', 'GRAPH_all' ], default_value = 'GRAPH_1_day', key='cmb_graph'), sg.T(10*' '),
                 sg.Quit(auto_size_button=True)],
            ]
    win2 = sg.Window('Graph of HISTORY for packets').Layout(layout)
    win2.Finalize()



    while True:
        ev2, vals2 = win2.Read(timeout=5000)
        print(ev2, vals2)
        #-------------------------------------------------------
        if ev2 == '__TIMEOUT__':
            pass
        #-------------------------------------------------------
        if ev2 is None or ev2 == 'Quit' or ev2 == 'Exit':
            win2.Close()
            break
        #-------------------------------------------------------
        event_menu_2(ev2, vals2, _gl, win2)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
