from kivy.app import App
from kivy.base import EventLoop
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager

from stores import *

class Manager(ScreenManager):
  go = ObjectProperty(None)
  game = ObjectProperty(None)
  store = ObjectProperty(None)

class BlipApp(App):

  def on_start(self):
    EventLoop.window.bind(on_keyboard=self.keyboard)
    self.m.store.scroll.start()

  def keyboard(self, window, key, *largs):
    if key == 27:
      if blip.m.current in ['store','info']:
        blip.m.current = 'menu'
      elif blip.m.current == 'menu':
        blip.stop()
      return True
    if key == 108 and invincible:
      self.m.game.lock = not self.m.game.lock
      print('TOGGLE LEVEL LOCK')

  def on_stop(self, *largs):
    self.m.game.stop()
    check_store.put('highscore',value=store.get('highscore')['value'])
    check_store.put('coins',value=store.get('coins')['value'])

  def build(self):

    if adverts and not PREMIUM:
      AdBuddiz.setPublisherKey('32ff3b4a-489f-4098-9fd3-143080874a62')
      AdBuddiz.cacheAds(PythonActivity.mActivity)
      AdBuddiz.showAd(PythonActivity.mActivity)
    self.icon = 'assets/icon.png'
    self.m = Manager()

    if check_store.exists('last_game') and check_store.get('last_game')['level'] > 0:
      self.m.menu.label_1.text = 'RESUME'

    return self.m

blip = BlipApp()
