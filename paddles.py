#!/usr/bin/env python3
"""Original offline fullscreen Pong. Keyboard taps glide briefly for SSH play."""
import curses,json,math,os,random,time

try:
    import pi18n
except ImportError:
    pi18n = None
from arcade import DEFAULT_STRINGS
from pathlib import Path
from ui import put,run
VERSION='1.1.0'
LEVELS={'easy':(13,10,.35),'normal':(19,17,.16),'hard':(26,24,.08)}
SCORES=Path.home()/'.local/share/arcadewisp/paddle-scores.json'
class Pong:
 def __init__(self,w,h,rng=None,difficulty='normal',two=False,mode='classic'):
  self.w=w;self.h=h;self.rng=rng or random.Random();self.difficulty=difficulty;self.two=two;self.mode=mode;self.elapsed=0;self.score=[0,0];self.left=self.right=h/2;self.rally=0;self.best=0;self.ai_target=h/2;self.ai_clock=0;self.serve=.8;self.reset()
 def reset(self):
  self.x=self.w/2;self.y=self.h/2;speed=LEVELS[self.difficulty][0];self.vx=self.rng.choice((-speed,speed));self.vy=self.rng.uniform(-7,7);self.serve=.8;self.rally=0
 def step(self,dt,move=0,rightmove=0):
  dt=min(.08,max(0,dt));speed,ai_speed,reaction=LEVELS[self.difficulty]
  self.left=max(3,min(self.h-4,self.left+move*30*dt))
  if self.two:self.right=max(3,min(self.h-4,self.right+rightmove*30*dt))
  else:
   self.ai_clock+=dt
   if self.ai_clock>=reaction:self.ai_clock=0;self.ai_target=self.y+self.rng.uniform(-1.8,1.8)
   delta=self.ai_target-self.right;self.right=max(3,min(self.h-4,self.right+max(-ai_speed*dt,min(ai_speed*dt,delta))))
  if self.serve>0:self.serve=max(0,self.serve-dt);return
  self.elapsed+=dt
  if self.mode=='sprint':self.vx=math.copysign(min(speed*2,abs(self.vx)+dt*.25),self.vx)
  # Small substeps prevent fast balls skipping the paddle plane.
  steps=max(1,math.ceil(abs(self.vx)*dt/.5));tick=dt/steps
  for _ in range(steps):
   prev=self.x;self.x+=self.vx*tick;self.y+=self.vy*tick
   if self.mode=='gate' and ((prev<self.w/2<=self.x) or (self.x<=self.w/2<prev)):
    gate=self.h/2+math.sin(self.elapsed*.8)*max(0,self.h/2-6)
    if abs(self.y-gate)>3:self.x=prev;self.vx=-self.vx
   if self.y<2:self.y=4-self.y;self.vy=abs(self.vy)
   if self.y>self.h-3:self.y=2*(self.h-3)-self.y;self.vy=-abs(self.vy)
   for plane,center,direction in ((3,self.left,1),(self.w-4,self.right,-1)):
    crossing=(self.vx<0 and prev>=plane>=self.x) if direction==1 else (self.vx>0 and prev<=plane<=self.x)
    if crossing and abs(self.y-center)<=2.5:
     self.x=plane;self.vx=direction*min(speed*2,abs(self.vx)*1.045);self.vy=(self.y-center)*5;self.rally+=1;self.best=max(self.best,self.rally)
   if self.x<0:self.score[1]+=1;self.reset();break
   if self.x>self.w-1:self.score[0]+=1;self.reset();break

def load_scores():
 try:
  if SCORES.is_symlink():return {}
  data=json.loads(SCORES.read_text());return data if isinstance(data,dict) else {}
 except (OSError,ValueError):return {}
def save_result(g):
 try:
  if any(p.is_symlink() for p in [SCORES]+list(SCORES.parents)):return False
  SCORES.parent.mkdir(parents=True,exist_ok=True,mode=0o700);data=load_scores();key=('two' if g.two else g.difficulty)+'-'+g.mode;old=data.get(key,{})
  data[key]={'best_rally':max(g.best,int(old.get('best_rally',0))),'wins':int(old.get('wins',0))+(1 if g.score[0]>=7 else 0),'games':int(old.get('games',0))+1}
  temp=SCORES.with_suffix('.tmp');fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as f:json.dump(data,f)
  temp.replace(SCORES);return True
 except (OSError,ValueError,TypeError):return False

