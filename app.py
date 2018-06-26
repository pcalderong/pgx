from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import config
from flask import render_template, request
import json
from fileUtils import readFile
import datetime
from mlUtils import startML

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)

@app.route('/')
@app.route('/index')
def index():
    gmCount = getCountGMnoconocido()
    countPacientes = getCountPacientes()
    countTratamiento = getCountTratamiento()
    ciudad, countLentos = getCountLentos()
    tratamientos = getAllTratamientos()
    rangoEdades = getRangosEdades()
    return render_template('index.html', classDashboard = 'active',
                                         toggleDiv='display: none;',
                           gmCount = gmCount,
                                         pacientes=countPacientes,
                                         countTratamiento = countTratamiento,
                                         tratamiento = [1,2],
                           tratamientos = tratamientos,
                           ciudad = ciudad,
                           countLentos = countLentos,
                           rangoEdades = rangoEdades)


@app.route('/enfermedad')
def enfermedad():
    return render_template('enfermedad.html', classEnfermedad='active', listEnfermedades = getAllEnfermedades())

@app.route('/prediccion')
def prediccion():
    return render_template('machineLearning.html', classML='active')

@app.route('/predictGM')
def predictGM():
    return render_template('machineLearning.html', classML='active', pacientes = generatePrediccion())

@app.route('/applyPrediccion')
def applyPrediccion():
    msj = "Se han actualizado los registros satisfactoriamente"
    list = generatePrediccion()
    for row in list:
        p = Paciente.query.filter(Paciente.id == row[0]).first()
        p.fk_grupo_metabolico = getGMId(row[7])
        db.session.commit()
        db.session.close()
    return render_template('machineLearning.html', classML='active', mensajeSuccess = msj)

@app.route('/addEnfermedad', methods=['POST'])
def addEnfermedad():
    _nombre_ = request.form['inputNombre']
    _descripcion_ = request.form['inputDescripcion']
    enf = Enfermedad(_nombre_, _descripcion_)
    enf.save()
    return redirect(url_for('enfermedad'))


@app.route('/tratamiento')
def tratamiento():
    return render_template('tratamiento.html', classTratamiento='active', enfermedades = getAllEnfermedades(), tratamientos = getAllTratamientos())

@app.route('/guiasTerapeuticas')
def guiasTerapeuticas():
    return render_template('guiasTerapeuticas.html', classGuias='active', guiasTerapeuticas = getAllGuiasTerapeuticas(),
                                                                          gruposMetabolicos = getAllGruposMetabolicos(),
                                                                          tratamientos = getAllTratamientos())

@app.route('/paciente')
def paciente():
    return render_template('paciente.html', classPaciente='active',
                                        pacientes = getPacientes(),
                                        tratamientos = getAllTratamientos(),
                                        gruposMetabolicos = getAllGruposMetabolicos(),
                                        paises = getPaises())

@app.route('/addTratamiento', methods=['POST'])
def addTratamiento():
    _nombre_ = request.form['inputNombre']
    _descripcion_ = request.form['inputDescripcion']
    _enfermedad_ = request.form['selectEnfermedad']
    tto = Tratamiento(_nombre_, _descripcion_, _enfermedad_)
    tto.save()
    return redirect(url_for('tratamiento'))

@app.route('/addGuiaTerapeutica', methods=['POST'])
def addGuiaTerapeutica():
    _grupo_metabolico_ = request.form['selectGMetabolico']
    _recomendacion_ = request.form['inputRecomendacion']
    _tratamiento_ = request.form['selectTratamiento']
    gt = Guia_Terapeutica(_recomendacion_, _tratamiento_, _grupo_metabolico_)
    gt.save()
    return redirect(url_for('guiasTerapeuticas'))

