import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

# 1. Postavke stranice
st.set_page_config(page_title="VPN Upravljanje - HŽI", layout="wide")

@st.cache_data
def load_data():
    try:
        if os.path.exists('baza.csv'):
            with open('baza.csv', mode='r', encoding='utf-8-sig', errors='replace') as f_baza:
                # Preskačemo prvi red (1;2;3...)
                baza = pd.read_csv(f_baza, sep=';', engine='python', skiprows=1)
        else:
            st.error("Datoteka baza.csv nije pronađena!")
            return None, None
            
        if os.path.exists('ponuda_uredaja.csv'):
            with open('ponuda_uredaja.csv', mode='r', encoding='utf-8-sig', errors='replace') as f_ponude:
                ponude = pd.read_csv(f_ponude, sep=',', engine='python')
        else:
            ponude = pd.DataFrame()
            
        baza.columns = baza.columns.str.strip()

        # POPIS OBAVEZNIH STUPACA KOJE SI NABROJAO
        obavezni_stupci = [
            "MSISDN (Voice)", "IME", "PREZIME", "Account/Contract", "REGIJA", 
            "skraćeni broj", "status pretplatnika", "VPN Profil", 
            "MCD/CP - broj preosatlih mjesečnih naknada", "mjesec isteka MCD/CP", 
            "Broj Sim kartice", "VPN Private bill (Y/N)", "Imsi Number"
        ]

        # Ako neki od stupaca nedostaje u CSV-u, dodaj ga kao praznu kolonu
        for col in obavezni_stupci:
            if col not in baza.columns:
                baza[col] = ""
        
        return baza, ponude
    except Exception as e:
        st.error(f"Greška pri učitavanju: {e}")
        return None, None

def sacuvaj_u_csv(df):
    header_row = ";".join([str(i+1) for i in range(len(df.columns))])
    try:
        with open('baza.csv', 'w', encoding='utf-8-sig') as f:
            f.write(header_row + "\n")
            df.to_csv(f, sep=';', index=False)
        return True
    except Exception as e:
        st.error(f"Zatvorite Excel! Datoteka je zaključana. ({e})")
        return False

# 2. Inicijalizacija
df_baza, df_ponude = load_data()

if df_baza is not None:
    st.title("📱 VPN Sistem - Sindikat prometnik vlakova Hrvatske")

    # --- FORMA ZA NOVOG KORISNIKA ---
    st.sidebar.header("➕ Novi Korisnik")
    
    with st.sidebar.form("forma_novi_korisnik"):
        novi_podaci = {}
        
        # Ovdje definiramo točan redoslijed polja u sidebaru
        lista_polja = [
            "MSISDN (Voice)", "IME", "PREZIME", "Account/Contract", "REGIJA", 
            "skraćeni broj", "status pretplatnika", "VPN Profil", 
            "MCD/CP - broj preosatlih mjesečnih naknada", "mjesec isteka MCD/CP", 
            "Broj Sim kartice", "VPN Private bill (Y/N)", "Imsi Number"
        ]
        
        # Generiranje polja za unos
        for col in lista_polja:
            novi_podaci[col] = st.text_input(f"{col}")
        
        # Ostali stupci koji možda postoje u bazi, a nisu na listi iznad
        ostali_stupci = [c for c in df_baza.columns if c not in lista_polja]
        for col in ostali_stupci:
            novi_podaci[col] = st.text_input(f"{col} (ostalo)")

        submit_button = st.form_submit_button("Spremi u bazu.csv")
        
        if submit_button:
            if novi_podaci["MSISDN (Voice)"]:
                novi_red_df = pd.DataFrame([novi_podaci])
                # Osiguravamo da novi red ima sve stupce kao i baza
                for col in df_baza.columns:
                    if col not in novi_red_df.columns:
                        novi_red_df[col] = ""
                
                df_baza = pd.concat([df_baza, novi_red_df], ignore_index=True)
                
                if sacuvaj_u_csv(df_baza):
                    st.sidebar.success(f"Korisnik {novi_podaci['MSISDN (Voice)']} dodan!")
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.sidebar.error("MSISDN (Voice) je obavezan!")

    # --- PRETRAGA I UREĐIVANJE ---
    st.subheader("🔍 Pretraga i brza izmjena")
    msisdn_input = st.text_input("Unesite MSISDN za pretragu:")

    if msisdn_input:
        target_col = "MSISDN (Voice)"
        mask = df_baza[target_col].astype(str).str.contains(msisdn_input)
        filtered_df = df_baza[mask].copy()

        if not filtered_df.empty:
            # Prikaz editora
            edited_df = st.data_editor(filtered_df, use_container_width=True)

            if st.button("💾 Spremi izmjene napravljene u tablici"):
                df_baza.update(edited_df)
                if sacuvaj_u_csv(df_baza):
                    st.success("✅ Izmjene spremljene u baza.csv!")
                    st.cache_data.clear()
        else:
            st.warning("Broj nije pronađen.")

    # --- PONUDA ---
    if not df_ponude.empty:
        with st.expander("📦 Ponuda uređaja"):
            st.dataframe(df_ponude, use_container_width=True)