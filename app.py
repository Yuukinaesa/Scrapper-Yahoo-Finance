import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

def fetch_stock_data(symbols):
    data = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = round(info.get('regularMarketPrice', info.get('regularMarketPreviousClose')) or 0)
        forward_dividend_yield = info.get('dividendYield', 0) * 100  
        stock_data = {
            'Symbol': symbol,
            'Price/Book (PBVR)': info.get('priceToBook'),
            'Trailing P/E (PER)': info.get('trailingPE'),
            'Total Debt/Equity (mrq) (DER)': info.get('debtToEquity'),
            'Return on Equity (%) (ROE)': round((info.get('returnOnEquity') or 0) * 100),
            'Diluted EPS (ttm) (EPS)': round(info.get('trailingEps') or 0),
            'Forward Annual Dividend Rate (DPS)': round(info.get('dividendRate') or 0),
            'Forward Annual Dividend Yield (%)': round(forward_dividend_yield or 0),
            'Current Price (Hrg)': current_price
        }
        data[symbol] = stock_data
    return data

def main():
    st.set_page_config(page_title="Yahoo Finance Statistics Scraper", layout="wide")
    st.title('Yahoo Finance Statistics Scraper')

    st.sidebar.header('Input Parameters')
    symbols = st.sidebar.text_area('Masukkan simbol saham (pisahkan dengan koma)', 'BBCA.JK,BBRI.JK,GOTO.JK,TLKM.JK,WSKT.JK,ASII.JK')
    modal_rupiah = st.sidebar.number_input("Masukkan modal dalam Rupiah", step=1000000, format="%d")
    period = st.sidebar.selectbox(
        'Pilih jangka waktu data historis',
        ['1d', '5d', '1mo', '1y', '2y', '3y', '4y', '5y', 'max'],
        index=8
    )

    if st.sidebar.button('Ambil Data'):
        try:
            symbols_list = [symbol.strip().upper() for symbol in symbols.split(',')]
            stocks_data = fetch_stock_data(symbols_list)
            df = pd.DataFrame(stocks_data).T
            df['Jumlah Saham'] = modal_rupiah / df['Current Price (Hrg)'].fillna(0)
            df['Jumlah Lot'] = df['Jumlah Saham'] // 100  
            df['Jumlah Saham'] = df['Jumlah Lot'] * 100  
            df['Dividen (Hasil)'] = df['Jumlah Saham'] * df['Forward Annual Dividend Rate (DPS)']
            df['Modal'] = df['Jumlah Lot'] * 100 * df['Current Price (Hrg)']  

            df.fillna(value={
                'Current Price (Hrg)': 0,
                'Price/Book (PBVR)': 0,
                'Trailing P/E (PER)': 0,
                'Total Debt/Equity (mrq) (DER)': 0,
                'Return on Equity (%) (ROE)': 0,
                'Diluted EPS (ttm) (EPS)': 0,
                'Forward Annual Dividend Rate (DPS)': 0,
                'Forward Annual Dividend Yield (%)': 0,
                'Jumlah Saham': 0,
                'Dividen (Hasil)': 0,
                'Jumlah Lot': 0,
                'Modal': 0  
            }, inplace=True)

            st.subheader('Data Statistik Terbaru')
            with st.expander("Tampilkan Data Statistik"):
                st.dataframe(df.reset_index(drop=True).style.format({
                    'Current Price (Hrg)': 'Rp{:,.0f}',
                    'Price/Book (PBVR)': '{:.2f}',
                    'Trailing P/E (PER)': '{:.2f}',
                    'Total Debt/Equity (mrq) (DER)': '{:.2f}',
                    'Return on Equity (%) (ROE)': '{:.0f}%',
                    'Diluted EPS (ttm) (EPS)': '{:.0f}',
                    'Forward Annual Dividend Rate (DPS)': 'Rp{:,.0f}',
                    'Forward Annual Dividend Yield (%)': '{:.0f}%',
                    'Jumlah Saham': '{:.0f}',
                    'Dividen (Hasil)': 'Rp{:,.0f}',
                    'Jumlah Lot': '{:.0f}',
                    'Modal': 'Rp{:,.0f}'
                }))

            st.subheader('Chart Analysis')
            col1, col2 = st.columns(2)

            with col1:
                with st.expander("Tampilkan Chart Dividen"):
                    fig1 = px.bar(df.reset_index(), x='Dividen (Hasil)', y='index', orientation='h', 
                                  title='Dividen (Hasil) per Emiten',
                                  color='index')
                    fig1.update_layout(showlegend=False)
                    fig1.update_xaxes(title_text='Dividen (Hasil)')
                    fig1.update_yaxes(title_text='Emiten')
                    st.plotly_chart(fig1)

            with col2:
                with st.expander("Tampilkan Chart Forward Annual Dividend Yield"):
                    fig2 = px.bar(df.reset_index(), x='Forward Annual Dividend Yield (%)', y='index', orientation='h', 
                                  title='Forward Annual Dividend Yield (%) Emiten',
                                  color='index')
                    fig2.update_layout(showlegend=False)
                    fig2.update_xaxes(title_text='Forward Annual Dividend Yield (%)')
                    fig2.update_yaxes(title_text='Emiten')
                    st.plotly_chart(fig2)

            st.subheader('Real-time Stock Price Charts')
            for symbol in symbols_list:
                with st.expander(f'{symbol} - Real-time Stock Price'):
                    placeholder = st.empty()
                    data = yf.download(symbol, period=period, interval='1d')['Close']
                    if not data.empty:
                        fig = px.line(data, title=f'{symbol} Stock Price ({period})')
                        placeholder.plotly_chart(fig)
                    else:
                        st.warning(f'Tidak ada data untuk {symbol} dalam periode {period}.')

        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    main()
