import streamlit as st
import os
from google import genai

# Config Halaman
st.set_page_config(page_title="Gemini Agentic AI", page_icon="🤖", layout="wide")

st.title("🤖 Enterprise Agentic AI (Powered by Gemini)")
st.caption("Aplikasi Cloud Otomasi untuk Project Engineer, Electrical Engineering, & Stock Analytics")

# 1. Inisialisasi Gemini Client menggunakan Secrets dari Cloud
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY belum dikonfigurasi di Streamlit Secrets!")
    st.stop()

client = genai.Client(api_key=api_key)

# 2. Sidebar - Pengaturan Domain Kebutuhan
st.sidebar.header("⚙️ Pengaturan Agen")
domain = st.sidebar.selectbox(
    "Pilih Domain Pekerjaan:",
    [
        "Project Management Monitoring",
        "Electrical Engineering Calculation",
        "Stock Market Screener (IHSG)"
    ]
)

# System Prompt Spesifik per Domain
system_prompts = {
    "Project Management Monitoring": """
    Anda adalah Senior Project Engineer AI Agent. Tugas Anda:
    - Menganalisis laporan fisik, foto lapangan, atau jadwal proyek.
    - Menghitung deviasi jadwal/biaya dan memberikan tindakan korektif (EVM).
    - Menyusun laporan ringkasan eksekutif secara terstruktur.
    """,
    "Electrical Engineering Calculation": """
    Anda adalah Lead Electrical Engineer AI Agent. Tugas Anda:
    - Melakukan kalkulasi teknis (voltage drop, ukuran kabel, breaker, atau pembebanan trafo).
    - Memeriksa kesesuaian spesifikasi terhadap standar PUIL / IEC.
    - Menganalisis Single Line Diagram (SLD) atau dokumen teknis listrik.
    """,
    "Stock Market Screener (IHSG)": """
    Anda adalah Equity Research Analyst AI Agent khusus pasar saham Indonesia (IHSG). Tugas Anda:
    - Menganalisis laporan keuangan emiten, rasio fundamental (PER, PBV, ROE, FCF).
    - Memandu strategi swing/value investing dengan target keuntungan 10-20% terukur.
    - Memberikan penilaian risiko dan Margin of Safety yang realistis.
    """
}

# 3. Form Input Pengguna
st.subheader(f"📌 Domain Terpilih: {domain}")

uploaded_file = st.file_uploader(
    "Unggah Dokumen Pendukung (PDF, Gambar/SLD, Foto Site, Laporan Keuangan):", 
    type=["pdf", "png", "jpg", "jpeg", "txt"]
)

user_prompt = st.text_area(
    "Masukkan instruksi atau pertanyaan teknis Anda:", 
    height=120,
    placeholder="Contoh: Analisis dokumen terlampir dan berikan ringkasan risiko serta rekomendasi tindak lanjutnya."
)

btn_process = st.button("🚀 Jalankan Agen AI", type="primary")

# 4. Eksekusi Proses Agen Gemini
if btn_process:
    if not user_prompt:
        st.warning("Silakan masukkan instruksi terlebih dahulu!")
    else:
        with st.spinner("Agen Gemini sedang memproses data di Cloud..."):
            try:
                # Menggabungkan System Prompt dan User Input
                full_prompt = f"{system_prompts[domain]}\n\nInstruksi Pengguna:\n{user_prompt}"
                contents_payload = [full_prompt]

                # Jika ada file yang diunggah
                if uploaded_file is not None:
                    # Simpan temporary file untuk di-upload ke Gemini API
                    temp_file_path = f"temp_{uploaded_file.name}"
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Upload file ke Gemini
                    uploaded_gemini_file = client.files.upload(file=temp_file_path)
                    contents_payload.append(uploaded_gemini_file)

                # Eksekusi Gemini 2.5 Flash (Model Cepat, Multimodal, & Gratis di Free Tier)
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=contents_payload
                )

                st.success("✅ Analisis Agen AI Selesai!")
                st.markdown("### 📊 Hasil Analisis & Rekomendasi:")
                st.markdown(response.text)

                # Cleanup temporary file jika ada
                if uploaded_file is not None:
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    client.files.delete(name=uploaded_gemini_file.name)

            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses data: {str(e)}")
