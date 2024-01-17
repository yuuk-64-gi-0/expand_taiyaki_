import pygame as pg
import pygame.locals as pglc
import os
import sys
import platform
import numpy as np
import pyaudio
import typing
import copy
import time
from typing import Union
from typing import Callable
from typing import Tuple as tyTuple
from typing import List as tyList
from typing import Dict as tyDict
import defcom

with open(defcom.defcomfile,"w",encoding='utf-8',newline='\n') as fw:
    for comkey in defcom.comkeys:
        fw.write("%s:%s\n" % (comkey,str(defcom.defcom[comkey])))

pickarg : Callable[[str],str] = lambda let:sys.argv[sys.argv.index(let)+1]

inf = float("inf")
if "-c" in sys.argv:
    commandfile = pickarg("-c")
else:
    commandfile = os.path.abspath("current.in")

if "-w" in sys.argv:
    windowtitle = pickarg("-w")
else:
    windowtitle = "Image window"
defcomfile = os.path.abspath("defcom.in")
imgdir = os.path.abspath("imgfiles")
MachineOS = platform.system()
comcheckinterval = 1

coordtype = typing.NewType("list[float,float]",typing.List[float])
Colortype = typing.NewType("tuple[int,int,int] | tuple[int,int,int,int]",typing.Tuple[int])
CLcodetype = typing.NewType("str:'#%02x%02x%02x'",str)

def CLcode2hex(CLcode : CLcodetype) -> Colortype:
    if len(CLcode.replace("#","")) == 3:
        trCL = "".join(list(map(lambda CLval:CLval * 2,CLcode.replace("#","")[:3])))
    else:
        trCL = CLcode.replace("#","")[:6]
    outtuple = (int(trCL[:2],16),int(trCL[2:4],16),int(trCL[4:],16))
    return outtuple

hex2floatCL :Callable[[Union[tyList[int],tyTuple[int]]],tyTuple[float]]= lambda CLhex:tuple(map(lambda x:x/255,CLhex))
float2hexCL :Callable[[Union[tyList[float],tyTuple[float]]],tyTuple[int]]= lambda CLflt:tuple(map(lambda x:int(min(255,max(0,x*255))),CLflt))
float2CLcode :Callable[[Union[tyList[float],tyTuple[float]]],CLcodetype] = lambda CLflt:"#" + "".join(list(map(lambda x:"%02x" % int(min(255,max(0,x*255))),CLflt)))
hex2CLcode :Callable[[Colortype],CLcodetype] = lambda CLhex:"#" + "".join(list(map(lambda x:"%02x" % int(min(255,max(0,x))),CLhex[:3])))
CLcode2float :Callable[[Colortype],Union[tyList[float],tyTuple[float]]] = lambda CLcode:hex2floatCL(CLcode)

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
    currentcom = comfile2dict(commandfile)
    curvals = [currentcom[key0] for key0 in comkeys]
except:
    currentcom = copy.deepcopy(defaultcom)
    curvals = copy.deepcopy(defvals)
valtypes = defcom.valtypes
lastcomcheck = time.time()

v2h_linear:typing.Callable[[float,float,float,float],float] = lambda vol,wflv,minh,maxh:minh+(maxh - minh) * min(1,max(0,vol)) * (1 - wflv * vol)
def v2h_sigmoid(vol : float,wflv : float,minh : float,maxh : float) -> float:
    cst = np.log(81)
    x = vol - 0.5
    sgm = (1/(1 + np.exp(-cst*x)) - 1/10) * 10 / 8
    return v2h_linear(sgm,wflv,minh,maxh)

v2h_dict = {
    "linear":v2h_linear,
    "sigmoidal":v2h_sigmoid
}

screen_fps = max(1,int(currentcom.get("image fps",60))) #240
audio_smp = 44100
audio_fps = int(audio_smp/(screen_fps+2))#int(1024 * 1)
audio_dpt = int(audio_smp/(screen_fps+2))#int(720 * 1)

def audiostop(audio, stream):
    stream.stop_stream()
    stream.close()
    audio.terminate()

def audiostart(audiochname : str):
    global audio_fps
    selectedch = defcom.audio_name2ch[audiochname]
    audio = pyaudio.PyAudio() 
    stream = audio.open(
        format = pyaudio.paInt16,
        rate = audio_smp,
        channels = 1, 
        input_device_index = selectedch,
        input = True, 
        frames_per_buffer = audio_fps)#1024
    return audio, stream

def audiochange(audiochname : str):
    global audio
    global stream
    audiostop(audio, stream)
    audio, stream = audiostart(audiochname)


pg.init()
tempfont = pg.font.SysFont(None,200)
mainwin_size = (max(1,int(currentcom["window width"])),max(1,int(currentcom["window height"])))
mainwin_bgcl = currentcom["bg color"]
mainwin = pg.display.set_mode(mainwin_size)
pg.display.set_caption(windowtitle)
try:
    imgsur = pg.image.load(currentcom["image file"]).convert_alpha()
