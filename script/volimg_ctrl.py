import tkinter
import tkinter.ttk as ttk
import os
import platform
import typing
import defcom
import copy
import shutil
import atexit
import numpy as np
import pyaudio
from PIL import Image, ImageTk
import filemng as fm 
import subprocess as sp
from datetime import datetime as dtime

with open(defcom.defcomfile,"w",encoding='utf-8',newline='\n') as fw:
    for comkey in defcom.comkeys:
        fw.write("%s:%s\n" % (comkey,str(defcom.defcom[comkey])))

thispid = os.getpid()

inf = float("inf")
#commandfile = os.path.abspath("current.in")
commandfile_pre_list = sorted(filter(lambda name:name.startswith("current_"),os.listdir()))
commandfile = os.path.abspath("current_%s.in" % (dtime.now().strftime("%Y%m%d%H%M%S") + str(thispid)))
defcomfile = os.path.abspath("defcom.in")
configdir = os.path.abspath("config_files")
MachineOS = platform.system()
fontname = 'Yu Gothic'
print("OS:",MachineOS)
tpalafter = None
ctiid = None

def audiostop(audio, stream):
    stream.stop_stream()
    stream.close()
    audio.terminate()

def windowdestroy():
    global app_0
    #global prc_imgwin
    global commandfile
    #if prc_imgwin.poll() is None:
    for prc_imgwin in prc_imgwin_list:
        if prc_imgwin.poll() is None:
            prc_imgwin.kill()
    if not(tpalafter is None):
        app_0.after_cancel(tpalafter)
    if not(ctiid is None):
        app_0.after_cancel(ctiid)
    app_0.destroy()
    print("windowdestroy")
    if commandfile.endswith("_s.in"):
        os.remove(commandfile)
    else:
        os.rename(commandfile,commandfile.replace(".in","_e.in"))
    exit()

#atexit.register(windowdestroy)

def typecheck(val : str,truetype : type):
    if truetype == bool and not(val.capitalize() in ["True","False"]):
        return (False,"must be True or False")
    elif truetype == float and not(val.replace("-","").replace(".","").replace("_","").isnumeric()):
        return (False,"must be float or integer number")
    elif truetype == int and not(val.replace("-","").replace("_","").isnumeric()):
        return (False,"must be integer number")
    elif truetype == os.PathLike and not(os.path.isfile(val)):
        return (False,"not found %s" % val)
    elif truetype == defcom.colortype and not(defcom.iscolortype(val)):
        return (False,"must be color_name or color_code(like #ffffff)")
    elif truetype == defcom.expandtype and not(defcom.isexpandtype(val)):
        return (False,"must be " + "|".join(defcom.expandmodes))
    elif truetype == defcom.audiochnametype and not(defcom.isaudiochnametype(val)):
        return (False,"must be audio channel name")
    else:
        return (True,"")

def comfile2dict(comfile : os.PathLike) -> dict:
    with open(comfile,"r",newline="\n",encoding='utf-8') as fr:
        fileval = fr.read().splitlines()
    outdict = {}
    for comval in fileval:
        if comval:
            outdict[comval[:comval.index(":")]] = comval[comval.index(":")+1:]
    return outdict


defaultcom = comfile2dict(defcomfile)
comkeys = defcom.comkeys
defvals = [defaultcom[key0] for key0 in comkeys]
try:
    commandfile_pre = commandfile_pre_list[-1]
    currentcom = comfile2dict(commandfile_pre)
    curvals = [currentcom[key0] for key0 in comkeys]
    shutil.copy(commandfile_pre,commandfile)
    if commandfile_pre.endswith("_e.in"):
        os.remove(commandfile_pre)
        del commandfile_pre_list[-1]
    else:
        os.rename(commandfile,commandfile.replace(".in","_s.in"))
        commandfile = commandfile.replace(".in","_s.in")
except:
    currentcom = copy.deepcopy(defaultcom)
    curvals = copy.deepcopy(defvals)
    shutil.copy(defcomfile,commandfile)
valtypes = defcom.valtypes

ctrlwinwidth = 480
ctrlwinheight = 800
app_0 = tkinter.Tk()
#app_0.iconphoto(True,tkinter.PhotoImage(file=icofilename))
app_0.geometry("%dx%d" % (ctrlwinwidth,ctrlwinheight))
app_0.title("Controller %d" % len(commandfile_pre_list))

imgwinwidth = int(currentcom["window width"])
imgwinheight = int(currentcom["window height"])
#app_1 = tkinter.Toplevel()

