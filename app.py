from flask import Flask, session, Response
from flask import request, render_template, url_for, redirect, flash, send_from_directory,make_response,jsonify
from dbconnect import connection
from functools import wraps
from passlib.hash import sha256_crypt
import gc
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json
import warnings

app = Flask(__name__)

dia = str(datetime.now().strftime("%d-%m-%Y"))


UPLOAD_FOLDER = "./static/uploads"
PORTIFOLIO_FOLDER = "./static/portifolio_img"
# MEMORY_GAME_FOLDER = "/Users/rafael/Desktop/Projetos Python/Portifolio Rafael/static/memorygame"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}



app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PORTIFOLIO_FOLDER'] = PORTIFOLIO_FOLDER



def InsertSql(myDict,table):
    try:
        print('INSERINDO AGENDA....')
        c, conn = connection()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in myDict.keys())
            values = ', '.join("'" + str(x) + "'" for x in myDict.values())
            c.execute('SET @@auto_increment_increment=1;')
            conn.commit()
            sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % (table, columns, values)
            c.execute(sql)
            conn.commit()
        print(f'INSERIDO : { myDict} {{status :: OK}} ')
    except Exception as e:
        print(f' ERROR:       {str(e)}')
        return (str(e))
def SelectSql(table, coluna,value):
    try:
        c,conn = connection()
        x = c.execute(f"""SELECT * FROM {table} WHERE {coluna}= '{value}'""")
        if int(x) > 0:
            myresult = c.fetchall()
            return myresult
        if int(x) == 0:
            return False
    except Exception as e:
        print(f' ERROR:       {str(e)}')
        return (str(e))

def UpdateQuerySql(mydict,table,item,modifica):
    print(' ATUALIZANDO DADOS .... ')
    c, conn = connection()
    for k in mydict:
        coluna = (k)
        value = (mydict[k])
        sql = (f"""UPDATE `{table}` SET `{coluna}` = '{value}' WHERE (`{item}` = '{modifica}');""")
        c.execute(sql)
        conn.commit()
        conn.close
    print(f'--->>> ATUALIZAÇÃO da TABELA :{table}  == > DATA {mydict}{{status :: OK}} .... ')


def Select_all(table):
    try:
        c,conn = connection()
        x = c.execute(f"""SELECT * FROM {table}""")
        if int(x) > 0:
            myresult = c.fetchall()
            return myresult
        if int(x) == 0:
            return False
    except Exception as e:
        print(f' ERROR:       {str(e)}')
        return (str(e))


def delete_all_rows(table):
    try:
        print(f'DELETENDO ITENS DA TABELA {table}....')
        c, conn = connection()
        sql = "DELETE FROM %s ;" % (table)
        c.execute(sql)
        conn.commit()
        print('TODAS AS ROWS FORAM DELETADAS {{status :: OK}} ')
    except Exception as e:
        print(f' ERROR:       {str(e)}')
        return (str(e))
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Precisa fazer o Login")
            return redirect(url_for('login'))
    return wrap









@app.route('/transfer_images/<filename>', methods=['GET', 'POST'])
def memory_images(filename):
    return send_from_directory(app.config['PORTIFOLIO_FOLDER'],
                               filename)

@app.route("/", methods=['GET'])
def home():
    files = os.listdir(UPLOAD_FOLDER)
    jobs = Select_all('portifolio')
    print(jobs)


    return render_template("teste.html", files=jobs)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    jobs = Select_all('portifolio')
    print(jobs)
    return render_template('dashboard.html')


@app.route('/logout/')
@login_required
def logout():
    session.clear()
    # flash('Voce esta saindo do APP! Obrigado')
    return redirect(url_for('home'))

@app.route('/login/', methods=['POST'])
def login():
    error = ''
    try:
        if request.method == 'POST':
            email = request.form['email']
            # print(email)
            check_user = SelectSql('usuarios', 'email', email)
            # print(check_user)
            if check_user == False:
                print("Login ou Senha Errada, confira e tenta novamente", 'erro')
                return redirect(url_for('index'))
            else:
                user = check_user[0]
                email = user[2]
                id = user[0]
                check_password = user[3]
                if email == 'admin@admin.com' and request.form['password'] == '12345':
                    print('admin area')
                    session['logged_in'] = True
                    session['email'] = email
                    session['ID_User'] = id
                    session['admin'] = True
                    return redirect(url_for('dashboard'))
                else:
                    if sha256_crypt.verify(request.form['password'], check_password):
                        session['logged_in'] = True
                        session['email'] = email
                        session['ID_User'] = id

                        return redirect(url_for('home'))

                    else:
                        print('senha erro')
                        # flash("Login ou Senha Errada, confira e tenta novamente", 'erro')
                        return redirect(url_for('home'))

        return render_template("teste.html", error=error)
    except Exception as e:
        # flash(e)
        return render_template('teste.html', error=error)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/insert_usuario', methods=['GET', 'POST'])
