import win32traceutil

import win32con
import sys
from ctypes import *
import time

import _mshtml

import win32con

from ctypes import *
from ctypes.wintypes import *
from comtypes import IUnknown
from comtypes.automation import IDispatch, VARIANT
from comtypes.client import wrap, GetModule

#from win32com.client import *
#cast = gencache.GetModuleForProgID('htmlfile')

if not hasattr(sys, 'frozen'):
    GetModule('atl.dll')
    GetModule('shdocvw.dll')

kernel32 = windll.kernel32
user32 = windll.user32
atl = windll.atl                  # If this fails, you need atl.dll

import win32con
from ctypes import *
from comtypes import IUnknown
from comtypes.automation import VARIANT
from comtypes.client import GetEvents
from comtypes.gen import SHDocVw
from comtypes.gen import MSHTML

kernel32 = windll.kernel32
user32 = windll.user32

WNDPROC = WINFUNCTYPE(c_long, c_int, c_uint, c_int, c_int)

class WNDCLASS(Structure):
    _fields_ = [('style', c_uint),
                ('lpfnWndProc', WNDPROC),
                ('cbClsExtra', c_int),
                ('cbWndExtra', c_int),
                ('hInstance', c_int),
                ('hIcon', c_int),
                ('hCursor', c_int),
                ('hbrBackground', c_int),
                ('lpszMenuName', c_char_p),
                ('lpszClassName', c_char_p)]

class RECT(Structure):
    _fields_ = [('left', c_long),
                ('top', c_long),
                ('right', c_long),
                ('bottom', c_long)]

class PAINTSTRUCT(Structure):
    _fields_ = [('hdc', c_int),
                ('fErase', c_int),
                ('rcPaint', RECT),
                ('fRestore', c_int),
                ('fIncUpdate', c_int),
                ('rgbReserved', c_char * 32)]

class POINT(Structure):
    _fields_ = [('x', c_long),
                ('y', c_long)]
    
class MSG(Structure):
    _fields_ = [('hwnd', c_int),
                ('message', c_uint),
                ('wParam', c_int),
                ('lParam', c_int),
                ('time', c_int),
                ('pt', POINT)]

def ErrorIfZero(handle):
    if handle == 0:
        raise WinError
    else:
        return handle

def _createDiv(doc):
    div = doc.createElement('div')
    print div
    style = div.style
    print style
    #style2 = style.QueryInterface(MSHTML.IHTMLStyle2)
    #style3 = style.QueryInterface(MSHTML.IHTMLStyle3)
    style.position = 'absolute'
    print "pos", style.position
    style.top = 0
    print "top", style.top
    sys.stdout.flush()
    print "left before", style.left
    style.left = 0
    print "left", style.left
    style.overflow = 'scroll'
    print "overflow", style.overflow
    style.overflowX = 'hidden'
    print "overflowX", style.overflowX
    style.width = 300
    print "width", style.width
    style.height = 100
    print "height", style.height
    style.scrollbarBaseColor = '#3366CC'
    style.borderBottom = '2px solid black'
    style.scrollbarHighlightColor = '#99CCFF'
    style.scrollbarArrowColor = 'white'
    div.innerHTML = 'Hello'
    return div

#b = Dispatch('InternetExplorer.Application')
#b.Navigate('about:<h1 id=header>Hello</h1><iframe id=frm src="about:"></iframe>')
#b.Visible = 1
#doc1 = cast.IHTMLDocument2(b.Document)
#header = doc1.all.item('header')
#frm = doc1.all.item('frm')
#frm2 = doc1.frames('frm')
#doc2 = cast.IHTMLDocument2(frm2.document)
#div = doc2.createElement('div')
#cast.DispHTMLBody(doc2.body).appendChild(div)

#popup = cast.DispHTMLWindow2(doc1.parentWindow).createPopup()
#doc3 = cast.IHTMLDocument2(popup.document)
#body = cast.DispHTMLBody(doc3.body)
#div = _createDiv()

class EventSink(object):
    # some DWebBrowserEvents
    def OnVisible(self, this, *args):
        print "OnVisible", args

    def BeforeNavigate(self, this, *args):
        print "BeforeNavigate", args

    def NavigateComplete(self, this, *args):
        if self._loaded:
            return
        self._loaded = True
        print "NavigateComplete", this, args
        #pDoc = wrap(this)
        #print dir(pDoc)
        #sys.stdout.flush()
        return
        #div = _createDiv(doc2)
        #print div, div.document
        #doc2.body.appendChild(div)
        #cast.DispHTMLBody(doc2.body).appendChild(div)


    # some DWebBrowserEvents2
    def BeforeNavigate2(self, this, *args):
        print "BeforeNavigate2", args

    def NavigateComplete2(self, this, *args):
        print "NavigateComplete2", args

    def DocumentComplete(self, this, *args):
        print "DocumentComplete", args
        self._loaded()
        print doc
        #div = doc.createElement("div")
        #print div
        #style = div.style
        #print style
        #return

        div = _createDiv(doc)
        print "body", doc.body, doc.body.__instance__._iid_
        doc.body.appendChild(div)
        for fn in dir(doc.body):
            print fn
        h2 = doc.getElementsByTagName('h2')
        h2 = h2.item(0)
        print h2
        for fn in dir(h2):
            print "h2", fn
        print h2._iid_
        print doc._iid_
        print div._iid_
        print div.style._iid_

    def NewWindow2(self, this, *args):
        print "NewWindow2", args
        return
        v = cast(args[1]._.c_void_p, POINTER(VARIANT))[0]
        v.value = True

    def NewWindow3(self, this, *args):
        print "NewWindow3", args
        return
        v = cast(args[1]._.c_void_p, POINTER(VARIANT))[0]
        v.value = True

