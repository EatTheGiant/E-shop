#!/usr/bin/env python
# -*- coding: utf_8 -*-

##------------------------------------------------------------------------------------------------------------------
##DONE do profilu zakaznika vlozit historiu jeho objednavok (prehlad) ak nejake uz ma
##DONE potvrdenie objednavky - insert alebo update tab_zakaznici
##DONE po uploade obrazkov zobrazit v editaii produktu (umoznit odstranenie a oznacenie jedneho ako hlavny obrazok)
##FIXME po pridavani produktu uz neinsertnut druhykrat v rezime pridavania produktu
##------------------------------------------------------------------------------------------------------------------

import os, datetime
import sqlite3
from flask import Flask, render_template, jsonify, g, redirect, request, make_response
from flaskrun import flaskrun
from functools import wraps

path = lambda p1, p2: os.path.abspath(os.path.join(p1, p2))

mapuj_stlpce = lambda nazvy, hodnoty: dict(zip(nazvy, hodnoty))

daj_session_id = lambda request: '[{br}]{cas}'.format(br  = request.user_agent.browser, cas = presny_cas_str())

def presny_cas():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=2)

def presny_cas_str():
    return presny_cas().strftime("%Y-%m-%d %H:%M:%S.%f")

_POVOLENE_PRIPONY = set(['jpg', 'png'])

def povoleny_typ_upload_suboru(filename, *args, **kwargs):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in _POVOLENE_PRIPONY

_BASEDIR = os.path.dirname(os.path.realpath(__file__))
if _BASEDIR is None:
    _BASEDIR = path(os.getcwd(), os.path.dirname(__file__))

_DATABASE = path(_BASEDIR, 'db/eshop_data.db')
_UPLOAD_DIR = path(_BASEDIR, 'static/img/velke')

# staticka cesta, jedine do nej sa dokaze pozriet uzivatel

app = Flask(__name__, static_url_path='/static')
app.url_map.strict_slashes = False

def safe_str(obj):
    try:
        if not obj or not str(obj).strip():
            return ""
        else:
            return str(obj)
    except UnicodeEncodeError:
        return unicode(obj).encode('ascii', 'xmlcharrefreplace')
    pass

def get_db():
    '''
    funkcia get_db:
    >>> ziskanie konekcie na databazu SQLite
    >>> konekciu uklada do globalnej premennej
    '''
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(_DATABASE)
    return db
    pass

@app.teardown_appcontext
def close_connection(exception):
    '''
    funkcia close_connection:
    >>> uzavrie konekciu na databazu SQLite pri ukonceni aplikacie
    '''
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    pass

def query_db(query, args=(), one=False, commit=False):
    '''
    funkcia query_db:
    >>> vykonava SQL prikazy (napr. select, update, delete) podla parametrov
    '''
    cur = get_db().execute(query, args)
    if (commit):
        get_db().commit()
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
    pass

#=======================================================================    
#=======================================================================    
#=======================================================================    

