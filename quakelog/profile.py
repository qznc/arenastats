from replay import _ZERO_PROPERTIES
from report import _WEAPON_NAMES, _WEAPONS
from nicklog import merge_player_lines
from utils import Toggler, googlechart_url

import os

def _player_overview(player):
	odd = Toggler("even", "odd")
	html = "<h2>Totals</h2>"
	html += '<table class="overview">'
	html += '<tr class="%s"><th>Kills</th><td>%d</td></tr>\n' % (odd, player.kill_count)
	html += '<tr class="%s"><th>Deaths</th><td>%d</td></tr>\n' % (odd, player.death_count)
	html += '<tr class="%s"><th>Caps</th><td>%d</td></tr>\n' % (odd, player.flag_caps)
	html += '<tr class="%s"><th>Suicides</th><td>%d</td></tr>\n' % (odd, player.suicides)
	html += '<tr class="%s"><th>Team Kills</th><td>%d</td></tr>\n' % (odd, player.team_kills)
	html += '<tr class="%s"><th>Health</th><td>%d</td></tr>\n' % (odd, player.health)
	html += '<tr class="%s"><th>Armor</th><td>%d</td></tr>\n' % (odd, player.armor)
	html += '</table>\n'
	return html

def _average_weapon_row(row):
	"""Interpolate value series by replaceing zeros with average values"""
	i = 0
	while i < len(row):
		if row[i] > 0.0:
			i += 1
			continue
		j = i+1
		while j < len(row): # search end of zero series
			if row[j] > 0.0:
				break
			j += 1
		if j == len(row): # edge case: end reached
			if j > i+1:
				j -= 1
				row[j] = row[i]
			else:
				break
		if i == 0: # edge case: started with zeros
			row[i-1] = row[j]
		diff = (row[j] - row[i-1]) / (1+j-i)
		plus = row[i-1]
		for k in xrange(i, j):
			plus += diff
			row[k] = plus
		i = j
	return row

def _hitrate_data(player_timeline):
	data = []
	for p in player_timeline:
		datapoint = []
		for weapon,x,y in _WEAPONS:
			wdata = getattr(p, weapon, {}) 
			datapoint.append(wdata.get('hitrate', 0))
		data.append(datapoint)
	data = map(list, zip(*data))
	avg_data = [_average_weapon_row(lst[:]) for lst in data]
	return data, avg_data

def _stat_development(player_timeline):
	html = "<h2>Stat Development</h2>\n"
	data = "|".join([
		",".join(str(p.kill_count) for p in player_timeline),
		",".join(str(p.death_count) for p in player_timeline),
		",".join(str(p.flag_caps) for p in player_timeline),
		])
	url="http://chart.apis.google.com/chart?cht=lc&chs=450x150&chd=t:%s&chdl=Frags|Deaths|Caps&chco=FF0000,00FF00,0000FF" % data
	html += '<img src="%s" />\n' % url
	return html

def merge(player_into, player_from):
	for key in _ZERO_PROPERTIES:
		val = getattr(player_from, key)
		val_old = getattr(player_into, key)
		setattr(player_into, key, val + val_old)
	for w,x,y in _WEAPONS:
		wstats = getattr(player_into, w)
		for attr in ['shots', 'hits', 'kills', 'deaths']:
			wstats[attr] = getattr(player_from, w)[attr]
	return player_into

_ODD_CLASS = {True: 'odd', False: 'even'}
_HTML= """\
<html>
<head>
	<title>%s</title>
	<style>
	tr.odd { background-color: #ddd; }
	th { font-weight: normal; text-align: left; }
	</style>
</head>
<body>
	<h1>%s profile</h1>
	<h2>Hitrate Development</h2>
	<script type="text/javascript" src="media/protovis-3.1/protovis-d3.1.js"></script>
	<script type="text/javascript" src="media/hitrate_diagram.js"></script>
	<script type="text/javascript+protovis">
	%s
	draw_hitrate(hitrate_points, hitrate_points_interpolated, weapons);
	</script>
	%s
</body>
</html>
"""
def player_profile(player_timeline):
	player = reduce(merge, player_timeline)
	weapon_list = [_WEAPON_NAMES[w].replace("&nbsp;", " ") for (w,y,z) in _WEAPONS]
	data, avg_data = _hitrate_data(player_timeline)
	data = "var hitrate_points = %s;\n" % (str(data))
	data += "var hitrate_points_interpolated = %s;\n" % (str(avg_data))
	data += "var weapons = %s;\n" % weapon_list
	html = ""
	html += _stat_development(player_timeline)
	html += _player_overview(player)
	html += '\n<table style="font-size: 0.8em; float: right;">'
	odd = False
	for prop in _ZERO_PROPERTIES:
		html += '<tr class="%s"><th>%s</th><td>%d</td></tr>\n' % (_ODD_CLASS[odd], prop, getattr(player, prop))
		odd = not odd
	for weapon,x,y in _WEAPONS:
		for key, val in getattr(player, weapon).items():
			html += '<tr class="%s"><th>%s %s</th><td>%d</td></tr>\n' % (_ODD_CLASS[odd], weapon, key, val)
	html += "</table>\n"
	return _HTML % (player.nick, player.nick, data, html)

def _player_overview_item(player_timeline):
	slug_nick = player_timeline[0].slug_nick
	nick = player_timeline[0].nick
	return '<p><a href="p_%s.html">%s</a></p>' % (slug_nick, nick)

def _player_elos(timelines):
	elos = [[p.elo for p in line] for line in timelines]
	nicks = [p[0].nick for p in timelines]
	url = googlechart_url(data=elos, legend=nicks)
	print url
	return '<img src="%s" alt="player ELO ratings" />\n' % url

_OVERVIEW_FILE = "players.html"
_OVERVIEW_HTML= """\
<html>
<head>
	<title>Player Overview</title>
</head>
<body>
	<h1>Player Overview</h1>
	%s
</body>
</html>
"""
def player_overview(timelines):
	html = ""
	html += _player_elos(timelines)
	for player_timeline in timelines:
		html += _player_overview_item(player_timeline)
	fh = open(_OVERVIEW_FILE, 'w')
	fh.write(_OVERVIEW_HTML % html)
	fh.close()

def write_profiles(options):
	fh = open(options.nicklog)
	timelines = list(merge_player_lines(fh))
	fh.close()
	for player_timeline in timelines:
		fname = os.path.join(options.directory, "p_"+player_timeline[0].slug_nick+".html")
		pfh = open(fname, 'w')
		pfh.write(player_profile(player_timeline))
		pfh.close()
	player_overview(timelines)