class Browser(EventSink):
    def __init__(self, application, appdir):
        EventSink.__init__(self)
        self.platform = 'mshtml'
        self.application = application
        self.appdir = appdir
        self.already_initialised = False
        self._loaded = False

        CreateWindowEx = windll.user32.CreateWindowExA
        CreateWindowEx.argtypes = [c_int, c_char_p, c_char_p, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int]
        CreateWindowEx.restype = ErrorIfZero

        # Create an instance of IE via AtlAxWin.
        atl.AtlAxWinInit()
        hInstance = kernel32.GetModuleHandleA(None)

        hwnd = CreateWindowEx(0,
                              "AtlAxWin",
                              win32con.NULL,
                              win32con.WS_OVERLAPPEDWINDOW |
                              win32con.WS_VISIBLE | 
                              win32con.WS_HSCROLL | win32con.WS_VSCROLL,
                              win32con.CW_USEDEFAULT,
                              win32con.CW_USEDEFAULT,
                              win32con.CW_USEDEFAULT,
                              win32con.CW_USEDEFAULT,
                              win32con.NULL,
                              win32con.NULL,
                              hInstance,
                              win32con.NULL)

        # Get the IWebBrowser2 interface for the IE control.
        self.pBrowserUnk = POINTER(IUnknown)()
        atl.AtlAxGetControl(hwnd, byref(self.pBrowserUnk))
        # the wrap call querys for the default interface
        self.pBrowser = wrap(self.pBrowserUnk)
        self.pBrowser.RegisterAsBrowser = True
        self.pBrowser.AddRef()

        self.conn = GetEvents(self.pBrowser, sink=self,
                        interface=SHDocVw.DWebBrowserEvents2)

        # Show Window
        windll.user32.ShowWindow(c_int(hwnd), c_int(win32con.SW_SHOWNORMAL))
        windll.user32.UpdateWindow(c_int(hwnd))

    def _alert(self, txt):
        self.get_prompt_svc().alert(None, "Alert", txt)

    def load_app(self):

        uri = self.application
        if uri.find(":") == -1:
            # assume file
            uri = 'file://'+os.path.abspath(uri)

	print "load_app", uri

        self.application = uri
        v = byref(VARIANT())
        self.pBrowser.Navigate(uri, v, v, v, v)


    def _addXMLHttpRequestEventListener(self, node, event_name, event_fn):
        
        listener = xpcom.server.WrapObject(ContentInvoker(node, event_fn),
                                            interfaces.nsIDOMEventListener)
        print event_name, listener
        node.addEventListener(event_name, listener, False)
        return listener

    def addEventListener(self, node, event_name, event_fn):
        
        listener = xpcom.server.WrapObject(ContentInvoker(node, event_fn),
                                            interfaces.nsIDOMEventListener)
        node.addEventListener(event_name, listener, True)
        return listener

    def mash_attrib(self, attrib_name):
        return attrib_name

    def _addWindowEventListener(self, event_name, event_fn):
        
        listener = xpcom.server.WrapObject(ContentInvoker(self.window_root,
                                                          event_fn),
                                            interfaces.nsIDOMEventListener)
        self.window_root.addEventListener(event_name, listener, True)
        return listener

    def getXmlHttpRequest(self):
        xml_svc_cls = components.classes[ \
            "@mozilla.org/xmlextras/xmlhttprequest;1"]
        return xml_svc_cls.createInstance(interfaces.nsIXMLHttpRequest)
        
    def getUri(self):
        return self.application

    def _loaded(self):

        print "loaded"

        if self.already_initialised:
            return
        self.already_initialised = True

        doc = _mshtml.wrap(self.pBrowser.Document)

        from __pyjamas__ import pygwt_processMetas, set_main_frame
        #from __pyjamas__ import set_gtk_module
        set_main_frame(self)
        #set_gtk_module(gtk)

        (pth, app) = os.path.split(self.application)
        if self.appdir:
            pth = os.path.abspath(self.appdir)
        sys.path.append(pth)

def MainWin(one_event):

    # Pump Messages
    msg = MSG()
    pMsg = pointer(msg)
    NULL = c_int(win32con.NULL)
    
    while windll.user32.GetMessageA( pMsg, NULL, 0, 0) != 0:

        windll.user32.TranslateMessage(pMsg)
        windll.user32.DispatchMessageA(pMsg)

        #print msg.message, msg.wParam, msg.lParam
        #if msg.message == 161: # win32con.WM_DESTROY:
        #    windll.user32.PostQuitMessage(0)

        if one_event:
            break

    return msg.wParam
    
class ContentInvoker:

    def __init__(self, node, event_fn):
        self._node = node
        self._event_fn = event_fn

    def handleEvent(self, event):
        self._event_fn(self._node, event, False)

global wv
wv = None

def is_loaded():
    return wv.already_initialised

def run(one_event=False, block=True):
    MainWin(one_event) # TODO: ignore block arg for now

def setup(application, appdir=None, width=800, height=600):

    global wv
    wv = Browser(application, appdir)

    while 1:
        if is_loaded():
            return
        run(one_event=True)
