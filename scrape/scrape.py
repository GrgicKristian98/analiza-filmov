import json
import requests
from bs4 import BeautifulSoup


# S to funkcijo s strani boxofficemojo.com pridobimo filme z največjim zaslužkom v določenem letu in jih shranimo v
# filmi.json datoteko
def pridobi_filme():
    filmi_list = []
    leto_index = 1977

    while leto_index <= 2020:
        stran = 'https://www.boxofficemojo.com/year/world/%s/' % str(leto_index)
        html_text = requests.get(stran).text
        soup = BeautifulSoup(html_text, 'lxml')

        # Implementacija pridobivanja podatkov

        filmi = soup.findAll('tr')
        del filmi[0]
        for film in filmi:
            naziv = film.find('a', class_='a-link-normal').text
            zasluzek = film.findAll('td', class_='a-text-right mojo-field-type-money')[0].text

            zasluzek = zasluzek.replace('$', '').replace(',', '')

            temp_dict = {
                'naziv': naziv,
                'zasluzek': int(zasluzek),
                'leto_izida': leto_index
            }
            filmi_list.append(temp_dict)

        leto_index = leto_index + 1

    with open('filmi.json', 'w') as file:
        json.dump(filmi_list, file)


# S to funkcijo s strani metacritic.com pridobimo podrobnosti vseh filmov, ki smo jih shranili v datoteko filmi.json
def pridobi_podrobnosti_filmov_metacritic():
    filmi_podrobno_list = []
    znaki = [', ', ': ', ' ']
    znaki_2 = ["'", '?', '&' '& ']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36'}

    with open('filmi.json', 'r') as file:
        filmi = json.load(file)

    # index = 0
    for film in filmi:
        # index = index + 1

        naziv = film['naziv']
        zasluzek = film['zasluzek']
        pravo_leto_izida = film['leto_izida']

        naziv_preurejen = naziv
        for z in znaki:
            naziv_preurejen = naziv_preurejen.replace(z, '-')
        for z in znaki_2:
            naziv_preurejen = naziv_preurejen.replace(z, '')

        # soup = ''
        # mesec_izida = ''
        # datum_izida = ''

        # request = 0
        # pravi_film = False

        naziv_preurejen = naziv_preurejen.lower()
        stran = 'https://www.metacritic.com/movie/%s' % naziv_preurejen

        # ------------ PRVA ITERACIJA (pridobivanje ustreznega filma glede na leto izdaje) -----------------------------
        # while not pravi_film:
        #     request = requests.get(stran, headers=headers)
        #
        #     if request.status_code == 200:
        #         html_text = request.text
        #         soup = BeautifulSoup(html_text, 'lxml')
        #
        #         datum_izida = soup.find('span', class_='release_date')
        #
        #         if datum_izida is not None:
        #             datum_izida = datum_izida.findAll('span')
        #             if len(datum_izida) == 2:
        #                 datum_izida = datum_izida[1].text
        #             else:
        #                 break
        #             if datum_izida != 'TBA':
        #                 mesec_izida = datum_izida.split(',')[0].split()[0]
        #                 pridobljeno_leto_izida = datum_izida.split(',')[1]
        #             else:
        #                 break
        #         else:
        #             break
        #
        #         if int(pridobljeno_leto_izida) != pravo_leto_izida:
        #             naziv_preurejen = naziv_preurejen + '-' + str(pravo_leto_izida)
        #             stran = 'https://www.metacritic.com/movie/%s' % naziv_preurejen
        #         else:
        #             pravi_film = True
        #     else:
        #         break

        request = requests.get(stran, headers=headers)

        print(naziv_preurejen)

        if request.status_code == 200:
            html_text = request.text
            soup = BeautifulSoup(html_text, 'lxml')

            datum_izida = soup.find('span', class_='release_date')

            if datum_izida is not None:
                datum_izida = datum_izida.findAll('span')
                if len(datum_izida) == 2:
                    datum_izida = datum_izida[1].text
                else:
                    continue
                if datum_izida != 'TBA':
                    mesec_izida = datum_izida.split(',')[0].split()[0]
                    pridobljeno_leto_izida = datum_izida.split(',')[1]
                else:
                    continue
            else:
                continue

            if pridobljeno_leto_izida.strip().isdigit():
                if int(pridobljeno_leto_izida) == pravo_leto_izida:
                    ocena_kritikov = ''
                    ocena_uporabnikov = ''

                    ocena_kritikov_positive_perfect = soup.find('span', class_='metascore_w larger movie positive '
                                                                               'perfect')
                    ocena_kritikov_positive = soup.find('span', class_='metascore_w larger movie positive')
                    ocena_kritikov_mixed = soup.find('span', class_='metascore_w larger movie mixed')
                    ocena_kritikov_negative = soup.find('span', class_='metascore_w larger movie negative')
                    ocena_kritikov_tbd = soup.find('span', class_='metascore_w larger movie tbd')

                    if ocena_kritikov_positive_perfect is not None:
                        ocena_kritikov = ocena_kritikov_positive_perfect.text
                    elif ocena_kritikov_positive is not None:
                        ocena_kritikov = ocena_kritikov_positive.text
                    elif ocena_kritikov_mixed is not None:
                        ocena_kritikov = ocena_kritikov_mixed.text
                    elif ocena_kritikov_negative is not None:
                        ocena_kritikov = ocena_kritikov_negative.text
                    elif ocena_kritikov_tbd is not None:
                        ocena_kritikov = ocena_kritikov_tbd.text

                    ocena_uporabnikov_positive_perfect = soup.find('span',
                                                                   class_='metascore_w user larger movie positive perfect')
                    ocena_uporabnikov_positive = soup.find('span', class_='metascore_w user larger movie positive')
                    ocena_uporabnikov_mixed = soup.find('span', class_='metascore_w user larger movie mixed')
                    ocena_uporabnikov_negative = soup.find('span', class_='metascore_w user larger movie negative')
                    ocena_uporabnikov_tbd = soup.find('span', class_='metascore_w user larger movie tbd')

                    if ocena_uporabnikov_positive_perfect is not None:
                        ocena_uporabnikov = ocena_uporabnikov_positive_perfect.text
                    elif ocena_uporabnikov_positive is not None:
                        ocena_uporabnikov = ocena_uporabnikov_positive.text
                    elif ocena_uporabnikov_mixed is not None:
                        ocena_uporabnikov = ocena_uporabnikov_mixed.text
                    elif ocena_uporabnikov_negative is not None:
                        ocena_uporabnikov = ocena_uporabnikov_negative.text
                    elif ocena_uporabnikov_tbd is not None:
                        ocena_uporabnikov = ocena_uporabnikov_tbd.text

                    if ocena_kritikov == 'tbd':
                        ocena_kritikov = None
                    else:
                        ocena_kritikov = int(ocena_kritikov)
                    if ocena_uporabnikov == 'tbd':
                        ocena_uporabnikov = None
                    else:
                        ocena_uporabnikov = float(ocena_uporabnikov)

                    trajanje_neurejen = soup.find('div', class_='runtime')
                    produkcijska_hisa = soup.find('span', class_='distributor')
                    oznacba_primernosti = soup.find('div', class_='rating')
                    reziser = soup.find('div', class_='director')
                    zanri = soup.find('div', class_='genres')
                    korenski_element_opisa = soup.find('div', class_='summary_deck details_section')

                    trajanje_urejen = ''
                    if trajanje_neurejen is not None:
                        trajanje_neurejen = trajanje_neurejen.findAll('span')[1].text
                        razdeljen_tekst = trajanje_neurejen.split()
                        if len(razdeljen_tekst) == 2:
                            minute_tekst = razdeljen_tekst[1]
                            if minute_tekst == 'min':
                                trajanje_urejen = trajanje_neurejen.replace(' min', '')
                            elif minute_tekst == 'mins':
                                trajanje_urejen = trajanje_neurejen.replace(' mins', '')
                        else:
                            trajanje_urejen = trajanje_neurejen.strip()
                        trajanje_urejen = int(trajanje_urejen)
                    else:
                        trajanje_urejen = None

                    if produkcijska_hisa is not None:
                        produkcijska_hisa = produkcijska_hisa.find('a').text
                    else:
                        produkcijska_hisa = None

                    if oznacba_primernosti is not None:
                        oznacba_primernosti = oznacba_primernosti.findAll('span')[1].text.strip()
                    else:
                        oznacba_primernosti = None

                    if reziser is not None:
                        reziser = reziser.find('a').text
                    else:
                        reziser = None

                    if zanri is not None:
                        zanri = zanri.findAll('span')[1].findAll('span')
                    else:
                        zanri = None

                    list_zanrov = []
                    for zanr in zanri:
                        list_zanrov.append(zanr.text)
                    urejen_list_zanrov = sorted(list_zanrov)

                    if korenski_element_opisa is not None:
                        opis_1 = korenski_element_opisa.find('span', class_='blurb blurb_collapsed')
                        if opis_1 is not None:
                            opis = opis_1.text
                        else:
                            opis_2 = korenski_element_opisa.findAll('span')[1].find('span')
                            opis = opis_2.text
                    else:
                        opis = None

                    temp_dict = {
                        'naziv': naziv,
                        'zasluzek': zasluzek,
                        'ocena_kritikov': ocena_kritikov,
                        'ocena_uporabnikov': ocena_uporabnikov,
                        'trajanje_filma': trajanje_urejen,
                        'mesec_izida': mesec_izida,
                        'leto_izida': pravo_leto_izida,
                        'produkcijska_hisa': produkcijska_hisa,
                        'oznacba_primernosti_filma': oznacba_primernosti,
                        'reziser': reziser,
                        'zanri_filma': urejen_list_zanrov,
                        'opis': opis
                    }
                    filmi_podrobno_list.append(temp_dict)

                    # if index > 20:
                    #     break

                else:
                    print("NAPAKA - leto izdaje filma ni ustrezno!")
                    continue
            else:
                print("NAPAKA - pridobljeni podatek ni število!")
                continue
        else:
            print("NAPAKA - stran ne obstaja!")
            continue

    with open('filmi_podrobno.json', 'w') as file:
        json.dump(filmi_podrobno_list, file)