def insert_usuario():
    try:
        if request.method == "POST":

            c, conn = connection()
            nome = request.form['nome']
            email = request.form['email']
            password = sha256_crypt.encrypt((str(request.form['password'])))

            print(nome)
            print(email)
            print(password)
            #print(confirme_password)
            x = c.execute("""
                            SELECT
                                *
                            FROM
                                usuarios
                            WHERE
                               email=%s""", [email])
            if int(x) > 0:
                flash("E-mail já está cadastrado. Verifique se está correto o email.")
                return render_template('register.html')
            if int(x) == 0:
                if sha256_crypt.verify(request.form['confirme_password'],password):

                    pontos = 0
                    c.execute("""
                    INSERT INTO
                          usuarios
                             (nome,email,password,pontos)
                             VALUES
                              (%s,%s,%s,%s)""",
                          [nome, email, password, pontos])
                    flash("Obrigado por Registrar")
                    session['logged_in'] = True
                    session['username'] = nome
                    session['email'] = email
                    session['notificacoes'] = 0
                    session['pontos'] = 0
                    conn.commit()
                    c.close()
                    conn.close()
                    gc.collect()
                    flash("Cliente Cadastrado com Sucesso")
                    return render_template('teste.html')
                else:
                    flash("Passwords diferentes, insira novamente")

                    return render_template('register.html')

            return render_template('register.html')
    except Exception as e:
        return (str(e))

@app.route('/add_jobs/', methods=['GET', 'POST'])
def add_jobs():
    c, conn = connection()
    c.execute("""
                                                        SELECT
                                                            *
                                                        FROM
                                                            portifolio
                                                        """)

    jobs = c.fetchall()

    gc.collect()
    c.close()

    return render_template('add_jobs.html', students=jobs)

@app.route('/insert_jobs', methods = ['POST'])