@app.route('/addPaciente', methods=['POST'])
def addPaciente():
    _cedula_ = request.form['inputCedula']
    _fecha_nacimiento_ = request.form['inputFechaNacimiento']
    _alelo_1_ = request.form['inputAlelo1']
    _alelo_2_ = request.form['inputAlelo2']
    _grupo_metabolico_ = request.form['selectGMetabolico']
    _tratamiento_ = request.form['selectTratamiento']
    _pais_ = request.form['selectPais']
    _ciudad_ = request.form['selectCiudad']

    paciente = Paciente(_cedula_, _fecha_nacimiento_, _alelo_1_, _alelo_2_, _tratamiento_, _grupo_metabolico_, _pais_, _ciudad_)
    paciente.save()
    return redirect(url_for('paciente'))

@app.route('/uploadFilePacientes', methods=['POST'])
def uploadFilePacientes():
    _pacientes_file_ = request.files['filePacientes']
    df_paciente = readFile(_pacientes_file_)
    for p in df_paciente.as_matrix():
        _cedula_ = p[0]
        _fecha_nacimiento_ = p[1]
        _alelo_1_ = p[2]
        _alelo_2_ = p[3]
        _tratamiento_ = getTratamiento(p[4])
        _grupo_metabolico_ = getGMId(p[5])
        _pais_ = getUbicacion(p[6])
        _ciudad_ = getUbicacion(p[7])

        paciente = Paciente(_cedula_, _fecha_nacimiento_, _alelo_1_, _alelo_2_, _tratamiento_, _grupo_metabolico_, _pais_, _ciudad_)
        paciente.save()
    return redirect(url_for('paciente'))

@app.route('/uploadFileGuias', methods=['POST'])
def uploadFileGuias():
    _guias_file_ = request.files['fileGuias']
    df_guias = readFile(_guias_file_)
    for g in df_guias.as_matrix():
        _grupo_metabolico_ = getGMId(g[0])
        _recomendacion_ = g[2]
        _tratamiento_ = getTratamiento(g[1])
        gt = Guia_Terapeutica(_recomendacion_, _tratamiento_, _grupo_metabolico_)
        gt.save()
    return redirect(url_for('guiasTerapeuticas'))

@app.route('/getCiudad')
def getCiudad():
    ciudades = getCiudades(request.args.get('pais'))
    list = []
    for c in ciudades:
        elem = {"id":c[1],"nombre":c[2]}
        list.append(elem)
    return json.dumps(list)

@app.route('/findRecomendaciones')
def findRecomendaciones():
    guias = findRecomendacionesByCedula(request.args.get('inputCedula'))
    tratamiento = getTratamientoById(guias[0].fk_tratamiento)
    grupo_metabolico = getGrupoMetabolicoById(guias[0].fk_grupo_metabolico)
    countPaises = getCountPaises()
    countPacientes = getCountPacientes()
    return render_template('index.html', classDashboard = 'active',
                                         cedula = request.args.get('inputCedula'),
                                         tratamiento = tratamiento,
                                         grupo_metabolico = grupo_metabolico,
                                         recomendaciones = guias,
                                         paises = countPaises,
                                         pacientes = countPacientes)

@app.route('/getGruposMetabolicosChart')
def getGruposMetabolicosChart():
    idLento = getGMId('Lento')
    idNormal = getGMId('Normal')
    idRapido = getGMId('Rapido')
    lento = getCountPacienteByGM(idLento)
    normal = getCountPacienteByGM(idNormal)
    rapido = getCountPacienteByGM(idRapido)
    total = lento + rapido + normal
    result = [getPorcentaje(lento, total), getPorcentaje(rapido, total), getPorcentaje(normal, total),total]
    return json.dumps(result)

@app.route('/getGruposMetabolicosChartByTratamiento')
def getGruposMetabolicosChartByTratamiento():
    tratamiento = request.args.get('tratamientoId')
    idLento = getGMId('Lento')
    idNormal = getGMId('Normal')
    idRapido = getGMId('Rapido')
    lento = getCountPacienteByTto(idLento, tratamiento)
    normal = getCountPacienteByTto(idNormal, tratamiento)
    rapido = getCountPacienteByTto(idRapido, tratamiento)
    total = lento + rapido + normal
    result = [getPorcentaje(lento, total), getPorcentaje(rapido, total), getPorcentaje(normal, total),total]
    return json.dumps(result)

