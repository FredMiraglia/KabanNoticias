import html
import re
import urllib.parse
import feedparser
import requests
import streamlit as st

# Configuração da página mobile-friendly com Kabar e ícone 3D
st.set_page_config(
    page_title="Kabar - Notícias Globais e Esportes",
    page_icon="https://images.unsplash.com/photo-1614730321146-b6fa6a46bcb4?w=128&q=80",
    layout="centered",
)

# Estilização CSS Avançada (Glassmorphism & Neon accents)
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #111827 100%);
        color: #f3f4f6;
    }
    .kabar-hero {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 10px 0 20px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
    }
    .kabar-logo-3d {
        width: 64px;
        height: 64px;
        border-radius: 16px;
        object-fit: cover;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
        border: 2px solid rgba(59, 130, 246, 0.5);
    }
    .kabar-title-group h1 {
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #60a5fa, #3b82f6, #9333ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .kabar-title-group p {
        font-size: 0.9rem;
        color: #9ca3af;
        margin: 2px 0 0 0;
    }
    .news-card {
        padding: 18px;
        border-radius: 16px;
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        margin-bottom: 16px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        display: flex;
        gap: 16px;
        align-items: flex-start;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .news-card:hover {
        transform: translateY(-2px);
        border-color: rgba(96, 165, 250, 0.4);
    }
    .news-image {
        width: 120px;
        height: 95px;
        object-fit: cover;
        border-radius: 12px;
        flex-shrink: 0;
        background-color: #1f2937;
    }
    .news-content {
        flex-grow: 1;
    }
    .news-title {
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
        text-decoration: none;
        display: block;
        margin-bottom: 6px;
        line-height: 1.35;
    }
    .news-title:hover {
        color: #60a5fa;
        text-decoration: underline;
    }
    .news-summary {
        font-size: 12px;
        color: #9ca3af;
        line-height: 1.45;
        margin-bottom: 12px;
    }
    .news-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        padding-top: 10px;
    }
    .news-source {
        font-size: 11px;
        color: #60a5fa;
        font-weight: 600;
        background: rgba(59, 130, 246, 0.1);
        padding: 2px 8px;
        border-radius: 6px;
    }
    .share-buttons {
        display: flex;
        gap: 6px;
    }
    .share-btn {
        background-color: rgba(55, 65, 81, 0.6);
        color: #e5e7eb;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 10px;
        text-decoration: none;
        font-weight: 600;
        transition: background 0.2s, color 0.2s;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    .share-btn:hover {
        background-color: #3b82f6;
        color: white;
    }
    .disclaimer-box {
        font-size: 10px;
        color: #6b7280;
        text-align: center;
        padding: 15px 0;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 30px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Feeds RSS temáticos
RSS_SOURCES = {
    "⚽ Esportes & Futebol": {
        "GE - Globo Esporte": "https://ge.globo.com/rss/ge/",
        "Lance!": "https://www.lance.com.br/rss",
        "UOL Esporte": "https://esporte.uol.com.br/index.xml",
    },
    "🎯 Concursos & Empregos": {
        "E-Konomista Empregos": "https://www.ekonomista.pt/emprego/feed/",
        "G1 Carreiras": "https://g1.globo.com/rss/g1/concursos-e-emprego/",
    },
    "🏛️ Política & Brasil": {
        "G1 Política": "https://g1.globo.com/rss/g1/politica/",
        "CNN Brasil": "https://www.cnnbrasil.com.br/feed/",
    },
    "🚀 Tecnologia & Ciência": {
        "Tecnoblog": "https://tecnoblog.net/feed/",
        "Canaltech": "https://canaltech.com.br/rss/",
    },
    "📈 Economia": {
        "G1 Economia": "https://g1.globo.com/rss/g1/economia/",
        "InfoMoney": "https://www.infomoney.com.br/feed/",
    },
}

# Imagens ilustrativas seguras (Unsplash) por categoria
CATEGORY_IMAGES = {
    "⚽ Esportes & Futebol": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=300&q=80",
    "🎯 Concursos & Empregos": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=300&q=80",
    "🏛️ Política & Brasil": "https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=300&q=80",
    "🚀 Tecnologia & Ciência": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=300&q=80",
    "📈 Economia": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=300&q=80",
}

# Cabeçalho Principal com Logo 3D
st.markdown(
    """
    <div class="kabar-hero">
        <img src="https://images.unsplash.com/photo-1614730321146-b6fa6a46bcb4?w=250&q=80" class="kabar-logo-3d" alt="Kabar 3D Logo">
        <div class="kabar-title-group">
            <h1>Kabar</h1>
            <p>Seu agregador de notícias global e interativo</p>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# Painel Lateral de Controle
st.sidebar.markdown("### 🌍 **Configurações Kabar**")
st.sidebar.markdown("Personalize os feeds exibidos:")

selected_categories = []
for category in RSS_SOURCES.keys():
    if st.sidebar.checkbox(category, value=True):
        selected_categories.append(category)

# Seção de escolha de clube favorito (aparece se a categoria de esportes estiver marcada)
clube_selecionado = "Todos os Clubes"
if "⚽ Esportes & Futebol" in selected_categories:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚽ **Seu Clube de Futebol**")
    clubes_lista = [
        "Todos os Clubes",
        "Flamengo",
        "Palmeiras",
        "Corinthians",
        "São Paulo",
        "Vasco",
        "Fluminense",
        "Botafogo",
        "Grêmio",
        "Internacional",
        "Atlético-MG",
        "Cruzeiro",
        "Bahia",
        "Remo",
        "Paysandu",
        "Santos",
    ]
    clube_selecionado = st.sidebar.selectbox("Escolha seu time do coração:", clubes_lista)

if st.sidebar.button("🔄 Atualizar Feed", use_container_width=True):
    st.rerun()

st.sidebar.markdown("---")

# ESPAÇO DE CONTATO PARA O DONO DO APP
st.sidebar.markdown("### 💬 Fale com o Desenvolvedor")
st.sidebar.markdown(
    "Tem alguma sugestão, encontrou um erro ou quer sugerir um novo tema? Mande uma mensagem!"
)

with st.sidebar.form("form_contato"):
    nome_usuario = st.text_input("Seu Nome")
    mensagem_usuario = st.text_area("Sua Mensagem ou Sugestão")
    enviar_msg = st.form_submit_button("Enviar Mensagem")

    if enviar_msg:
        if nome_usuario and mensagem_usuario:
            meu_whatsapp = "5591998339441"
            texto_wpp = f"Olá! Me chamo {nome_usuario} e enviei esta mensagem pelo app Kabar:\n\n{mensagem_usuario}"
            link_wpp_dono = f"https://api.whatsapp.com/send?phone={meu_whatsapp}&text={urllib.parse.quote(texto_wpp)}"

            st.success("Mensagem pronta para envio!")
            st.markdown(
                f'<a href="{link_wpp_dono}" target="_blank" style="display: block; text-align: center; background-color: #25d366; color: white; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 10px;">📲 Clique aqui para enviar no WhatsApp do Dono</a>',
                unsafe_allow_html=True,
            )
        else:
            st.warning("Por favor, preencha o nome e a mensagem.")

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Dica:** Instale este app na tela inicial do seu celular para acesso rápido."
)


# Função robusta para buscar feed via HTTP simulando um navegador real
def fetch_feed_data(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return feedparser.parse(response.content)
    except Exception:
        pass
    return feedparser.parse(url)


# Renderização por Abas Dinâmicas
if selected_categories:
    tabs = st.tabs(selected_categories)

    for i, category in enumerate(selected_categories):
        with tabs[i]:
            sources = RSS_SOURCES[category]
            total_cat_articles = 0
            fallback_image = CATEGORY_IMAGES.get(
                category, "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=300&q=80"
            )

            for source_name, url in sources.items():
                feed = fetch_feed_data(url)

                if not feed or not feed.entries:
                    continue

                for entry in feed.entries:
                    title = entry.get("title", "Sem título")
                    link = entry.get("link", "#")
                    summary = entry.get(
                        "summary",
                        entry.get("description", "Sem descrição disponível."),
                    )

                    # Se estiver na aba de esportes e o usuário escolheu um clube específico, aplica o filtro
                    if category == "⚽ Esportes & Futebol" and clube_selecionado != "Todos los Clubes" and clube_selecionado != "Todos os Clubes":
                        texto_analise = f"{title} {summary}".lower()
                        if clube_selecionado.lower() not in texto_analise:
                            continue  # Pula notícias que não citam o time escolhido

                    total_cat_articles += 1
                    clean_summary = re.sub("<.*?>", "", summary)
                    if len(clean_summary) > 130:
                        clean_summary = clean_summary[:130] + "..."

                    image_url = fallback_image

                    # Links de compartilhamento social
                    share_text = f"Olha essa notícia no Kabar: {title} - {link}"
                    encoded_text = urllib.parse.quote(share_text)
                    encoded_url = urllib.parse.quote(link)
                    encoded_title = urllib.parse.quote(title)

                    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                    twitter_url = f"https://twitter.com/intent/tweet?text={encoded_title}&url={encoded_url}"
                    facebook_url = (
                        f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"
                    )
                    telegram_url = (
                        f"https://t.me/share/url?url={encoded_url}&text={encoded_title}"
                    )

                    # Card Moderno com Glassmorphism
                    st.markdown(
                        f"""
                        <div class="news-card">
                            <img src="{image_url}" class="news-image" alt="Thumbnail">
                            <div class="news-content">
                                <a href="{link}" target="_blank" class="news-title">{title}</a>
                                <div class="news-summary">{clean_summary}</div>
                                <div class="news-footer">
                                    <span class="news-source">{source_name}</span>
                                    <div class="share-buttons">
                                        <a href="{whatsapp_url}" target="_blank" class="share-btn" title="WhatsApp">💬 Wpp</a>
                                        <a href="{twitter_url}" target="_blank" class="share-btn" title="X (Twitter)">🐦 X</a>
                                        <a href="{facebook_url}" target="_blank" class="share-btn" title="Facebook">📘 Face</a>
                                        <a href="{telegram_url}" target="_blank" class="share-btn" title="Telegram">✈️ Tel</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Limita a exibir até 6 notícias correspondentes por fonte
                    if total_cat_articles >= 10:
                        break

            if total_cat_articles == 0:
                if category == "⚽ Esportes & Futebol" and clube_selecionado != "Todos os Clubes":
                    st.info(f"Nenhuma notícia recente encontrada especificamente sobre o **{clube_selecionado}** no momento. Tente selecionar 'Todos os Clubes' para ver o feed geral de esportes.")
                else:
                    st.info("Nenhuma notícia encontrada nesta categoria no momento.")
else:
    st.warning("⚠️ Nenhuma categoria selecionada na barra lateral.")

# Rodapé com Aviso Legal
st.markdown(
    """
    <div class="disclaimer-box">
        <strong>Kabar Notícias Globais</strong> é um agregador independente de links RSS públicos. 
        Todo o conteúdo, marcas e direitos autorais das notícias exibidas pertencem exclusivamente aos seus respectivos veículos de imprensa originais.
    </div>
    """,
    unsafe_allow_html=True,
)
