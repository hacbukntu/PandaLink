from flask import Flask, render_template, request, redirect
import sqlite3, random, string

app = Flask(__name__)

def generar_codigo():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def db():
    return sqlite3.connect('db.db')

@app.route('/', methods=['GET','POST'])
def index():
    short_link = None
    if request.method == 'POST':
        url = request.form['url']
        codigo = generar_codigo()

        conn = db()
        c = conn.cursor()
        c.execute("INSERT INTO links (codigo, url, clicks) VALUES (?,?,0)", (codigo,url))
        conn.commit()
        conn.close()

        short_link = request.host_url + codigo

    return render_template('index.html', short_link=short_link)

@app.route('/<codigo>')
def visitar(codigo):
    if request.headers.get("User-Agent") == "":
        return "Bot bloqueado"
    
    conn = db()
    c = conn.cursor()
    c.execute("SELECT id,url,clicks FROM links WHERE codigo=?", (codigo,))
    data = c.fetchone()
    if data:
        link_id, url, clicks = data
        c.execute("UPDATE links SET clicks=? WHERE id=?", (clicks+1, link_id))
        conn.commit()
        conn.close()
        return render_template("espera.html", url=url)
    return render_template("error.html")

@app.route('/go')
def go():
    return redirect(request.args.get('url'))

@app.route("/privacidad")
def privacidad():
    return render_template("privacidad.html")

@app.route("/contacto")
def contacto():
    return render_template("contacto.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

conn = db()
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY, codigo TEXT, url TEXT, clicks INTEGER)")
conn.commit()
conn.close()

if __name__ == "__main__":
    app.run()
