import streamlit as st
import pandas as pd
import locale
import io

# Tenta definir o locale brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except:
        st.warning("Não foi possível aplicar formatação pt-BR. Verifique o sistema.")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("estoque comp.xlsx", sheet_name="Planilha1")
    df.columns = df.columns.str.strip()
    return df

def main():
    st.title("Estoque por Comprador +100d")
    
    df = carregar_dados()
    
    df['Comprador'] = df['Comprador'].astype(str).str.strip()
    compradores = sorted(df['Comprador'].dropna().unique())
    comprador_selecionado = st.selectbox("Selecione o comprador:", compradores)

    df_filtrado = df[df['Comprador'] == comprador_selecionado]

    valor_total = df_filtrado['Valor Estoque'].sum()
    qtd_total = df_filtrado['Qtd Estoque'].sum()
    total_itens = len(df_filtrado)

    col1, col2, col3 = st.columns(3)
    col1.metric("Valor Total do Estoque", f"R$ {locale.format_string('%.2f', valor_total, grouping=True)}")
    col2.metric("Qtd Total em Estoque", f"{locale.format_string('%.0f', qtd_total, grouping=True)} un")
    col3.metric("Total de Itens", f"{total_itens} itens")

    # Estiliza produtos com mais de 200 dias
    def destacar_linha(row):
        try:
            dias = row['Dias de Estoque']
            if pd.notna(dias) and float(dias) > 200:
                return ['background-color: #fdd835'] * len(row)
        except:
            pass
        return [''] * len(row)

    st.subheader("Tabela de Produtos")
    st.markdown("**Observação:** Produtos em amarelo têm mais de 200 dias de estoque.")
    
    st.dataframe(df_filtrado.style.apply(destacar_linha, axis=1))
    
    # Botão para exportar para Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Estoque')
    excel_buffer.seek(0)
    
    st.download_button(
        label="Baixar Planilha Excel",
        data=excel_buffer,
        file_name=f'estoque_{comprador_selecionado}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == "__main__":
    main()
