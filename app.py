import streamlit as st
import yfinance as yf
import pandas as pd

def fetch_stock_data(symbols):
    data = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        info = stock.info
        stock_data = {
            'Price/Book': info.get('priceToBook'),
            'Trailing P/E': info.get('trailingPE'),
            'Total Debt/Equity (mrq)': info.get('debtToEquity'),
            'Return on Equity (%)': info.get('returnOnEquity') * 100,
            'Diluted EPS (ttm)': info.get('trailingEps'),
            'Forward Annual Dividend Rate': info.get('dividendRate')
        }
        data[symbol] = stock_data
    return data

def main():
    st.title('Yahoo Finance Statistics Scraper')

    # Input form untuk simbol saham
    symbols = st.text_area('Masukkan simbol saham (pisahkan dengan koma)', 'GGRM.JK,MPMX.JK')

    if st.button('Ambil Data'):
        try:
            symbols_list = [symbol.strip().upper() for symbol in symbols.split(',')]
            stocks_data = fetch_stock_data(symbols_list)

            # Buat DataFrame dari data saham
            df = pd.DataFrame(stocks_data).T
            df.reset_index(inplace=True)
            df.rename(columns={'index': 'Symbol'}, inplace=True)

            # Tampilkan data yang diminta
            st.subheader('Data Statistik Terbaru')
            st.dataframe(df)

            # Unduh data ke dalam file Excel
            if st.button('Unduh Data Excel'):
                excel_file = df.to_excel('stock_data.xlsx', index=False)
                st.success('Data berhasil diunduh ke dalam file Excel: [stock_data.xlsx](stock_data.xlsx)')
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    main()
