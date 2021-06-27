Tämä on keskustelusovellus, jonka ominaisuuksiin kuuluu:

- Eri keskustelupalstoille pääsy
- Keskustelun/Keskusteluaiheviestin julkaiseminen halutulle palstalle
- Viestien/Kommenttien lähettäminen eri keskusteluihin
- Omia keskusteluaiheita ja viestejä voi muokata tai poistaa
- Admin voi luoda uuden keskustelupalstan tai poistaa olemassa olevan
- Tietokantaan voi luoda salaisen palvelimen komentoriviä käyttäen ja määrittää ketkä pääsevät palstalle
- Voi hakea keskusteluaiheita ja viestejä hakusanalla

Sovelluksen toimintaperiaate on se, että käyttäjän syöttämät tiedot otetaan vastaan ja viedään tietokantaan.
Tieto otetaan tietokannasta ulos ja näytetään sovelluksen front-end:ssa.

Sovellus on toteutettu käyttäen postgresql ja flask. Sovellusta voi testata osoitteessa: https://test-forums.herokuapp.com/ 
admin käyttäjää voi kokeilla käyttäjänimellä: admin ja salasanalla: admin123
Salainen palvelin admininpalsta näkyy vain jos on kirjautunut sisään admin käyttäjällä
