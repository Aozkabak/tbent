import io
import sqlite3
import pandas as pd
import streamlit as st

# PDF Oluşturma İçin ReportLab Bileşenleri
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Entegre Tesisler Bilgisayar Takip Çizelgesi",
    layout="wide",
    page_icon="💻",
)

# --- VERİTABANI BAĞLANTISI ---
DB_NAME = "bilgisayar_takip.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS envanter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT,
            adi_soyadi TEXT,
            bolumu TEXT,
            pc_marka TEXT,
            pc_model TEXT,
            pc_seri_no TEXT,
            monitor_marka TEXT,
            monitor_model TEXT,
            monitor_seri_no TEXT,
            yazici TEXT,
            isletim_sistemi TEXT,
            office_surumu TEXT,
            virus_koruma TEXT,
            kullanim_durumu TEXT,
            aciklama TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


def get_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM envanter", conn)
    conn.close()
    # Tablodaki tüm NaN / None değerlerini boş metin ile değiştir
    return df.fillna("")


# --- TÜRKÇE KARAKTER DÜZELTME FONKSİYONU ---
def tr_fix(text):
    if not text or pd.isna(text) or str(text).lower() == "nan":
        return "-"
    text = str(text)
    mapping = {
        'ı': 'i', 'İ': 'I',
        'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U',
        'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O',
        'ç': 'c', 'Ç': 'C'
    }
    for search, replace in mapping.items():
        text = text.replace(search, replace)
    return text


