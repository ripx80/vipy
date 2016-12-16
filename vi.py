#!/usr/bin/python2.7

#encoding:utf-8

__author__="Ripx80"
__date__="27.03.2013"
__copyright__="Copyleft"
__version__="1.0"

import os
import argparse
import re
from subprocess import call,check_output
import logging
#media-video/ffmpeg threads zlib encode x264 hardcoded-tables truetype fdk libass

#save crop in file for later use!

class Log(object):
    def __init__(self,lvl='WARNING',frmt='%(asctime)s %(levelname)s:%(message)s',dfmt='%d-%m-%Y %H:%M',logfile=None):
        logging.basicConfig(filename=logfile,level=lvl,format=frmt,datefmt=dfmt)
        log = logging.getLogger(__name__)
        log.addHandler(logging.NullHandler())
        self.log=log

    def getLevel(self):
        return ['CRITICAL','ERROR','WARNING','INFO','DEBUG']


def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def check_env(commands):
    for prog in commands:
        fpath, fname = os.path.split(commands[prog])
        if not is_exe(commands[prog]):
            print 'Programm not found: '+commands[prog]
            exit(1)

def create_dirs(struct):
    for i in struct.keys():
        if not os.path.isdir(struct[i]):
            os.makedirs(struct[i])


class Extractor(object):
    def __init__(self,commands,movfile,raw,preview,copy,force,encaudio,oaudio,ovideo,osub):
        self.commands=commands
        self.setMovfile(movfile)
        self.streamMap={'0:0':'und','0:1':'ger','0:2':'eng','eng':'en','ger':'de'}
        #self.,audioAllow=['aac']
        self.raw='%s/%s'%(raw,self.movname)
        self.preview=preview
        self.copy=copy
        self.force=force
        self.encaudio=encaudio
        self.oaudio=oaudio
        self.ovideo=ovideo
        self.osub=osub
        self.scanStreams()

    def setCrop(self):
        log.debug('croping detection')
        #if no crop detected use -f15 in cut command. mplayer v1

        #log.debug('find preview crop')
        crop=check_output(self.commands['ffmpeg']+' -y -i "%s" -vf cropdetect -t 100 -ss 600 -an -f rawvideo /dev/null 2>&1 | grep crop | tail -n1 | cut -f14 -d\ '%(self.movfile,),shell=True).replace("\n", "")
        if len(crop)<=0:
            log.error('can not crop detection from file: '+self.movfile)
            log.error('with command:'+self.commands['ffmpeg']+' -y -i "%s" -vf cropdetect -t 100 -ss 600 -an -f rawvideo /dev/null 2>&1 | grep crop | tail -n1 | cut -f15 -d\ '%(self.movfile,))
            raise RuntimeError('can not crop detection from file: '+self.movfile)
        else:
            self.crop=crop

    def scanStreams(self):
        log.info('scanning maps')
        tmp={'Video':[],'Audio':[],'Subtitle':[]}

        for i in check_output(self.commands['ffmpeg']+' -i "%s" 2>&1 | grep "Stream" | sed -e \'s/^[ \t]*//\''%(self.movfile,),shell=True).split('\n'):
            if len(i)<3:
                continue
            try:
                m=re.search('Stream #(\d:\d)(\(\w+\))?: (Audio|Video|Subtitle): (\w+)', i)
                if m.group(2) and (m.group(2)[1:-1] != 'und'):
                    tmp[m.group(3)].append([m.group(1),m.group(2)[1:-1],m.group(4)])
                else:
                    #get lang from mapping
                    tmp[m.group(3)].append([m.group(1),self.streamMap[m.group(1)],m.group(4)])
            except AttributeError:
                log.error('canot find map in line: '+i+' in movie: '+self.movfile)
                exit(1)
        self.streams=tmp

    def createMovdir(self):
        if not os.path.isdir(self.raw):
            os.makedirs(self.raw)

    def extract(self):
        self.createMovdir()
        if self.oaudio:
            self.extract_m4a()
        elif self.ovideo:
            self.extract_m4v()
        elif self.osub:
            self.extract_srt()
        else:
            self.extract_m4v()
            self.extract_m4a()
            self.extract_srt()
        return self.raw

    def extract_m4v(self):
        self.setCrop()
        log.debug('extract video stream')

        if self.preview:
            codec='-c:v libx264 -preset medium -crf 23 -tune film'
        elif self.copy or self.streams['Video'][0][2] =='h264' and not self.force:
            codec='-c:v copy'
        else:
            codec='-c:v libx264 -preset slower -crf 20 -tune film'
        #print self.commands['ffmpeg']+' -y -sn -an -i "%s" -map %s -vf %s %s "%s/main.m4v"'%(self.movfile,self.streams['Video'][0][0],self.crop,codec,self.raw)
        call(self.commands['ffmpeg']+' -y -sn -an -i "%s" -map %s %s %s "%s/main.m4v"'%(self.movfile,self.streams['Video'][0][0],((codec != '-c:v copy') and (['-vf '+self.crop]) or (' '))[0],codec,self.raw),shell=True);

        log.debug(self.commands['ffmpeg']+' -y -sn -an -i "%s" -map %s %s %s "%s/main.m4v"'%(self.movfile,self.streams['Video'][0][0],((codec != '-c:v copy') and (['-vf '+self.crop]) or (' '))[0],codec,self.raw))

    def extract_m4a(self):
        for i in self.streams['Audio']:
            log.debug('find not allowed audio codec: %s. converting..'%(i[2],))
            #print self.commands['ffmpeg']+' -i "%s" -acodec libfdk_aac -map %s -ac 2 -b:a 128k -vn -y "%s/%s.m4a"'%(self.movfile,i[0],self.raw,self.streamMap[i[1]])
            if self.encaudio:
                codec='-ac 2 -b:a 128k'
            else:
                codec=''
            #print self.commands['ffmpeg']+' -i "%s" -acodec libfdk_aac -map %s %s -vn -y "%s/%s.m4a"'%(self.movfile,i[0],codec,self.raw,self.streamMap[i[1]])
            call(self.commands['ffmpeg']+' -i "%s" -acodec libfdk_aac -map %s %s -vn -y "%s/%s.m4a"'%(self.movfile,i[0],codec,self.raw,self.streamMap[i[1]]),shell=True)

    def extract_srt(self):
        for i in self.streams['Subtitle']:
            log.debug('extracting subtitles to srt files')
            log.debug(self.commands['ffmpeg']+' -i "%s" -scodec srt -map %s -an -vn -y "%s/%s.srt"'%(self.movfile,i[0],self.raw,i[1]))
            call(self.commands['ffmpeg']+' -i "%s" -scodec srt  -map %s -an -vn -y "%s/%s.srt"'%(self.movfile,i[0],self.raw,self.streamMap[i[1]]),shell=True)


    def checkPath(self,fpath):
        if not os.path.exists(fpath):
            log.error('Can not find file: '+fpath)
            raise IOError('Can not find file: '+fpath)
        else:
            return True

    def setMovfile(self,ffile):
        if self.checkPath(ffile):
            self.movfile=ffile
            self.movname=os.path.splitext(os.path.basename(self.movfile))[0]


