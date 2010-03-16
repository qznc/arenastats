# -!- encoding: utf-8 -!-

def gen_player_links(players, team_id):
	ps = list()
	for p in players:
		if hasattr(p, 'team_id') and p.team_id == team_id:
			ps.append('<a href="#%s">%s</a>' % (p.slug_nick, p.nick))
	return ", ".join(ps)

def pluralize(number, unit, zero=True):
	if 0 == number and not zero:
		return ""
	elif 1 == number:
		return "%d %s" % (number, unit)
	else: # plural
		return "%d %ss" % (number, unit)

def general_game_info(game, levelshots):
	html = '<div class="game_stats"\n'
	html += '<img src="%s/%s.jpg" />' % (levelshots, game.mapname)
	html += '<table class="game_info">\n'
	html += "<tr><td>Map</td><td>%s</td></tr>\n" % (game.mapname)
	html += "<tr><td>Date</td><td>%s</td></tr>\n" % (game.datetime)
	html += "<tr><td>Game type</td><td>%s</td></tr>\n" % (game.gametype)
	html += '<tr><td>Total Frags</td><td><a href="#kill_matrix">%d</a></td></tr>\n' % (game.frag_count)
	html += "</table>\n"
	html += '<table>\n<tr class="game_result">\n'
	html += '<td class="team_red">%s</td>' % game.teams[1].capture_count
	html += "<td>vs</td>"
	html += '<td class="team_blue">%s</td>' % game.teams[2].capture_count
	html += "</tr><tr>"
	players = game.sortedPlayers()
	html += '<td>%s</td><td> </td><td>%s</td>' % (gen_player_links(players, 1), gen_player_links(players, 2))
	html += "</tr>\n</table>\n"
	html += "</div>\n\n"
	return html

def _award_html(award):
	return '<span class="award" title="%s (%s)">%s</span>' %\
			(award.description, award.value, award.name)

def _player_html(player):
	return '<a class="team_%s" href="#%s">%s</a>' %\
			(player.team_color, player.slug_nick, player.nick)

def emph_percentage(hitrate, lower_bound):
	if hitrate > lower_bound:
		return "<strong>%.1f%%</strong>" % hitrate
	else:
		return "%.1f%%" % hitrate

_ODD_CLASS = {True: ' class="odd"', False: ''}
_WEAPONS = [
# internal key, descriptive name, hitrate emphasize
	('gauntlet', 'Gauntlet', 1),
	('machinegun', "Machine&nbsp;gun", 30),
	('shotgun', 'Shotgun', 20),
	('rocketlauncher', 'Rocket&nbsp;launcher', 30),
	('plasmagun', 'Plasma&nbsp;gun', 20),
	('grenadelauncher', 'Grenade&nbsp;launcher', 10),
	('lightninggun', 'Lightning&nbsp;gun', 30),
	('railgun', 'Railgun', 40),
	('bfg', 'Big&nbsp;F***ing&nbsp;Gun', 1),
]
_WEAPON_NAMES = dict()
for w, name, x in _WEAPONS:
	_WEAPON_NAMES[w] = name
