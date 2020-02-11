from flask import Flask, session, Response
from flask import request, render_template, url_for, redirect, flash, send_from_directory
from dbconnect import connection
from functools import wraps
from passlib.hash import sha256_crypt
import gc
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json


app = Flask(__name__)

dia = str(datetime.now().strftime("%d-%m-%Y"))


UPLOAD_FOLDER = "./static/uploads"
MEMORY_GAME_FOLDER = "/Users/rafael/Desktop/Projetos Python/Portifolio Rafael/static/memorygame"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MEMORY_GAME_FOLDER'] = MEMORY_GAME_FOLDER
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Precisa fazer o Login")
            return redirect(url_for('login'))
    return wrap

@app.route('/transfer/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    if filename == '.DS_Store':
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                               'cartaz_logo.jpg')
    else:
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/transfer_images/<filename>', methods=['GET', 'POST'])
def memory_images(filename):

    return send_from_directory(app.config['MEMORY_GAME_FOLDER'],
                               filename)

@app.route("/", methods=['GET'])
def home():
    files = os.listdir(UPLOAD_FOLDER)


    return render_template("teste.html", files=files)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    try:
        if request.method == 'GET':
            return render_template('dashboard.html')
    except Exception as e:
        return (str(e))

@app.route('/logout/')
@login_required
def logout():
    session.clear()
    flash('Voce esta saindo do APP! Obrigado')
    return redirect(url_for('home'))

@app.route('/login/', methods=['POST'])
def login():
    error = ''

    try:
        c, conn = connection()
        print('connect')
        if request.method == 'POST':
            email = request.form['email']
            print(email)
            x = c.execute("""
                            SELECT
                                *
                            FROM
                                usuarios
                            WHERE
                               email=%s""", [email])
            print(x)

            if int(x) > 0:
                data = c.fetchone()[3]
                print(data)

                # if int(x) > 0:
                if sha256_crypt.verify(request.form['password'], data):
                    session['logged_in'] = True
                    session['username'] = email
                    flash("Bem-Vindo")
                    return redirect(url_for('home'))

                else:
                    flash("SENHA INVALIDA")
            if int(x) == 0:
                email = request.form['email']
                print(email)

                password_admin = "figueiradafoz"
                data = sha256_crypt.encrypt((str(password_admin)))


                if sha256_crypt.verify(request.form['password'], data):
                    session['admin'] = True
                    session['email'] = email

                    return redirect(url_for('dashboard'))
                else:
                    flash("USUARIO NAO EXISTE, FACA CADASTRO ")

            # if int(x) > 0:
            #     myresult = c.fetchall()
            #     for x in myresult:
            #         id_usuario = x[0]
            #         nome = x[1]
            #         senha = x[2]
            #         email = x[3]
            #         pontos = x[7]
            #     print(myresult)
            #     session['logged_in'] = True
            #     # session['id_user'] = id_user
            #     session['username'] = nome
            #     # session['endereco'] = endereco
            #     # session['telefone'] = telefone
            #     session['email'] = email
            #     session['user_pontos'] = pontos
            #     session['notificacoes'] = 0
            #
            #     c.close()
            #     flash("Bem Vindo " + nome)
            #     return redirect(url_for('home'))



            if request.form['email'] == "admin@admin.com" and request.form['password'] == "123456":
                session['admin'] = True
                session['email'] = email

                return redirect(url_for('dashboard'))


        return render_template("teste.html", error=error)
    except Exception as e:
        flash(e)
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
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


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



# def main ():
#     app.secret_key = 'valeteDjLm'
#     port = int(os.environ.get("PORT", 5002))
#     app.run (host="0.0.0.0", port=port)
#
# if __name__ == "__main__":
#    main()


if __name__ == "__main__":

    app.secret_key = 'maya2019'
    app.run(debug=True, port=5002)