# S to funkcijo s strani rottentomatoes.com pridobimo podrobnosti vseh filmov, ki smo jih shranili v datoteko filmi.json
def pridobi_podrobnosti_filmov_rotten_tomatoes():
    filmi_podrobno_list = []
    znaki = ["?", "!", ":", "&", "'", ",", "- ", "-", "."]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36'}

    with open('filmi.json', 'r') as file:
        filmi = json.load(file)

    # index = 0
    for film in filmi:
        # index = index + 1

        naziv = film['naziv']
        pravo_leto_izida = film['leto_izida']

        naziv_preurejen = naziv.lower()
        for z in znaki:
            naziv_preurejen = naziv_preurejen.replace(z, '')
        naziv_preurejen = naziv_preurejen.replace(' ', '_')

        stran = 'https://www.rottentomatoes.com/m/%s' % naziv_preurejen

        request = requests.get(stran, headers=headers)

        print(naziv_preurejen)

        if request.status_code == 200:
            html_text = request.text
            soup = BeautifulSoup(html_text, 'lxml')

            pridobljeno_leto_izida = soup.find('p', class_='scoreboard__info')

            if pridobljeno_leto_izida is not None:
                pridobljeno_leto_izida = pridobljeno_leto_izida.text.split(',')[0]
            else:
                print("NAPAKA - vsebina teksta je 'None'!")
                continue

            if pridobljeno_leto_izida.isdigit():
                if int(pridobljeno_leto_izida) == pravo_leto_izida:
                    score_board_attrs = soup.find('score-board').attrs

                    ocena_kritikov = score_board_attrs['tomatometerscore']
                    ocena_uporabnikov = score_board_attrs['audiencescore']

                    st_ocen_kritikov = soup.find('a', {'data-qa': 'tomatometer-review-count'})
                    st_ocen_uporabnikov = soup.find('a', {'data-qa': 'audience-rating-count'})

                    if ocena_kritikov != '':
                        ocena_kritikov = int(ocena_kritikov)
                    else:
                        ocena_kritikov = None

                    if ocena_uporabnikov != '':
                        ocena_uporabnikov = int(ocena_uporabnikov)
                    else:
                        ocena_uporabnikov = None

                    if st_ocen_kritikov is not None:
                        st_ocen_kritikov = int(st_ocen_kritikov.text.split()[0])
                    else:
                        st_ocen_kritikov = None

                    if st_ocen_uporabnikov is not None:
                        st_ocen_uporabnikov = st_ocen_uporabnikov.text.split()
                        if st_ocen_uporabnikov[0] != 'Fewer':
                            st_ocen_uporabnikov = st_ocen_uporabnikov[0].replace(',', '')
                        else:
                            st_ocen_uporabnikov = st_ocen_uporabnikov[2]
                        if st_ocen_uporabnikov[-1] == '+':
                            st_ocen_uporabnikov = int(st_ocen_uporabnikov.replace('+', ''))
                        else:
                            st_ocen_uporabnikov = int(st_ocen_uporabnikov)
                    else:
                        st_ocen_uporabnikov = None

                    temp_dict = {
                        'naziv': naziv,
                        'ocena_kritikov': ocena_kritikov,
                        'ocena_uporabnikov': ocena_uporabnikov,
                        'st_ocen_kritikov': st_ocen_kritikov,
                        'st_ocen_uporabnikov': st_ocen_uporabnikov,
                        'leto_izida': int(pridobljeno_leto_izida)
                    }
                    filmi_podrobno_list.append(temp_dict)
                else:
                    print("NAPAKA - leto izdaje filma ni ustrezno!")
                    continue
            else:
                print("NAPAKA - pridobljeni podatek ni število!")
                continue
        else:
            print("NAPAKA - stran ne obstaja!")
            continue

        # if index > 10:
        #     break

    with open('filmi_podrobno_rt.json', 'w') as file:
        json.dump(filmi_podrobno_list, file)


if __name__ == '__main__':
    # pridobi_filme()
    pridobi_podrobnosti_filmov_metacritic()
    # pridobi_podrobnosti_filmov_rotten_tomatoes()