def loop(s):
 s.timeout(16);h,w=s.getmaxyx();mode='classic';difficulty='normal';two=False;g=Pong(w,h,difficulty=difficulty);last=time.monotonic();paused=False;menu=True;left_dir=right_dir=0;left_until=right_until=0;trail=[];recorded=False;notice=''
 if curses.has_colors():
  curses.start_color();curses.use_default_colors()
  for i,c in enumerate((curses.COLOR_CYAN,curses.COLOR_MAGENTA,curses.COLOR_YELLOW,curses.COLOR_WHITE),1):curses.init_pair(i,c,-1)
 def color(i):return curses.color_pair(i) if curses.has_colors() else 0
 S=pi18n.load('arcadewisp',DEFAULT_STRINGS) if pi18n else DEFAULT_STRINGS
 diffname={'easy':S['EASY'],'normal':S['NORMAL'],'hard':S['HARD']}[difficulty]
 while True:
  h,w=s.getmaxyx();key=s.getch();now=time.monotonic();dt=min(.08,now-last);last=now;s.erase()
  if key in (27,ord('q'),ord('Q')):return
  if key in (ord('h'),ord('H')):menu=not menu;left_until=right_until=0
  if menu:
   if key in (ord('1'),ord('2'),ord('3')):difficulty=('easy','normal','hard')[key-ord('1')]
   if key in (ord('m'),ord('M')):two=not two
   if key in (ord('c'),ord('C')):mode=('classic','gate','sprint')[(('classic','gate','sprint').index(mode)+1)%3]
   if key in (10,13):g=Pong(w,h,difficulty=difficulty,two=two,mode=mode);menu=False;paused=False;recorded=False;trail=[]
   put(s,2,max(2,w//2-13),S['DUEL_TITLE'],color(1)|curses.A_BOLD)
   diffname={'easy':S['EASY'],'normal':S['NORMAL'],'hard':S['HARD']}[difficulty]
   lines=[S['DUEL_TAG'],S['DUEL_DIFFS'],S['DUEL_SELECTED'].format(diff=diffname),S['DUEL_PLAYERS'].format(who=S['TWO'] if two else S['SOLO']),S['DUEL_MODE'].format(mode=mode.upper()),S['DUEL_START'],S['DUEL_P1'],S['DUEL_SOLOKEYS'],S['DUEL_KEYS'],S['DUEL_RULE'],S['DUEL_TAPS'],S['DUEL_INPUT_NOTE']]
   for i,t in enumerate(lines):put(s,5+i,max(2,w//2-30),t,color(4))
   scores=load_scores().get(('two' if two else difficulty)+'-'+mode,{})
   put(s,20,max(2,w//2-30),S['BEST_RALLY'].format(rally=scores.get('best_rally',0),games=scores.get('games',0)),color(3))
   s.refresh();continue
  if key==curses.KEY_RESIZE:g=Pong(w,h,difficulty=difficulty,two=two,mode=mode);recorded=False;trail=[];paused=True;notice=S['RESIZED']
  if key==ord(' '):paused=not paused;left_until=right_until=0
  if key in (ord('r'),ord('R')):g=Pong(w,h,difficulty=difficulty,two=two,mode=mode);paused=False;recorded=False;trail=[];notice=''
  if key in (ord('w'),ord('W'),ord('s'),ord('S')):left_dir=-1 if key in (ord('w'),ord('W')) else 1;left_until=now+.13
  if key in (curses.KEY_UP,curses.KEY_DOWN):
   direction=-1 if key==curses.KEY_UP else 1
   if two:right_dir=direction;right_until=now+.13
   else:left_dir=direction;left_until=now+.13
  if w<50 or h<23:put(s,2,2,S['RESIZE_PONG']);s.refresh();continue
  finished=max(g.score)>=7
  if not paused and not finished:g.step(dt,left_dir if now<left_until else 0,right_dir if now<right_until else 0);trail=(trail+[(g.x,g.y)])[-5:]
  if finished and not recorded:notice=S['SAVED'] if save_result(g) else S['NOT_SAVED'];recorded=True
  put(s,0,2,S['PONG_HUD'].format(diff=diffname,who=S['TWO'] if two else S['SOLO'],mode=mode.upper()),color(1)|curses.A_BOLD)
  put(s,1,2,S['PONG_SCORE'].format(l=g.score[0],r=g.score[1],rally=g.rally,best=g.best),color(3)|curses.A_BOLD)
  for y in range(3,h-3,2):put(s,y,w//2,'┆',curses.A_DIM)
  if mode=='gate':
   gate=g.h/2+math.sin(g.elapsed*.8)*max(0,g.h/2-6)
   for y in range(3,h-3):
    if abs(y-gate)>3:put(s,y,w//2,'▒',color(2))
  for x,y in trail[:-1]:put(s,round(y),round(x),'·',color(1)|curses.A_DIM)
  for n in range(-2,3):put(s,round(g.left)+n,2,'█',color(1));put(s,round(g.right)+n,w-3,'█',color(2))
  put(s,round(g.y),round(g.x),'●',color(3)|curses.A_BOLD)
  if finished:put(s,h//2,max(2,w//2-15),(S['LEFT_WINS'] if g.score[0]>=7 else S['RIGHT_WINS'])+S['REMATCH_TAIL'],color(3)|curses.A_BOLD)
  elif paused:put(s,h//2,w//2-8,S['PAUSED_SERVE'],color(3))
  elif g.serve>0:put(s,h//2+2,max(2,w//2-8),S['SERVE'],color(3))
  put(s,h-2,2,notice or S['HELP_PONG'])
  put(s,h-1,2,S['FOOT_PONG'],color(1))
  s.refresh()
if __name__=='__main__':
 import sys
 if '--version' in sys.argv:print(VERSION)
 else:raise SystemExit(run(loop))