except:
    imgsur = tempfont.render("?",True,"#FFFFFF","#FF0000")
bfupdatearea = mainwin.fill(mainwin_bgcl,special_flags=pg.BLEND_RGBA_MULT)
mainwin.convert_alpha()
pg.display.update()
(audio,stream) = audiostart(currentcom["channel"])

def getvol():
    global stream
    global currentcom
    try:
        wavedata = stream.read(audio_dpt)
        audiodata = np.frombuffer(wavedata, dtype='int16')#datastock(np.frombuffer(wavedata, dtype='int16'),ppt) * winfunc
    except:
        audiodata = np.zeros(audio_dpt,dtype='int16')
        global audio
        (audio,stream) = audiostart(currentcom["channel"])
        print("audio restarted")
    purevol = max(abs(audiodata))#audiodata.std()
    allvol = purevol / (2 ** 15) * float(currentcom["gain amp.%"]) / 100
    return allvol

def drawimg(img_H_scale : float):
    global currentcom
    global mainwin
    global mainwin_size
    global bfupdatearea
    global imgsur
    resized_imgsur = pg.transform.scale_by(imgsur,(float(currentcom["img W_scale"]),img_H_scale)).convert_alpha()
    pos = (int(currentcom["pos x"]),mainwin_size[1]-int(currentcom["pos y"])-resized_imgsur.get_height())
    newupdatearea = mainwin.blit(resized_imgsur,pos,special_flags=pg.BLEND_PREMULTIPLIED)
    updatearea = pg.Rect.union(bfupdatearea,newupdatearea)
    bfupdatearea = newupdatearea
    return {"renewedRects":updatearea}

def getdiff():
    global currentcom
    global screen_fps
    global audio_dpt
    global audio_fps
    newcomdict = comfile2dict(commandfile)
    diffterms = list(filter(lambda key1:currentcom[key1] != newcomdict[key1],comkeys))
    currentcom = copy.deepcopy(newcomdict)
    if "channel" in diffterms:
        audiochange(currentcom["channel"])
    if "image file" in diffterms:
        global imgsur
        try:
            imgsur = pg.image.load(currentcom["image file"]).convert_alpha()
        except:
            imgsur = tempfont.render("?",True,"#FFFFFF","#FF0000")
    if bool({"window height","window width"} & set(diffterms)):
        global mainwin
        global mainwin_size
        mainwin_size = (max(1,int(currentcom["window width"])),max(1,int(currentcom["window height"])))
        mainwin = pg.display.set_mode(mainwin_size)
        pg.display.update()
    if "bg color" in diffterms:
        global mainwin_bgcl
        mainwin_bgcl = currentcom["bg color"]
        pg.display.update()
    if "display" in diffterms:
        global bfupdatearea
        pg.display.update(bfupdatearea)
    if "image fps" in diffterms:
        screen_fps = max(1,int(currentcom.get("image fps",screen_fps)))
        audio_fps = int(audio_smp/(screen_fps+2))
        audio_dpt = int(audio_smp/(screen_fps+2))
        audiochange(currentcom["channel"])

loop1 = True
fpsc_sec = int(time.time())
lastrendtime = time.time()
framec = 0

while loop1:
    now_time = time.time()
    if now_time - lastrendtime >= 0.9/screen_fps:
        lastrendtime = now_time
        allvol = getvol()
        wflv = 0
        print("\rVolume: %3d" % (int(allvol * 100)),"%",end="")
        imgh_scale = v2h_dict[currentcom["expand mode"]](allvol,wflv,float(currentcom["min img H_scale"]),float(currentcom["max img H_scale"]))
        mainwin.fill(mainwin_bgcl)
        #renewedRectlist = []
        
        if eval(currentcom["display"].capitalize()):
            renewedRect = drawimg(imgh_scale)["renewedRects"]
        else:
            renewedRect = bfupdatearea
            bfupdatearea = pg.Rect((0,0,0,0))
        #list(map(pg.display.update,renewedRectlist))
        #pg.display.update(renewedRect)
        pg.display.update()
        for event in pg.event.get():
            if (event.type == pglc.QUIT) or (event.type == pglc.KEYDOWN and event.key == pglc.K_ESCAPE):
                loop1 = False
                pg.quit()

        nfpssec = int(time.time())
        if nfpssec != fpsc_sec:
            print(" fps: %d    " % framec,end="")
            framec = 1
            fpsc_sec = nfpssec
        else:
            framec += 1
    else:
        time.sleep(0.1/screen_fps)
    if now_time - lastcomcheck >= comcheckinterval:
        getdiff()
        lastcomcheck = now_time