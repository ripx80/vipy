#!/usr/bin/python3
# coding: utf8

import os
subs='subs'
mov='finish'
ml=os.listdir(mov)
for i in os.listdir(subs):
	if i+'.mp4' in ml:
		print('Add subtitle to movie: '+i)
		tl=os.listdir(subs+'/'+i)
		if len(tl) == 2:
			os.system('MP4Box -add %s/%s/de.srt:hdlr=subtl:lang=ger:group=2:layer=-1 -add %s/%s/en.srt:hdlr=subtl:lang=eng:group=3:layer=-1 %s/%s.mp4'%(subs,i,subs,i,mov,i))
		elif tl[0]=='de.srt':
			 os.system('MP4Box -add %s/%s/de.srt:hdlr=subtl:lang=ger:group=2:layer=-1 %s/%s.mp4'%(subs,i,mov,i))
		else:
			os.system('MP4Box -add %s/%s/en.srt:hdlr=subtl:lang=eng:group=2:layer=-1 %s/%s.mp4'%(subs,i,mov,i))
	
#MP4Box -add tt0080455/de.srt:hdlr=sbtl:lang=ger:group=2:layer=-1 tt0080455.mp4
# mplayer -identify -frames 0 finish/tt0844894.mp4 | grep 'AUDIO_ID' | tail -n1
