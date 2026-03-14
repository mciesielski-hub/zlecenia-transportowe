import streamlit as st
from datetime import date, timedelta
import io
import zipfile

DEFAULT_CLIENT = 'Klient: Id oddzialu: 24, Pelna nazwa oddzialu: Dachser Koninko, Kraj: PL, Kod pocztowy: 95-010, Miasto: Strykow, NIP 7281006020'
DEFAULT_PRICE = '892 EUR'

TEMPLATES = {
    'Landsberg': {
        'client': DEFAULT_CLIENT,
        'price': DEFAULT_PRICE,
        'via_text': 'Slubice',
        'stops': [
            {'type': 'ZALADUNEK',   'name': 'Dachser Koninko',    'street': 'Drukarska',             'city': '60-023; Koninko; PL',      'time': '18:30', 'day_offset': 0},
            {'type': 'ROZLADUNEK', 'name': 'Dachser Radeburg',    'street': 'Thomas-Dachser-Strasse 1','city': '01471; Radeburg; DE',      'time': '02:30', 'day_offset': 1},
            {'type': 'ROZLADUNEK', 'name': 'Dachser Landsberg',   'street': 'Brehnaer Strasse 4',    'city': '06188; Landsberg; DE',     'time': '05:00', 'day_offset': 1},
            {'type': 'ZALADUNEK',  'name': 'Dachser Landsberg',   'street': 'Brehnaer Strasse 4',    'city': '06188; Landsberg; DE',     'time': '05:00', 'day_offset': 1},
            {'type': 'ROZLADUNEK', 'name': 'Dachser Schonefeld',  'street': 'Thomas-Dachser-Allee 2','city': '12529; Schonefeld; DE',    'time': '18:00', 'day_offset': 1},
            {'type': 'ROZLADUNEK (POWROT)', 'name': 'Dachser Koninko', 'street': 'Drukarska',        'city': '60-023; Koninko; PL',      'time': '',      'day_offset': 2},
        ]
    },
    'DSV Eupen': {
        'client': 'DSV ROAD NV, BE, 0404507618',
        'price': '692 EUR',
        'vehicle_reg': 'OKR2CN5',
        'via_text': 'Neunkirchen',
        'stops': [
            {'type': 'ZALADUNEK',          'name': 'Schenker',               'street': 'Siebeponisweg 9', 'city': '4700; Eupen; BE',           'time': '13:10', 'day_offset': 0},
            {'type': 'PRZELADUNEK',        'name': 'Schenker Deutschland AG','street': 'Boxbergweg 6',    'city': '66538; Neunkirchen; DE',    'time': '21:10', 'day_offset': 1},
            {'type': 'ROZLADUNEK (POWROT)','name': 'Schenker',               'street': 'Siebeponisweg 9', 'city': '4700; Eupen; BE',           'time': '13:10', 'day_offset': 2},
        ]
    },
    'Dachser Mouscron': {
        'client': 'SA DACHSER Belgium, BE 7700 Mouscron, VAT: BE 0415394184',
        'price': '1626 EUR',
        'via_text': 'Alsdorf / Koln',
        'stops': [
            {'type': 'ZALADUNEK',   'name': 'Dachser Mouscron', 'street': 'Hansestrasse 52',        'city': '7700; Mouscron; BE',        'time': '21:00', 'day_offset': 0},
            {'type': 'ROZLADUNEK', 'name': 'Dachser Alsdorf',   'street': 'Thomas-Dachser-Strasse 1','city': '52477; Alsdorf; DE',       'time': '01:30', 'day_offset': 1},
            {'type': 'ROZLADUNEK', 'name': 'Dachser Koln',      'street': 'Rue du Berger',          'city': '51149; Koln; DE',           'time': '03:00', 'day_offset': 1},
            {'type': 'ZALADUNEK',  'name': 'Dachser Koln',      'street': 'Rue du Berger',          'city': '51149; Koln; DE',           'time': '19:00', 'day_offset': 1},
            {'type': 'ROZLADUNEK (POWROT)', 'name': 'Dachser Wissous', 'street': 'Hansestrasse 52', 'city': '91320; Wissous; FR',        'time': '02:30', 'day_offset': 2},
        ]
    }
}

def is_workday(d):
    return d.weekday() < 5

def generate_order(template_name, start_date, day_num):
    t = TEMPLATES[template_name]
    load_date = start_date + timedelta(days=day_num)
    ref = load_date.strftime('%Y-%m-%d')

    vehicle_line = ''
    if t.get('vehicle_reg'):
        vehicle_line = f'Nr rejestracyjny: {t["vehicle_reg"]}\n'

    stops_text = ''
    for i, stop in enumerate(t['stops'], 1):
        stop_date = load_date + timedelta(days=stop['day_offset'])
        time_str = f'  Godzina: {stop["time"]} ({stop_date.strftime("%d.%m.%Y")})\n' if stop['time'] else ''
        stops_text += f'''{stop['type']} {i}:
  Firma: {stop['name']}
  Ulica: {stop['street']}
  Miasto: {stop['city']}
{time_str}
'''

    content = f'''ZLECENIE TRANSPORTOWE
=====================
Szablon: {template_name}
Data: {load_date.strftime('%d.%m.%Y')}
Referencja: {ref}
Klient: {t['client']}
{vehicle_line}Cena: {t['price']}

{stops_text}TRASA: via {t['via_text']}
'''
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
            zf.writestr(f'zlecenie_{ref}.txt', content)
    zip_buffer.seek(0)

    st.success(f'Wygenerowano {len(orders)} zlecen!')
    st.download_button(
        label='Pobierz wszystkie zlecenia (ZIP)',
        data=zip_buffer,
        file_name=f'zlecenia_{template}_{start}.zip',
        mime='application/zip'
    )

    st.subheader('Podglad zlecen:')
    for ref, content in orders:
        with st.expander(f'Zlecenie {ref}'):
            st.text(content)