class Packer(object):

    def __init__(self,commands,raw,results,delraw):
        self.commands=commands
        self.results=results
        self.raw=raw
        self.delraw=delraw
        self.movname=os.path.basename(raw)

    def scanDir(self):
        dirs=os.listdir(self.raw)
        m4a,m4v,srt=[],[],[]
        for i in dirs:
            ext=os.path.splitext(i)[1][1:]
            if ext == 'm4a':
                m4a.append(i)
            elif ext == 'm4v':
                m4v.append(i)
            elif ext == 'srt':
                srt.append(i)
            else:
                continue
        self.files={'m4v':m4v,'m4a':m4a,'srt':srt}
        print self.files

    def pack(self):
        self.scanDir()
        maps,meta,cmd='','',''
        mapcnt,acnt,srtcnt=0,0,0
        for i in self.files['m4v']:
            cmd+=' -i "%s/%s"'%(self.raw,i)
            maps+='-map %d:0'%(mapcnt,)
            mapcnt+=1
        for i in self.files['m4a']:
            maps+=' -map %d:0'%(mapcnt,)
            cmd+=' -i "%s/%s"'%(self.raw,i)
            if i[0:2] == 'de':
                meta+=' -metadata:s:a:%d language=ger'%(acnt,)
            elif i[0:2]=='en':
                meta+=' -metadata:s:a:%d language=eng'%(acnt,)
            else:
                log.error('found unkown audio language')
            mapcnt+=1
            acnt+=1

        for i in self.files['srt']:
            maps+=' -map %d:0'%(mapcnt,)
            cmd+=' -i "%s/%s"'%(self.raw,i)
            if i[0:2] == 'de':
                meta+=' -metadata:s:s:%d language=ger'%(srtcnt,)
            elif i[0:2]=='en':
                meta+=' -metadata:s:s:%d language=eng'%(srtcnt,)
            else:
                log.error('found unkown subtitle language')
            mapcnt+=1
            srtcnt+=1
        #print '%s%s %s%s -vcodec copy -acodec copy -scodec mov_text -y "%s/%s.mp4"'%(self.commands['ffmpeg'],cmd,maps,meta,self.results,self.movname)
        call('%s%s %s%s -vcodec copy -acodec copy -scodec mov_text -y "%s/%s.mp4"'%(self.commands['ffmpeg'],cmd,maps,meta,self.results,self.movname),shell=True)

        if self.delraw:
            import shutil
            shutil.rmtree(self.raw)


