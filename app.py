import streamlit as st
from datetime import date, timedelta
import io
import zipfile

DEFAULT_CLIENT = 'Klient: Id oddzialu: 24, Pelna nazwa oddzialu: Dachser Koninko, Kraj: PL, Kod pocztowy: 95-010, Miasto: Strykow, NIP: 7281006020'
DEFAULT_PRICE = '892 EUR'

TEMPLATES = {
    'Landsberg': {
        'client': DEFAULT_CLIENT,
        'price': DEFAULT_PRICE,
        'via_text': 'Slubice',
        'stops': [
            {'type': 'ZALADUNEK',        'name': 'Dachser Koninko',    'street': 'Drukarska',              'city': '60-023; Koninko; PL',      'time': '18:30', 'day_offset': 0},
            {'type': 'ROZLADUNEK',       'name': 'Dachser Radeburg',   'street': 'Thomas-Dachser-Str 1',   'city': '01471; Radeburg; DE',      'time': '02:30', 'day_offset': 1},
            {'type': 'ROZLADUNEK',       'name': 'Dachser Landsberg',  'street': 'Brehnaer Strasse 4',     'city': '06188; Landsberg; DE',     'time': '05:00', 'day_offset': 1},
            {'type': 'ZALADUNEK',        'name': 'Dachser Landsberg',  'street': 'Brehnaer Strasse 4',     'city': '06188; Landsberg; DE',     'time': '05:00', 'day_offset': 1},
            {'type': 'ROZLADUNEK',       'name': 'Dachser Schonefeld', 'street': 'Thomas-Dachser-Allee 2', 'city': '12529; Schonefeld; DE',    'time': '18:00', 'day_offset': 1},
            {'type': 'ROZLADUNEK POWROT','name': 'Dachser Koninko',    'street': 'Drukarska',              'city': '60-023; Koninko; PL',      'time': '',      'day_offset': 2},
        ]
    },
    'DSV Eupen': {
        'client': 'DSV ROAD NV, BE, 0404507618',
        'price': '692 EUR',
        'vehicle_reg': 'OKR2CN5',
        'via_text': 'Neunkirchen',
        'stops': [
            {'type': 'ZALADUNEK',        'name': 'Schenker',               'street': 'Siebeponisweg 9',  'city': '4700; Eupen; BE',              'time': '13:10', 'day_offset': 0},
            {'type': 'PRZELADUNEK',      'name': 'Schenker Deutschland AG','street': 'Boxbergweg 6',     'city': '66538; Neunkirchen; DE',       'time': '21:10', 'day_offset': 1},
            {'type': 'ROZLADUNEK POWROT','name': 'Schenker',               'street': 'Siebeponisweg 9',  'city': '4700; Eupen; BE',              'time': '13:10', 'day_offset': 2},
        ]
    },
    'Dachser Mouscron': {
        'client': 'SA DACHSER Belgium, BE 7700 Mouscron, VAT: BE 0415394184',
        'price': '1626 EUR',
        'via_text': 'Alsdorf / Koln',
        'stops': [
            {'type': 'ZALADUNEK',        'name': 'Dachser Mouscron',  'street': 'Hansestrasse 52',         'city': '7700; Mouscron; BE',        'time': '21:00', 'day_offset': 0},
            {'type': 'ROZLADUNEK',       'name': 'Dachser Alsdorf',   'street': 'Thomas-Dachser-Str 1',   'city': '52477; Alsdorf; DE',        'time': '01:30', 'day_offset': 1},
            {'type': 'ROZLADUNEK',       'name': 'Dachser Koln',      'street': 'Rue du Berger',           'city': '51149; Koln; DE',           'time': '03:00', 'day_offset': 1},
            {'type': 'ZALADUNEK',        'name': 'Dachser Koln',      'street': 'Rue du Berger',           'city': '51149; Koln; DE',           'time': '19:00', 'day_offset': 1},
            {'type': 'ROZLADUNEK POWROT','name': 'Dachser Wissous',   'street': 'Hansestrasse 52',         'city': '91320; Wissous; FR',        'time': '02:30', 'day_offset': 2},
        ]
    },
    'Bremen - Koninko': {
        'client': 'Klient: Id oddzialu: 20, Pelna nazwa oddzialu: Dachser Bremen, Kraj: DE, Kod pocztowy: 28197, Miasto: Bremen',
        'price': '723,71 EUR',
        'via_text': 'Schonefeld',
        'stops': [
            {'type': 'ZALADUNEK',        'name': 'Dachser Bremen',     'street': 'Senator-Blase-Strasse 23', 'city': '28197; Bremen; DE',     'time': '17:00', 'day_offset': 0},
            {'type': 'ROZLADUNEK',       'name': 'Dachser Schonefeld', 'street': 'Thomas-Dachser-Allee 2',  'city': '12529; Schonefeld; DE', 'time': '01:00', 'day_offset': 1},
            {'type': 'ROZLADUNEK POWROT','name': 'Dachser Sp. z o.o.','street': 'Drukarska',                'city': '60-023; Koninko; PL',   'time': '03:00', 'day_offset': 1},
        ]
    },
    'Koninko - Bremen': {
        'client': 'Klient: Id oddzialu: 24, Pelna nazwa oddzialu: Dachser Koninko, Kraj: PL, Kod pocztowy: 95-010, Miasto: Strykow, NIP: 7281006020',
        'price': '672 EUR',
        'via_text': 'Hamburg',
        'stops': [
            {'type': 'ZALADUNEK',        'name': 'Dachser Sp. z o.o.',             'street': 'Drukarska',               'city': '60-023; Koninko; PL',  'time': '12:34', 'day_offset': 0},
            {'type': 'ROZLADUNEK',       'name': 'Dachser Food Logistics Hamburg', 'street': 'Rungedamm 34',             'city': '21035; Hamburg; DE',   'time': '12:35', 'day_offset': 0},
            {'type': 'ROZLADUNEK POWROT','name': 'Dachser Bremen',                 'street': 'Senator-Blase-Strasse 23', 'city': '28197; Bremen; DE',    'time': '12:34', 'day_offset': 1},
        ]
    },
    'Willebroek': {
        'client': 'Klient: Id oddzialu: 151, Pelna nazwa oddzialu: Dachser Langenhagen, Kraj: DE, Kod pocztowy: 30855, Miasto: Langenhagen',
        'price': '1991 EUR',
        'via_text': 'Schonefeld / Magdeburg / Langenhagen',
        'stops': [
            {'type': 'ZALADUNEK',        'name': 'Dachser',                               'street': 'Schoondonkweg',            'city': '2830; Willebroek; BE',      'time': '16:00', 'day_offset': 0},
            {'type': 'ROZLADUNEK',       'name': 'Dachser Schonefeld',                    'street': 'Thomas-Dachser-Allee 2',  'city': '12529; Schonefeld; DE',     'time': '05:00', 'day_offset': 1},
            {'type': 'ROZLADUNEK',       'name': 'Dachser GmbH Logistikzentrum Magdeburg','street': 'Wormlitzer Strasse 2',     'city': '39126; Magdeburg; DE',      'time': '17:00', 'day_offset': 1},
            {'type': 'ROZLADUNEK',       'name': 'Dachser Langenhagen',                   'street': 'Kemptener Strasse',        'city': '30855; Langenhagen; DE',    'time': '19:00', 'day_offset': 1},
            {'type': 'ROZLADUNEK POWROT','name': 'Dachser',                               'street': 'Schoondonkweg',            'city': '2830; Willebroek; BE',      'time': '04:00', 'day_offset': 2},
        ]
    }
}

