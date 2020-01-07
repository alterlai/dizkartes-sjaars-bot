import mechanize
import bs4 as bs
import urllib
from http.cookiejar import CookieJar
import config as cfg


ACCEPTED_PROFILES = set()

def main():
	url = "https://www.dizkartes.nl/verbanden/2830"
	base_url = "https://www.dizkartes.nl"
	auth_url = "https://www.dizkartes.nl/login"

	ignore = set()		# verbanden om te negeren
	accept = set()		# verbanden die we wel willen

	# Authentication
	cj = CookieJar()
	br = mechanize.Browser()
	br.set_cookiejar(cj)

	br.open(auth_url)
	br.select_form(nr=0)
	br.form['login_username'] = cfg.username
	br.form['login_password'] = cfg.password
	br.submit()

	soup = bs.BeautifulSoup(br.open(url), 'html5lib')
	data = [link for link in soup.findAll('div', {"class": "content"}) if 'profiel' in str(link)]

	# get all links from the page.
	links = []
	for div in data:
		links += [link['href'] for link in div.findAll('a') if 'profiel' in str(link)]

	for profiel_url in links:
		print(profiel_url)
		page = bs.BeautifulSoup(br.open(base_url+profiel_url), 'html5lib')

		verbanden = []
		for verband_div in page.findAll("div", {"class": "col-xs-6"}):
			for verband in verband_div.select('a'):
				verbanden.append(verband.getText())
		print("Is een van deze verbanden een mannen JC?")
		print("kies -1 voor geen van deze verbanden.")

		# Ignore alle verbanden die al in de ignore lijst staan.
		if all(elem in ignore for elem in verbanden):
			print("Ignored person")
			continue
		if any(elem in accept for elem in verbanden):
			add_profile(page)
			print("Added person")
			continue
		else:
			for i in range(len(verbanden)):
				if verbanden[i] not in ignore:
					print("[%d] -> %s" % (i, verbanden[i]))
			ans = input(":")

			if ans == -1:
				ignore.add(set(verbanden))			# voeg alle verbanden toe aan de ignore list
			else:
				accept.add(verbanden[int(ans)])	 	# voeg toe aan accepted.
				verbanden.remove(verbanden[int(ans)])
				ignore.update(verbanden)				# voeg de rest van de verbanden toe aan ignored
				add_profile(page)

def add_profile(page):
	global ACCEPTED_PROFILES
	ACCEPTED_PROFILES.add(page)

main()
print(ACCEPTED_PROFILES)