@app.route('/getGruposMetabolicosChartByEdad')
def getGruposMetabolicosChartByEdad():
    rangoId = request.args.get('rangoId')
    rangos = getRangosEdades()
    now = datetime.datetime.now()
    startYear = now.year - rangos[int(rangoId)][1]
    endYear = now.year - rangos[int(rangoId)][0]
    idLento = getGMId('Lento')
    idNormal = getGMId('Normal')
    idRapido = getGMId('Rapido')
    lento = getCountPacientesByEdad(idLento, startYear, endYear)
    normal = getCountPacientesByEdad(idNormal, startYear, endYear)
    rapido = getCountPacientesByEdad(idRapido, startYear, endYear)
    total =lento + rapido + normal
    result = [getPorcentaje(lento, total), getPorcentaje(rapido, total), getPorcentaje(normal, total),total]
    return json.dumps(result)

# ===============

def getCountGMnoconocido():
    return Paciente.query.filter(Paciente.fk_grupo_metabolico == 4).count()

def generatePrediccion():
    queryOrig = db.session.query(Paciente).filter(Paciente.fk_grupo_metabolico != 4).statement
    queryPred = db.session.query(Paciente).filter(Paciente.fk_grupo_metabolico == 4).statement
    prediccion = startML(queryOrig, queryPred, db.session.bind)
    pacientesPrediccion = getAllPacientesPrediccion(prediccion)
    return pacientesPrediccion

def getAllPacientesPrediccion(prediccion):
    pacientes = Paciente.query.filter(Paciente.fk_grupo_metabolico == 4).all()
    listPacientes = []
    for p in pacientes:
        row = [p.id,p.cedula,p.fecha_nacimiento,p.alelo_1,p.alelo_2]
        row.append(getTratamientoById(p.fk_tratamiento)[1])
        row.append(getGrupoMetabolicoById(p.fk_grupo_metabolico))
        if p.id in prediccion.keys():
            pred = prediccion[p.id]
            row.append(getGrupoMetabolicoById(int(pred)))
            listPacientes.append(row)
        else:
            row.append(getGrupoMetabolicoById(p.fk_grupo_metabolico))
    return listPacientes

def getPorcentaje(numero, total):
    if total > 0:
        return int((numero*100)/total)
    else:
        return 0

def getCountPacientesByEdad(gmId, startYear, endYear):
    return Paciente.query.filter(db.and_
                                 (Paciente.fk_grupo_metabolico==gmId,
                                  db.extract('year',Paciente.fecha_nacimiento) >= startYear,
                                  db.extract('year',Paciente.fecha_nacimiento) <= endYear)).count()

def getRangosEdades():
    rangos={}
    pointer = 1925
    now = datetime.datetime.now()
    limit = now.year
    i = 0
    while pointer < limit:
        rangos[i] =[limit-pointer, limit-pointer+9]
        # rangos.append(rango)
        i = i+1
        pointer = pointer + 10
    return rangos

def getCountPacienteByTto(gm,idTratamiento):
    return Paciente.query.filter(db.and_
                                 (Paciente.fk_grupo_metabolico==gm,
                                  Paciente.fk_tratamiento == idTratamiento)).count()

def getCountLentos():
    gmId = getGMId('Lento')
    pacientesLentos =Paciente.query.filter(Paciente.fk_grupo_metabolico==gmId) \
        .add_columns(Paciente.fk_estado).all()

    dictCiudades = {}
    for p in pacientesLentos:
        if p[1] in dictCiudades:
            dictCiudades[p[1]] = dictCiudades[p[1]] + 1
        else:
            dictCiudades[p[1]] = 1
    if dictCiudades:
        idCiudad = max(dictCiudades.keys(), key=lambda k: dictCiudades[k])
        pacientesTotal = Paciente.query.filter(Paciente.fk_estado == idCiudad).count()
        nombreCiudad = getUbicacionById(idCiudad)
        return nombreCiudad,getPorcentaje(dictCiudades[idCiudad],pacientesTotal)
    else:
        return "", 0

def getCountPacienteByGM(gm):
    return Paciente.query.filter(Paciente.fk_grupo_metabolico==gm).count()

def getCountTratamiento():
    return Tratamiento.query.count()

