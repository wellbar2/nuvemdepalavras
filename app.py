import streamlit as st
from collections import Counter
import json
import io
import nltk
from nltk.stem import WordNetLemmatizer
import streamlit.components.v1 as components

# Baixar os recursos necessários do NLTK
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("wordnet")
nltk.download("omw-1.4")

st.set_page_config(page_title="Nuvem de Palavras", layout="wide")

st.title("Gerar Nuvem de Palavras")
st.markdown("Envie um arquivo `.txt` onde **cada linha é um termo**.")

# Checkbox para aplicar lematização
use_lemmatization = False
#use_lemmatization = st.checkbox("Usar lematização nas palavras (Funciona melhor para inglês)", value=False)

uploaded_file = st.file_uploader("Selecione o arquivo .txt", type="txt")

if uploaded_file is not None:
    conteúdo = uploaded_file.read().decode("utf-8")
    termos = [linha.strip() for linha in conteúdo.splitlines() if linha.strip()]

    if not termos:
        st.warning("O arquivo está vazio ou não contém termos válidos.")
    else:
        if use_lemmatization:
            lemmatizer = WordNetLemmatizer()
            # Tokeniza cada linha, lematiza cada palavra e junta novamente
            termos = [
                ' '.join([lemmatizer.lemmatize(palavra) for palavra in nltk.word_tokenize(termo.lower())])
                for termo in termos
            ]
        else:
            termos = [termo.lower() for termo in termos]

        frequencias = Counter(termos)

        tamanhoMinimo = 10
        tamanhoMaximo = 100
        maiorFrequencia = max(frequencias.values()) if frequencias else 1

        words = [{
            'text': termo,
            'size': int(((freq / maiorFrequencia) * (tamanhoMaximo - tamanhoMinimo)) + tamanhoMinimo),
            'count': freq
        } for termo, freq in frequencias.items()]

        # HTML com D3.js
        html_content = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Nuvem de Palavras Interativa</title>
    <script src="https://d3js.org/d3.v5.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3-cloud/1.2.5/d3.layout.cloud.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
        }}
        #word-cloud {{
            width: 1000px;
            height: 600px;
            border: 1px solid #ccc;
            margin: auto;
        }}
    </style>
</head>
<body>
    <h1 style="text-align: center;">Nuvem de palavras</h1>
    <div id="word-cloud"></div>
    <script>
        var words = {json.dumps(words)};

        var width = 1000;
        var height = 600;

        var svg = d3.select("#word-cloud").append("svg")
            .attr("width", width)
            .attr("height", height);

        var layout = d3.layout.cloud()
            .size([width, height])
            .words(words)
            .padding(2)
            .rotate(function() {{ return ~~(Math.random() * 2) * 90; }})
            .font("Impact")
            .fontSize(function(d) {{ return d.size; }})
            .on("end", draw);

        layout.start();

        function draw(words) {{
            svg.append("g")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
              .selectAll("text")
                .data(words)
              .enter().append("text")
                .style("font-size", function(d) {{ return d.size + "px"; }})
                .style("font-family", "Impact")
                .style("fill", function(d, i) {{ return d3.schemeCategory10[i % 10]; }})
                .attr("text-anchor", "middle")
                .attr("transform", function(d) {{
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                }})
                .text(function(d) {{ return d.text; }})
                .on("mouseover", function(event, d) {{
                    d3.select(this).style("fill", "red");
                }})
                .on("mouseout", function(event, d, i) {{
                    d3.select(this).style("fill", function(d, i) {{ return d3.schemeCategory10[i % 10]; }});
                }});
        }}

        // Criação da legenda abaixo da nuvem de palavras
        var legend = d3.select("body").append("div")
            .attr("id", "legend")
            .style("width", "1000px")
            .style("margin", "20px auto 0 auto")
            .style("background-color", "rgba(255,255,255,0.8)")
            .style("padding", "5px")
            .style("border", "1px solid #ccc");

        legend.append("h3")
            .style("font-size", "14px")
            .style("margin", "2px 0")
            .text("Top 20 Palavras");

        var legendData = words.sort(function(a, b) {{ return b.count - a.count; }}).slice(0,20);
        legend.selectAll("p")
            .data(legendData)
            .enter().append("p")
            .style("font-size", "12px")
            .style("margin", "2px 0")
            .html(function(d, i) {{
                return '<span style="color:' + d3.schemeCategory10[i % 10] + ';">&#9679;</span> ' + d.text + ' (' + d.count + ')';
            }});
    </script>
</body>
</html>"""

        # Mostra a prévia renderizada da nuvem
        st.subheader("Prévia da Nuvem de Palavras")
        components.html(html_content, height=800, scrolling=True)

        # Prepara para download
        html_bytes = io.BytesIO()
        html_bytes.write(html_content.encode("utf-8"))
        html_bytes.seek(0)

        st.download_button(
            label="Baixar Nuvem de Palavras (HTML)",
            data=html_bytes,
            file_name="nuvem_de_palavras.html",
            mime="text/html"
        )