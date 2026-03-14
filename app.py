import streamlit as st
from datetime import date, timedelta
import io
import zipfile

DEFAULT_CLIENT = \"Klient: Id oddziału: 24, Pełna nazwa oddziału: Dachser Koninko, Kraj: PL, Kod pocztowy: 95-010, Miasto: Stryków, NIP 7281006020\"
DEFAULT_PRICE = \"892 EUR\"

TEMPLATES = {
    \"Landsberg\": {
        \"client\": DEFAULT_CLIENT,
        \"price\": DEFAULT_PRICE,
        \"load_1_name\": \"Dachser Koninko\",
        \"load_1_street\": \"Drukarska\",
        \"load_1_city\": \"60-023; Koninko; PL\",
        \"via_text\": \"Słubice\",
        \"unload_1_name\": \"Dachser Radeburg\",
        \"unload_1_street\": \"Thomas-Dachser-Straße 1\",
        \"unload_1_city\": \"01471; Radeburg; DE\",
        \"unload_2_name\": \"Dachser Landsberg\",
        \"unload_2_street\": \"Brehnaer Straße 4\",
        \"unload_2_city\": \"06188; Landsberg; DE\",
        \"load_2_name\": \"Dachser Landsberg\",
        \"load_2_street\": \"Brehnaer Straße 4\",
        \"load_2_city\": \"06188; Landsberg; DE\",
        \"unload_3_name\": \"Dachser Schönefeld\",
        \"unload_3_street\": \"Thomas-Dachser-Allee 2\",
        \"unload_3_city\": \"12529; Schönefeld; DE\",
        \"unload_4_name\": \"Dachser Koninko\",
        \"unload_4_street\": \"Drukarska\",
        \"unload_4_city\": \"60-023; Koninko; PL\",
        \"t1\": \"18:30\",
        \"t2\": \"02:30\",
        \"t3\": \"05:00\",
        \"t4\": \"18:00\",
        \"t5\": \"02:00\",
        \"t6\": \"05:00\",
    },
    \"Bremen\": {
        \"client\": \"Klient: Id oddziału: 20, Pełna nazwa oddziału: Dachser Bremen, Kraj: DE, Kod pocztowy: 28197, Miasto: Bremen\",
        \"price\": \"723,71 EUR\",
        \"load_1_name\": \"Dachser Bremen\",
        \"load_1_street\": \"Senator-Blase-Straße 23\",
        \"load_1_city\": \"28197; Bremen; DE\",
        \"via_text\": \"\",
        \"unload_1_name\": \"Dachser Schönefeld\",
        \"unload_1_street\": \"Thomas-Dachser-Allee 2\",
        \"unload_1_city\": \"12529; Schönefeld; DE\",
        \"unload_2_name\": \"Dachser Koninko\",
        \"unload_2_street\": \"Drukarska\",
        \"unload_2_city\": \"60-023; Koninko; PL\",
        \"load_2_name\": \"\",
        \"load_2_street\": \"\",
        \"load_2_city\": \"\",
        \"unload_3_name\": \"\",
        \"unload_3_street\": \"\",
        \"unload_3_city\": \"\",
        \"unload_4_name\": \"\",
        \"unload_4_street\": \"\",
        \"unload_4_city\": \"\",
        \"t1\": \"17:00\",
        \"t2\": \"01:00\",
        \"t3\": \"03:00\",
        \"t4\": \"\",
        \"t5\": \"\",
        \"t6\": \"\",
    },
    \"Pusty własny\": {
        \"client\": DEFAULT_CLIENT,
        \"price\": DEFAULT_PRICE,
        \"load_1_name\": \"\",
        \"load_1_street\": \"\",
        \"load_1_city\": \"\",
        \"via_text\": \"\",
        \"unload_1_name\": \"\",
        \"unload_1_street\": \"\",
        \"unload_1_city\": \"\",
        \"unload_2_name\": \"\",
        \"unload_2_street\": \"\",
        \"unload_2_city\": \"\",
        \"load_2_name\": \"\",
        \"load_2_street\": \"\",
        \"load_2_city\": \"\",
        \"unload_3_name\": \"\",
        \"unload_3_street\": \"\",
        \"unload_3_city\": \"\",
        \"unload_4_name\": \"\",
        \"unload_4_street\": \"\",
        \"unload_4_city\": \"\",
        \"t1\": \"18:30\",
        \"t2\": \"02:30\",
        \"t3\": \"05:00\",
        \"t4\": \"18:00\",
        \"t5\": \"02:00\",
        \"t6\": \"05:00\",
    },
}

