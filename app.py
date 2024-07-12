import streamlit as st
import yfinance as yf
import pandas as pd

def fetch_stock_data(symbols):
    data = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = round(info.get('regularMarketPrice', info.get('regularMarketPreviousClose')) or 0)
        forward_dividend_yield = round(info.get('dividendYield', 0) * 100, 2)
        stock_data = {
            'Symbol': symbol,
            'Current Price': current_price,
            'Price/Book (PBVR)': info.get('priceToBook'),
            'Trailing P/E (PER)': info.get('trailingPE'),
            'Total Debt/Equity (mrq) (DER)': info.get('debtToEquity'),
            'Return on Equity (%) (ROE)': round((info.get('returnOnEquity') or 0) * 100),
            'Diluted EPS (ttm) (EPS)': round(info.get('trailingEps') or 0),
            'Forward Annual Dividend Rate (DPS)': round(info.get('dividendRate') or 0),
            'Forward Annual Dividend Yield (%)': forward_dividend_yield,
        }
        data[symbol] = stock_data
    return data

def main():
    st.set_page_config(page_title="Yahoo Finance Statistics Scraper", layout="wide")
    st.title('Yahoo Finance Statistics Scraper')
    st.write('👈 Silahkan pilih aplikasi yang digunakan pada menu sidebar. 👈')


    st.sidebar.header('Input Parameters')
    symbols = st.sidebar.text_area('Masukkan simbol saham (pisahkan dengan koma)', 'BBCA.JK,BBRI.JK,GOTO.JK,TLKM.JK,WSKT.JK,ASII.JK')
    modal_rupiah = st.sidebar.number_input("Masukkan modal dalam Rupiah", step=1000000, format="%d")

    st.sidebar.success('''
    
    **@Yuukinaesa** \n
                    Arfan Hidayat Priyantono ✅
    ''')

    if st.sidebar.button('Ambil Data'):
        try:
            symbols_list = [symbol.strip().upper() for symbol in symbols.split(',')]
            stocks_data = fetch_stock_data(symbols_list)
            df = pd.DataFrame(stocks_data).T
            df['Jumlah Saham'] = modal_rupiah / df['Current Price'].fillna(0)
            df['Jumlah Lot'] = df['Jumlah Saham'] // 100  
            df['Jumlah Saham'] = df['Jumlah Lot'] * 100  
            df['Dividen'] = df['Jumlah Saham'] * df['Forward Annual Dividend Rate (DPS)']
            df['Modal'] = df['Jumlah Lot'] * 100 * df['Current Price']

            df.fillna(value={
                'Current Price': 0,
                'Price/Book (PBVR)': 0,
                'Trailing P/E (PER)': 0,
                'Total Debt/Equity (mrq) (DER)': 0,
                'Return on Equity (%) (ROE)': 0,
                'Diluted EPS (ttm) (EPS)': 0,
                'Forward Annual Dividend Rate (DPS)': 0,
                'Forward Annual Dividend Yield (%)': 0,
                'Jumlah Saham': 0,
                'Dividen': 0,
                'Jumlah Lot': 0,
                'Modal': 0
            }, inplace=True)

            st.subheader('Data Statistik Terbaru')
            with st.expander("Tampilkan Data Statistik Lengkap"):
                st.dataframe(df.reset_index(drop=True).style.format({
                    'Current Price': 'Rp{:,.0f}',
                    'Price/Book (PBVR)': '{:.2f}',
                    'Trailing P/E (PER)': '{:.2f}',
                    'Total Debt/Equity (mrq) (DER)': '{:.2f}',
                    'Return on Equity (%) (ROE)': '{:.0f}%',
                    'Diluted EPS (ttm) (EPS)': '{:.0f}',
                    'Forward Annual Dividend Rate (DPS)': 'Rp{:,.0f}',
                    'Forward Annual Dividend Yield (%)': '{:.2f}%',
                    'Jumlah Saham': '{:.0f}',
                    'Dividen': 'Rp{:,.0f}',
                    'Jumlah Lot': '{:.0f}',
                    'Modal': 'Rp{:,.0f}'
                }))

            st.subheader('Data Statistik Sederhana')
            selected_columns = [
                'Symbol',
                'Current Price',
                'Forward Annual Dividend Rate (DPS)',
                'Forward Annual Dividend Yield (%)',
                'Jumlah Saham',
                'Jumlah Lot',
                'Dividen',
                'Modal'
            ]
            with st.expander("Tampilkan Data Statistik Sederhana"):
                st.dataframe(df[selected_columns].reset_index(drop=True).style.format({
                    'Current Price': 'Rp{:,.0f}',
                    'Forward Annual Dividend Rate (DPS)': 'Rp{:,.0f}',
                    'Forward Annual Dividend Yield (%)': '{:.2f}%',
                    'Jumlah Saham': '{:.0f}',
                    'Jumlah Lot': '{:.0f}',
                    'Dividen': 'Rp{:,.0f}',
                    'Modal': 'Rp{:,.0f}'
                }))

        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    main()
