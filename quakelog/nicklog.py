from datetime import datetime
from utils import slugify
from replay import Player, _ZERO_PROPERTIES, _STAT_WEAPONS

_COUNT = 1
def player_line(player):
	global _COUNT
	out = datetime.now().strftime("%Y.%m.%d-%H:%M:%S-")
	out += "%05d " % _COUNT
	_COUNT += 1
	out += player.serialize()
	return out

def read_player_line(line):
	n1 = line.index('"')
	n2 = line.index('"', n1+1)
	nick = line[n1+1:n2]
	p = Player()
	setattr(p, 'nick', nick)
	setattr(p, 'slug_nick', slugify(p.nick))
	attribs = line[n2+2:].split(" ")
	for attr in attribs[2:]:
		attr = attr.split(":")
		if len(attr) == 2:
			key, val = attr
			setattr(p, key, int(val))
		elif len(attr) == 5:
			weapon, shots, hits, kills, deaths = attr
			setattr(p, weapon, dict(shots=int(shots), hits=int(hits), kills=int(kills), deaths=int(deaths)))
		else:
			print attr
	for prop in _ZERO_PROPERTIES:
		if not hasattr(p, prop):
			setattr(p, prop, 0)
	return p

def merge(player_from, player_into):
	for key in _ZERO_PROPERTIES:
		val = getattr(player_from, key)
		val_old = getattr(player_into, key)
		setattr(player_into, key, val + val_old)
	for w in _STAT_WEAPONS.values():
		wstats = getattr(player_into, w)
		for attr in ['shots', 'hits', 'kills', 'deaths']:
			wstats[attr] = getattr(player_from, w)[attr]

def merge_player_lines(lines):
	players = dict()
	for line in lines:
		player = read_player_line(line)
		if not player.nick in players:
			players[player.nick] = player
		else:
			merge(player, players[player.nick])
	for nick, player in players.items():
		yield player

def append_nicklog(fh, games):
	for game in games:
		for player in game.players.values():
			if not hasattr(player, 'team_id'):
				continue
			fh.write("%s\n" % player_line(player))