def is_workday(d):
    return d.weekday() < 5

def generate_order(template_name, start_date, day_num):
    t = TEMPLATES[template_name]
    load_date = start_date + timedelta(days=day_num)
    ref = load_date.strftime('%Y-%m-%d')
    client = t['client']
    price = t['price']
    via = t['via_text']
    vreg = t.get('vehicle_reg', '')
    vehicle_line = 'Nr rejestracyjny: ' + vreg + chr(10) if vreg else ''
    stops_text = ''
    for i, stop in enumerate(t['stops'], 1):
        stype = stop['type']
        sname = stop['name']
        sstreet = stop['street']
        scity = stop['city']
        stime = stop['time']
        stop_date = load_date + timedelta(days=stop['day_offset'])
        sdate = stop_date.strftime('%d.%m.%Y')
        time_line = '  Godzina: ' + stime + ' (' + sdate + ')' + chr(10) if stime else ''
        stops_text += stype + ' ' + str(i) + ':' + chr(10)
        stops_text += '  Firma: ' + sname + chr(10)
        stops_text += '  Ulica: ' + sstreet + chr(10)
        stops_text += '  Miasto: ' + scity + chr(10)
        stops_text += time_line + chr(10)
    load_str = load_date.strftime('%d.%m.%Y')
    content = 'ZLECENIE TRANSPORTOWE' + chr(10)
    content += '=====================' + chr(10)
    content += 'Szablon: ' + template_name + chr(10)
    content += 'Data: ' + load_str + chr(10)
    content += 'Referencja: ' + ref + chr(10)
    content += 'Klient: ' + client + chr(10)
    content += vehicle_line
    content += 'Cena: ' + price + chr(10) + chr(10)
    content += stops_text
    content += 'TRASA: via ' + via + chr(10)
    return ref, content

st.title('Generator zlecen transportowych')
st.write('Wybierz szablon, date startowa i liczbe dni, nastepnie kliknij Generuj.')
col1, col2, col3 = st.columns(3)
with col1:
    template = st.selectbox('Szablon', list(TEMPLATES.keys()))
with col2:
    start = st.date_input('Data startowa', value=date.today())
with col3:
    days = st.number_input('Liczba dni', min_value=1, max_value=90, value=20)
if st.button('Generuj zlecenia'):
    orders = []
    day_counter = 0
    generated = 0
    while generated < days:
        d = start + timedelta(days=day_counter)
        if is_workday(d):
            ref, content = generate_order(template, start, day_counter)
            orders.append((ref, content))
            generated += 1
        day_counter += 1
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for ref, content in orders:
            zf.writestr('zlecenie_' + ref + '.txt', content)
    zip_buffer.seek(0)
    st.success('Wygenerowano ' + str(len(orders)) + ' zlecen!')
    st.download_button(
        label='Pobierz wszystkie zlecenia (ZIP)',
        data=zip_buffer,
        file_name='zlecenia_' + template + '_' + str(start) + '.zip',
        mime='application/zip'
    )
    st.subheader('Podglad zlecen:')
    for ref, content in orders:
        with st.expander('Zlecenie ' + ref):
            st.text(content)
