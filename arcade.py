#!/usr/bin/env python3
"""Original offline terminal arcade collection; no commercial assets or unlocks."""
import curses,json,os,random,time
from pathlib import Path
from ui import put,run
import paddles
VERSION='1.0.0'
RECORDS=Path.home()/'.local/share/arcadewisp/records.json'
class Bricks:
 def __init__(self,w,h,level=1):
  self.w=w;self.h=h;self.level=level;self.paddle=w/2;self.x=w/2;self.y=h-7;self.vx=14;self.vy=-9;self.lives=3;self.score=0;self.over=False;self.won=False
  self.bricks={(x,y):1+(y//2+level)%2 for y in range(4, min(14,8+level),2) for x in range(4,w-5,6)}
 def step(self,dt,move=0,fire=False):
  dt=min(.06,max(0,dt));self.paddle=max(5,min(self.w-6,self.paddle+move*35*dt));self.x+=self.vx*dt;self.y+=self.vy*dt
  if self.x<2:self.x=2;self.vx=abs(self.vx)
  if self.x>self.w-3:self.x=self.w-3;self.vx=-abs(self.vx)
  if self.y<3:self.y=3;self.vy=abs(self.vy)
  for (x,y),hp in list(self.bricks.items()):
   if x-1<=self.x<=x+4 and abs(self.y-y)<.8:
    self.bricks[x,y]-=1;self.vy=-self.vy;self.score+=5
    if self.bricks[x,y]<=0:del self.bricks[x,y];self.score+=10
    break
  if self.vy>0 and self.y>=self.h-5 and abs(self.x-self.paddle)<=4:self.y=self.h-5;self.vy=-abs(self.vy);self.vx=(self.x-self.paddle)*4 or 3
  if self.y>self.h-2:
   self.lives-=1;self.x=self.paddle;self.y=self.h-7;self.vy=-9
   if self.lives<=0:self.over=True
  if not self.bricks:self.over=True;self.won=True
 def draw(self,s,color):
  for (x,y),hp in self.bricks.items():put(s,y,x,'▰▰▰▰',color(1 if hp==1 else 2))
  put(s,self.h-4,round(self.paddle)-3,'━━━━━━━',color(1));put(s,round(self.y),round(self.x),'●',color(3))
class Invaders:
 def __init__(self,w,h,level=1):
  self.w=w;self.h=h;self.level=level;self.ship=w/2;self.enemies=[(x,y) for y in (4,6,8) for x in range(6,w-6,7)];self.bullets=[];self.bombs=[];self.offset=0;self.direction=1;self.timer=0;self.cooldown=0;self.rng=random.Random();self.lives=3;self.score=0;self.over=False;self.won=False
 def step(self,dt,move=0,fire=False):
  dt=min(.06,max(0,dt));self.ship=max(2,min(self.w-3,self.ship+move*32*dt));self.cooldown=max(0,self.cooldown-dt);self.timer+=dt
  if fire and self.cooldown==0:self.bullets.append([self.ship,self.h-5]);self.cooldown=.2
  if self.timer>.45/max(1,self.level*.4):
   self.timer=0;self.offset+=self.direction
   if self.enemies and (min(x+self.offset for x,y in self.enemies)<3 or max(x+self.offset for x,y in self.enemies)>self.w-4):self.direction=-self.direction;self.enemies=[(x,y+1) for x,y in self.enemies]
   if self.enemies and self.rng.random()<.7:x,y=self.rng.choice(self.enemies);self.bombs.append([x+self.offset,y])
  for b in self.bullets:b[1]-=24*dt
  for b in self.bombs:b[1]+=10*dt
  for b in self.bullets[:]:
   for enemy in self.enemies[:]:
    x,y=enemy
    if abs(b[0]-x-self.offset)<2 and abs(b[1]-y)<1:self.enemies.remove(enemy);self.bullets.remove(b);self.score+=20;break
  for b in self.bombs[:]:
   if abs(b[0]-self.ship)<2 and b[1]>=self.h-5:self.bombs.remove(b);self.lives-=1
  self.bullets=[b for b in self.bullets if b[1]>2];self.bombs=[b for b in self.bombs if b[1]<self.h-2]
  if self.lives<=0 or any(y>=self.h-6 for x,y in self.enemies):self.over=True
  if not self.enemies:self.over=True;self.won=True
 def draw(self,s,color):
  for x,y in self.enemies:put(s,y,round(x+self.offset),'▟█▙',color(2))
  for x,y in self.bullets:put(s,round(y),round(x),'│',color(1))
  for x,y in self.bombs:put(s,round(y),round(x),'•',color(3))
  put(s,self.h-4,round(self.ship)-1,'╱▲╲',color(1))
class Drop:
 def __init__(self,w,h,level=1):
  self.w=w;self.h=h;self.level=level;self.player=w/2;self.vx=0;self.platforms=[[3,h-5,9],[w/2,h-12,10],[w-18,h-19,9]];self.elapsed=0;self.score=0;self.lives=1;self.over=False;self.won=False;self.rng=random.Random();self.spawn=0
 def step(self,dt,move=0,fire=False):
  dt=min(.06,max(0,dt));self.elapsed+=dt;self.vx+=(move*45-self.vx*5)*dt;self.player=max(1,min(self.w-2,self.player+self.vx*dt));speed=3+self.elapsed*.06;self.spawn+=dt
  for p in self.platforms:p[1]-=speed*dt
  if self.spawn>2.1:self.spawn=0;self.platforms.append([self.rng.randrange(2,self.w-13),self.h-2,self.rng.randrange(6,13)])
  self.platforms=[p for p in self.platforms if p[1]>2]
  # Fixed player row: steer through the gaps as platforms rise.
  for x,y,length in self.platforms:
   if abs(y-self.h/2)<.45 and x<=self.player<=x+length:self.over=True
  self.score=int(self.elapsed*10)
 def draw(self,s,color):
  for x,y,length in self.platforms:put(s,round(y),round(x),'═'*length,color(2))
  put(s,self.h//2,round(self.player),'◆',color(1)|curses.A_BOLD)

def records():
 try:
  if RECORDS.is_symlink():return {}
  data=json.loads(RECORDS.read_text());return data if isinstance(data,dict) else {}
 except (OSError,ValueError):return {}
def record(mode,score,won=False):
 try:
  if any(p.is_symlink() for p in [RECORDS]+list(RECORDS.parents)):return False
  RECORDS.parent.mkdir(parents=True,exist_ok=True,mode=0o700);data=records();old=data.get(mode,{})
  badges=set(old.get('badges',[]));badges.add('First run')
  if score>=150:badges.add('Score 150')
  if won:badges.add('Clear a wave')
  data[mode]={'best':max(score,int(old.get('best',0))),'runs':int(old.get('runs',0))+1,'badges':sorted(badges)}
  temp=RECORDS.with_suffix('.tmp');fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as f:json.dump(data,f)
  temp.replace(RECORDS);return True
 except (OSError,ValueError,TypeError):return False

def mini(s,mode,level):
 h,w=s.getmaxyx();cls={'bricks':Bricks,'invaders':Invaders,'drop':Drop}[mode];g=cls(w,h,level);s.timeout(16);last=time.monotonic();paused=False;direction=0;until=0;recorded=False;note=''
 def color(i):return curses.color_pair(i) if curses.has_colors() else 0
 while True:
  key=s.getch();now=time.monotonic();dt=now-last;last=now;s.erase();h,w=s.getmaxyx()
  if key in (27,ord('q'),ord('Q')):
   if not recorded:record(mode,g.score,g.won)
   return
  if key==ord(' '):paused=not paused
  if key in (ord('r'),ord('R'),curses.KEY_RESIZE):g=cls(w,h,level);recorded=False;paused=key==curses.KEY_RESIZE
  if key in (ord('a'),ord('A'),curses.KEY_LEFT):direction=-1;until=now+.13
  if key in (ord('d'),ord('D'),curses.KEY_RIGHT):direction=1;until=now+.13
  if w<50 or h<25:put(s,2,2,'Resize to 50x25. Q returns to menu.');s.refresh();continue
  if not paused and not g.over:g.step(dt,direction if now<until else 0,key in (ord('f'),ord('F'),curses.KEY_UP))
  if g.over and not recorded:note='Saved locally.' if record(mode,g.score,g.won) else 'Scores not saved.';recorded=True
  put(s,0,2,'ARCADEWISP | '+mode.upper()+' | level '+str(level),color(1)|curses.A_BOLD);put(s,1,2,'Score '+str(g.score)+' | lives '+str(g.lives),color(3));g.draw(s,color)
  if g.over:put(s,h//2,max(2,w//2-16),('WAVE CLEAR' if g.won else 'RUN ENDED')+' | R retry',color(3)|curses.A_BOLD)
  elif paused:put(s,h//2,w//2-4,'PAUSED',color(3))
  put(s,h-2,2,note or 'A/D or arrows move | F fire (invaders) | Space pause | R retry | Q menu')
  put(s,h-1,2,'Drop: steer through gaps. Bricks: keep the ball up. Invaders: clear the wave.',color(1));s.refresh()
def loop(s):
 if curses.has_colors():
  curses.start_color();curses.use_default_colors()
  for i,c in enumerate((curses.COLOR_CYAN,curses.COLOR_MAGENTA,curses.COLOR_YELLOW,curses.COLOR_WHITE),1):curses.init_pair(i,c,-1)
 s.timeout(100);level=1
 while True:
  s.erase();h,w=s.getmaxyx();put(s,2,max(2,w//2-16),'ARCADEWISP | TERMINAL ARCADE',curses.A_BOLD)
  lines=['1 Paddle duel (classic, gate, sprint; solo/two players)','2 Brick breaker - clear the colored wall','3 Invaders - dodge and shoot the wave','4 Drop - steer through rising platform gaps','+/- level for bricks/invaders: '+str(level),'All modes included. No paid unlocks.','Local best scores and badges. No Game Center/network.','Q quits. Minimum terminal 50x25.']
  for i,t in enumerate(lines):put(s,5+i*2,3,t)
  data=records()
  for i,mode in enumerate(('bricks','invaders','drop')):
   row=data.get(mode,{});put(s,h-4+i,3,mode+': best '+str(row.get('best',0))+' | '+', '.join(row.get('badges',[])))
  s.refresh();key=s.getch()
  if key in (27,ord('q'),ord('Q')):return
  if key in (ord('+'),ord('=')):level=min(5,level+1)
  if key==ord('-'):level=max(1,level-1)
  if key==ord('1'):paddles.loop(s)
  if key in (ord('2'),ord('3'),ord('4')):mini(s,('bricks','invaders','drop')[key-ord('2')],level)
if __name__=='__main__':
 import sys
 if '--version' in sys.argv:print(VERSION)
 else:raise SystemExit(run(loop))