comkeylabels :typing.List[tkinter.Label]= []
for ind0,comkey in enumerate(comkeys):
    comkeylabels.append(tkinter.Label(
        app_0,font=(fontname,15),text=f"{comkey}({valtypes[ind0].__name__})",anchor=tkinter.E,
        justify='right',background="#ffffff",width=18))
    comkeylabels[-1].place(x=10,y=50+40*ind0)

alertlabel=tkinter.Label(app_0,font=(fontname,15),text="",justify='left',anchor=tkinter.W,background="#f0f0f0",width=36,wraplength=(ctrlwinwidth-20))
alertlabel.place(x=10,y=50+40*len(comkeys))

#comvale-ntries :typing.List[tkinter.Entry] = []

def filename2ent(ent : tkinter.Entry):
    filepath = fm.fileselect()
    filename = os.path.basename(filepath)
    if not(filename in os.listdir()):
        shutil.copy(filepath,os.path.join(os.path.dirname(__file__),filename))
    ent.config(state="normal")
    ent.delete(0,tkinter.END)
    ent.insert(tkinter.END,filename)
    ent.config(state="readonly")

comvalwidgets = []
for ind1,comkey in enumerate(comkeys):
    #defval = defaultcom[comkey] 
    curval = currentcom[comkey]
    if valtypes[ind1] == bool:
        comvalwidgets.append(ttk.Combobox(
            app_0,font=(fontname,14),width=18,background='#f0f0f0',values=("True","False")))
        comvalwidgets[-1].set(str(curval))
    elif valtypes[ind1] == int:
        comvalwidgets.append(ttk.Spinbox(
            app_0,font=(fontname,14),width=20,background='#f0f0f0',from_=-inf,to=inf,increment=1))
        comvalwidgets[-1].set(int(curval))
    elif valtypes[ind1] == os.PathLike:
        comvalwidgets.append(tkinter.Entry(
            app_0,font=(fontname,14),width=20,bg='#f0f0f0'))
        comvalwidgets[ind1].insert(tkinter.END,curval)
        comvalwidgets[ind1].bind("<Button-1>",lambda event:filename2ent(event.widget))
        comvalwidgets[ind1].configure(state="readonly")
    elif valtypes[ind1] == defcom.expandtype:
        comvalwidgets.append(ttk.Combobox(
            app_0,font=(fontname,14),width=18,background='#f0f0f0',values=tuple(defcom.expandmodes)))
        comvalwidgets[-1].set(str(curval))
    elif valtypes[ind1] == defcom.audiochnametype:
        comvalwidgets.append(ttk.Combobox(
            app_0,font=(fontname,14),width=18,background='#f0f0f0',values=tuple(defcom.audio_names)))
        comvalwidgets[-1].set(str(curval))
    else:
        comvalwidgets.append(tkinter.Entry(
            app_0,font=(fontname,14),width=20,bg='#f0f0f0'))
        comvalwidgets[ind1].insert(tkinter.END,curval)
    comvalwidgets[ind1].place(x=ctrlwinwidth//2,y=50+40*ind1)

def file2ent(comfile : os.PathLike):
    global app_0
    global comvalwidgets
    comdict = comfile2dict(comfile)
    for ind3,comkey in enumerate(comkeys):
        if valtypes[ind3] in [bool,defcom.expandtype]:
            comvalwidgets[ind3].set(str(comdict[comkey]))
        elif valtypes[ind3] == int:
            comvalwidgets[ind3].set(int(comdict[comkey]))
        elif valtypes[ind3] == os.PathLike:
            comvalwidgets[ind3].configure(state="normal")
            comvalwidgets[ind3].delete(0,tkinter.END)
            comvalwidgets[ind3].insert(tkinter.END,comdict[comkey])
            comvalwidgets[ind3].configure(state="readonly")
        else:
            comvalwidgets[ind3].delete(0,tkinter.END)
            comvalwidgets[ind3].insert(tkinter.END,comdict[comkey])

def ent2file():
    outtextlines = []
    for ind2,comkey in enumerate(comkeys):
        comval = str(comvalwidgets[ind2].get())
        outtextlines.append(comkey + ":" + comval)
    outtext = "\n".join(outtextlines)
    with open(commandfile,"w",encoding='utf-8',newline="\n") as fw:
        fw.write(outtext)

def ent2file_user(dstpath : os.PathLike):
    outtextlines = []
    for ind2,comkey in enumerate(comkeys):
        comval = str(comvalwidgets[ind2].get())
        outtextlines.append(comkey + ":" + comval)
    outtext = "\n".join(outtextlines)
    with open(dstpath,"w",encoding='utf-8',newline="\n") as fw:
        fw.write(outtext)

def getents():
    outlist = []
    for ind2 in range(len(comkeys)):
        outlist.append(str(comvalwidgets[ind2].get()))
    return outlist

def getwindowproperty():
    global app_0
    [nowwidth,nowheight,posx,psoy] = list(map(int,app_0.geometry().replace("x","+").split("+")))
    return {"width":nowwidth,"height":nowheight,"position":[posx,psoy]}

diff_terms : typing.Dict[str,typing.Any] = {}
def monitorentry():
    global comvalwidgets
    global app_0
    global tpalafter
    global alertlabel
    global diff_terms
    global currentcom
    tpalafter = app_0.after(500,monitorentry)
    entrylist = getents()
    filedict = comfile2dict(commandfile)
    filevals = [filedict[key3] for key3 in comkeys]
    alerttext = ""
    diff_flag = False
    for ind4,nowent in enumerate(entrylist):
        valuealert = typecheck(nowent,valtypes[ind4])
        if not(valuealert[0]):
            #comvalwidgets[ind4].configure(background='#ff8080')
            comkeylabels[ind4].configure(background='#ff8080')
            alerttext += comkeys[ind4] +" : "+valuealert[1] + "\n"
        elif nowent != filevals[ind4]:
            comkeylabels[ind4].configure(background='#ffc080')
            #alerttext += comkeys[ind4] +" : not exported\n"
            diff_flag = True
            diff_terms[comkeys[ind4]] = nowent
        else:
            comkeylabels[ind4].configure(background='#ffffff')
    alertlabel["text"] = alerttext
    if diff_flag:
        ent2file()
        currentcom = comfile2dict(commandfile)

monitorentry()







wzcount = 0
nwzcount = 0
def catchwinzombie():
    global app_0
    global swpid
    global wzcount
    global nwzcount
    funcinterval = 1000
    winpro = getwindowproperty()
    if winpro["width"] == 1 and winpro["height"] == 1:
        wzcount += 1
        nwzcount = 0
    else:
        nwzcount += 1
        wzcount = 0
    if wzcount > 5:
        print("Zombie window may have existed. The process will be killed in %d seconds." % (11-wzcount),end="\r")
    if wzcount > 10:
        try:
            windowdestroy()
        except:
            pass
        exit()
    if nwzcount < 10:
        swpid = app_0.after(funcinterval,catchwinzombie)
catchwinzombie()

#prc_imgwin = sp.Popen("python3 imgwin.py -c %s -w %s" % (os.path.basename(commandfile),'"Image window %d"' % len(commandfile_pre_list)))
prc_imgwin_list = [sp.Popen("python3 imgwin.py -c %s -w %s" % (os.path.basename(commandfile),'"Image window %d"' % len(commandfile_pre_list)))]
def addimgwin():
    global prc_imgwin_list
    prc_imgwin_list.append(sp.Popen("python3 imgwin.py -c %s -w %s" % (os.path.basename(commandfile),'"Image window %d"' % len(commandfile_pre_list))))

def catchterminatedimgwin():
    global app_0
    #global prc_imgwin
    global prc_imgwin_list
    global ctiid
    funcinterval = 1000
    ctiid = app_0.after(funcinterval,catchterminatedimgwin)
    if set(map(lambda prc:type(prc.poll()),prc_imgwin_list)) == {int}:#type(prc_imgwin.poll()) == int:
        try:
            windowdestroy()
        except Exception as e:
            print("abnormal terminated with")
            print(e)
            exit()
catchterminatedimgwin()


def LFLTvolume(audiodata : np.ndarray, Lfrq : int, Hfrq : int):
    spct = np.fft.fft(audiodata,norm="ortho")
    freq = abs(np.fft.fftfreq(len(audiodata)))
    fltarray = (freq >= Lfrq) * (freq <= Hfrq)
    flteddata = np.fft.ifft(spct * fltarray).real.astype(int)
    return flteddata.std() / (2 ** 15)


btn_read_cr = tkinter.Button(app_0,text="add Image window",font=(fontname,10),command=addimgwin)
btn_read_cr.place(x=10,y=10)
btn_read_cr = tkinter.Button(app_0,text="read config",font=(fontname,10),command=lambda:file2ent(fm.fileselect(".in",configdir)))
btn_read_cr.place(x=160,y=10)
btn_write_cr = tkinter.Button(app_0,text="export config",font=(fontname,10),command=lambda:ent2file_user(fm.filesave(".in",configdir)))
btn_write_cr.place(x=264,y = 10)
btn_read_def = tkinter.Button(app_0,text="read default",font=(fontname,10),command=lambda:file2ent(defcomfile))
btn_read_def.place(x=379,y = 10)



print("Window ready")
app_0.protocol("WM_DELETE_WINDOW", windowdestroy)
app_0.mainloop()