def getCountPaises():
    return Ubicacion.query.filter(Ubicacion.parent == 0).count()

def getCountPacientes():
    return Paciente.query.count()

def getTratamientoById(id):
    tto =  Tratamiento.query.filter(Tratamiento.id == id).add_columns(Tratamiento.nombre).first()
    return tto

def getGrupoMetabolicoById(id):
    return Grupo_Metabolico.query.filter(Grupo_Metabolico.id == id).add_columns(Grupo_Metabolico.nombre).first()[1]

def findRecomendacionesByCedula(cedula):
    paciente = Paciente.query.filter(Paciente.cedula == cedula).first()
    tratamiento = paciente.fk_tratamiento
    grupo_metabolico = paciente.fk_grupo_metabolico
    guias = Guia_Terapeutica.query.filter(db.and_
                                          (Guia_Terapeutica.fk_tratamiento == tratamiento,
                                           Guia_Terapeutica.fk_grupo_metabolico == grupo_metabolico)).all()
    return guias

def getUbicacionById(id):
    return Ubicacion.query.filter(Ubicacion.id == id).add_columns(Ubicacion.nombre).first()[1]

def getUbicacion(nombre):
    return Ubicacion.query.filter(Ubicacion.nombre == nombre).add_columns(Ubicacion.id).first()[1]

def getGMId(nombre):
    return Grupo_Metabolico.query.filter(Grupo_Metabolico.nombre == nombre).add_columns(Grupo_Metabolico.id).first()[1]

def getTratamiento(nombre):
    tto = Tratamiento.query.filter(Tratamiento.nombre == nombre).add_columns(Tratamiento.id).first()[1]
    return tto

def getPacientes():
    pacientes = Paciente.query.join(Tratamiento, Tratamiento.id == Paciente.fk_tratamiento) \
        .join(Grupo_Metabolico, Grupo_Metabolico.id == Paciente.fk_grupo_metabolico) \
        .join(Ubicacion, Ubicacion.id == Paciente.fk_pais) \
        .add_columns(Paciente.cedula, Paciente.fecha_nacimiento, Paciente.alelo_1, Paciente.alelo_2,
                     Tratamiento.nombre, Grupo_Metabolico.nombre, Ubicacion.nombre).all()
    return pacientes


def getPaises():
    return Ubicacion.query.filter(Ubicacion.parent==0).all()

def getCiudades(pais):
    ciudades = Ubicacion.query.filter(Ubicacion.parent==pais) \
                              .add_columns(Ubicacion.id, Ubicacion.nombre)\
                              .all()
    return ciudades

def getAllGruposMetabolicos():
    return Grupo_Metabolico.query.all()

def getAllPacientes():
    return Paciente.query.all()

def getAllEnfermedades():
    return Enfermedad.query.all()

def getAllTratamientos():
    ttoList = Tratamiento.query.join(Enfermedad, Enfermedad.id == Tratamiento.fk_enfermedad)\
                                .add_columns(Tratamiento.id,Tratamiento.nombre, Tratamiento.descripcion, Enfermedad.nombre).all()
    return ttoList

def getAllGuiasTerapeuticas():
    gtList = Guia_Terapeutica.query.join(Grupo_Metabolico, Grupo_Metabolico.id == Guia_Terapeutica.fk_grupo_metabolico)\
                                .join(Tratamiento, Tratamiento.id == Guia_Terapeutica.fk_tratamiento)\
                                .add_columns(Grupo_Metabolico.nombre, Tratamiento.nombre, Guia_Terapeutica.recomendacion).all()
    return gtList

class Enfermedad(db.Model):
    __tablename__ = 'enfermedad'
    __table_args__ = {"schema": "pgx"}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String())
    descripcion = db.Column(db.String())
    tratamientos = db.relationship("Tratamiento")

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def save(self):
        db.session.add(self)
        db.session.commit()
        db.session.close()

