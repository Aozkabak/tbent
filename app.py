# 1. Mevcut sekme tanımınızı şu şekilde güncelleyin:
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Envanter Listesi & İndirme",
    "📊 Rapor & Grafikler",
    "➕ Yeni Kayıt / Güncelleme",
    "🗑️ Kayıt Sil",
    "📥 Excel'den Veri Yükle",
    "💾 Veri Yedekle & Yükle",
])

# ... (tab1, tab2, tab3, tab4, tab5 kodları aynı kalıyor) ...

# TAB 6: VERİ YEDEKLEME VE GERİ YÜKLEME (Kodun en sonuna ekleyin)
with tab6:
    st.subheader("💾 Veritabanı Yedekleme ve Geri Yükleme")
    st.info(
        "İnternet üzerinde (Streamlit Cloud vb.) çalışan uygulamalarda sunucu kapandığında SQLite verileri sıfırlanabilir. "
        "Veri kaybı yaşamamak için düzenli olarak veritabanınızı bilgisayarınıza indirin veya yedek dosyanızı geri yükleyin."
    )

    col_backup, col_restore = st.columns(2)

    # 1. Veritabanını İndir (Yedek Al)
    with col_backup:
        st.markdown("### 💾 1. Veritabanı Yedeği İndir")
        st.caption("Mevcut SQLite veritabanını (.db) bilgisayarınıza indirir.")

        try:
            with open(DB_NAME, "rb") as db_file:
                db_bytes = db_file.read()

            tarih_str = datetime.now().strftime("%Y%m%d_%H%M")
            st.download_button(
                label="📥 Veritabanı Yedeğini İndir (.db)",
                data=db_bytes,
                file_name=f"bilgisayar_takip_backup_{tarih_str}.db",
                mime="application/x-sqlite3",
                type="primary",
            )
        except Exception as e:
            st.error(f"Yedek dosyası hazırlanırken hata oluştu: {e}")

    # 2. Veritabanını Yükle (Geri Yükle)
    with col_restore:
        st.markdown("### 📤 2. Veritabanı Yedeği Geri Yükle")
        st.caption("Daha önce indirdiğiniz `.db` dosyasını yükleyerek verileri geri getirir.")

        uploaded_db = st.file_uploader(
            "Yedek veritabanı dosyasını (.db) seçin", type=["db", "sqlite", "sqlite3"]
        )

        if uploaded_db is not None:
            confirm_restore = st.checkbox("Mevcut verilerin üzerine yazılmasını onaylıyorum.")
            
            if st.button("🔄 Yedeği Geri Yükle", type="secondary"):
                if confirm_restore:
                    try:
                        with open(DB_NAME, "wb") as f:
                            f.write(uploaded_db.getbuffer())
                        st.success("✅ Veritabanı başarıyla geri yüklendi ve güncellendi!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Veritabanı geri yüklenirken hata oluştu: {e}")
                else:
                    st.warning("Lütfen geri yükleme işlemini onaylamak için kutucuğu işaretleyin.")
