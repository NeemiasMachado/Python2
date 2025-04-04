from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
import plotly.graph_objects as go
from dash import Dash, html, dcc
import dash
import numpy as np
import config

app =Flask(__name__)
DB_PATH = config.DB_PATH

# Função para inicializar o banco
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inadimplencia (
            mes TEXT PRIMARY KEY,
            inadimplencia REAL
            )
        ''')
        cursor.execute('''
           CREATE TABLE IF NOT EXISTS selic (
            mes TEXT PRIMARY KEY,
            selic_diaria REAL           
            ) 
        ''')
        conn.commit()

@app.route('/')
def index():
     return render_template_string('''
        <h1> Upload de dados Econômicos </h1>
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <label> Arquivo de Inadimplencia (CSV) :</label>
            <input type="file" name="campo_inadimplencia" required><br><br>

            <label> Arquivo da Taxa Selic (CSV) : </label>
            <input type="file" name="campo_selic" required><br><br>

            <input type="submit" value="Fazer upload">
        <form>
        <br><br>
        <a href="/consultar"> Consultar Dados Armazenado </a><br>
        <a href="/graficos"> Visualizar Gráficos </a><br>
        <a href="/editar_inadimplencia"> Editar Inadimplencias </a><br>
        <a href="/correlacao"> Analisar Correlação </a><br>
    ''')

@app.route('/upload', methods=["POST"])
def upload_dados():
   
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')

    # Verifica se os aarquivos foram enviados
    if not inad_file or not selic_file:
        return jsonify({"Erro":"Ambos os arquivos devem ser enviados"})
    
    inad_df = pd.read_csv(inad_file, sep=';', names=['data','inadimplencia'], header=0)
    selic_df = pd.read_csv(selic_file, sep=';', names=['data','selic_diaria'], header=0)

    inad_df['data'] = pd.to_datetime(inad_df['data'], format="%d/%m/%Y")
    selic_df['data'] = pd.to_datetime(selic_df['data'], format="%d/%m/%Y")

    inad_df['mes'] = inad_d['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    inad_mensal = inad_df[["mes","inadimplencia"]].drop_duplicates()
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    with sqlite3.connect(DB_PATH) as conn:
        inad_mensal.to_sql('inadimplencia', conn, if_exists='replace', index=False)
        selic_mensal.to_sql('selic', conn, if_exists='replace', index=False)
    
    return jsonify({"Mensagem": "dados armazenados com sucesso"})

@app.route('/consultar', methods=['GET', 'POST'])
def consultar_dados():
    # Resultado se essa pagina for carregada recebendo o POST
    if request.method == 'POST':
        tabela = request.form.get('campo_tabela')
        if tabela not in ['inadimplencia', 'selic']:
            return jsnofify({"erro":"Tabela inválida."}),400

        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
            return df.to_html(index=False)

    # Resultado da pagina sendo carregada a primeira vez, sem receber o POST
    return render_template_string('''
        <h1> Consulta de tabelas </h1>
        <form method="post">
            <label></label>
            <select name="campo_tabela">
                <option value="inadimplencia">  </option>
                <option value="selic">  Selic </option>
            </select>
            <input type="submit" value="Consultar">
        <form>
        <br><a href="/> Voltar </a>  
    ''')

@app.route('/graficos')
def graficos():
    with sqlite3.connect(DB_PATH) as conn:
        inad_df = pd.read_sql_query("SELECT * FROM inadimplencia", conn)
        selic_df = pd.read_sql_query("SELECT * FROM selic", conn)
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=inad_df['mes'], y=inad_df['inadimplencia'],mode='lines+markers', name='Inadimplência'))
    fig1.update_layout(title='Evoluçõ da inadimplência', xaxis_title='Mês', yaxis_title='%', template='plotly_dark')

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=selic_df['mes'], y=selic_diaria['inadimplencia'],mode='lines+markers', name='SELIC'))
    fig2.update_layout(title='Média mensal da Selic', xaxis_title='Mês', yaxis_title='Taxa', template='plotly_dark')

    grapf_html_1 = fig1.to_html(full_html=False, include_plotlyjs='cdn')
    grapf_html_2 = fig2.to_html(full_html=False, include_plotlyjs=False)

    return render-template_string('''
        <html>
            <hread>
                <title> Gráficos Econômicos </title>
                <style>
                    .container{
                    display:flex
                    justfy-content:space:space-around;
                }
                .graph{
                    widht: 48%;
                }
                </style>
            <hread>
            <body>
                <h1 style="text-align: center">Gráficos Econômicos </h1>
                <div class="conteiner">
                    <div class="graph"> {{ grafico1|safe }} </div>
                    <div class="graph"> {{ grafico2|safe }} </div>
                </div>
                <br><br>
                <div style="text=-align: center"><a href="/">Voltar</a></div>
            </body>
        <html>
    ''', grafico1=graph_html_1, grafico2=grapf_html_2)
 
    # Iniciar o servidor Flask da aplicação

if __name__ == '__main__':
    init_db()
    app.run(debug=True)