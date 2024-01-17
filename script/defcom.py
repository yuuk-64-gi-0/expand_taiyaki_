import os
import re
import typing
import webcolors as wc
import pyaudio

expandmodes = ["linear","sigmoidal"]
expandtype = typing.NewType("list",str)
colortype = typing.NewType("hex colorcode",str)
colornames = wc.CSS21_NAMES_TO_HEX.keys() | wc.CSS2_NAMES_TO_HEX.keys() | wc.CSS3_NAMES_TO_HEX.keys() | wc.HTML4_NAMES_TO_HEX.keys()
colorcode_re = re.compile("^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")

audio = pyaudio.PyAudio()
audio_name2ch :typing.Dict[str,int]= {}
for ch in range(audio.get_device_count()):
    if (audio.get_device_info_by_index(ch)['hostApi'] == 0) and (audio.get_device_info_by_index(ch)['maxInputChannels'] != 0):
        channelname = audio.get_device_info_by_index(ch)['name']
        try:
            audio_name2ch[channelname.encode("shift-jis").decode("utf-8")] = ch
        except:
            audio_name2ch[channelname] = ch
        
audio_names = list(audio_name2ch.keys())
audiochnametype = typing.NewType("input device",str)

defcomfile = os.path.abspath("defcom.in")
comkeys =  ["channel"      ,"gain amp.%","image file"        ,"display","pos x","pos y","img W_scale","min img H_scale","max img H_scale","image fps","expand mode","window height","window width","bg color"]
valtypes = [audiochnametype,float       ,os.PathLike         ,bool     ,int    ,int    ,float        ,float            ,float            ,int        ,expandtype   ,int            ,int           ,colortype]
comvals =  [audio_names[1] ,100         ,"sweets_taiyaki.png",True     ,130    ,0      ,0.3          ,0.3              ,0.9              ,30         ,"linear"     ,500            ,480           ,"#00FF00"]
defcom = dict(zip(comkeys,comvals))

isexpandtype : typing.Callable[[str],bool] = lambda checkstr:(checkstr in expandmodes)
iscolortype : typing.Callable[[str],bool] = lambda checkstr:bool(colorcode_re.match(checkstr)) or (checkstr in colornames)
isaudiochnametype : typing.Callable[[str],bool] = lambda checkstr:(checkstr in audio_names)

"""
with open(defcomfile,"w",encoding='utf-8',newline='\n') as fw:
    for comkey in comkeys:
        fw.write("%s:%s\n" % (comkey,str(defcom[comkey])))
"""