import streamlit as st
import yfinance as yf
import pandas as pd

def fetch_stock_data(symbols):
    data = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = info.get('regularMarketPrice')
        if current_price is None:
            current_price = info.get('regularMarketPreviousClose')  # Gunakan harga tutup sebelumnya jika harga saat ini tidak tersedia
        stock_data = {
            'Symbol': symbol,
            'Price/Book (PBVR)': info.get('priceToBook'),
            'Trailing P/E (PER)': info.get('trailingPE'),
            'Total Debt/Equity (mrq) (DER)': info.get('debtToEquity'),
            'Return on Equity (%) (ROE)': info.get('returnOnEquity') * 100,
            'Diluted EPS (ttm) (EPS)': info.get('trailingEps'),
            'Forward Annual Dividend Rate (DPS)': info.get('dividendRate'),
            'Current Price (Hrg)': current_price
        }
        data[symbol] = stock_data
    return data

def main():
    st.title('Yahoo Finance Statistics Scraper')

    # Input form untuk simbol saham
    symbols = st.text_area('Masukkan simbol saham (pisahkan dengan koma)', 'MPMX.JK,GGRM.JK')

    modal_rupiah = st.number_input("Masukkan modal dalam Rupiah", step=1000000, format="%d")

    if st.button('Ambil Data'):
        try:
            symbols_list = [symbol.strip().upper() for symbol in symbols.split(',')]
            stocks_data = fetch_stock_data(symbols_list)

            # Buat DataFrame dari data saham
            df = pd.DataFrame(stocks_data).T

            # Hitung jumlah saham yang dapat dibeli dengan modal yang dimasukkan
            df['Jumlah Saham'] = modal_rupiah / df['Current Price (Hrg)'].fillna(0)
            df['Jumlah Saham'] = df['Jumlah Saham'].apply(lambda x: round(x, 2))  # Memformat jumlah saham menjadi dua angka di belakang koma

            # Hitung dividen dan total nilai yang dihasilkan dari dividen
            df['Dividen (Hasil)'] = df['Jumlah Saham'] * df['Forward Annual Dividend Rate (DPS)']
            total_dividen = df['Dividen (Hasil)'].sum()

            # Tampilkan hasil perhitungan
            st.subheader('Data Statistik Terbaru')
            st.dataframe(df)
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    main()
