from kivy.properties import ObjectProperty, NumericProperty, BoundedNumericProperty, ReferenceListProperty, StringProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.core.text import LabelBase

from game import BlipGame
from app import *
from stores import *

import datetime
from time import time

from os import listdir # for getting files in directories and making directories

from urllib2 import urlopen, URLError # for getting data from url request

from math import sqrt

FONTS = [
  {
    'name': 'odin',
    'fn_regular': 'assets/font/Odin-Rounded-Regular.ttf',
    'fn_bold': 'assets/font/Odin-Rounded-Bold.ttf'
  },
  {
    'name': 'gemelli',
    'fn_regular': 'assets/font/gemelli.regular.ttf'
  }
]

for i in FONTS: ##  register new fonts
  LabelBase.register(**i)

class Ball(Widget):
  vel_x = NumericProperty(0)
  vel_y = NumericProperty(0)

  vel = ReferenceListProperty(vel_x,vel_y)

  moving = False
  falling = False

  rotation = NumericProperty(0)
  rotate = -4
  turning = False

  tex = StringProperty(check_store['ball']['active'])

  def move(self):
    if self.moving:
      self.pos = Vector(*self.vel) + self.pos
    if self.turning:
      self.rotation += self.rotate

class Platform(Widget):
  moving = False
  moved = False
  looped = False

  rotation = NumericProperty(0)
  side_pos = -1 ## -1 = left, 1 = right ##

  tex = StringProperty('assets/levels/platform_g.png')

  def move(self):
    if self.moving:
      self.y -= self.height

class Spike(Widget):
  moving = False
  speed = 10

  shifting = False
  x_dir = 0.05
  y_dir = 0
  change = 1
  delta = BoundedNumericProperty(0,min=-2,max=2)

  def move(self):
    if self.moving:
      self.y -= self.speed
      if self.y < -self.height:
        self.moving = False
    elif self.shifting:
      self.x += self.x_dir * self.width
      self.y += self.y_dir * self.width
      try:
        self.delta += max(abs(self.x_dir),abs(self.y_dir)) * self.change
      except ValueError:
        self.x_dir *= -1
        self.y_dir *= -1
        self.change *= -1

class Coin(Widget):
  pass

class TitleCanvas(Widget):

  def play(self):
    global blip

    blip.m.current = 'game'
    if check_store.exists('last_game') and check_store.get('last_game')['level'] > 0:
      blip.m.game.resuming = True
    blip.m.game.reset()

  def nav(self,l):
    blip.m.current = l

class Dot(Widget):
  y_inc = BoundedNumericProperty(0,min=0,max=20)
  y_dir = 1

  def __init__(self, *args, **kwargs):
    super(Dot, self).__init__(*args, **kwargs)
    Clock.schedule_interval(self.update, 1 / 20)

  def update(self,t):
    try:
      self.y_inc += self.y_dir
      self.y += self.y_dir
    except ValueError:
      self.y_dir *= -1

class Title(Widget):
  pass

class BackButton(Widget):
  def back(self):
    blip.m.current = 'menu'

class Music(Widget):
  if check_store['settings']['music']:
    speaker_source = StringProperty('assets/gui/music_icon_on.png')
    music = True
  else:
    speaker_source = StringProperty('assets/gui/music_icon_off.png')
    music = False

  def no_audio(self):
    if self.music:
      blip.m.game.sounds['background_music'].volume = 0
      self.speaker_source = 'assets/gui/music_icon_off.png'
      check_store.put('settings',music=False,audio=check_store['settings']['audio'])
      self.music = False
    else:
      blip.m.game.sounds['background_music'].volume = 1
      self.speaker_source = 'assets/gui/music_icon_on.png'
      check_store.put('settings',music=True,audio=check_store['settings']['audio'])
      self.music = True

class Speaker(Widget):
  if check_store['settings']['audio']:
    speaker_source = StringProperty('assets/gui/sound_icon_on.png')
    audio = True
  else:
    speaker_source = StringProperty('assets/gui/sound_icon_off.png')
    audio = False

  def no_audio(self):
    if self.audio:
      for i,j in blip.m.game.sounds.iteritems():
        if i != 'background_music':
          j.volume = 0
      self.speaker_source = 'assets/gui/sound_icon_off.png'
      check_store.put('settings',audio=False,music=check_store['settings']['music'])
      self.audio = False
    else:
      for i,j in blip.m.game.sounds.iteritems():
        if i != 'background_music':
          j.volume = 1
      self.speaker_source = 'assets/gui/sound_icon_on.png'
      check_store.put('settings',audio=True,music=check_store['settings']['music'])
      self.audio = True

class LinkButton(Widget):
  col = ListProperty([1,1,1,0])

  def link(self,u):
    open_url(u)

class Information(Widget):
  pass

class Tutorial(Widget):
  tut = ObjectProperty(Image(source='assets/gui/instructions.zip',anim_delay=-1))

class AimBall(Widget):
  rotation = BoundedNumericProperty(0,min=-86,max=86)

