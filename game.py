from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader as s
from kivy.properties import ObjectProperty, ReferenceListProperty, StringProperty, ListProperty
from kivy.clock import Clock
from kivy.vector import Vector

from math import atan2, degrees, sqrt
from ceil import ceil

from random import choice, sample, randint, random

from stores import *
from app import *
from spikes import a as spike_patterns
from coins import a as coin_positions

class BlipGame(Widget):
  sounds = {
    'blip': s.load('assets/audio/blip.ogg'),
    'knock': s.load('assets/audio/knock.ogg'),
    'background_music': s.load('assets/audio/background_music.ogg'),
    'coin' : s.load('assets/audio/coin.ogg')
  }

  lock = False

  for f,i in sounds.iteritems():
    i.seek(0)

  if not check_store['settings']['music']:
    sounds['background_music'].volume = 0

  if not check_store['settings']['audio']:
    for i,j in sounds.iteritems():
      if i != 'background_music':
        j.volume = 0

  sounds['background_music'].loop = True
  sounds['background_music'].play()

  platform = ObjectProperty(None)
  ball = ObjectProperty(None)
  aimball = ObjectProperty(None)
  debug = ObjectProperty(None)
  tutorial = ObjectProperty(None)
  tutorial2 = ObjectProperty(None)
  coin = ObjectProperty(None)

  pattern = []

  s1 = ObjectProperty(None)
  s2 = ObjectProperty(None)
  s3 = ObjectProperty(None)
  s4 = ObjectProperty(None)
  s5 = ObjectProperty(None)
  s6 = ObjectProperty(None)
  s7 = ObjectProperty(None)
  s8 = ObjectProperty(None)
  s9 = ObjectProperty(None)
  s10 = ObjectProperty(None)

  spikes = ReferenceListProperty(s1,s2,s3,s4,s5,s6,s7,s8,s9,s10)
  tutorials = ReferenceListProperty(tutorial,tutorial2)

  touch_since_throw = True
  correct_angle = True

  retried = False
  resuming = False

  move_coin = True

  def __init__(self, *args, **kwargs):
    super(BlipGame, self).__init__(*args, **kwargs)
    Clock.schedule_interval(self.update, 1 / 60)

  def update(self,t):

    for i in self.spikes:
      i.speed = self.platform.height

    if self.resuming:
      self.resume()
      if self.platform.rotation > 14:
        self.platform.tex = 'assets/levels/platform_b.png'
      elif self.platform.rotation > 29:
        self.platform.tex = 'assets/levels/platform_r.png'
      self.resuming = False # this statement resumes the game after closing down

    if self.platform.y < 0:
      self.refresh_page() # this statement refreshes the page when the user completes a level

    elif self.platform.y < self.height * 8 / 10 and self.platform.looped:
      self.platform.moving = False
      self.platform.y = self.height * 8 / 10

    if self.ball.top > self.height:
      self.ball.vel_y *= -1 # bounce

    elif (self.ball.x < 0) or (self.ball.right > self.width): # bounce
      self.ball.rotate *= -1
      self.ball.vel_x *= -1
      if self.ball.y > self.height * 1 / 10 and not self.ball.falling:
        self.sounds['knock'].play()

    elif self.ball.collide_widget(self.platform) and self.ball.vel_y > 0 and self.ball.center_y < self.platform.y:
      self.ball.vel_y *= -1

    if self.ball.y < 0: # gameover
      if not self.platform.moved and not invincible:
        self.gameover()
      self.ball.moving = False
      self.ball.center = self.width * 1 / 8,self.height * 1 / 10

    if self.ball.center_y > self.platform.top and (self.platform.x < self.ball.center_x < self.platform.right or self.ball.collide_widget(self.platform)) \
       and not self.platform.moving: # complete level

      for wi in self.spikes:
        wi.moving = True

      self.platform.moving = True
      self.platform.moved = True
      self.platform.looped = False

      self.ball.falling = True
      self.ball.turning = False

      if not self.platform.x < self.ball.center_x < self.platform.right:
        self.ball.center = self.platform.center_x, self.platform.top + self.platform.height

    elif self.ball.falling:
      self.ball.vel_x *= 0.95
      self.ball.vel_y = -self.platform.height
      if not self.platform.x <= self.ball.center_x <= self.platform.right:
        self.ball.vel_x *= -1
      if self.platform.top < self.ball.y:
        if self.ball.vel_y < 0:
          self.ball.vel_y *= 1.2
        else:
          self.ball.vel_y *= -1.2
      else:
        self.ball.vel_y = -self.platform.height
        self.ball.y = self.platform.top

    self.grab_collision()

    if self.ball.collide_widget(self.coin) and not self.move_coin: # grabs coin collisions and adds on points
      self.sounds['coin'].play()

      coins = store['coins']['value']
      check_store.put('coins',value=coins+4)
      store.put('coins',value=coins+4)
      self.coin.opacity = 0
      self.move_coin = True

    self.ball.move()
    self.platform.move()

    for wi in self.spikes:
      wi.move()

  def grab_collision(self):
    if not self.platform.moving:
      for wi in self.spikes:
        for point in [[wi.x,wi.center_y],[wi.right,wi.center_y],[wi.center_x,wi.y],[wi.center_x,wi.top]]:
          if self.ball.x <= point[0] <= self.ball.right and self.ball.y <= point[1] <= self.ball.top:
            if not invincible and not self.ball.falling:
              self.gameover()
            else:
              self.ball.moving = False
              self.ball.turning = False
              self.ball.center = self.width * 1 / 8,self.height * 1 / 10
            return

  def refresh_page(self):
    self.sounds['blip'].play()

    coins = store['coins']['value']
    check_store.put('coins',value=coins+1)
    store.put('coins',value=coins+1)

    self.platform.looped = True
    self.platform.y = self.height

    self.ball.rotate = -4
    self.ball.falling = False

    for wi in self.spikes:
      wi.moving = False
      wi.shifting = False
      wi.pos = -self.width,-self.height

    if not self.lock:
      self.platform.rotation += 1
      if self.platform.rotation > 14:
        self.platform.tex = 'assets/levels/platform_b.png'
      elif self.platform.rotation > 29:
        self.platform.tex = 'assets/levels/platform_r.png'

      self.platform.side_pos *= -1
      if self.platform.side_pos == -1:
        self.platform.x = 0
      else:
        self.platform.x = self.width - self.platform.width

    self.place_spikes()

    if self.move_coin:
      coin_pos = choice(coin_positions)

      tries = 0
      self.coin.center = self.width * coin_pos[0], self.height * coin_pos[1]
      while (self.coin_collide() or self.coin.center in self.pattern) and tries < 15:
        print('repositioning coin to suit spikes')
        coin_pos = choice(coin_positions)
        self.coin.center = self.width * coin_pos[0], self.height * coin_pos[1]
        tries += 1
      self.coin.opacity = 1
      self.move_coin = False

    if showall:
      self.debug.text = str(self.pattern)
      self.debug.pos = 0,self.height-self.debug.height
    else:
      self.debug.pos = self.width,self.height

    if self.platform.rotation < 2:
      self.tutorial2.text = 'Avoid the spikes!'

    self.tutorial.opacity = 0

    if self.platform.rotation > 1:
      self.tutorial2.opacity = 0

    self.cache()

  def coin_collide(self):
    for wi in self.spikes:
      if wi.collide_widget(self.coin):
        return True

  def place_spikes(self):
    level = ceil(self.platform.rotation,5)
    if level > 10:
      level = randint(1,10)

    self.pattern = choice(spike_patterns[self.platform.side_pos])
    while len(self.pattern) < level:
      self.pattern = choice(spike_patterns[self.platform.side_pos])

    print(self.pattern)

    if len(self.pattern) > level:
      self.pattern = sample(self.pattern,level)

    spike_n = 0
    for i in self.pattern:
      self.spikes[spike_n].center = self.width * i[0],self.height * i[1]
      spike_n += 1

    for sp in sample(self.spikes,randint(0,3)):
      sp.shifting = True
      sp.x_dir = (random() - 0.5) * 0.07
      sp.y_dir = (random() - 0.5) * 0.07

  def cache(self):
    check_store.put('last_game',level=self.platform.rotation,pattern=self.pattern,side=self.platform.side_pos,retried=self.retried)

  def gameover(self):
    self.ball.center = self.width * 1 / 8,self.height * 1 / 10
    self.ball.vel = Vector(0,0)
    self.ball.moving = False
    self.ball.falling = False
    self.ball.turning = False
    self.ball.rotate = -4

    if self.platform.rotation > store.get('highscore')['value']:
      blip.m.go.hs.text = 'BEST: ' + str(self.platform.rotation)
      store.put('highscore',value=self.platform.rotation)
      check_store.put('highscore',value=self.platform.rotation)

    blip.m.go.current.text = 'YOU SCORED ' + str(self.platform.rotation)
    blip.m.go.continuebutton.start_angle = 0
    blip.m.go.continuebutton.opacity = 1

    self.parent.parent.current = 'GOmenu'

    check_store.put('last_game',level=0)

  def resume(self):
    for i in self.tutorials:
      i.opacity = 0

    self.platform.rotation = check_store.get('last_game')['level']
    self.platform.side_pos = check_store.get('last_game')['side']
    if self.platform.side_pos == -1:
      self.platform.x = 0
    else:
      self.platform.x = self.width - self.platform.width

    pattern = check_store.get('last_game')['pattern']

    spike_n = 0
    for i in pattern:
      self.spikes[spike_n].center = self.width * i[0],self.height * i[1]
      spike_n += 1

    for sp in sample(self.spikes,randint(0,3)):
      sp.shifting = True
      sp.x_dir = (random() - 0.5) * 0.065
      sp.y_dir = (random() - 0.5) * 0.065

    blip.m.menu.label_1.text = 'PLAY'

    self.retried = check_store.get('last_game')['retried']

  def reset(self):

    self.ball.center = self.width * 1 / 8,self.height * 1 / 10
    self.ball.vel = Vector(0,0)
    self.ball.moving = False
    self.ball.turning = False
    self.ball.rotate = -4

    self.platform.rotation = 0

    self.platform.side_pos = -1
    self.platform.moved = False
    self.platform.moving = False
    self.platform.looped = False

    self.platform.tex = 'assets/levels/platform_g.png'

    self.platform.pos = 0,self.height * 8 / 10

    self.retried = False

    self.coin.pos = 0-self.coin.width,0-self.coin.height
    self.move_coin = True

    for i in self.spikes:
      i.pos = -self.width,-self.height

  def update_aimball(self,pos): ## Function to move the aiming pointer to the correct angle
    if pos.y > self.height * 8 / 10:
      return 0
    else:
      dx = pos.x - (self.width / 8)
      dy = pos.y - (self.height / 10)

      if dy > 0:
        new_angle = degrees(atan2(dx,dy))
      else:
        new_angle = degrees(atan2(-dx,-dy))

      try: ## trys to rotate to the new angle...
        self.aimball.rotation = new_angle
        self.correct_angle = True
      except: ## ...but if it's out of bounds, forget about it
        self.aimball.height = 0
        self.correct_angle = False

      return 1

  def throw_ball(self,pos):
    if pos.y > self.height * 8 / 10:
      return 0
    else:
      self.platform.moved = False
      self.ball.turning = True

      dx = pos.x - (self.width / 8)
      dy = pos.y - (self.height / 10)

      if dy < 0:
        dy = -dy
        dx = -dx

      hyp = sqrt(dx*dx + dy*dy)

      uvec_x = dx / hyp
      uvec_y = dy / hyp

      self.ball.vel = Vector(uvec_x * self.width / 45,uvec_y * self.width / 45)

      return 1

  def on_touch_move(self,touch):
    if not self.ball.moving and not self.platform.moving:
      if self.update_aimball(touch):
        self.aimball.height = self.aimball.width * 20

  def on_touch_down(self,touch):
    if not self.ball.moving and not self.platform.moving:
      if self.update_aimball(touch):
        self.aimball.height = self.aimball.width * 20
    if self.ball.moving:
      self.touch_since_throw = False

    if self.platform.rotation < 1:
      self.tutorial2.text = 'Release to throw the ball!'

  def on_touch_up(self,touch):
    self.aimball.height = 0
    if not self.ball.moving and self.touch_since_throw and self.correct_angle and not self.platform.moving:
      if self.throw_ball(touch):
        self.ball.moving = True
    if not self.touch_since_throw:
      self.touch_since_throw = True

  def stop(self):
    for i,j in self.sounds.iteritems():
      j.stop()
