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
        'load_1_name': 'Dachser Koninko',
        'load_1_street': 'Drukarska',
        'load_1_city': '60-023; Koninko; PL',
        'via_text': 'Slubice',
        'unload_1_name': 'Dachser Radeburg',
        'unload_1_street': 'Thomas-Dachser-Strasse 1',
        'unload_1_city': '01471; Radeburg; DE',
        'unload_2_name': 'Dachser Landsberg',
        'unload_2_street': 'Brehnaer Strasse 4',
        'unload_2_city': '06188; Landsberg; DE',
        'load_2_name': 'Dachser Landsberg',
        'load_2_street': 'Brehnaer Strasse 4',
        'load_2_city': '06188; Landsberg; DE',
        'unload_3_name': 'Dachser Schonefeld',
        'unload_3_street': 'Thomas-Dachser-Allee 2',
        'unload_3_city': '12529; Schonefeld; DE',
        'unload_4_name': 'Dachser Koninko',
        'unload_4_street': 'Drukarska',
        'unload_4_city': '60-023; Koninko; PL',
        't1': '18:30',
        't2': '02:30',
        't3': '05:00',
        't4': '18:00',
    }
}

def is_workday(d):
    return d.weekday() < 5

def generate_order(template_name, start_date, day_num):
    t = TEMPLATES[template_name]
    load_date = start_date + timedelta(days=day_num)
    unload_date = load_date + timedelta(days=1)
    ref = load_date.strftime('%Y-%m-%d')
    content = f'''ZLECENIE TRANSPORTOWE
=====================
Data: {load_date.strftime('%d.%m.%Y')}
Referencja: {ref}
Klient: {t['client']}
Cena: {t['price']}

ZALADUNEK 1:
  Firma: {t['load_1_name']}
  Ulica: {t['load_1_street']}
  Miasto: {t['load_1_city']}
  Godzina: {t['t1']}

ROZLADUNEK 1:
  Firma: {t['unload_1_name']}
  Ulica: {t['unload_1_street']}
  Miasto: {t['unload_1_city']}
  Godzina: {t['t2']} ({unload_date.strftime('%d.%m.%Y')})

ROZLADUNEK 2:
  Firma: {t['unload_2_name']}
  Ulica: {t['unload_2_street']}
  Miasto: {t['unload_2_city']}
  Godzina: {t['t3']} ({unload_date.strftime('%d.%m.%Y')})

ZALADUNEK 2:
  Firma: {t['load_2_name']}
  Ulica: {t['load_2_street']}
  Miasto: {t['load_2_city']}
  Godzina: {t['t3']} ({unload_date.strftime('%d.%m.%Y')})

ROZLADUNEK 3:
  Firma: {t['unload_3_name']}
  Ulica: {t['unload_3_street']}
  Miasto: {t['unload_3_city']}
  Godzina: {t['t4']} ({unload_date.strftime('%d.%m.%Y')})

ROZLADUNEK 4 (POWROT):
  Firma: {t['unload_4_name']}
  Ulica: {t['unload_4_street']}
  Miasto: {t['unload_4_city']}

TRASA: {t['load_1_city']} -> via {t['via_text']} -> {t['unload_2_city']} -> {t['unload_3_city']} -> powrot
'''
    return ref, content

st.title('Generator zlecen transportowych')
st.write('Wpisz np. **Landsberg 20 dni** lub wypelnij formularz ponizej.')

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
