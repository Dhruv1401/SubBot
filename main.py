import discord, asyncio, os, keep_alive, urllib.request, replit, pymongo, requests
from bs4 import BeautifulSoup
TOKEN = ('ODc2MzQ1MTUzNTA4NDkxMjg0.YRiuBg.yFtc96VtCbo5-A7wzlRxD9l3hqc')
CLIENTID = os.getenv('876345153508491284')
client = discord.Client()
mongopass = os.getenv('PASS')
othermongopass = os.getenv('OTHERPASS')
pre = 's-'

cmds = {
  'sub': 's sub subscribe signup sign follow notify'.split(),
  'usub': 'u us usub unsub unsubscribe unsb uns ussignup unsign usign usingup unfollow ufollow stop unotify unnotify'.split(),
  'subs': 'ss subs sbs followers subscribers count amount subcount c'.split()
}

dbclient = pymongo.MongoClient('mongodb+srv://SBOT:'+mongopass+'@cluster0-umm9w.mongodb.net/test?retryWrites=true&w=majority')
privatedbclient = pymongo.MongoClient('mongodb+srv://SubscriberBot:'+othermongopass+'@cluster0-g8eqc.mongodb.net/test?retryWrites=true&w=majority')

pdb = privatedbclient.lastposts
db = dbclient.database

async def watch_repltalk(client):
  page = urllib.request.urlopen('https://repl.it/talk/all?order=new')
  code = BeautifulSoup(page, 'html.parser')
  lastseen = pdb.last.find_one({'key': 1})
  lastseen = lastseen['title']
  lastposted = code.find_all('div', attrs={'class': 'board-post-list-item-post-title'})[2].text
  posturl = 'https://repl.it' + code.find_all('a', attrs={'class': 'jsx-4091790247 paper jsx-2258667558 theme interactive responsive listItem'})[2]['href']
  postauthor = code.find_all('span', attrs={'class': 'jsx-4044439717'})[24].text.split('(')[0].strip()
  postdescription = code.find_all('div', attrs={'class': 'jsx-3614942138 board-post-list-item-post-preview'})[2].text
  postauthorprof = 'https://repl.it/@' + postauthor
  if not lastposted == lastseen:
    print('New Post:', lastposted, ' ', posturl)
    pdb.last.delete_one({'key': 1})
    pdb.last.insert_one({'title': lastposted, 'key': 1})
    notifierscollection = db[postauthor].find({})
    notifiers = []
    for n in notifierscollection:
      notifiers.append(client.get_user(n['did']))
    for n in notifiers:
      embed=discord.Embed(title=lastposted, url=posturl, description=postdescription, color=0x0080ff)
      embed.set_author(name=postauthor, url=postauthorprof)
      await n.send(' ', embed=embed)    


@client.event
async def on_ready():
  replit.clear()
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='REPL TALK'))
  print('Logged in as: ', end = '')
  print(client.user.name)
  print('Invite: https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=0'.format(os.environ['CLIENTID']))
  print('Connected to '+str(len(client.guilds)+1)+' servers.')
  print('--------------------------------------------------------')

@client.event
async def on_message(message):
  content = message.content
  command = content.split()[0][len(pre):].lower()
  try: args = ' '.join(content.split()[1:])
  except: args = ''
  channel = message.channel
  author = message.author
  if not message.content.startswith(pre): return
  if command == 'watch':
    await watch_repltalk(client)
  elif command in cmds['sub']:
    try:
      if str(requests.get('https://repl.it/@'+args)).endswith('[404]>'): 
        raise Exception('Not found')
      if db[args].find_one({'did': author.id}):
        await channel.send('Already subscribed to ' + args)
        return
      try: db[args].insert_one({'did': author.id})
      except:
        db.create_collection(args)
        db[args].insert_one({'did': author.id})
      await channel.send('Subscribed to ' + args)
    except:
      await channel.send(args + ' is not a real repl.it user')
  elif command in cmds['usub']:
    if not db[args].find_one({'did': author.id}):
      await channel.send('Not subscribed to ' + args)
      return
    db[args].delete_one({'did': author.id})
    await channel.send('Unsubscribed to ' + args)
  elif command in cmds['subs']:
    numsubs = str(len(list(db[args].find({}))))
    await channel.send(args + "'s Subscriber Count: `" + numsubs + '`')
  elif command == 'help':
    await channel.send('`sub <user>`, `unsub <user>`, `subs <user>`')

keep_alive.keep_alive()
client.run(os.environ['TOKEN'])