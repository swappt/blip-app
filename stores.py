from kivy.storage.jsonstore import JsonStore

from os import mkdir

from sys import argv # for reading commandline arguments

import webbrowser

adverts = True
try: #'!!!! this line should be removed upon release !!!!'
  from jnius import autoclass, cast # for accessing java classes
except ImportError: #'!!!! this line should be removed upon release !!!!'
  adverts = False #'!!!! this line should be removed upon release !!!!'

storage_dir = '.'

'''this line controls how many retries the user gets. change it for the premium version!!!'''
MAX_RETRIES = 2

def open_url(url):
  webbrowser.open(url)

if adverts: #'!!!! this line should be removed upon release !!!!'
  PythonActivity = autoclass('org.kivy.android.PythonActivity')
  AdBuddiz = autoclass('com.purplebrain.adbuddiz.sdk.AdBuddiz')
  Environment = autoclass('android.os.Environment')
  storage_dir = Environment.getExternalStorageDirectory().getPath()
  context = autoclass('org.kivy.android.PythonActivity').mActivity
  Uri = autoclass('android.net.Uri')
  Intent = autoclass('android.content.Intent')

  def open_url(url):
    intent = Intent()
    intent.setAction(Intent.ACTION_VIEW)
    intent.setData(Uri.parse(url))
    currentActivity = cast('android.app.Activity', context)
    currentActivity.startActivity(intent)


check_store = JsonStore('chk.json')

if check_store.exists('path'):
  store = JsonStore(check_store.get('path')['value'] + '.data.json')
  store.put('highscore',value=check_store.get('highscore')['value'])
  store.put('coins',value=check_store.get('coins')['value'])
  store.put('ball',active=check_store.get('ball')['active'],unlocked=check_store.get('ball')['unlocked'])
else:
  try:
    mkdir(storage_dir + '/blip')
  except OSError:
    pass
  store = JsonStore(storage_dir + '/blip/.data.json')
  check_store.put('path',value=storage_dir+'/blip/')

if not store.exists('highscore'):
  store.put('highscore',value=0)
if not store.exists('coins'):
  store.put('coins',value=0)
if not store.exists('ball'):
  store.put('ball',unlocked=['assets/balls/a.png'],active='assets/balls/a.png')

if not check_store.exists('retry'):
  check_store.put('retry',remaining=MAX_RETRIES,time=0)
if not check_store.exists('settings'):
  check_store.put('settings',music=True,audio=True)
if not check_store.exists('store'):
  check_store.put('store',remaining=2,time=0)

check_store.put('highscore',value=store.get('highscore')['value'])
check_store.put('coins',value=store.get('coins')['value'])
check_store.put('ball',active=store.get('ball')['active'],unlocked=store.get('ball')['unlocked'])

showall = False
invincible = False
for i in argv: ## this picks up other command line arguments to run the program.
  if i == 'patterns':
    showall = True
    adverts = False
    print('PATTERN DEBUGGING IS ENABLED')
  if i == 'invincible':
    invincible = True
    print('INVINCIBILITY IS ENABLED')
    adverts = False


'''THE FOLLOWING LINE CONTROLS THE PREMIUM'''
PREMIUM = False