def player_info(player):
	html = '<div class="player_stats" id="%s">\n' % player.slug_nick
	html += '<table class="player_info">\n'
	html += '<tr><td colspan="2" class="name team_%s"><strong>%s</strong></td></tr>\n' % (player.team_color, player.nick)
	html += '<tr><th>Weapons</th><td><span title="Most shots (normalized by reload times)">%s</span> / <span title="Most kills">%s</span></td></tr>\n' %\
			(_WEAPON_NAMES[player.weapon_most_shots], _WEAPON_NAMES[player.weapon_most_kills])
	html += '<tr class="odd"><th>Frags</th><td>%d &nbsp; (%s, %s, %s)</td></tr>\n' % (player.kill_count, pluralize(player.flag_carrier_kills, "carrier"), pluralize(player.team_kills, "mate"), pluralize(player.flag_assist_kills, "flag assist"))
	html += '<tr><th>Damage given</th><td>%d &nbsp; (%.0f per frag)</td></tr>\n' % (getattr(player, 'damage_given', -1), 100 * player.dmg_kill_ratio)
	html += '<tr class="odd"><th>Team damage given</th><td>%d (%s)</td></tr>\n' % (getattr(player, 'team_damage_given', -1), pluralize(player.team_kills, "frag"))
	html += '<tr><th>Damage received</th><td>%d &nbsp; (collected %d health %d armor)</td></tr>\n' % (getattr(player, 'damage_received', -1), player.health, player.armor)
	html += '<tr class="odd"><th>Damage rate</th><td>%s</td></tr>\n' % (emph_percentage(player.damage_rate * 100.0, 110))
	html += '<tr><th>Flag caps</th><td>%d</td></tr>\n' % (player.flag_caps)
	html += '<tr class="odd"><th>Flag returns</th><td>%d &nbsp; (%s)</td></tr>\n' % (player.flag_returns, pluralize(player.flag_assist_returns, "assist"))
	html += '<tr><th>Suicides</th><td>%d</td></tr>\n' % (player.suicides)
	html += '<tr class="odd"><th>Defends</th><td>%s &nbsp; %s &nbsp; %s</td></tr>\n' % (pluralize(player.flag_defends, "flag"), pluralize(player.base_defends, "base"), pluralize(player.carrier_defends, "carrier"))
	html += '<tr><th>Streaks</th><td>%s &nbsp; %s &nbsp; %s</td></tr>\n' % (pluralize(player.kill_streak, "frag"), pluralize(player.death_streak, "death"), pluralize(player.cap_streak, "cap"))
	html += '<tr class="odd"><th>Score</th><td>%d</td></tr>\n' % (player.score)
	awards = ", ".join(_award_html(a) for a in player.awards)
	html += "<tr><th>Awards&nbsp;(%d)</th><td>%s</td></tr>\n" % (len(player.awards), awards)
	html += '<tr class="odd"><th>Easiest Prey</th><td>%s</td></tr>\n' % (player.easiest_prey.nick)
	html += "</table>\n"
	html += '<table class="weapon_info">\n'
	html += "<tr><th>Weapon</th><th>Hitrate</th><th>Fragrate</th></tr>\n"
	odd = True
	for w, wname, emph_rate in _WEAPONS:
		stats = getattr(player, w, None)
		if not stats:
			continue
		if int(stats['shots']) < 1:
			continue
		odd_class = _ODD_CLASS[odd]
		html += "<tr%s><td>%s</td>" % (odd_class, wname)
		html += '<td class="rate">%s&nbsp;/&nbsp;%s = &nbsp; %s</td>' %\
						(stats['hits'], stats['shots'], emph_percentage(stats['hitrate']*100, emph_rate))
		html += '<td class="rate">%s&nbsp;/&nbsp;%s = &nbsp; %s</td>' %\
						(stats['kills'], stats['deaths'], emph_percentage(stats['killrate']*100, 100))
		html += "</tr>\n"
		odd = not odd
	html += "</table>\n"
	html += "</div>\n"
	return html

def kill_matrix(game):
	html = "<table>\n"
	def filter(p):
		return hasattr(p, 'player_kill_count')
	ps = game.sortedPlayers(include=filter)
	html += "<tr><th>Frags</th>"
	for p in ps:
		html += '<th class="team_%s">%s</th>' % (p.team_color, p.nick)
	html += "<th>Total Frags</th></tr>\n"
	odd = False
	for p in ps:
		odd_class = _ODD_CLASS[odd]
		html += '<tr%s><th class="team_%s">%s</th>' % (odd_class, p.team_color, p.nick)
		for p2 in ps:
			kill_count = p.player_kill_count.get(p2, 0)
			teamkill = ""
			if p.team_id == p2.team_id and kill_count > 0:
				teamkill = ' teamkill'
			html += '<td class="kill_count %s">%d</td>' % (teamkill, kill_count)
		html += '<td class="kill_count">%s</td></tr>\n' % (p.kill_count)
		odd = not odd
	html += "<tr%s><th>Total deaths</th>" % _ODD_CLASS[odd]
	for p in ps:
		html += '<td class="kill_count">%s</td>' % (p.death_count)
	html += "<td></td></tr>\n"
	html += "</table>"
	return html
			
def award_table(players):
	html = ""
	awards = list()
	for p in players:
		if not hasattr(p, 'awards'):
			continue
		for a in p.awards:
			awards.append((p,a))
	awards.sort(cmp=lambda (p,a), (p2,a2): cmp(a.name,a2.name))
	for p, a in awards:
		winner = _player_html(p)
		award = _award_html(a)
		img = a.img_url or "media/award.png"
		html += u'<div class="award"><div class="symbol"><img src="%s" alt="Award" /></div><div class="name">%s</div>\
		<div class="winner">%s</div></div>\n' % (img, award, winner)
	return html.encode('utf-8')

_HTML = """\
<html>
<head>
	<title>ArenaStats Game Report - %s</title>
	<link rel="stylesheet" type="text/css" href="media/style.css" /
</head>
<body>
	<h1>ArenaStats Game Report</h1>
	%s
	<div id="footer">
		This space intentionally left blank.
	</div>
</body></html>
"""

def html_report(game, levelshots):
	html = ""
	html += general_game_info(game, levelshots)
	html += '<div id="award_table">\n'
	html += award_table(game.sortedPlayers())
	html += '</div>\n'
	html += '<div id="kill_matrix">\n'
	html += kill_matrix(game)
	html += '</div>\n'
	html += '<div id="red_team" class="red_players">\n'
	for p in game.sortedPlayers():
		if hasattr(p, 'team_id') and p.team_id == 1:
			html += player_info(p)
	html += '</div>\n'
	html += '<div id="blue_team" class="blue_players">\n'
	for p in game.players.values():
		if hasattr(p, 'team_id') and p.team_id == 2:
			html += player_info(p)
	html += '</div>\n'
	return _HTML % (game.title, html)