def init_state():
    st.session_state.setdefault(\"selected_template\", \"Landsberg\")
    st.session_state.setdefault(\"template_data\", TEMPLATES[\"Landsberg\"].copy())

def apply_template(name):
    st.session_state[\"selected_template\"] = name
    st.session_state[\"template_data\"] = TEMPLATES[name].copy()

def next_workdays(start_date, count):
    days = []
    current = start_date
    while len(days) < count:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days

def shift_dates(load_date):
    if load_date.weekday() == 4:
        return {
            \"d1\": load_date,
            \"d2\": load_date + timedelta(days=3),
            \"d3\": load_date + timedelta(days=3),
            \"d4\": load_date + timedelta(days=3),
            \"d5\": load_date + timedelta(days=4),
            \"d6\": load_date + timedelta(days=4),
        }
    return {
        \"d1\": load_date,
        \"d2\": load_date + timedelta(days=1),
        \"d3\": load_date + timedelta(days=1),
        \"d4\": load_date + timedelta(days=1),
        \"d5\": load_date + timedelta(days=2),
        \"d6\": load_date + timedelta(days=2),
    }

def fmt(d, t):
    return f\"{d.strftime('%d-%m-%Y')} {t}\"

def block(label, dt, name, street, city):
    return f\"\"\"{label}; {dt}
{name}
{street}
{city}
\"\"\"

def build_order_text(load_date, cfg):
    ds = shift_dates(load_date)
    parts = [
        f\"Referencja: {ds['d1'].strftime('%Y-%m-%d')}\",
        f\"Cena: {cfg['price']}\",
        cfg[\"client\"],
        \"\",
        block(\"Załadunek\", fmt(ds[\"d1\"], cfg[\"t1\"]), cfg[\"load_1_name\"], cfg[\"load_1_street\"], cfg[\"load_1_city\"]).strip(),
    ]

    if cfg[\"via_text\"].strip():
        parts.extend([\"\", cfg[\"via_text\"].strip()])

    if cfg[\"unload_1_name\"].strip():
        parts.extend([\"\", block(\"Rozładunek\", fmt(ds[\"d2\"], cfg[\"t2\"]), cfg[\"unload_1_name\"], cfg[\"unload_1_street\"], cfg[\"unload_1_city\"]).strip()])

    if cfg[\"unload_2_name\"].strip():
        parts.extend([\"\", block(\"Rozładunek\", fmt(ds[\"d3\"], cfg[\"t3\"]), cfg[\"unload_2_name\"], cfg[\"unload_2_street\"], cfg[\"unload_2_city\"]).strip()])

    if cfg[\"load_2_name\"].strip():
        parts.extend([\"\", block(\"Załadunek\", fmt(ds[\"d4\"], cfg[\"t4\"]), cfg[\"load_2_name\"], cfg[\"load_2_street\"], cfg[\"load_2_city\"]).strip()])

    if cfg[\"unload_3_name\"].strip():
        parts.extend([\"\", block(\"Rozładunek\", fmt(ds[\"d5\"], cfg[\"t5\"]), cfg[\"unload_3_name\"], cfg[\"unload_3_street\"], cfg[\"unload_3_city\"]).strip()])

    if cfg[\"unload_4_name\"].strip():
        parts.extend([\"\", block(\"Rozładunek\", fmt(ds[\"d6\"], cfg[\"t6\"]), cfg[\"unload_4_name\"], cfg[\"unload_4_street\"], cfg[\"unload_4_city\"]).strip()])

    return \"\
\".join(parts) + \"\
\"

def generate_files(start_date, num_days, cfg):
    files = []
    for d in next_workdays(start_date, num_days):
        filename = f\"zlecenie_{d.strftime('%Y-%m-%d')}.txt\"
        content = build_order_text(d, cfg)
        files.append((filename, content))
    return files

def zip_files(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, \"w\", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files:
            zf.writestr(filename, content.encode(\"utf-8\"))
    return buffer.getvalue()

init_state()

st.set_page_config(page_title=\"Generator zleceń TSL\", layout=\"wide\")
st.title(\"Generator zleceń transportowych\")

col1, col2 = st.columns([1, 2])

with col1:
    selected = st.selectbox(
        \"Szablon trasy\",
        options=list(TEMPLATES.keys()),
        index=list(TEMPLATES.keys()).index(st.session_state[\"selected_template\"])
    )
    if selected != st.session_state[\"selected_template\"]:
        apply_template(selected)

    start_date = st.date_input(\"Data startowa\", value=date.today())
    num_days = st.number_input(\"Liczba dni roboczych\", min_value=1, max_value=365, value=20, step=1)

    if st.button(\"Wczytaj szablon ponownie\"):
        apply_template(st.session_state[\"selected_template\"])

with col2:
    st.subheader(\"Edycja szablonu\")
    cfg = st.session_state[\"template_data\"]

    cfg[\"client\"] = st.text_area(\"Klient\", value=cfg[\"client\"], height=80)
    cfg[\"price\"] = st.text_input(\"Cena\", value=cfg[\"price\"])

    c1, c2 = st.columns(2)

    with c1:
        cfg[\"load_1_name\"] = st.text_input(\"Załadunek 1 - nazwa\", value=cfg[\"load_1_name\"])
        cfg[\"load_1_street\"] = st.text_input(\"Załadunek 1 - ulica\", value=cfg[\"load_1_street\"])
        cfg[\"load_1_city\"] = st.text_input(\"Załadunek 1 - miasto\", value=cfg[\"load_1_city\"])
        cfg[\"t1\"] = st.text_input(\"Załadunek 1 - godzina\", value=cfg[\"t1\"])

        cfg[\"unload_1_name\"] = st.text_input(\"Rozładunek 1 - nazwa\", value=cfg[\"unload_1_name\"])
        cfg[\"unload_1_street\"] = st.text_input(\"Rozładunek 1 - ulica\", value=cfg[\"unload_1_street\"])
        cfg[\"unload_1_city\"] = st.text_input(\"Rozładunek 1 - miasto\", value=cfg[\"unload_1_city\"])
        cfg[\"t2\"] = st.text_input(\"Rozładunek 1 - godzina\", value=cfg[\"t2\"])

        cfg[\"unload_2_name\"] = st.text_input(\"Rozładunek 2 - nazwa\", value=cfg[\"unload_2_name\"])
        cfg[\"unload_2_street\"] = st.text_input(\"Rozładunek 2 - ulica\", value=cfg[\"unload_2_street\"])
        cfg[\"unload_2_city\"] = st.text_input(\"Rozładunek 2 - miasto\", value=cfg[\"unload_2_city\"])
        cfg[\"t3\"] = st.text_input(\"Rozładunek 2 - godzina\", value=cfg[\"t3\"])

    with c2:
        cfg[\"load_2_name\"] = st.text_input(\"Załadunek 2 - nazwa\", value=cfg[\"load_2_name\"])
        cfg[\"load_2_street\"] = st.text_input(\"Załadunek 2 - ulica\", value=cfg[\"load_2_street\"])
        cfg[\"load_2_city\"] = st.text_input(\"Załadunek 2 - miasto\", value=cfg[\"load_2_city\"])
        cfg[\"t4\"] = st.text_input(\"Załadunek 2 - godzina\", value=cfg[\"t4\"])

        cfg[\"unload_3_name\"] = st.text_input(\"Rozładunek 3 - nazwa\", value=cfg[\"unload_3_name\"])
        cfg[\"unload_3_street\"] = st.text_input(\"Rozładunek 3 - ulica\", value=cfg[\"unload_3_street\"])
        cfg[\"unload_3_city\"] = st.text_input(\"Rozładunek 3 - miasto\", value=cfg[\"unload_3_city\"])
        cfg[\"t5\"] = st.text_input(\"Rozładunek 3 - godzina\", value=cfg[\"t5\"])

        cfg[\"unload_4_name\"] = st.text_input(\"Rozładunek 4 - nazwa\", value=cfg[\"unload_4_name\"])
        cfg[\"unload_4_street\"] = st.text_input(\"Rozładunek 4 - ulica\", value=cfg[\"unload_4_street\"])
        cfg[\"unload_4_city\"] = st.text_input(\"Rozładunek 4 - miasto\", value=cfg[\"unload_4_city\"])
        cfg[\"t6\"] = st.text_input(\"Rozładunek 4 - godzina\", value=cfg[\"t6\"])

    cfg[\"via_text\"] = st.text_area(\"Dodatkowy tekst na trasie\", value=cfg[\"via_text\"], height=70)

generate = st.button(\"Generuj zlecenia\", type=\"primary\")

if generate:
    files = generate_files(start_date, int(num_days), st.session_state[\"template_data\"])
    zip_data = zip_files(files)

    st.success(f\"Wygenerowano {len(files)} plików TXT.\")
    st.download_button(
        label=\"Pobierz wszystkie jako ZIP\",
        data=zip_data,
        file_name=\"zlecenia_transportowe.zip\",
        mime=\"application/zip\"
    )

    st.subheader(\"Podgląd i pobieranie\")
    for filename, content in files:
        with st.expander(filename):
            st.code(content, language=\"text\")
            st.download_button(
                label=f\"Pobierz {filename}\",
                data=content,
                file_name=filename,
                mime=\"text/plain\",
                key=f\"download_{filename}\"
            )