def insert_jobs():

    if request.method == "POST":
        flash("Job Cadastrado com Sucesso")
        c, conn = connection()
        nome = request.form['nome']
        descricao = request.form['descricao']
        linguagem = request.form['linguagem']
        entrada = request.form['entrada']
        prazo = request.form['prazo']
        link = request.form['link']
        categoria = request.form['categorias_insert']
        cliente = request.form['cliente']
        status = request.form['status_insert']

        print(f"""
NOME:{nome}
DESCRICAO:{descricao}
LINGUAGEM:{linguagem}
ENTRADA:{entrada}
PRAZO:{prazo}
LINK:{link}
CATEGORIA:{categoria}
STATUS:{status}
CLIENTE:{cliente}""")


        f = request.files['file']

        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['PORTIFOLIO_FOLDER'], filename))


        c.execute("""
            INSERT INTO
             portifolio
            (cliente,nome,descricao,linguagem,entrada,prazo,link,arquivo,atualizado,categoria,status)
                VALUES
              (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                  [cliente,nome,descricao,linguagem,entrada,prazo,link,filename,dia,categoria,status])

        return redirect(url_for('add_jobs'))

@app.route('/update_jobs/', methods=['POST', 'GET'])
def update_jobs():
    if request.method == 'POST':

        c, conn = connection()
        x = request.form
        print(x)
        job_id = request.form['id']
        nome = request.form['nome']
        descricao = request.form['descricao']
        linguagem = request.form['linguagem']
        entrada = request.form['entrada']
        prazo = request.form['prazo']
        link = request.form['link']
        cliente = request.form['cliente']
        categoria = request.form['categoria']
        status = request.form['status']

        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            flash(f'Trabalho:{nome} do Cliente {cliente}foi Editado com Sucesso')
            c.execute("""
                                                UPDATE
                                            portifolio
                                                SET
                                             nome=%s,cliente=%s,descricao=%s,
                                             linguagem=%s,entrada=%s,prazo=%s,link=%s,atualizado=%s,categoria=%s,status=%s
                                                WHERE
                                                idportifolio=%s""",
                      [nome, cliente, descricao, linguagem, entrada, prazo, link, dia, categoria, status, job_id])

            return redirect(url_for('add_jobs'))
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':

            c.execute("""
                                                UPDATE
                                            portifolio
                                                SET
                                             nome=%s,cliente=%s,descricao=%s,
                                             linguagem=%s,entrada=%s,prazo=%s,link=%s,atualizado=%s,categoria=%s,status=%s
                                                WHERE
                                                idportifolio=%s""",
                      [nome, cliente, descricao, linguagem, entrada, prazo, link, dia, categoria, status, job_id])
            flash(f'Trabalho:{nome} do Cliente {cliente}foi Editado com Sucesso')

            return redirect(url_for('add_jobs'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        #
        #     if f and allowed_file(f.filename):
        #         filename = secure_filename(f.filename)
        #         f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(filename)
        c.execute("""
                                    UPDATE
                                portifolio
                                    SET
                                 nome=%s,cliente=%s,descricao=%s,
                                 linguagem=%s,entrada=%s,prazo=%s,link=%s,atualizado=%s,categoria=%s,status=%s,arquivo=%s
                                    WHERE
                                    idportifolio=%s""",
                  [nome, cliente, descricao, linguagem, entrada, prazo, link, dia, categoria, status,filename, job_id])



        flash(f'Trabalho:{nome} do Cliente {cliente}foi Editado com Sucesso')
        return redirect(url_for('add_jobs'))

@app.route('/delete_jobs/<string:id_data>', methods = ['GET'])
def delete_usuario(id_data):
    flash("Trabalho Removido com Sucesso")
    c, conn = connection()
    c.execute("""
 DELETE
 FROM
 portifolio
  WHERE
idportifolio=%s""",
              [id_data])
    return redirect(url_for('add_jobs'))

@app.route('/portifolio/', methods=['GET', 'POST'])
def portifolio():
    c, conn = connection()
    c.execute("""
                               SELECT
                                   *
                               FROM
                                   portifolio
                               """, )

    myresult = c.fetchall()
    data = []
    for row in myresult:
        id = row[0]

        if id == None:
            print('naovai')
        else:
            data.append({
                'idportifolio': row[0],
                'cliente': row[1],
                'nome': row[2],
                'descricao': row[3],
                'linguagem': row[4],
                'entrada': row[5],
                'prazo': row[6],
                'link': row[7],
                'arquivo': row[8],
                'atualizado': row[9],
                'categoria': row[10],
                'status': row[11]
            })



    # return jsonify(matching_results=data)
    return Response(json.dumps(data), mimetype='application/json')

@app.route('/mensagens', methods=['POST'])
def mensagem():
    try:
        if request.method == "POST":
            c, conn = connection()
            nome = request.form['nome']
            email = request.form['email']
            mensagem = request.form['mensagem']
            print(nome)
            print(email)
            print(mensagem)
            c.execute("""
                                INSERT INTO
                                      mensagem
                                         (nome,email,mensagem)
                                         VALUES
                                          (%s,%s,%s)""",
                      [nome, email, mensagem])
            flash("Mensagem Enviada")
            conn.commit()
            c.close()
            conn.close()
            gc.collect()
            return render_template('teste.html')
        else:
            flash("Falha ao enviar, tente novamente!")
            return render_template('teste.html')
    except Exception as e:
        return (str(e))


@app.route("/mensagens_contato", methods=['GET', 'POST'] )
def api_info():
    c, conn = connection()
    c.execute("""
                                                                               SELECT
                                                                                   *
                                                                               FROM
                                                                                   mensagem
                                                                               """)

    myresult = c.rowcount
    conn.commit()
    c.close()
    conn.close()
    gc.collect()

    return json.dumps(myresult)

@app.route("/jobs_cadastrados", methods=['GET', 'POST'] )
def jobs_cadastrados():
    c, conn = connection()
    c.execute("""
                                                                               SELECT
                                                                                   *
                                                                               FROM
                                                                                   portifolio
                                                                               """)

    myresult = c.rowcount


    return json.dumps(myresult)





@app.route("/jogo_memoria/", methods=['GET', 'POST'])
def memory_game():
    # if request.method == 'POST':
    c, conn = connection()
    c.execute("""SELECT  foto FROM memorygame """)
    myresult = c.fetchall()


    print(myresult)
    return render_template("jogo_memoria.html", cards=myresult)



@app.route("/conferencia-teste/", methods=['GET', 'POST'])
def teste():
    return render_template("teste.html")


@app.route("/conferencia-email/", methods=['GET', 'POST'])
def prepara_email():
    if request.method == 'POST':
        print(request.form)
        links = {}
        for aula in request.form:
            print(aula)
            if aula == 'aula1':
                links.update({aula:''})



        return make_response(jsonify({'resp': 'USUÁRIO JÁ ESTÁ CADASTRADO NA PLATAFORMA'}), 200)




def main ():
    app.secret_key = 'valeteDjLm'
    port = int(os.environ.get("PORT", 5002))
    app.run (host="0.0.0.0", port=port)


if __name__ == "__main__":
   main()

#
# if __name__ == "__main__":
#
#     app.secret_key = 'maya2019'
#     app.run(debug=True, port=5002)
