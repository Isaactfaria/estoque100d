import streamlit as st
import pandas as pd
import locale
import io
import numpy as np

# Tenta definir o locale brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except:
        st.warning("Não foi possível aplicar formatação pt-BR. Verifique o sistema.")

def carregar_dados(uploaded_file):
    if uploaded_file is not None:
        try:
            # Tenta ler como Excel primeiro
            df = pd.read_excel(uploaded_file)
        except:
            try:
                # Se falhar, tenta ler como CSV
                df = pd.read_csv(uploaded_file)
            except Exception as e:
                st.error(f"Erro ao carregar o arquivo: {str(e)}")
                return None
        
        df.columns = df.columns.str.strip()
        return df
    return None

def main():
    st.title("Estoque por Comprador +100d")
    
    # Upload de arquivo
    uploaded_file = st.file_uploader("Carregue seu arquivo Excel", type=['xlsx'])
    
    if uploaded_file is not None:
        df = carregar_dados(uploaded_file)
        
        if df is not None:
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

            st.subheader("Tabela de Produtos")
            st.markdown("**Observação:** Produtos em amarelo têm mais de 200 dias de estoque.")
            
            # Estiliza produtos com mais de 200 dias
            def destacar_linha(row):
                try:
                    dias = row['Dias de Estoque']
                    if pd.notna(dias) and float(dias) > 200:
                        return ['background-color: #fdd835'] * len(row)
                except:
                    pass
                return [''] * len(row)

            st.dataframe(df_filtrado.style.apply(destacar_linha, axis=1))
            
            # Botão para exportar para Excel
            try:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_filtrado.to_excel(writer, index=False, sheet_name='Estoque')
                excel_buffer.seek(0)
                
                st.download_button(
                    label="Baixar Planilha Excel",
                    data=excel_buffer,
                    file_name=f'estoque_{comprador_selecionado}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            except Exception as e:
                st.error(f"Erro ao criar o arquivo Excel: {str(e)}")
                
            # Botão para exportar como CSV como backup
            csv_buffer = io.StringIO()
            df_filtrado.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            st.download_button(
                label="Baixar Planilha CSV",
                data=csv_buffer.getvalue(),
                file_name=f'estoque_{comprador_selecionado}.csv',
                mime='text/csv'
            )
        else:
            st.error("Erro ao carregar o arquivo. Por favor, verifique se o arquivo está no formato correto.")
    else:
        st.info("Por favor, carregue um arquivo Excel para começar.")

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
