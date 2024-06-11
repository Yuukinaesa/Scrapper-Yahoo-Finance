import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import random

def fetch_stock_data(symbols):
    data = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = round(info.get('regularMarketPrice', info.get('regularMarketPreviousClose')) or 0)
        forward_dividend_yield = info.get('dividendYield', 0) * 100  # Convert to percentage
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

def random_color():
    return "rgba({}, {}, {}, 0.6)".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def main():
    st.set_page_config(page_title="Yahoo Finance Statistics Scraper", layout="wide")
    st.title('Yahoo Finance Statistics Scraper')

    st.sidebar.header('Input Parameters')
    symbols = st.sidebar.text_area('Masukkan simbol saham (pisahkan dengan koma)', 'BBCA.JK,BBRI.JK,GOTO.JK,TLKM.JK,WSKT.JK,ASII.JK')
    modal_rupiah = st.sidebar.number_input("Masukkan modal dalam Rupiah", step=1000000, format="%d")

    if st.sidebar.button('Ambil Data'):
        try:
            symbols_list = [symbol.strip().upper() for symbol in symbols.split(',')]
            stocks_data = fetch_stock_data(symbols_list)

            df = pd.DataFrame(stocks_data).T
            df['Jumlah Saham'] = modal_rupiah / df['Current Price (Hrg)'].fillna(0)
            df['Jumlah Lot'] = df['Jumlah Saham'] // 100  # Jumlah lot yang bisa dibeli, dibulatkan ke bawah ke bilangan genap terdekat
            df['Jumlah Saham'] = df['Jumlah Lot'] * 100  # Jumlah saham berdasarkan jumlah lot yang dapat dibeli
            df['Dividen (Hasil)'] = df['Jumlah Saham'] * df['Forward Annual Dividend Rate (DPS)']
            
            # Handle None values by filling with a default value
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
                'Jumlah Lot': 0
            }, inplace=True)

            # Display the dataframe
            st.subheader('Data Statistik Terbaru')
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
                'Jumlah Lot': '{:.0f}'
            }))

            # Display horizontal bar charts with random colors
            st.subheader('Chart Analysis')
            col1, col2 = st.columns(2)

            # Random colors for each bar
            df['Color'] = df.apply(lambda x: random_color(), axis=1)

            fig1 = px.bar(df.reset_index(), x='Dividen (Hasil)', y='index', orientation='h', 
                          title='Dividen (Hasil) per Emiten',
                          color='index', color_discrete_sequence=df['Color'].tolist())
            fig1.update_layout(showlegend=False)
            fig1.update_xaxes(title_text='Dividen (Hasil)')
            fig1.update_yaxes(title_text='Emiten')
            col1.plotly_chart(fig1)

            fig2 = px.bar(df.reset_index(), x='Forward Annual Dividend Yield (%)', y='index', orientation='h', 
                          title='Forward Annual Dividend Yield (%) Emiten',
                          color='index', color_discrete_sequence=df['Color'].tolist())
            fig2.update_layout(showlegend=False)
            fig2.update_xaxes(title_text='Forward Annual Dividend Yield (%)')
            fig2.update_yaxes(title_text='Emiten')
            col2.plotly_chart(fig2)
            
            # Save as CSV button
            if st.button("Save as CSV"):
                csv_data = df.to_csv(index=False, sep=';')
                st.download_button(label="Download CSV", data=csv_data, file_name="stock_data.csv", mime="text/csv")

        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    main()




