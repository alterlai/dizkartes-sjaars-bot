import mechanize
import bs4 as bs
from http.cookiejar import CookieJar
import config as cfg
import pandas as pd

ACCEPTED_PROFILES = pd.DataFrame(columns=['Naam', 'verbanden', '#verbanden', 'Telefoon', 'Geboortedatum', 'E-mail'])

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
			parse_profile(page, verbanden)
			print("Added person")
			continue
		else:
			for i in range(len(verbanden)):
				if verbanden[i] not in ignore:
					print("[%d] -> %s" % (i, verbanden[i]))
			ans = int(input(":"))

			if ans == -1:
				ignore.update(verbanden)			# voeg alle verbanden toe aan de ignore list
			else:
				parse_profile(page, verbanden)
				accept.add(verbanden[ans])	 	# voeg toe aan accepted.
				verbanden.remove(verbanden[ans])
				ignore.update(verbanden)				# voeg de rest van de verbanden toe aan ignored
	return


def parse_profile(page, verbanden):
	global ACCEPTED_PROFILES
	data = {}

	data['Naam'] = page.findAll("h1")[1].getText()
	data['verbanden'] = verbanden
	data['#verbanden'] = len(verbanden)

	""" 
	Vanwege de grafwebsite die dizkartes heeft is een oplossing die werkt. Lelijk als de nacht.
	Deze fixt geboortedatum, email en nummer.
	"""
	info_divs = page.find("div", {'class': ["col-sm-9 spacing-small"]}).findChildren()
	add_next = False
	for item in info_divs:
		if add_next:
			data[string] = str.strip(item.getText())
			add_next = False
		string = str.strip(item.getText())
		if string in ACCEPTED_PROFILES.columns:
			add_next = True

	ACCEPTED_PROFILES = ACCEPTED_PROFILES.append(data, ignore_index=True)

main()
ACCEPTED_PROFILES.to_excel("output.xlsx")