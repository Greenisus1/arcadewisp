import unittest,tempfile,random
from pathlib import Path
from unittest.mock import patch
import arcade,paddles
class Tests(unittest.TestCase):
 def test_bricks_bounce(self):
  g=arcade.Bricks(80,30);g.x=1;g.vx=-10;g.step(.02);self.assertGreater(g.vx,0)
 def test_bricks_clear(self):
  g=arcade.Bricks(80,30);g.bricks={};g.step(.02);self.assertTrue(g.won)
 def test_bricks_lost(self):
  g=arcade.Bricks(80,30);g.y=31;g.x=0;g.lives=1;g.step(.02);self.assertTrue(g.over)
 def test_invaders_fire(self):
  g=arcade.Invaders(80,30);g.step(.02,fire=True);self.assertEqual(len(g.bullets),1);g.step(.02,fire=True);self.assertEqual(len(g.bullets),1)
 def test_invaders_hit(self):
  g=arcade.Invaders(80,30);g.enemies=[(10,4)];g.bullets=[[10,4.5]];g.step(.02);self.assertTrue(g.won);self.assertEqual(g.score,20)
 def test_invaders_bomb(self):
  g=arcade.Invaders(80,30);g.bombs=[[g.ship,26]];g.lives=1;g.step(.02);self.assertTrue(g.over)
 def test_drop_score(self):
  g=arcade.Drop(80,30);g.platforms=[]
  for _ in range(20):g.step(.05)
  self.assertEqual(g.score,10)
 def test_drop_collision(self):
  g=arcade.Drop(80,30);g.platforms=[[g.player-2,g.h/2,8]];g.step(.01);self.assertTrue(g.over)
 def test_records(self):
  with tempfile.TemporaryDirectory() as d,patch.object(arcade,'RECORDS',Path(d)/'r.json'):
   self.assertTrue(arcade.record('drop',160));self.assertTrue(arcade.record('drop',10));r=arcade.records()['drop'];self.assertEqual(r['best'],160);self.assertEqual(r['runs'],2);self.assertIn('Score 150',r['badges'])
 def test_record_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   dest=Path(d)/'target';dest.write_text('unchanged');link=Path(d)/'r.json';link.symlink_to(dest)
   with patch.object(arcade,'RECORDS',link):self.assertFalse(arcade.record('drop',1))
   self.assertEqual(dest.read_text(),'unchanged')
 def test_paddle_bounds(self):
  g=paddles.Pong(80,30,two=True)
  for _ in range(500):g.step(.05,1,-1)
  self.assertTrue(3<=g.left<=26);self.assertTrue(3<=g.right<=26)
 def test_paddle_plane(self):
  g=paddles.Pong(80,30);g.serve=0;g.x=4;g.y=g.left;g.vx=-100;g.vy=0;g.step(.05);self.assertGreater(g.vx,0)
 def test_gate(self):
  g=paddles.Pong(80,30,mode='gate');g.serve=0;g.x=39.5;g.y=3;g.vx=20;g.vy=0;g.step(.05);self.assertLess(g.vx,0)
if __name__=='__main__':unittest.main()