def prihlasenie_nutne(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not 'login' in request.cookies:
            return redirect("/prihlasit", code=302)
        return f(*args, **kwargs)
    return wrapper

def zisti_prihlasenie(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        _je_admin   = False
        _prihlaseny = False
        _login      = ''
        if 'login' in request.cookies:
            _prihlaseny = True
            _login      = request.cookies['login']
        if 'role' in request.cookies and 'ADMIN' in request.cookies['role'].split(','):
            _je_admin = True
        kwargs['admin']      = _je_admin
        kwargs['prihlaseny'] = _prihlaseny
        kwargs['login']      = _login
        return f(*args, **kwargs)
    return wrapper


def vytvor_session(request):
    session_id = daj_session_id(request)                
    resp = jsonify({'message': 'OK'})
    expiracna_doba = datetime.datetime.now()
    expiracna_doba += datetime.timedelta(hours=8)
    resp.set_cookie('session_id', session_id, expires=expiracna_doba)    
    return resp

@app.route("/kosik/<produkt_id>", methods=['PUT'])
def vloz_do_kosika(produkt_id, *args, **kwargs):
    #--------------------------------------------------
    SESSION_ID = ''
    nova_session = False
    if request.cookies \
    and 'session_id' in request.cookies \
    and request.cookies['session_id'] is not None:
        SESSION_ID = request.cookies['session_id']
    
    if SESSION_ID == '':
        nova_session = True
        SESSION_ID = daj_session_id(request);
    #--------------------------------------------------
    SEL_SQL = ''' select ifnull(max(obj_id), -1) from tab_objednavky where obj_session = '{str}' '''.format(str = SESSION_ID)
    _id_objednavky = query_db(SEL_SQL)[0][0]
    
    _datum_cas = presny_cas_str()

    _obr_id = safe_str(request.json['obrazok'])
    print(">>>> obr_id" + _obr_id)

    _id_existujuca_polozka = -1

    if (_id_objednavky < 0):
        '''
        '''
        ##============================================
        INS_HLAVICKY_SQL = '''
            INSERT INTO tab_objednavky (
                zak_id, obj_session, obj_datum_cas, obj_cena, obj_stav, obj_id
            ) VALUES (
                {zak_id}, '{obj_session}', '{obj_datum_cas}',   
                (select sum(pro_cena) from tab_produkty where pro_id = {pro_id}), 
                'KOS', 
                (select ifnull(max(obj_id),0)+1 from tab_objednavky)
            )
        '''
        query_db(INS_HLAVICKY_SQL.format(
            zak_id          = 0,        
            obj_session     = SESSION_ID,   
            obj_datum_cas   = _datum_cas,     
            pro_id          = produkt_id)
            , commit = True)
        
        _id_objednavky = query_db(SEL_SQL)[0][0]
        ##============================================
    else:
        SEL_EXISTUJUCA_POLOZKA_SQL = '''
            select ifnull(max(pol_id), -1) as polozka_id
            from tab_polozky_objednavky
            where obj_id = {obj_id}
            and   pro_id = {produkt_id}
            and   obr_id = {obr_id}
        '''.format(
            obj_id      = _id_objednavky,
            produkt_id  = produkt_id,
            obr_id      = _obr_id)
        _id_existujuca_polozka = query_db(SEL_EXISTUJUCA_POLOZKA_SQL)[0][0]

    if (_id_existujuca_polozka < 0):
        ### ------------------------------------------------------------
        ### objednavka neobsahuje polozku s rovnakym "pro_id" a "obr_id"
        ### ------------------------------------------------------------
        INS_POLOZKY_SQL = '''
            INSERT INTO tab_polozky_objednavky (
                obj_id,
                cena,
                pocet,
                pro_id,
                pol_id,
                obr_id
            ) VALUES (
                {obj_id},
                (select sum(pro_cena) from tab_produkty where pro_id = {produkt_id}),
                1,
                {produkt_id},
                (select ifnull(max(pol_id),0)+1 from tab_polozky_objednavky),
                {obr_id}
            )
        '''
        query_db(INS_POLOZKY_SQL.format(
            obj_id      = _id_objednavky,
            produkt_id  = produkt_id,
            obr_id      = _obr_id)
        , commit = True)
    else:
        ### -------------------------------------------------------------
        ### objednavka uz obsahuje polozku s rovnakym "pro_id" a "obr_id"
        ### -------------------------------------------------------------
        UPD_POCET_SQL = """
        update tab_polozky_objednavky
            set pocet = ifnull(pocet,0) + 1
            where pol_id = {}
        """.format( _id_existujuca_polozka )
        query_db(UPD_POCET_SQL, commit = True)
        ### -------------------------------------------------------------

    UPD_CENA_SQL = '''
    update tab_objednavky set obj_cena = (
        select ifnull(sum(pol.cena * pol.pocet),0) as cena
        from tab_polozky_objednavky pol
        where pol.obj_id = tab_objednavky.obj_id
    )
    where obj_id = {}
    '''
    query_db(UPD_CENA_SQL.format(
        _id_objednavky
    ), commit = True)

    resp = jsonify({'message': 'OK'})
    if nova_session:
        expiracna_doba = datetime.datetime.now()
        expiracna_doba += datetime.timedelta(hours=2)
        resp.set_cookie('session_id', SESSION_ID, expires=expiracna_doba) 
    return resp

    
#>>> zobrazi zakladny prehlad(main stranku) nacita template prehlad.html
@app.route("/prehlad")
@zisti_prihlasenie
def zobraz_prehlad(*args, **kwargs):
    return render_template('prehlad.html', kwargs = kwargs)
    pass

@app.route("/prihlasit", methods=['GET'])
@zisti_prihlasenie
def prihlasit_get(*args, **kwargs):
    return render_template('prihlasit.html', kwargs = kwargs)

@app.route("/prihlasit", methods=['PUT'])
def prihlasit_put(*args, **kwargs):
    _meno  = safe_str(request.json['meno'])
    _heslo = safe_str(request.json['heslo'])
    SQL = "select ifnull(max(pou_id),0), ifnull(pou_role,'') from tab_pouzivatelia where pou_login = '{}' and pou_heslo = '{}' "
    rec = query_db(SQL.format(_meno, _heslo), ())[0]
    if rec is not None:
        _id         = rec[0]
        _role       = rec[1]
        if _id and _id > 0:
            resp = jsonify({'sprava': 'PRIHLÁSENÝ',
                            'login': _meno})
            expire_date = datetime.datetime.now()
            expire_date = expire_date + datetime.timedelta(hours=2)
            ## nasetujem COOKIE:
            resp.set_cookie('login',     _meno, expires=expire_date)
            resp.set_cookie('role',      _role, expires=expire_date)
            return resp
    return jsonify({'sprava': 'NEPRIHLÁSENÝ'})

@app.route("/odhlasit", methods=['GET'])
def odhlasit_get():
    resp = make_response(redirect('/prehlad'))
    resp.set_cookie('login', '', expires=0)
    resp.set_cookie('role', '', expires=0)
    resp.set_cookie('session_id', '', expires=0)
    return resp

@app.route("/kosik", methods=['PUT'])
@prihlasenie_nutne
@zisti_prihlasenie
def zobraz_kosik2( *args, **kwargs):
    SESSION_ID = ''
    nova_session = False
    if request.cookies \
    and 'session_id' in request.cookies \
    and request.cookies['session_id'] is not None:
        SESSION_ID = request.cookies['session_id']
    #-------------------------------------------
    _meno    = safe_str(request.json['meno'   ])
    _ulica   = safe_str(request.json['ulica'  ])
    _psc     = safe_str(request.json['psc'    ])
    _obec    = safe_str(request.json['obec'   ])
    _email   = safe_str(request.json['email'  ])
    _platba  = safe_str(request.json['platba' ])
    _doprava = safe_str(request.json['doprava'])
    #-------------------------------------------
    SEL_SQL = ''' select ifnull(max(obj_id), -1) from tab_objednavky where obj_session = '{str}' '''.format(str = SESSION_ID)
    _id_objednavky = query_db(SEL_SQL)[0][0]

    #TODO zakaznik sa insertne iba v pripade, ak este neexistoval pre daneho pouzivatela

    _login = kwargs['login']
    SEL_ZAKAZNIK_ID = """
      select ifnull(max(z.zak_id),0) as zak_id from tab_zakaznici z
      join tab_pouzivatelia p on z.pou_id = p.pou_id and p.pou_login = '{login}'
    """.format(login = _login)

    _zak_id = query_db(SEL_ZAKAZNIK_ID, ())[0][0]

    query_db(" update tab_objednavky set obj_stav = 'OBJ', zak_id = {zak_id}, obj_platba = {platba}, obj_doprava = {doprava} where obj_session = '{session}' "
             .format(zak_id  = _zak_id,
                     platba  = _platba,
                     doprava = _doprava,
                     session = SESSION_ID),
             commit=True)

    resp = jsonify({'message': 'OK'})
    resp.set_cookie(key='session_id', value='', expires=0)
    return resp
    pass

@app.route("/kategorie", methods=['GET'] )
def vrat_kategorie_json():
    SQL = '''
        select kat_kod, kat_nazov from cis_kategorie
    '''
    return jsonify(collection=[mapuj_stlpce(('id','kategoria_nazov'),i) for i in query_db(SQL)])
    pass

@app.route("/plusminus", methods=['PUT'] )
def plusminus_put():
    pol_id = request.json["pol_id"]
    zmena  = request.json["zmena"]
    _pocet = query_db("select ifnull(sum(pocet),0) from tab_polozky_objednavky where pol_id = {}".format(pol_id))[0][0]
    if _pocet < 1 or (_pocet + int(zmena)) < 1:
        query_db("delete from tab_polozky_objednavky where pol_id = {}".format(pol_id), commit=True)
    else:
        query_db("update tab_polozky_objednavky set pocet = pocet + {} where pol_id = {}".format(zmena, pol_id), commit=True)
    return jsonify("Updated")

@app.route("/kosik", methods=['GET'] )
@prihlasenie_nutne
@zisti_prihlasenie
def obsahkosik_get(*args, **kwargs):
    _login = kwargs['login']
    SQL = """
        select
            p.pou_id                     as pou_id,
            ifnull(z.zak_meno,'')        as cele_meno,
            ifnull(z.zak_ulica_cislo,'') as ulica_cislo,
            ifnull(z.zak_psc,'')         as psc,
            ifnull(z.zak_obec,'')        as obec,
            ifnull(z.zak_email,'')       as email,
            ifnull(z.zak_telefon,'')     as telefon
        from tab_pouzivatelia p
        left outer join tab_zakaznici z on z.pou_id = p.pou_id
        where pou_login = '{login}'
    """.format(login = _login)
    rec = query_db(SQL, ())
    #--------------------------------
    kwargs['pou_id']      = rec[0][0]
    kwargs['cele_meno']   = rec[0][1]
    kwargs['ulica_cislo'] = rec[0][2]
    kwargs['psc']         = rec[0][3]
    kwargs['obec']        = rec[0][4]
    kwargs['email']       = rec[0][5]
    kwargs['telefon']     = rec[0][6]
    #--------------------------------
    SESSION_ID = ''
    if request.cookies \
    and 'session_id' in request.cookies \
    and request.cookies['session_id'] is not None:
        SESSION_ID = request.cookies['session_id']
    SQL = '''
        select
          o.obj_id, 
          p.pol_id, 
          p.pro_id, 
          pr.pro_nazov as nazov,
          (select ifnull(max(obr.obr_subor),'') from tab_obrazky obr where obr.obr_id = p.obr_id) as obrazok,
          p.pocet,
          pr.pro_cena as jedn_cena, 
          (pr.pro_cena * p.pocet) as suma_riadku
        from tab_objednavky o, tab_polozky_objednavky p, tab_produkty pr
        where o.obj_session = '{obj_session}'
        and o.obj_id = p.obj_id 
        and pr.pro_id = p.pro_id
    '''.format(obj_session = SESSION_ID)
    nazvy_stlpcov = ('obj_id','pol_id','pro_id', 'nazov', 'obrazok', 'pocet', 'jedn_cena', 'suma_riadku')
    kosik_zoznam = [mapuj_stlpce(nazvy_stlpcov, r) for r in query_db(SQL)]
    celkova_cena = 0.0
    for r in kosik_zoznam:
        celkova_cena += r['suma_riadku']
    return render_template("kosik.html",
        kwargs       = kwargs,
        kosik        = kosik_zoznam,
        celkova_cena = celkova_cena)

    
# >>> vysklada produkt na ktory zakaznik klikne
# >>> vyberie ho iba ak je jeho stav A
@app.route("/produkty", methods=['GET'] )
def vrat_produkty_json():
    SQL = '''
        select 
        pro.pro_id   ,
        pro.pro_nazov,
        pro.pro_popis,
        pro.kat_kod  ,
        pro.pro_cena ,
        (select ifnull(max(obr.obr_subor),'') from tab_obrazky obr 
         where obr.pro_id = pro.pro_id and obr.hlav_obr = 1) as obr_subor
        from tab_produkty pro
        where pro.pro_stav = 'A'
        and exists (
            select 1 from tab_obrazky obr 
            where obr.pro_id = pro.pro_id and obr.hlav_obr = 1
        )
    '''
    nazvy_stlpcov = ('id', 'produkt_nazov', 'produkt_popis', 'kategoria_id', 'produkt_cena', 'produkt_obrazok')
    return jsonify(collection=[mapuj_stlpce(nazvy_stlpcov, i) for i in query_db(SQL)])
    pass

@app.route("/produktygaleria", methods=['GET'] )
def vrat_produkty_galeriu_json():
    SQL = '''
        select 
        obr.obr_id   ,
        obr.obr_subor,
        obr.pro_id  ,
        obr.hlav_obr
        from tab_obrazky obr
    '''
    nazvy_stlpcov = ('id', 'produkt_obrazok', 'produkt_id', 'hlavny_obrazok')
    return jsonify(collection=[mapuj_stlpce(nazvy_stlpcov, i) for i in query_db(SQL)])
    pass  

@app.route("/obrazkyzoznam", methods=['GET'] )
def vrat_obrazky_json():
    SQL = '''
        select 
        pro.pro_id   ,
        pro.pro_nazov,
        pro.kat_kod  ,
        (select ifnull(max(obr.obr_subor),'') from tab_obrazky obr 
         where obr.pro_id = pro.pro_id and obr.hlav_obr = 1) as obr_subor
        from tab_produkty pro
        where pro.pro_stav = 'A'
    '''
    nazvy_stlpcov = ('id', 'produkt_nazov', 'kategoria_id', 'produkt_obrazok')
    return jsonify(collection=[mapuj_stlpce(nazvy_stlpcov, i) for i in query_db(SQL)])
    pass   
    
#>>> vytvori podstranku s id produktu vytvori ho podla template(vzoru produkt.html)
@app.route("/produkt/<produkt_id>")
@zisti_prihlasenie
def zobraz_produkt(produkt_id="1", *args, **kwargs):
    return render_template('produkt.html',kwargs = kwargs)

    pass

@app.route("/objednavka/<objednavka_id>", methods=['GET'])
@prihlasenie_nutne
@zisti_prihlasenie
def zobraz_detail_objednavky(objednavka_id = None, *args, **kwargs):
    if objednavka_id is None \
    or int(objednavka_id) <= 0:
        return "Nesprávna hodnota parametra 'objednavka_id' {}".format(objednavka_id)

    SQL = '''
    select
        obj_id,
        pocet,
        cena_jednotkova,
        cena_celkova,
        kat_kod,
        kat_nazov,
        pro_nazov,
        pro_popis
    from v_objednavka_detail
    where obj_id = {}
    '''

    nazvy_stlpcov = (
        'obj_id',
        'pocet',
        'cena_jednotkova',
        'cena_celkova',
        'kat_kod',
        'kat_nazov',
        'pro_nazov',
        'pro_popis'
    )
    polozky_zoznam = [mapuj_stlpce(nazvy_stlpcov, r) for r in query_db(SQL.format(objednavka_id))]
    objednavky = get_objednavky(objednavka_id)
    return render_template('objednavka_detail.html',
                           polozky = polozky_zoznam,
                           objednavka = objednavky[0],
                           kwargs = kwargs)
    pass

@app.route("/objednavky", methods=['GET'])
@prihlasenie_nutne
@zisti_prihlasenie
def zobraz_objednavky(*args, **kwargs):
    objednavky_zoznam = get_objednavky()
    return render_template('objednavky.html', objednavky = objednavky_zoznam, kwargs = kwargs)
    pass

@app.route("/produkt_editacia_zoznam", methods=['GET'])
@prihlasenie_nutne
@zisti_prihlasenie
def get_produkt_editacia_zoznam(*args, **kwargs):
    SQL = '''
        select
            pro_id   ,
            pro_nazov,
            pro_popis,
            kat_kod  ,
            kat_nazov,
            pro_cena
        from v_produkt_editacia_zoznam
    '''
    _produkty = [mapuj_stlpce(('id','nazov', 'popis', 'kat_kod', 'kat_nazov', 'cena'), i) for i in query_db(SQL)]
    return render_template('produkt_editacia_zoznam.html',
                           produkty = _produkty, kwargs = kwargs)
    pass


@app.route("/obrazok-nastav-hlavny/<obr_id>", methods=['PUT'])
@prihlasenie_nutne
@zisti_prihlasenie
def put_obrazok_nastav_hlavny(obr_id = None, *args, **kwargs):
    SQL = "update tab_obrazky set hlav_obr = 0 where pro_id = (select max(pro_id) from tab_obrazky where obr_id = {obr_id})".format(obr_id=obr_id)
    query_db(SQL, commit=True)
    SQL = "update tab_obrazky set hlav_obr = 1 where obr_id = {obr_id}".format(obr_id=obr_id)
    query_db(SQL, commit=True)
    return jsonify("OK")
    pass


@app.route("/produkt_editacia/<produkt_id>", methods=['GET'])
@prihlasenie_nutne
@zisti_prihlasenie
def get_produkt_editacia(produkt_id = None, *args, **kwargs):
    zaznam      = ''
    __id        = ''
    __nazov     = ''
    __popis     = ''
    __kat_kod   = '-1'
    __cena      = '0'

    if produkt_id is not None and int(produkt_id) > 0:
        SQL = '''
            select
                pro_id   ,
                pro_nazov,
                pro_popis,
                kat_kod  ,
                pro_cena
            from v_produkt_editacia_zoznam where pro_id = {produkt_id}
        '''
        zaznam = query_db(SQL.format(produkt_id = produkt_id))
        __id        = zaznam[0][0]
        __nazov     = zaznam[0][1].replace('\n','')
        __popis     = zaznam[0][2].replace('\n','')
        __kat_kod   = zaznam[0][3]
        __cena      = zaznam[0][4]

    SQL = '''select kat_kod, kat_nazov from cis_kategorie order by kat_nazov'''
    kategorie_zoznam = [mapuj_stlpce(('id','kategoria_nazov'), i) for i in query_db(SQL)]

    _obrazky = None
    SQL = '''SELECT obr_id, obr_subor, hlav_obr FROM tab_obrazky WHERE pro_id = {pro_id}'''.format(pro_id = produkt_id)
    zaznam = query_db(SQL)
    _obrazky = [mapuj_stlpce(('obr_id', 'obr_subor', 'hlav_obr'), i) for i in query_db(SQL)]

    return render_template('produkt_editacia.html',
                           kategorie = kategorie_zoznam,
                           zaznam = zaznam,
                           obrazky = _obrazky,
                           __id        = __id      ,
                           __nazov     = __nazov   ,
                           __popis     = __popis   ,
                           __kat_kod   = __kat_kod ,
                           __cena      = __cena    ,
                           kwargs      = kwargs)
    pass

@app.route("/produkt_editacia", methods=['PUT'])
@prihlasenie_nutne
@zisti_prihlasenie
def put_produkt_editacia(*args, **kwargs):
    _id        = safe_str(request.json['id'        ])
    _nazov     = safe_str(request.json['nazov'     ])
    _popis     = safe_str(request.json['popis'     ])
    _kategoria = safe_str(request.json['kategoria' ])
    _cena      = safe_str(request.json['cena'      ])

    _insert = True
    if _id is not None and _id.strip() != '' and int(_id) > 0:
        _insert = False

    SQL = ''
    if _insert:
        _id = query_db(" select ifnull(max(pro_id), 0)+1 from tab_produkty ")[0][0]
        SQL = '''
          INSERT INTO tab_produkty (pro_id, pro_nazov, pro_popis, pro_cena, pro_stav, kat_kod )
          VALUES ({id},'{nazov}','{popis}',{cena},'A','{kategoria}')
        '''
    else:
        SQL = '''
          update tab_produkty set
            pro_nazov = '{nazov}',
            pro_popis = '{popis}',
            pro_cena  = {cena},
            pro_stav  = 'A',
            kat_kod   = '{kategoria}'
          where pro_id = {id}
        '''

    query_db(SQL.format(id=_id, nazov=_nazov, popis = _popis, cena = _cena, kategoria = _kategoria ), commit=True)

    return jsonify("OK")
    pass

#
@app.route("/obrazok-upload/<produkt_id>", methods=['POST'])
@prihlasenie_nutne
@zisti_prihlasenie
def post_obrazok_upload(produkt_id = None, *args, **kwargs):
    print("produkt_id:", produkt_id)
    if produkt_id is not None and int(produkt_id) > 0:
        file = request.files['obrazok-upload']  # file input ma vo formulari id 'obrazok-upload'
        if file.filename == '':
            print ("Neznamy subor!")
            return 'CHYBA! (Neznamy subor)'
        if file and povoleny_typ_upload_suboru(file.filename):
            originalExtension = file.filename.rsplit('.', 1)[1].lower()
            newFilename = presny_cas().strftime("%Y%m%d_%H%M%S") + '.' + originalExtension
            newFilenameFull = os.path.join(_UPLOAD_DIR, newFilename)
            # ------------------------------------------------------------
            counter = 0
            while os.path.exists(newFilenameFull):
                counter += 1
                newFilename = newFilename.replace(".", str(counter) + ".", 1)
                newFilenameFull = os.path.join(_UPLOAD_DIR, newFilename)
            # ------------------------------------------------------------
            file.save(newFilenameFull)
            _obr_id = query_db(" select ifnull(max(obr_id), 0)+1 from tab_obrazky ")[0][0]
            SQL = "INSERT INTO tab_obrazky (obr_id, obr_subor, pro_id, hlav_obr) VALUES ({obr_id}, '{obr_subor}', {pro_id}, {hlav_obr})"\
                    .format(obr_id = _obr_id, obr_subor = newFilename, pro_id = produkt_id, hlav_obr = 0)
            query_db(SQL, commit=True)
        return 'O.K.'
    else:
        return 'CHYBA!'

@app.route("/registracia", methods=['GET'])
@zisti_prihlasenie
def get_registracia(*args, **kwargs):
    return render_template('registrovat.html', kwargs = kwargs)

@app.route("/registracia", methods=['PUT'])
def put_registracia(*args, **kwargs):
    _id         = None
    _meno       = safe_str(request.json['meno'])
    _heslo      = safe_str(request.json['heslo'])
    _role       = 'ZAKAZNIK'

    SQL = "select pou_id from tab_pouzivatelia where pou_login = '{}' ".format(_meno)
    rec = query_db(SQL, ())

    if rec is not None and len(rec) > 0:
        return jsonify({'chyba': "Prihlasovacie meno '{meno}' už existuje!".format(meno=_meno)})
    else:
        SQL = "select ifnull(max(pou_id),0)+1 from tab_pouzivatelia"
        _id = query_db(SQL)[0][0]

        SQL = "INSERT INTO tab_pouzivatelia(pou_id, pou_login, pou_heslo, pou_role) " + \
              "VALUES({id}, '{login}', '{heslo}', '{role}')"\
              .format(id=_id, login=_meno, heslo=_heslo, role=_role)
        query_db(SQL, commit=True)

        resp = jsonify({'sprava': 'PRIHLÁSENÝ', 'login': _meno})
        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(hours=2)
        ## nasetujem COOKIE:
        resp.set_cookie('login', _meno, expires=expire_date)
        resp.set_cookie('role',  _role, expires=expire_date)
        return resp
    return jsonify({'sprava': 'NEPRIHLÁSENÝ'})



@app.route("/profil", methods=['GET'])
@prihlasenie_nutne
@zisti_prihlasenie
def get_profil(*args, **kwargs):
    _login = kwargs['login']
    SQL = """
        select
            p.pou_id                     as pou_id,
            ifnull(z.zak_meno,'')        as cele_meno,
            ifnull(z.zak_ulica_cislo,'') as ulica_cislo,
            ifnull(z.zak_psc,'')         as psc,
            ifnull(z.zak_obec,'')        as obec,
            ifnull(z.zak_email,'')       as email,
            ifnull(z.zak_telefon,'')     as telefon
        from tab_pouzivatelia p
        left outer join tab_zakaznici z on z.pou_id = p.pou_id
        where pou_login = '{login}'
    """.format(login = _login)
    rec = query_db(SQL, ())
    #--------------------------------
    kwargs['pou_id']      = rec[0][0]
    kwargs['cele_meno']   = rec[0][1]
    kwargs['ulica_cislo'] = rec[0][2]
    kwargs['psc']         = rec[0][3]
    kwargs['obec']        = rec[0][4]
    kwargs['email']       = rec[0][5]
    kwargs['telefon']     = rec[0][6]
    #--------------------------------
    objednavky_zoznam = get_historia_objednavok(kwargs['pou_id'])
    return render_template('profil.html', objednavky = objednavky_zoznam, kwargs = kwargs)



@app.route("/profil_zmena", methods=['PUT'])
@zisti_prihlasenie
def put_profil_zmena(*args, **kwargs):
    _id         = None
    _meno       = safe_str(request.json['meno'])
    _heslo      = safe_str(request.json['heslo'])

    SQL = "select pou_id from tab_pouzivatelia where pou_login = '{}' ".format(_meno)
    rec = query_db(SQL, ())

    if rec is not None and len(rec) > 0:
        _id = rec[0][0]

        SQL = "update tab_pouzivatelia set pou_heslo = '{heslo}' where pou_id = {id} ".format(id=_id, heslo=_heslo)
        query_db(SQL, commit=True)

        resp = jsonify({'sprava': 'ZMENENÝ PROFIL', 'login': _meno})
        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(hours=2)
        ## nasetujem COOKIE:
        resp.set_cookie('login', _meno, expires=expire_date)
        return resp
    return jsonify({'sprava': 'NEZMENENÝ PROFIL'})

#/kontakt_zmena
@app.route("/kontakt_zmena", methods=['PUT'])
@zisti_prihlasenie
def put_kontakt_zmena(*args, **kwargs):
    _zak_id      = None
    _pou_id      = safe_str(request.json['pou_id'])
    _zak_meno    = safe_str(request.json['cele_meno'])
    _zak_ulica   = safe_str(request.json['ulica'])
    _zak_psc     = safe_str(request.json['psc'])
    _zak_obec    = safe_str(request.json['obec'])
    _zak_email   = safe_str(request.json['email'])
    _zak_telefon = safe_str(request.json['telefon'])

    SQL = "SELECT zak_id FROM tab_zakaznici WHERE pou_id = {pou_id}".format(pou_id = _pou_id)
    rec = query_db(SQL, ())

    if rec is None or len(rec) < 1:
        _zak_id = query_db("SELECT ifnull(max(zak_id), 0) + 1 FROM tab_zakaznici")[0][0] ## [0][0] - prvy riadok / prvy stlpec

        SQL = """
            insert into tab_zakaznici (
               zak_id,
               pou_id,
               zak_meno,
               zak_ulica_cislo,
               zak_psc,
               zak_obec,
               zak_telefon,
               zak_email
            ) values (
               {zak_id},
               {pou_id},
               '{zak_meno}',
               '{zak_ulica_cislo}',
               '{zak_psc}',
               '{zak_obec}',
               '{zak_telefon}',
               '{zak_email}'
            )""".format(
                zak_id          = _zak_id,
                pou_id          = _pou_id,
                zak_meno        = _zak_meno,
                zak_ulica_cislo = _zak_ulica,
                zak_psc         = _zak_psc,
                zak_obec        = _zak_obec,
                zak_telefon     = _zak_telefon,
                zak_email       = _zak_email )
        query_db(SQL, commit=True)
    elif rec is not None and len(rec) > 0:
        _zak_id = rec[0][0] ## [0][0] - prvy riadok / prvy stlpec
        SQL = """
              update tab_zakaznici set
                   zak_meno         = '{zak_meno}',
                   zak_ulica_cislo  = '{zak_ulica}',
                   zak_psc          = '{zak_psc}',
                   zak_obec         = '{zak_obec}',
                   zak_telefon      = '{zak_telefon}',
                   zak_email        = '{zak_email}'
              where zak_id = {zak_id}
            """.format(
                zak_id          = _zak_id,
                zak_meno        = _zak_meno,
                zak_ulica       = _zak_ulica,
                zak_psc         = _zak_psc,
                zak_obec        = _zak_obec,
                zak_telefon     = _zak_telefon,
                zak_email       = _zak_email )
        query_db(SQL, commit=True)
        resp = jsonify({'sprava': 'ZMENENÝ ZÁKAZNÍK', 'zak_id': _zak_id})
        return resp
    return jsonify({'sprava': 'NEZMENENÝ ZÁKAZNÍK'})

def get_historia_objednavok(_pou_id):
    SQL = '''
        select
            obj_id,
            obj_stav,
            obj_cena,
            obj_datum_cas,
            sposob_platby,
            sposob_dopravy
        from v_historia_objednavok
        where pou_id = {pou_id}
    '''.format(pou_id = _pou_id)

    nazvy_stlpcov = (
        'obj_id',
        'obj_stav',
        'obj_cena',
        'obj_datum_cas',
        'sposob_platby',
        'sposob_dopravy'
    )

    objednavky_zoznam = [mapuj_stlpce(nazvy_stlpcov, r) for r in query_db(SQL)]
    return objednavky_zoznam


def get_objednavky(objednavka_id = None):
    SQL = '''
        select
            obj_id,
            obj_stav,
            obj_cena,
            obj_datum_cas,
            obj_session,
            obj_platba,
            obj_doprava,
            zak_id,
            zak_meno,
            zak_ulica_cislo,
            zak_psc,
            zak_obec,
            zak_telefon,
            zak_email
        from v_objednavky_nevybavene
    '''

    nazvy_stlpcov = (
        'obj_id',
        'obj_stav',
        'obj_cena',
        'obj_datum_cas',
        'obj_session',
        'obj_platba',
        'obj_doprava',
        'zak_id',
        'zak_meno',
        'zak_ulica_cislo',
        'zak_psc',
        'zak_obec',
        'zak_telefon',
        'zak_email'
    )

    if objednavka_id is not None \
    and int(objednavka_id) > 0:
        SQL = SQL + " where obj_id = " + objednavka_id

    objednavky_zoznam = [mapuj_stlpce(nazvy_stlpcov, r) for r in query_db(SQL)]
    return objednavky_zoznam

@app.route("/sprava", methods=['PUT'])
def put_sprava():
    _sprava_email = safe_str(request.json['sprava_email'])
    _sprava_obsah = safe_str(request.json['sprava_obsah'])
    INS_SPRAVA_SQL = """
      insert into tab_spravy (spr_id, spr_email, spr_obsah, spr_cas)
      values ((select ifnull(max(spr_id),0) + 1 from tab_spravy), '{email}', '{obsah}', '{cas}')
    """.format(
        email = _sprava_email,
        obsah = _sprava_obsah,
        cas   = presny_cas_str()
    )
    query_db(INS_SPRAVA_SQL, commit=True)
    return jsonify("inserted")
    pass

#>>> takto vyzera jsonify do stavu ktory je citatelny pre javascript
@app.route("/data")
def vrat_data():
    return jsonify(json_list=query_db('select kat_kod, kat_nazov from cis_kategorie'))
    pass

    
@app.route("/")
def root():
    return redirect("/prehlad", code=302)
    pass

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    flaskrun(app)