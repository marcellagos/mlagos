import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import time

# ==================== CONFIGURAÇÃO INICIAL ====================
st.set_page_config(
    page_title="MLAGOS ATELIÊ | ERP",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== IDENTIDADE VISUAL ====================
def aplicar_estilos():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif;
            background-color: #222222;
            color: #D4AF37;
        }
        
        .main {
            background-color: #222222;
        }
        
        h1, h2, h3, h4, h5, h6, p, div, span, label {
            color: #D4AF37 !important;
            text-transform: uppercase;
            font-family: 'Montserrat', sans-serif;
        }
        
        .stButton>button {
            background-color: #D4AF37;
            color: #222222;
            border-radius: 8px;
            border: 2px solid #D4AF37;
            font-weight: 700;
            text-transform: uppercase;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: #222222;
            color: #D4AF37;
            border: 2px solid #D4AF37;
        }
        
        .stTextInput>div>div>input, .stSelectbox>div>div>select, 
        .stNumberInput>div>div>input, .stDateInput>div>div>input,
        .stTextArea>div>div>textarea {
            background-color: #333333;
            color: #D4AF37;
            border: 1px solid #D4AF37;
            border-radius: 6px;
        }
        
        .stDataFrame {
            background-color: #333333;
        }
        
        div[data-testid="stSidebar"] {
            background-color: #1a1a1a;
            border-right: 2px solid #D4AF37;
        }
        
        div[data-testid="stSidebar"] .stRadio label {
            color: #D4AF37 !important;
            font-weight: 600;
        }
        
        .destaque-painel {
            background-color: #333333;
            border: 2px solid #D4AF37;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
        }
        
        .status-online {
            color: #00C851 !important;
            font-weight: 700;
        }
        
        .status-offline {
            color: #ff4444 !important;
            font-weight: 700;
        }
        
        .log-sucesso {
            background-color: #1a1a1a;
            border-left: 4px solid #00C851;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 4px;
        }
        
        .kanban-coluna {
            background-color: #333333;
            border-radius: 10px;
            padding: 15px;
            min-height: 300px;
            border-top: 4px solid #D4AF37;
        }
        
        .card-kanban {
            background-color: #222222;
            border: 1px solid #D4AF37;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

aplicar_estilos()

# ==================== INICIALIZAÇÃO DO SESSION STATE ====================
def inicializar_estado():
    defaults = {
        'clientes': [
            {'Nome': 'ANA PAULA MENDES', 'Telefone': '(11) 98765-4321', 'Email': 'ana@email.com', 'Tipo': 'NOIVO', 'Data Cadastro': datetime.now().strftime('%d/%m/%Y')},
            {'Nome': 'CARLOS EDUARDO', 'Telefone': '(11) 91234-5678', 'Email': 'carlos@email.com', 'Tipo': 'NOIVO', 'Data Cadastro': datetime.now().strftime('%d/%m/%Y')}
        ],
        'financeiro': [
            {'Data': datetime.now().strftime('%d/%m/%Y'), 'Tipo': 'ENTRADA', 'Descrição': 'ENTRADA INICIAL', 'Valor': 5000.0, 'Categoria': 'VENDA'},
            {'Data': datetime.now().strftime('%d/%m/%Y'), 'Tipo': 'SAÍDA', 'Descrição': 'MATÉRIA-PRIMA', 'Valor': 1200.0, 'Categoria': 'INSUMO'}
        ],
        'kanban': {
            'A FAZER': [
                {'Pedido': 'ALI-001', 'Cliente': 'ANA PAULA MENDES', 'Descrição': 'ALIANÇA OURO 18K', 'Prazo': (datetime.now() + timedelta(days=10)).strftime('%d/%m/%Y'), 'Valor': 2500.0}
            ],
            'EM PRODUÇÃO': [
                {'Pedido': 'ALI-002', 'Cliente': 'CARLOS EDUARDO', 'Descrição': 'ANEL SOLITÁRIO', 'Prazo': (datetime.now() + timedelta(days=5)).strftime('%d/%m/%Y'), 'Valor': 3200.0}
            ],
            'PARA ENTREGA': [],
            'ENTREGUE': []
        },
        'estoque': [
            {'Item': 'OURO 18K', 'Quantidade': 50, 'Unidade': 'g', 'Valor Unit.': 350.0},
            {'Item': 'PRATA 950', 'Quantidade': 200, 'Unidade': 'g', 'Valor Unit.': 12.0},
            {'Item': 'DIAMANTE 20 PONTOS', 'Quantidade': 15, 'Unidade': 'un', 'Valor Unit.': 1200.0}
        ],
        'ecommerce': {
            'status': 'ONLINE',
            'ultima_sincronizacao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'pedidos_recebidos': []
        },
        'documentos': {
            'nfe_emitidas': [],
            'garantias_emitidas': []
        },
        'log_sincronizacao': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

inicializar_estado()

# ==================== FUNÇÕES UTILITÁRIAS ====================
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def gerar_id_pedido():
    return f"ECM-{random.randint(1000, 9999)}"

def calcular_saldo_financeiro():
    entradas = sum(item['Valor'] for item in st.session_state['financeiro'] if item['Tipo'] == 'ENTRADA')
    saidas = sum(item['Valor'] for item in st.session_state['financeiro'] if item['Tipo'] == 'SAÍDA')
    return entradas, saidas, entradas - saidas

# ==================== MÓDULO DASHBOARD ====================
def modulo_dashboard():
    st.markdown("## 💎 DASHBOARD MLAGOS ATELIÊ")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"<<div class='destaque-painel'><h3>CLIENTES</h3><h1>{len(st.session_state['clientes'])}</h1></div>", unsafe_allow_html=True)
    with col2:
        entradas, saidas, saldo = calcular_saldo_financeiro()
        st.markdown(f"<<div class='destaque-painel'><h3>SALDO</h3><h1>{formatar_moeda(saldo)}</h1></div>", unsafe_allow_html=True)
    with col3:
        total_pedidos = sum(len(itens) for itens in st.session_state['kanban'].values())
        st.markdown(f"<<div class='destaque-painel'><h3>PEDIDOS</h3><h1>{total_pedidos}</h1></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<<div class='destaque-painel'><h3>E-COMMERCE</h3><h1>{st.session_state['ecommerce']['status']}</h1></div>", unsafe_allow_html=True)
    
    st.markdown("### PEDIDOS EM PRODUÇÃO")
    df_pedidos = []
    for coluna, itens in st.session_state['kanban'].items():
        for item in itens:
            df_pedidos.append({
                'PEDIDO': item['Pedido'],
                'CLIENTE': item['Cliente'],
                'DESCRIÇÃO': item['Descrição'],
                'ETAPA': coluna,
                'VALOR': formatar_moeda(item['Valor']),
                'PRAZO': item['Prazo']
            })
    
    if df_pedidos:
        st.dataframe(pd.DataFrame(df_pedidos), use_container_width=True, hide_index=True)
    else:
        st.info("NENHUM PEDIDO EM PRODUÇÃO NO MOMENTO.")

# ==================== MÓDULO KANBAN ====================
def modulo_kanban():
    st.markdown("## 📋 KANBAN DE PRODUÇÃO")
    st.markdown("---")
    
    colunas = ['A FAZER', 'EM PRODUÇÃO', 'PARA ENTREGA', 'ENTREGUE']
    cols = st.columns(4)
    
    for i, coluna in enumerate(colunas):
        with cols[i]:
            st.markdown(f"<<div class='kanban-coluna'><h4>{coluna}</h4></div>", unsafe_allow_html=True)
            for pedido in st.session_state['kanban'][coluna]:
                st.markdown(f"""
                    <div class='card-kanban'>
                        <strong>{pedido['Pedido']}</strong><br>
                        {pedido['Cliente']}<<br>
                        <small>{pedido['Descrição']}</small><br>
                        <strong>{formatar_moeda(pedido['Valor'])}</strong><br>
                        <small>PRAZO: {pedido['Prazo']}</small>
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### NOVO PEDIDO")
    
    with st.form("novo_pedido"):
        col1, col2, col3 = st.columns(3)
        with col1:
            cliente = st.selectbox("CLIENTE", [c['Nome'] for c in st.session_state['clientes']])
        with col2:
            descricao = st.text_input("DESCRIÇÃO DA JOIA")
        with col3:
            valor = st.number_input("VALOR (R$)", min_value=0.0, value=0.0, step=100.0)
        
        prazo = st.date_input("PRAZO DE ENTREGA", datetime.now() + timedelta(days=15))
        
        if st.form_submit_button("➕ ADICIONAR PEDIDO"):
            novo_pedido = {
                'Pedido': f"ALI-{random.randint(100, 999)}",
                'Cliente': cliente,
                'Descrição': descricao.upper(),
                'Prazo': prazo.strftime('%d/%m/%Y'),
                'Valor': valor
            }
            st.session_state['kanban']['A FAZER'].append(novo_pedido)
            st.success("PEDIDO ADICIONADO COM SUCESSO!")
            st.rerun()

# ==================== MÓDULO FINANCEIRO ====================
def modulo_financeiro():
    st.markdown("## 💰 FLUXO DE CAIXA")
    st.markdown("---")
    
    entradas, saidas, saldo = calcular_saldo_financeiro()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("ENTRADAS", formatar_moeda(entradas))
    c2.metric("SAÍDAS", formatar_moeda(saidas))
    c3.metric("SALDO", formatar_moeda(saldo))
    
    st.markdown("### LANÇAMENTOS")
    df = pd.DataFrame(st.session_state['financeiro'])
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### NOVO LANÇAMENTO")
    
    with st.form("novo_lancamento"):
        col1, col2, col3 = st.columns(3)
        with col1:
            tipo = st.selectbox("TIPO", ["ENTRADA", "SAÍDA"])
        with col2:
            categoria = st.selectbox("CATEGORIA", ["VENDA", "INSUMO", "SERVIÇO", "DESPESA OPERACIONAL", "OUTROS"])
        with col3:
            valor_lanc = st.number_input("VALOR (R$)", min_value=0.0, value=0.0, step=50.0)
        
        descricao = st.text_input("DESCRIÇÃO")
        
        if st.form_submit_button("💾 SALVAR LANÇAMENTO"):
            st.session_state['financeiro'].append({
                'Data': datetime.now().strftime('%d/%m/%Y'),
                'Tipo': tipo,
                'Descrição': descricao.upper(),
                'Valor': valor_lanc,
                'Categoria': categoria
            })
            st.success("LANÇAMENTO REGISTRADO!")
            st.rerun()

# ==================== MÓDULO CLIENTES ====================
def modulo_clientes():
    st.markdown("## 👤 CADASTRO DE CLIENTES")
    st.markdown("---")
    
    df = pd.DataFrame(st.session_state['clientes'])
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### NOVO CLIENTE")
    
    with st.form("novo_cliente"):
        col1, col2, col3 = st.columns(3)
        with col1:
            nome = st.text_input("NOME COMPLETO")
        with col2:
            telefone = st.text_input("TELEFONE")
        with col3:
            email = st.text_input("EMAIL")
        
        tipo = st.selectbox("TIPO", ["NOIVO", "NOIVA", "CLIENTE VIP", "CLIENTE FINAL"])
        
        if st.form_submit_button("➕ CADASTRAR CLIENTE"):
            st.session_state['clientes'].append({
                'Nome': nome.upper(),
                'Telefone': telefone,
                'Email': email.lower(),
                'Tipo': tipo,
                'Data Cadastro': datetime.now().strftime('%d/%m/%Y')
            })
            st.success("CLIENTE CADASTRADO!")
            st.rerun()

# ==================== MÓDULO ESTOQUE ====================
def modulo_estoque():
    st.markdown("## 📦 ESTOQUE DE INSUMOS")
    st.markdown("---")
    
    df = pd.DataFrame(st.session_state['estoque'])
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### ADICIONAR ITEM")
    
    with st.form("novo_item"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            item = st.text_input("ITEM")
        with col2:
            qtd = st.number_input("QUANTIDADE", min_value=0, value=0, step=1)
        with col3:
            unidade = st.selectbox("UNIDADE", ["g", "kg", "un", "ct", "ml"])
        with col4:
            valor_unit = st.number_input("VALOR UNITÁRIO", min_value=0.0, value=0.0, step=10.0)
        
        if st.form_submit_button("➕ ADICIONAR AO ESTOQUE"):
            st.session_state['estoque'].append({
                'Item': item.upper(),
                'Quantidade': qtd,
                'Unidade': unidade,
                'Valor Unit.': valor_unit
            })
            st.success("ITEM ADICIONADO!")
            st.rerun()

# ==================== MÓDULO E-COMMERCE ====================
def modulo_ecommerce():
    st.markdown("## 🌐 INTEGRAÇÃO E-COMMERCE")
    st.markdown("---")
    
    # PAINEL DE STATUS
    st.markdown("### PAINEL DE CONEXÃO")
    
    status = st.session_state['ecommerce']['status']
    ultima_sinc = st.session_state['ecommerce']['ultima_sincronizacao']
    
    status_class = "status-online" if status == "ONLINE" else "status-offline"
    
    st.markdown(f"""
        <div class='destaque-painel'>
            <h4>STATUS DA CONEXÃO</h4>
            <h2 class='{status_class}'>● {status}</h2>
            <p>ÚLTIMA SINCRONIZAÇÃO: {ultima_sinc}</p>
            <p>PEDIDOS RECEBIDOS VIA SITE: {len(st.session_state['ecommerce']['pedidos_recebidos'])}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # BOTÃO DE SINCRONIZAR
    st.markdown("### SINCRONIZAÇÃO DE VENDAS")
    
    if st.button("🔄 SINCRONIZAR VENDAS DO SITE", use_container_width=True, type="primary"):
        with st.spinner("SINCRONIZANDO PEDIDOS COM O SITE..."):
            time.sleep(1.5)
            
            # DADOS DO PEDIDO SIMULADO
            pedido_ecommerce = {
                'Pedido': gerar_id_pedido(),
                'Cliente': 'ROBERTO ALVES',
                'Descrição': 'PAR DE ALIANÇAS CLÁSSICAS',
                'Valor': 3500.00,
                'Prazo': (datetime.now() + timedelta(days=20)).strftime('%d/%m/%Y'),
                'Origem': 'SITE E-COMMERCE'
            }
            
            # A) ADICIONAR CLIENTE
            cliente_existente = any(c['Nome'] == 'ROBERTO ALVES' for c in st.session_state['clientes'])
            if not cliente_existente:
                st.session_state['clientes'].append({
                    'Nome': 'ROBERTO ALVES',
                    'Telefone': '(11) 98888-7777',
                    'Email': 'roberto.alves@email.com',
                    'Tipo': 'CLIENTE FINAL',
                    'Data Cadastro': datetime.now().strftime('%d/%m/%Y')
                })
            
            # B) ADICIONAR FINANCEIRO COMO ENTRADA
            st.session_state['financeiro'].append({
                'Data': datetime.now().strftime('%d/%m/%Y'),
                'Tipo': 'ENTRADA',
                'Descrição': f"VENDA ECOMMERCE - {pedido_ecommerce['Pedido']}",
                'Valor': pedido_ecommerce['Valor'],
                'Categoria': 'VENDA'
            })
            
            # C) ADICIONAR NO KANBAN
            st.session_state['kanban']['A FAZER'].append(pedido_ecommerce)
            st.session_state['ecommerce']['pedidos_recebidos'].append(pedido_ecommerce)
            
            # ATUALIZAR STATUS
            st.session_state['ecommerce']['ultima_sincronizacao'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            st.session_state['ecommerce']['status'] = 'ONLINE'
            
            # LOG DE AÇÕES
            log = [
                "✅ CLIENTE 'ROBERTO ALVES' CADASTRADO/ATUALIZADO NA LISTA DE CLIENTES",
                f"✅ ENTRADA DE {formatar_moeda(pedido_ecommerce['Valor'])} REGISTRADA NO FLUXO DE CAIXA",
                f"✅ PEDIDO '{pedido_ecommerce['Pedido']}' - '{pedido_ecommerce['Descrição']}' ADICIONADO AO KANBAN NA COLUNA 'A FAZER'"
            ]
            st.session_state['log_sincronizacao'] = log
            
            st.balloons()
    
    # EXIBIR LOG DE SUCESSO
    if st.session_state['log_sincronizacao']:
        st.markdown("### LOG DE SINCRONIZAÇÃO")
        for msg in st.session_state['log_sincronizacao']:
            st.markdown(f"<<div class='log-sucesso'>{msg}</div>", unsafe_allow_html=True)
    
    # HISTÓRICO DE PEDIDOS ECOMMERCE
    if st.session_state['ecommerce']['pedidos_recebidos']:
        st.markdown("### HISTÓRICO DE PEDIDOS DO SITE")
        df = pd.DataFrame(st.session_state['ecommerce']['pedidos_recebidos'])
        df['Valor'] = df['Valor'].apply(formatar_moeda)
        st.dataframe(df, use_container_width=True, hide_index=True)

# ==================== MÓDULO DOCUMENTOS ====================
def modulo_documentos():
    st.markdown("## 📄 DOCUMENTOS (NFE / GARANTIA)")
    st.markdown("---")
    
    clientes = [c['Nome'] for c in st.session_state['clientes']]
    pedidos = []
    for coluna, itens in st.session_state['kanban'].items():
        for item in itens:
            pedidos.append(f"{item['Pedido']} - {item['Cliente']} - {item['Descrição']}")
    
    if not clientes or not pedidos:
        st.warning("CADASTRE CLIENTES E PEDIDOS ANTES DE EMITIR DOCUMENTOS.")
        return
    
    cliente_selecionado = st.selectbox("SELECIONE O CLIENTE", clientes)
    pedido_selecionado = st.selectbox("SELECIONE O PEDIDO", pedidos)
    
    # Extrair pedido
    pedido_id = pedido_selecionado.split(" - ")[0]
    pedido_info = None
    for coluna, itens in st.session_state['kanban'].items():
        for item in itens:
            if item['Pedido'] == pedido_id:
                pedido_info = item
                break
    
    if pedido_info:
        st.markdown(f"""
            <div class='destaque-painel'>
                <p><strong>PEDIDO:</strong> {pedido_info['Pedido']}</p>
                <p><strong>CLIENTE:</strong> {pedido_info['Cliente']}</p>
                <p><strong>DESCRIÇÃO:</strong> {pedido_info['Descrição']}</p>
                <p><strong>VALOR:</strong> {formatar_moeda(pedido_info['Valor'])}</p>
            </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 GERAR NFE", use_container_width=True, type="primary"):
            with st.spinner("TRANSMITINDO NFE PARA SEFAZ..."):
                time.sleep(2)
                
                chave_nfe = f"35{random.randint(100000000000000, 999999999999999)}5501{random.randint(100000000, 999999999)}"
                link_pdf = f"https://mlagosatelie.com.br/nfe/{chave_nfe}.pdf"
                
                doc = {
                    'Tipo': 'NFE',
                    'Cliente': cliente_selecionado,
                    'Pedido': pedido_id,
                    'Chave de Acesso': chave_nfe,
                    'Link PDF': link_pdf,
                    'Data Emissão': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'Status': 'AUTORIZADA'
                }
                st.session_state['documentos']['nfe_emitidas'].append(doc)
                
                st.success("NFE AUTORIZADA PELA SEFAZ!")
                st.markdown(f"**CHAVE DE ACESSO:** {chave_nfe}")
                st.markdown(f"**LINK PDF:** [CLIQUE AQUI PARA BAIXAR]({link_pdf})")
    
    with col2:
        if st.button("🛡️ GERAR CERTIFICADO DE GARANTIA ETERNA", use_container_width=True, type="primary"):
            with st.spinner("GERANDO CERTIFICADO DE GARANTIA..."):
                time.sleep(1.5)
                
                numero_garantia = f"GAR-{random.randint(100000, 999999)}"
                link_pdf = f"https://mlagosatelie.com.br/garantia/{numero_garantia}.pdf"
                
                texto_juridico = """
                CERTIFICADO DE GARANTIA ETERNA

                Pelo presente instrumento, a Mlagos Ateliê Joalheira, inscrita no CNPJ 00.000.000/0001-00, 
                garante ao titular deste certificado a reparação, reposição ou substituição gratuita do produto 
                descrito, em caso de defeito de fabricação, pelo prazo de 5 (cinco) anos, a contar da data de emissão.

                A GARANTIA ETERNA, conforme política comercial da Mlagos Ateliê, assegura ainda que, após o prazo 
                legal de 5 (cinco) anos, o cliente titular continuará beneficiando-se de condições especiais de manutenção, 
                conserto, limpeza e restauração do produto, sem custos de mão de obra, mediante a apresentação deste 
                certificado e do comprovante de aquisição.

                Esta garantia não cobre danos decorrentes de mau uso, acidentes, exposição a produtos químicos 
                agressivos, ou alterações efetuadas por terceiros não autorizados.
                """
                
                doc = {
                    'Tipo': 'GARANTIA ETERNA',
                    'Cliente': cliente_selecionado,
                    'Pedido': pedido_id,
                    'Número Garantia': numero_garantia,
                    'Link PDF': link_pdf,
                    'Texto Jurídico': texto_juridico,
                    'Data Emissão': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                }
                st.session_state['documentos']['garantias_emitidas'].append(doc)
                
                st.success("CERTIFICADO DE GARANTIA ETERNA GERADO!")
                st.markdown(f"**NÚMERO DA GARANTIA:** {numero_garantia}")
                st.markdown(f"**LINK PDF:** [CLIQUE AQUI PARA BAIXAR]({link_pdf})")
                
                with st.expander("VER TEXTO JURÍDICO COMPLETO"):
                    st.text(texto_juridico)
    
    # HISTÓRICO DE DOCUMENTOS
    st.markdown("---")
    st.markdown("### HISTÓRICO DE DOCUMENTOS EMITIDOS")
    
    todas_nfe = pd.DataFrame(st.session_state['documentos']['nfe_emitidas'])
    todas_garantias = pd.DataFrame(st.session_state['documentos']['garantias_emitidas'])
    
    if not todas_nfe.empty:
        st.markdown("**NFE EMITIDAS**")
        st.dataframe(todas_nfe, use_container_width=True, hide_index=True)
    
    if not todas_garantias.empty:
        st.markdown("**GARANTIAS EMITIDAS**")
        st.dataframe(todas_garantias.drop(columns=['Texto Jurídico'], errors='ignore'), use_container_width=True, hide_index=True)

# ==================== NAVEGAÇÃO LATERAL ====================
st.sidebar.markdown("# 💎 MLAGOS ATELIÊ")
st.sidebar.markdown("### ERP JOALHEIRO")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "MENU",
    [
        "💎 DASHBOARD",
        "📋 KANBAN",
        "💰 FINANCEIRO",
        "👤 CLIENTES",
        "📦 ESTOQUE",
        "🌐 INTEGRAÇÃO E-COMMERCE",
        "📄 DOCUMENTOS (NFE / GARANTIA)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"<<small>USUÁRIO: ADMINISTRADOR<br>DATA: {datetime.now().strftime('%d/%m/%Y')}</small>", unsafe_allow_html=True)

# ==================== ROTEAMENTO ====================
if menu == "💎 DASHBOARD":
    modulo_dashboard()
elif menu == "📋 KANBAN":
    modulo_kanban()
elif menu == "💰 FINANCEIRO":
    modulo_financeiro()
elif menu == "👤 CLIENTES":
    modulo_clientes()
elif menu == "📦 ESTOQUE":
    modulo_estoque()
elif menu == "🌐 INTEGRAÇÃO E-COMMERCE":
    modulo_ecommerce()
elif menu == "📄 DOCUMENTOS (NFE / GARANTIA)":
    modulo_documentos()