class ContinueButton(Widget):
  start_angle = BoundedNumericProperty(0,min=0,max=360)
  label = ObjectProperty(None)

  def __init__(self, *args, **kwargs):
    super(ContinueButton, self).__init__(*args, **kwargs)
    Clock.schedule_interval(self.update, 1 / 20)

  def update(self,t):
    if check_store['retry']['remaining'] > 0:
      blip.m.go.continuebutton.label.opacity = 0
      blip.m.go.continuebutton.contlabel.opacity = 1
      try:
        self.start_angle += 1.5
        self.active = True
      except ValueError:
        self.start_angle = 360
        self.active = False
        self.opacity = 0
    else:
      blip.m.go.continuebutton.label.opacity = 1
      blip.m.go.continuebutton.contlabel.opacity = 0
      blip.m.go.continuebutton.start_angle = 360
      self.active = False

    if blip.m.game.retried:
      self.opacity = 0

    if time() - check_store['retry']['time'] > 86399: # checks if a day has passed since a replay was used
      check_store.put('retry',remaining=MAX_RETRIES,time=check_store['retry']['time'])

    if time() - check_store['store']['time'] > 86399: # checks if a day has passed since an ad was used in the store (put here to avoid repetition)
      check_store.put('store',remaining=2,time=check_store['store']['time'])

  def back(self):
    if not PREMIUM:
      try:
        resp = urlopen('http://google.com',timeout=4)
      except URLError:
        blip.m.go.continuebutton.contlabel.text = 'No internet. Please try again later'
        self.active = False

    if (not blip.m.game.retried) and self.active:
      if adverts and not PREMIUM:
        AdBuddiz.showAd(PythonActivity.mActivity)
      blip.m.current = 'game'
      blip.m.game.retried = True
      blip.m.game.cache()

      if check_store.get('retry')['remaining'] == MAX_RETRIES:
        check_store.put('retry',remaining=check_store['retry']['remaining'],time=time())

      remain = check_store['retry']['remaining']
      check_store.put('retry',remaining=remain-1,time=check_store['retry']['time'])

class GameOver(Widget):
  hs = ObjectProperty(None)
  d = store

  def play(self):
    global blip

    blip.m.current = 'game'
    blip.m.game.reset()

  def nav(self,l):
    blip.m.current = l

class Information(Widget):
  tut = ObjectProperty(None)

class StoreScreen(Widget):
  scroll = ObjectProperty(None)
  coincounter = ObjectProperty(None)
  d = store

class InfoButton(Widget):
  icon = ObjectProperty(Image(source='assets/gui/info.zip',anim_delay=0.05))
  def change(self):
    blip.m.info.tut.tut.anim_delay = 0.03
    blip.m.current = 'info'

class AdButton(Widget):
  img = StringProperty('assets/store/ad_button.png')
  inet = True
  if not PREMIUM:
    try:
      inet = True
      resp = urlopen('http://google.com',timeout=4)
    except URLError:
      img = StringProperty('assets/store/connection.png')
      inet = False

  if check_store['store']['remaining'] <= 0:
    img = StringProperty('assets/store/back_later.png')

  t = 0

  def do_ad(self):
    try:
      self.inet = True
      resp = urlopen('http://google.com',timeout=4)
      self.img = 'assets/store/ad_button.png'
    except URLError:
      self.img = 'assets/store/connection.png'
      self.inet = False

    if self.inet and check_store['store']['remaining'] > 0 and time() - self.t > 2.5:
      if adverts and not PREMIUM:
        AdBuddiz.showAd(PythonActivity.mActivity)
      coins = check_store.get('coins')['value']
      check_store.put('coins',value=coins+10)
      store.put('coins',value=coins+10)

      self.t = time()
      print('done an ad')

      if check_store.get('store')['remaining'] == 2:
        check_store.put('store',remaining=check_store['store']['remaining'],time=time())

      remain = check_store['store']['remaining']
      check_store.put('store',remaining=remain-1,time=check_store['store']['time'])

    if check_store['store']['remaining'] <= 0:
      self.img = 'assets/store/back_later.png'