# --- PDF SİCİL KARTI OLUŞTURMA FONKSİYONU ---
def create_person_pdf(row):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=colors.HexColor("#1E3A8A")
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#4B5563")
    )

    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#1F2937"))
    cell_normal = ParagraphStyle('CellNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#374151"))

    story = []

    # Başlık ve Altbaşlık
    story.append(Paragraph(tr_fix("ENTEGRE TESİSLER BİLGİSAYAR TAKİP ÇİZELGESİ"), title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(tr_fix("PERSONEL DONANIM & SİCİL ZİMMET KARTI"), subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1E3A8A"), spaceAfter=15))

    # Tablo Verileri
    data = [
        [Paragraph(tr_fix("Kayıt ID / Durum"), cell_bold), Paragraph(f"#{row.get('id', '')} / {tr_fix(row.get('kullanim_durumu', ''))}", cell_normal), Paragraph(tr_fix("Bölümü"), cell_bold), Paragraph(tr_fix(row.get('bolumu', '')), cell_normal)],
        [Paragraph(tr_fix("Kullanıcı Adı"), cell_bold), Paragraph(tr_fix(row.get('kullanici_adi', '')), cell_normal), Paragraph(tr_fix("Adı Soyadı"), cell_bold), Paragraph(tr_fix(row.get('adi_soyadi', '')), cell_normal)],
        [Paragraph(tr_fix("PC Marka / Model"), cell_bold), Paragraph(f"{tr_fix(row.get('pc_marka', ''))} {tr_fix(row.get('pc_model', ''))}".strip(), cell_normal), Paragraph(tr_fix("PC Seri No"), cell_bold), Paragraph(tr_fix(row.get('pc_seri_no', '')), cell_normal)],
        [Paragraph(tr_fix("Monitör Marka / Model"), cell_bold), Paragraph(f"{tr_fix(row.get('monitor_marka', ''))} {tr_fix(row.get('monitor_model', ''))}".strip(), cell_normal), Paragraph(tr_fix("Monitör Seri No"), cell_bold), Paragraph(tr_fix(row.get('monitor_seri_no', '')), cell_normal)],
        [Paragraph(tr_fix("İşletim Sistemi"), cell_bold), Paragraph(tr_fix(row.get('isletim_sistemi', '')), cell_normal), Paragraph(tr_fix("Office Sürümü"), cell_bold), Paragraph(tr_fix(row.get('office_surumu', '')), cell_normal)],
        [Paragraph(tr_fix("Yazıcı"), cell_bold), Paragraph(tr_fix(row.get('yazici', '')), cell_normal), Paragraph(tr_fix("Virüs Koruma"), cell_bold), Paragraph(tr_fix(row.get('virus_koruma', '')), cell_normal)],
        [Paragraph(tr_fix("Açıklama"), cell_bold), Paragraph(tr_fix(row.get('aciklama', '')), cell_normal), "", ""]
    ]

    t = Table(data, colWidths=[120, 140, 120, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('SPAN', (1, 6), (3, 6)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#E5E7EB")),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor("#E5E7EB")),
    ]))

    story.append(t)
    story.append(Spacer(1, 40))

    # İmza Alanı
    imza_data = [
        [Paragraph(tr_fix("<b>Teslim Eden (BT Sorumlusu)</b>"), cell_normal), Paragraph(tr_fix("<b>Teslim Alan (Personel)</b>"), cell_normal)],
        [Paragraph(tr_fix("Ad Soyad: ...................................."), cell_normal), Paragraph(tr_fix("Ad Soyad: ...................................."), cell_normal)],
        [Paragraph(tr_fix("İmza: .........................................."), cell_normal), Paragraph(tr_fix("İmza: .........................................."), cell_normal)],
        [Paragraph(tr_fix("Tarih: ..... / ..... / 20..."), cell_normal), Paragraph(tr_fix("Tarih: ..... / ..... / 20..."), cell_normal)]
    ]
    imza_table = Table(imza_data, colWidths=[260, 260])
    imza_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(imza_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# --- ARAYÜZ STİL DÜZENLEMESİ ---
st.markdown(
    """
    <style>
    .main-header {
        font-size: 26px;
        font-weight: bold;
        color: #1e3a8a;
        text-align: center;
        padding-bottom: 15px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- LOGO VE BAŞLIK ALANI ---
col_logo, col_title = st.columns([1, 5])

with col_logo:
    try:
        st.image("logo.png", width=120)
    except:
        st.write("📂 *Logo yüklenemedi (logo.png dosyasını kontrol edin)*")

with col_title:
    st.markdown(
        "<h1 style='color: #1e3a8a; margin-top: 10px;'>ENTEGRE TESİSLER"
        " BİLGİSAYAR TAKİP ÇİZELGESİ</h1>",
        unsafe_allow_html=True,
    )

st.divider()

# Sekmeler
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Envanter Listesi & İndirme",
    "📊 Rapor & Grafikler",
    "➕ Yeni Kayıt / Güncelleme",
    "🗑️ Kayıt Sil",
    "📥 Excel'den Veri Yükle",
])

# TAB 1: LİSTELEME, FİLTRELEME VE EXCEL İNDİRME
with tab1:
    df = get_data()

    col_search, col_export = st.columns([3, 1])

    with col_search:
        search = st.text_input(
            "🔍 Kullanıcı Adı, Ad Soyad, Bölüm, Yazıcı veya Seri No ile Ara:",
            key="search_input",
        )
        if search:
            df_filtered = df[
                df["kullanici_adi"].str.contains(search, case=False)
                | df["adi_soyadi"].str.contains(search, case=False)
                | df["bolumu"].str.contains(search, case=False)
                | df["yazici"].str.contains(search, case=False)
                | df["pc_seri_no"].str.contains(search, case=False)
                | df["monitor_seri_no"].str.contains(search, case=False)
            ]
        else:
            df_filtered = df.copy()

    with col_export:
        st.write("###")
        if not df_filtered.empty:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_filtered.to_excel(writer, index=False, sheet_name="Envanter")
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Tümünü Excel Yap",
                data=excel_data,
                file_name="bilgisayar_envanter_raporu.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )

    st.divider()

    if not df_filtered.empty:
        # Başlıklar (Yazıcı sütunu eklendi)
        h_col1, h_col2, h_col3, h_col4, h_col5, h_col6, h_col7 = st.columns([1.5, 2, 1.8, 1.8, 1.8, 1.5, 1.2])
        with h_col1: st.markdown("**Kullanıcı Adı**")
        with h_col2: st.markdown("**Adı Soyadı**")
        with h_col3: st.markdown("**Bölümü**")
        with h_col4: st.markdown("**PC Marka/Model**")
        with h_col5: st.markdown("**Monitör Marka/Model**")
        with h_col6: st.markdown("**Yazıcı**")
        with h_col7: st.markdown("**İşlem**")
        
        st.divider()

        # Her kişi için aynı satırda bilgiler ve indirme butonu
        for idx, row in df_filtered.iterrows():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 2, 1.8, 1.8, 1.8, 1.5, 1.2])
            
            val_user = str(row.get('kullanici_adi', '')).strip()
            val_name = str(row.get('adi_soyadi', '')).strip()
            val_dept = str(row.get('bolumu', '')).strip()
            val_pc = f"{row.get('pc_marka', '')} {row.get('pc_model', '')}".strip()
            val_mon = f"{row.get('monitor_marka', '')} {row.get('monitor_model', '')}".strip()
            val_printer = str(row.get('yazici', '')).strip()

            with c1: st.write(val_user if val_user else "-")
            with c2: st.write(val_name if val_name else "-")
            with c3: st.write(val_dept if val_dept else "-")
            with c4: st.write(val_pc if val_pc else "-")
            with c5: st.write(val_mon if val_mon else "-")
            with c6: st.write(val_printer if val_printer else "-")
            
            with c7:
                pdf_bytes = create_person_pdf(row)
                st.download_button(
                    label="📄 PDF",
                    data=pdf_bytes,
                    file_name=f"sicil_karti_{val_user if val_user else 'personel'}.pdf",
                    mime="application/pdf",
                    key=f"pdf_btn_{row.get('id', idx)}"
                )
    else:
        st.info("Gösterilecek veri bulunamadı.")

# TAB 2: RAPOR VE GRAFİKLER
with tab2:
    st.subheader("📊 Envanter Analiz ve İstatistik Raporu")
    df_chart = get_data()

    if df_chart.empty:
        st.info("Henüz grafik oluşturulacak veri bulunmuyor.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Toplam Cihaz / Kayıt", len(df_chart))
        m2.metric(
            "Aktif Cihaz",
            len(df_chart[df_chart["kullanim_durumu"] == "AKTİF"]),
        )
        m3.metric(
            "Pasif Cihaz",
            len(df_chart[df_chart["kullanim_durumu"] == "PASİF"]),
        )
        m4.metric(
            "Virüs Koruma (VAR)",
            len(df_chart[df_chart["virus_koruma"] == "VAR"]),
        )

        st.divider()

        g1, g2 = st.columns(2)

        with g1:
            st.markdown("##### 🖥️ İşletim Sistemi Dağılımı")
            os_counts = df_chart[df_chart["isletim_sistemi"] != ""]["isletim_sistemi"].value_counts()
            st.bar_chart(os_counts)

        with g2:
            st.markdown("##### 🏢 Bölümlere Göre Cihaz Sayısı")
            dept_counts = df_chart[df_chart["bolumu"] != ""]["bolumu"].value_counts()
            st.bar_chart(dept_counts)

        g3, g4 = st.columns(2)

        with g3:
            st.markdown("##### 📄 Office Sürümü Dağılımı")
            office_counts = df_chart[df_chart["office_surumu"] != ""]["office_surumu"].value_counts()
            st.bar_chart(office_counts)

        with g4:
            st.markdown("##### 🛡️ Virüs Koruma Durumu")
            virus_counts = df_chart[df_chart["virus_koruma"] != ""]["virus_koruma"].value_counts()
            st.bar_chart(virus_counts)

# TAB 3: KAYIT VE GÜNCELLEME FORMU
with tab3:
    st.subheader("Bilgisayar Takip Formu")
    st.caption("Lütfen tüm metinleri BÜYÜK HARF ile giriniz.")

    islem_turu = st.radio("İşlem Seçiniz:", ["Yeni Kayıt", "Güncelleme"])

    df_current = get_data()
    selected_row = None

    if islem_turu == "Güncelleme" and not df_current.empty:
        record_to_edit = st.selectbox(
            "Güncellenecek Kaydı Seçin:",
            df_current["id"].astype(str)
            + " - "
            + df_current["kullanici_adi"]
            + " ("
            + df_current["adi_soyadi"]
            + ")",
            key="edit_select",
        )
        selected_id = int(record_to_edit.split(" - ")[0])
        selected_row = df_current[df_current["id"] == selected_id].iloc[0]

    with st.form("kayit_formu"):
        col1, col2 = st.columns(2)

        with col1:
            kullanici_adi = st.text_input(
                "KULLANICI ADI",
                value=selected_row["kullanici_adi"] if selected_row is not None else "",
            ).upper()
            adi_soyadi = st.text_input(
                "ADI SOYADI",
                value=selected_row["adi_soyadi"] if selected_row is not None else "",
            ).upper()
            bolumu = st.text_input(
                "BÖLÜMÜ",
                value=selected_row["bolumu"] if selected_row is not None else "",
            ).upper()

            # İlk elemanı BOŞ olan PC MARKA LİSTESİ
            pc_marka_listesi = ["", "DELL", "LENOVO", "HP", "ASUS", "ACER", "CASPER", "APPLE", "MSI"]
            mevcut_pc_marka = selected_row["pc_marka"] if selected_row is not None else ""
            default_pc_index = pc_marka_listesi.index(mevcut_pc_marka) if mevcut_pc_marka in pc_marka_listesi else 0

            pc_marka = st.selectbox("PC MARKA", pc_marka_listesi, index=default_pc_index)

            pc_model = st.text_input(
                "PC MODEL",
                value=selected_row["pc_model"] if selected_row is not None else "",
            ).upper()
            pc_seri_no = st.text_input(
                "PC SERİ NO",
                value=selected_row["pc_seri_no"] if selected_row is not None else "",
            ).upper()

        with col2:
            # İlk elemanı BOŞ olan MONİTÖR MARKA LİSTESİ
            monitor_marka_listesi = ["", "DELL", "LENOVO", "HP", "ASUS", "ACER", "SAMSUNG", "LG", "PHILIPS", "VIEWSONIC"]
            mevcut_mon_marka = selected_row["monitor_marka"] if selected_row is not None else ""
            default_mon_index = monitor_marka_listesi.index(mevcut_mon_marka) if mevcut_mon_marka in monitor_marka_listesi else 0

            monitor_marka = st.selectbox("MONİTÖR MARKA", monitor_marka_listesi, index=default_mon_index)

            monitor_model = st.text_input(
                "MONİTÖR MODEL",
                value=selected_row["monitor_model"] if selected_row is not None else "",
            ).upper()

            monitor_seri_no = st.text_input(
                "MONİTÖR SERİ NO",
                value=selected_row["monitor_seri_no"] if selected_row is not None else "",
            ).upper()

            yazici = st.text_input(
                "YAZICI",
                value=selected_row["yazici"] if selected_row is not None else "",
            ).upper()

            # Seçmeli alanlar başlarına boş seçenek eklendi
            isletim_opts = ["", "WINDOWS 11", "WINDOWS 10", "WINDOWS 8", "WINDOWS XP", "DİĞER"]
            isletim_sistemi = st.selectbox(
                "İŞLETİM SİSTEMİ",
                isletim_opts,
                index=isletim_opts.index(selected_row["isletim_sistemi"])
                if selected_row is not None and selected_row["isletim_sistemi"] in isletim_opts
                else 0,
            )

            office_opts = ["", "OFFİCE 2016", "OFFİCE 2019", "OFFİCE 2013", "OFFİCE 2010", "DİĞER"]
            office_surumu = st.selectbox(
                "OFFİCE SÜRÜMÜ",
                office_opts,
                index=office_opts.index(selected_row["office_surumu"])
                if selected_row is not None and selected_row["office_surumu"] in office_opts
                else 0,
            )

            virus_opts = ["", "VAR", "YOK", "GÜNCEL DEĞİL"]
            virus_koruma = st.selectbox(
                "VİRÜS KORUMA",
                virus_opts,
                index=virus_opts.index(selected_row["virus_koruma"])
                if selected_row is not None and selected_row["virus_koruma"] in virus_opts
                else 0,
            )

            durum_opts = ["", "AKTİF", "PASİF", "YEDEK", "HURDA"]
            kullanim_durumu = st.selectbox(
                "KULLANIM DURUMU",
                durum_opts,
                index=durum_opts.index(selected_row["kullanim_durumu"])
                if selected_row is not None and selected_row["kullanim_durumu"] in durum_opts
                else 0,
            )

            aciklama = st.text_area(
                "AÇIKLAMA",
                value=selected_row["aciklama"] if selected_row is not None else "",
            ).upper()

        submit = st.form_submit_button(
            "KAYDET" if islem_turu == "Yeni Kayıt" else "GÜNCELLE"
        )

        if submit:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()

            if islem_turu == "Yeni Kayıt":
                c.execute(
                    """
                    INSERT INTO envanter (
                        kullanici_adi, adi_soyadi, bolumu, pc_marka, pc_model, pc_seri_no,
                        monitor_marka, monitor_model, monitor_seri_no, yazici, isletim_sistemi, office_surumu,
                        virus_koruma, kullanim_durumu, aciklama
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        kullanici_adi,
                        adi_soyadi,
                        bolumu,
                        pc_marka,
                        pc_model,
                        pc_seri_no,
                        monitor_marka,
                        monitor_model,
                        monitor_seri_no,
                        yazici,
                        isletim_sistemi,
                        office_surumu,
                        virus_koruma,
                        kullanim_durumu,
                        aciklama,
                    ),
                )
                st.success("Yeni kayıt başarıyla eklendi!")
            else:
                c.execute(
                    """
                    UPDATE envanter SET 
                        kullanici_adi=?, adi_soyadi=?, bolumu=?, pc_marka=?, pc_model=?, pc_seri_no=?,
                        monitor_marka=?, monitor_model=?, monitor_seri_no=?, yazici=?, isletim_sistemi=?, office_surumu=?,
                        virus_koruma=?, kullanim_durumu=?, aciklama=?
                    WHERE id=?
                """,
                    (
                        kullanici_adi,
                        adi_soyadi,
                        bolumu,
                        pc_marka,
                        pc_model,
                        pc_seri_no,
                        monitor_marka,
                        monitor_model,
                        monitor_seri_no,
                        yazici,
                        isletim_sistemi,
                        office_surumu,
                        virus_koruma,
                        kullanim_durumu,
                        aciklama,
                        selected_id,
                    ),
                )
                st.success("Kayıt başarıyla güncellendi!")

            conn.commit()
            conn.close()
            st.rerun()

# TAB 4: KAYIT SİLME
with tab4:
    st.subheader("⚠️ Kayıt Silme İşlemi")
    df_delete = get_data()

    if df_delete.empty:
        st.info("Silinecek kayıt bulunmamaktadır.")
    else:
        record_to_delete = st.selectbox(
            "Silmek İstediğiniz Kaydı Seçin:",
            df_delete["id"].astype(str)
            + " - "
            + df_delete["kullanici_adi"]
            + " ("
            + df_delete["adi_soyadi"]
            + ")",
            key="delete_select",
        )

        delete_id = int(record_to_delete.split(" - ")[0])
        confirm = st.checkbox("Bu kaydı kalıcı olarak silmek istediğime eminim.")

        if st.button("🗑️ KAYDI SİL", type="primary"):
            if confirm:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("DELETE FROM envanter WHERE id=?", (delete_id,))
                conn.commit()
                conn.close()
                st.success(f"ID: {delete_id} numaralı kayıt başarıyla silindi!")
                st.rerun()
            else:
                st.warning("Lütfen silme işlemini onaylamak için kutucuğu işaretleyin.")

# TAB 5: EXCEL İLE TOPLU VERİ YÜKLEME
with tab5:
    st.subheader("📥 Excel Dosyasından Toplu Veri Aktarımı")
    st.info(
        "Excel dosyanızdaki sütun başlıkları şu şekilde olmalıdır: "
        "**KULLANICI ADI, ADI SOYADI, BÖLÜMÜ, PC MARKA, PC MODEL, PC SERİ NO, MONİTÖR MARKA, MONİTÖR MODEL, MONİTÖR SERİ NO, YAZICI, İŞLETİM SİSTEMİ, OFFİCE SÜRÜMÜ, VİRÜS KORUMA, KULLANIM DURUMU, AÇIKLAMA**"
    )

    uploaded_file = st.file_uploader(
        "Bir Excel dosyası (.xlsx veya .xls) seçin", type=["xlsx", "xls"]
    )

    if uploaded_file is not None:
        try:
            excel_df = pd.read_excel(uploaded_file).fillna("")
            st.write("📄 **Yüklenecek Veri Önizlemesi:**")
            st.dataframe(excel_df.head())

            if st.button("🚀 VERİLERİ VERİTABANINA AKTAR", type="primary"):
                column_mapping = {
                    "KULLANICI ADI": "kullanici_adi",
                    "ADI SOYADI": "adi_soyadi",
                    "BÖLÜMÜ": "bolumu",
                    "PC MARKA": "pc_marka",
                    "PC MODEL": "pc_model",
                    "PC SERİ NO": "pc_seri_no",
                    "MONİTÖR MARKA": "monitor_marka",
                    "MONİTÖR MODEL": "monitor_model",
                    "MONİTÖR SERİ NO": "monitor_seri_no",
                    "YAZICI": "yazici",
                    "İŞLETİM SİSTEMİ": "isletim_sistemi",
                    "OFFİCE SÜRÜMÜ": "office_surumu",
                    "VİRÜS KORUMA": "virus_koruma",
                    "KULLANIM DURUMU": "kullanim_durumu",
                    "AÇIKLAMA": "aciklama",
                }

                excel_df.rename(columns=column_mapping, inplace=True)

                for col in excel_df.select_dtypes(include="object").columns:
                    excel_df[col] = excel_df[col].astype(str).str.upper()

                conn = sqlite3.connect(DB_NAME)
                excel_df.to_sql(
                    "envanter",
                    conn,
                    if_exists="append",
                    index=False,
                    method="multi",
                )
                conn.close()

                st.success(
                    f"✅ Toplam {len(excel_df)} adet kayıt veritabanına başarıyla aktarıldı!"
                )
                st.rerun()

        except Exception as e:
            st.error(f"Excel dosyası okunurken bir hata oluştu: {e}")