##set command line parser###
##default##
parser = argparse.ArgumentParser(description='video converter in python')
parser.add_argument('--version', action='version', version='%(prog)s '+__version__+'. testet with mplayer-1.2')
parser.add_argument('-v','--verbose',help='set programm in debug mode',action='count',dest='verbose',default=False)
##args###
parser.add_argument('-d','--destination',help='set the root directory for structing files',default='./vipy',dest='root')
parser.add_argument('-dr','--delraw',help='delete the raw files after encoding',action='count',default=False,dest='delraw')
parser.add_argument('-pr','--preview',help='encode the m4v codec with medium qly',action='count',default=False,dest='preview')
parser.add_argument('-c','--copy',help='copy the video stream',action='count',default=False,dest='copy')
parser.add_argument('-f','--force',help='force to encode video stream',action='count',default=False,dest='force')
parser.add_argument('-ca','--caudio',help='encode audio stream (2 Channel)',action='count',default=False,dest='encaudio')
parser.add_argument('-oa','--audio',help='encode only the audio streams from movie file',action='count',default=False,dest='oaudio')
parser.add_argument('-ov','--video',help='encode only the video stream from movie file',action='count',default=False,dest='ovideo')
parser.add_argument('-os','--subtitles',help='encode only the subtitle streams from movie file',action='count',default=False,dest='osub')
##modes##
parser.add_argument('-e','--extract',help='extract raw files from movie',action='count',default=False,dest='extract')
parser.add_argument('-m','--merge',help='merge raw files together',action='count',default=False,dest='merge')

modes = parser.add_mutually_exclusive_group(required=True)
modes.add_argument('-lm','--loopmode',help='work over a directory with movie files. Example: ./src/example.avi or with pack option ./raw/moviename/',dest='loopdir')
modes.add_argument('-sm','--singlemode',help='take only one specified movie',dest='single')
args = parser.parse_args()

#definitions
commands={'ffmpeg':'/usr/bin/ffmpeg'}
struct={'results':'./vipy/results','raw':'./vipy/raw'}
check_env(commands) #checking environment
create_dirs(struct) #create structure


if args.verbose:
    log=Log('DEBUG').log
else:
    log=Log('INFO').log

packraw=False

if args.loopdir:
    args.loopdir=os.path.abspath(args.loopdir)
    dirs=os.listdir(args.loopdir)
    for i in dirs:
        if args.extract:
            ext=Extractor(commands,'%s/%s'%(args.loopdir,i),'%s/raw'%(args.root,),args.preview,args.copy,args.force,args.encaudio,args.oaudio,args.ovideo,args.osub)
            packraw=ext.extract()

        if args.merge:
            if packraw:
                pack=Packer(commands,packraw,'%s/results'%(args.root,),args.delraw)
            else:
                pack=Packer(commands,'%s/%s'%(args.loopdir,i),'%s/results'%(args.root,),args.delraw)
            pack.pack()

elif args.single:
    args.single=os.path.abspath(args.single)
    if args.extract:
        ext=Extractor(commands,args.single,'%s/raw'%(args.root,),args.preview,args.copy,args.force,args.encaudio,args.oaudio,args.ovideo,args.osub)
        packraw=ext.extract()

    if args.merge:
        if packraw:
            pack=Packer(commands,packraw,'%s/results'%(args.root,),args.delraw)
        else:
            pack=Packer(commands,args.single,'%s/results'%(args.root,),args.delraw)
        pack.pack()