class StoreScroll(Widget):
  offset_x = NumericProperty(0)
  touched = 0,0
  initial_touch = 0,0
  touching = False
  touch_time = time()
  t = time()
  try:
    date = urlopen('http://just-the-time.appspot.com').read().split(' ')[0].split('-',1)[1]
    month = int(date.split('-')[0])
    day = int(date.split('-')[1])
  except:
    month = datetime.date.today().month
    day = datetime.date.today().day
  print(month)
  print(day)

  def __init__(self,*args,**kwargs):
    super(StoreScroll,self).__init__(*args,**kwargs)
    Clock.schedule_interval(self.resize,1/10)

  def start(self):
    textures = listdir('assets/balls')
    textures.sort()
    for _ in range(10):
      for item in textures:
        if item.endswith('.meta'):
          print(item)
          textures.remove(item)
    textures.reverse()
    print(textures)
    for tex in textures:
      if tex[0] != '_' or 'assets/balls/' + tex in store['ball']['unlocked']:
        b = StoreButtons('assets/balls/' + tex,size_hint=(None,None))

        if 'assets/balls/' + tex in store['ball']['unlocked']:
          b.lock = 'assets/store/unlock.png'
          b.locked = False
        else:
          tier = [line for line in open('assets/balls/' + tex + '.meta','r') if line.startswith('tier=')]
          print(tier)
          tier = tier[0].strip()
          print(tier)
          tier = tier.split('=')
          print(tier)
          tier = int(tier[1])
          b.lock = ['assets/store/unlock.png','assets/store/150.png','assets/store/200.png','assets/store/300.png','assets/store/400.png'][tier]

          b.tier = [0,150,200,300,400][tier]

        self.add_widget(b)
      else: # if the ball is limited edition and not unlocked yet
        days = range(1,32)
        months = range(1,13)
        meta = open('assets/balls/' + tex + '.meta','r')
        for line in meta:
          if line.startswith('month='):
            l = line.split('=',1)[1]
            l = l.rstrip()
            months = l.split(',')
            months = map(int,months)
            print(months)
          elif line.startswith('day='):
            l = line.split('=',1)[1]
            l = l.rstrip()
            days = l.split(',')
            days = map(int,days)
            print(days)
        if self.day in days and self.month in months:
          b = StoreButtons('assets/balls/' + tex,size_hint=(None,None))
          b.lock = 'assets/store/400.png'
          b.tier = 400
          self.add_widget(b)

    for c in self.children:
      if c.tex == check_store['ball']['active']:
        c.lock = 'assets/store/selected.png'
        self.active = c

  def resize(self,t):
    if not self.touching:
      mi,ma = self.get_min_max()
      if ma.right < self.width - self.width * 1 / 25:
        self.offset_x += sqrt(self.width - ma.right)

      elif self.offset_x > 0:
        self.offset_x -= sqrt(mi.right)

    xpos = self.width * 1 / 25
    ypos = [0,self.height * 1 / 5 + self.width * 1 / 25,0]
    yselector = 1
    for c in self.children:
      c.height = self.height / 5
      c.width = self.height / 5

      c.pos = xpos + self.offset_x, ypos[yselector] + c.width * 1 / 5

      yselector *= -1
      if yselector > -1:
        xpos += c.width * 6 / 5

      if -c.width < c.x < self.width:
        c.opacity = 1
      else:
        c.opacity = 0
    blip.m.store.coincounter.text = 'COINS: ' + str(store['coins']['value'])
    if time() - self.t < 0.2:
      blip.m.store.coincounter.color = 1,0,0,1
    else:
      blip.m.store.coincounter.color = 1,1,1,1

  def invalid(self):
    self.t = time()

  def get_min_max(self):
    mi = self.children[0]
    ma = self.children[0]
    for c in self.children:
      if c.x < mi.x:
        mi = c
      elif c.x > ma.x:
        ma = c
    return mi,ma

  def get_button(self,x,y):
    for c in self.children:
      if c.x < x < c.right and c.y < y < c.top:
        return c

  def on_touch_down(self,touch):
    self.initial_touch = touch.x,touch.y
    self.touched = touch.x,touch.y
    self.touching = True
    self.touch_time = time()

  def on_touch_move(self,touch):
    self.offset_x += touch.x - self.touched[0]
    self.touched = touch.x,touch.y

  def on_touch_up(self,touch):
    self.touching = False

    dx = abs(touch.x - self.initial_touch[0])
    dy = abs(touch.y - self.initial_touch[1])
    d = dx + dy

    if time() - self.touch_time < 1.5 and d < self.width / 100:
      try:
        b = self.get_button(touch.x,touch.y)
        if not b.locked:
          self.active.lock = 'assets/store/unlock.png'
          self.active = b
        b.purchase()
      except AttributeError:
        pass

class StoreButtons(Widget):
  tex = StringProperty('assets/balls/a.png')
  lock = StringProperty('assets/store/200.png')
  locked = True

  tier = 200

  def __init__(self,texture,*args,**kwargs):
    super(StoreButtons,self).__init__(*args,**kwargs)
    self.tex = texture

  def purchase(self):
    if self.locked:
      coins = store['coins']['value']
      if coins >= self.tier:
        coins -= self.tier
        check_store.put('coins',value=coins)
        store.put('coins',value=coins)
        self.locked = False
        self.lock = 'assets/store/unlock.png'
        s = store['ball']['unlocked']
        s.append(self.tex)
        check_store.put('ball',active=check_store['ball']['active'],unlocked=s)
        store.put('ball',active=store['ball']['active'],unlocked=s)
      else:
        blip.m.store.scroll.invalid()
    else:
      blip.m.game.ball.tex = self.tex
      self.lock = 'assets/store/selected.png'
      check_store.put('ball',active=self.tex,unlocked=check_store['ball']['unlocked'])
      store.put('ball',active=self.tex,unlocked=store['ball']['unlocked'])

blip.run()