class Tratamiento(db.Model):
    __tablename__ = 'tratamiento'
    __table_args__ = {"schema": "pgx"}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String())
    descripcion = db.Column(db.String())
    fk_enfermedad = db.Column(db.Integer(), db.ForeignKey('pgx.enfermedad.id', name ='fk_enfermedad'))
    pacientes = db.relationship("Paciente")
    guias_terapeuticas = db.relationship("Guia_Terapeutica")

    def __init__(self, nombre, descripcion, fk_enfermedad):
        self.nombre = nombre
        self.descripcion = descripcion
        self.fk_enfermedad = fk_enfermedad

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def save(self):
        db.session.add(self)
        db.session.commit()
        db.session.close()

class Grupo_Metabolico(db.Model):
    __tablename__ = 'grupo_metabolico'
    __table_args__ = {"schema": "pgx"}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String())
    descripcion = db.Column(db.String())
    pacientes = db.relationship("Paciente")

    def __init__(self, nombre, descripcion, fk_enfermedad):
        self.nombre = nombre
        self.descripcion = descripcion
        self.fk_enfermedad = fk_enfermedad

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def save(self):
        db.session.add(self)
        db.session.commit()
        db.session.close()


class Guia_Terapeutica(db.Model):
    __tablename__ = 'guia_terapeutica'
    __table_args__ = {"schema": "pgx"}

    id = db.Column(db.Integer, primary_key=True)
    recomendacion = db.Column(db.String())
    fk_tratamiento = db.Column(db.Integer(), db.ForeignKey('pgx.tratamiento.id', name='fk_tratamiento'))
    fk_grupo_metabolico = db.Column(db.Integer(), db.ForeignKey('pgx.grupo_metabolico.id', name='fk_grupo_metabolico'))

    def __init__(self, recomendacion, fk_tratamiento, fk_grupo_metabolico):
        self.recomendacion = recomendacion
        self.fk_tratamiento = fk_tratamiento
        self.fk_grupo_metabolico = fk_grupo_metabolico

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def save(self):
        db.session.add(self)
        db.session.commit()
        db.session.close()

class Ubicacion(db.Model):
    __tablename__ = 'ubicacion'
    __table_args__ = {"schema": "pgx"}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String())
    parent = db.Column(db.Integer())
    paises = db.relationship("Paciente", foreign_keys='Paciente.fk_pais')
    estados = db.relationship("Paciente", foreign_keys='Paciente.fk_estado')

    def __init__(self, nombre, parent):
        self.nombre = nombre
        self.parent = parent

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def save(self):
        db.session.add(self)
        db.session.commit()
        db.session.close()

    def getPaises(self):
        return Ubicacion.query.filter()

    def getCiudades(self, idPais):
        return Ubicacion.query.filter()

class Paciente(db.Model):
    __tablename__ = 'paciente'
    __table_args__ = {"schema": "pgx"}

    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String())
    fecha_nacimiento = db.Column(db.Date())
    alelo_1 = db.Column(db.String())
    alelo_2 = db.Column(db.String())
    batch = db.Column(db.Integer())
    fk_tratamiento = db.Column(db.Integer(), db.ForeignKey('pgx.tratamiento.id', name ='fk_tratamiento'))
    fk_grupo_metabolico = db.Column(db.Integer(), db.ForeignKey('pgx.grupo_metabolico.id', name ='fk_grupo_metabolico'))
    fk_pais = db.Column(db.Integer(), db.ForeignKey('pgx.ubicacion.id', name ='fk_pais'))
    fk_estado = db.Column(db.Integer(), db.ForeignKey('pgx.ubicacion.id', name ='fk_estado'))

    def __init__(self, cedula, fecha_nacimiento, alelo_1, alelo_2, fk_tratamiento, fk_grupo_metabolico, fk_pais, fk_estado):
        self.cedula = cedula
        self.fecha_nacimiento = fecha_nacimiento
        self.alelo_1 = alelo_1
        self.alelo_2 = alelo_2
        self.fk_tratamiento = fk_tratamiento
        self.fk_grupo_metabolico = fk_grupo_metabolico
        self.fk_pais = fk_pais
        self.fk_estado = fk_estado
        self.batch=1

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def save(self):
        db.session.add(self)
        db.session.commit()
        db.session.close()


if __name__ == "__main__":
    app.run()