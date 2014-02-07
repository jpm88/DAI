#!/usr/bin/python
# -*-coding: utf-8 -*-

import web
from web import form
from web.contrib.template import render_mako
import dbm
from mako.template import Template
import sys
import pymongo

paginas=[]
paginas.insert(0,"Vacia")
paginas.insert(1,"Vacia")
paginas.insert(2,"Vacia") 

       
urls = (
    '/*', 'index',
    	'/formulario', 'formulario',
	'/modifica', 'modifica',
	'/desconectar', 'desconectar',	
	'/cadenas', 'cadenas'
)
app = web.application(urls, globals())


if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'usuario':''})
    web.config._session = session
else:
    session = web.config._session


###########mongodb#############


try:
    conn=pymongo.MongoClient()
    print "Connected successfully!!!"
except pymongo.errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e 

db = conn.RegistroUsurarios

usuarios = db.usuarios

render = web.template.render('./static/')

def contra_correcta (usuario):
        return usuario


def comprueba_identificacion ():
        usuario = session.usuario
        return usuario

formularioDatos = form.Form( 
    	form.Textbox("nombre", form.notnull,form.Validator('No vacio', lambda x:x!=""), description = "Nombre:", value=""),
	 form.Textbox("apellido1", form.notnull,form.Validator('No vacio', lambda x:x!=""), description = "Primer apellido:", value=""),
	 form.Textbox("apellido2", form.notnull, form.Validator('No vacio', lambda x:x!=""), description = "Segundo apellido:", value=""),
	 form.Textbox("tarjeta", form.notnull, form.regexp('^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$', "Formato incorrecto"), description = "Tarjeta de credito:", value=""),
	 form.Password("contrasena", form.Validator('5 caracteres', lambda x: len(x)>=5),description = "Contrasena:", value=""),
	 form.Password("repite", form.Validator('No vacio', lambda x:x!=None),description = "Repite Contrasena:", value=""),	 

    		form.Button("Enviar"),
	  validators = [form.Validator("No coinciden las contraseñas", lambda x: x.contrasena == x.repite)] 
) 



formacceso = form.Form( 
	form.Textbox("usuario",form.notnull, form.Validator('No vacio', lambda x:x!=None), description = "Usuario:"),
	form.Password("contra",form.notnull, form.Validator('No vacio', lambda x:x!=None),description = "Contraseña:"),
	form.Button("Enviar"),
		)

formmodifica = form.Form( 
	form.Textbox("usuario",form.notnull, form.Validator('No vacio', lambda x:x!=None), description = "Usuario:"),
	form.Textbox("dni",form.notnull, form.Validator('No vacio', lambda x:x!=None),description = "Dni:"),
	form.Button("Enviar"),
		)


class index:
	def GET(self):
			
			usuario = comprueba_identificacion ()
			

			formu = formacceso	

			if usuario:				
				return render.indexlog(usuario=usuario)
			else:
				return render.index(formu)

	def POST(self): 

		usuario = comprueba_identificacion ()		

		formu = formacceso
                if not formu.validates ():
                        return render.index(formu) 
		i = web.input()
                usuario = i.usuario
                contra = i.contra

		
                if contra == contra_correcta(usuario):
                        session.usuario = usuario
                        return render.indexlog(usuario=usuario)
		else:

			return render.index(formu)


class desconectar:
        def GET(self):
        		
				session.kill()
								   
				return web.seeother('/')  

class cadenas:
        def GET(self):
        		
				usuario = comprueba_identificacion ()
				paginas[0]='cadenas' 
								   
				return render.pagina1(usuario, paginas)

class formulario:
	def GET(self):
		
		
		form = formularioDatos()
		return render.formulario(form)
		
	

	def POST(self):

		form = formularioDatos()

		if not form.validates():
			mensaje='Error. Datos incorrectos'			
			return render.formulario(form)		
		else:	
			usuario1 = {'Nombre': form.d.nombre, "Apellido1": form.d.apellido1,"Apellido2": form.d.apellido2, "Tarjeta de credito": form.d.tarjeta, "Contrasena": form.d.contrasena}
			 
			#Guardamos el usuario
			usuarios.insert(usuario1)

			mensaje='Usuario introducido correctamente'			
			return render.formulario2(form.d.nombre)



class modifica:
	def GET(self):
		
		
		#form2 = formmodifica()
		#return render.modifica(form2)
		form = formularioDatos()
		
		p_usu = usuarios.find_one({'Nombre':session.usuario})
		#print p_usu
		
		form.nombre.value = p_usu['Nombre']
		form.apellido1.value = p_usu['Apellido1']
		form.apellido2.value = p_usu['Apellido2']
		form.tarjeta.value = p_usu['Tarjeta de credito']
			 			
		return render.formulario(form)
		
	

	def POST(self):

		form = formularioDatos()

		if not form.validates():
			mensaje='Error. Datos incorrectos'			
			return render.formulario(form)		
		else:

			 usuarios.update({"Nombre" : session.usuario},{"Nombre": form.d.nombre, "Apellido1": form.d.apellido1, "Apellido2": form.d.apellido2, "Tarjeta de credito": form.d.tarjeta, 			"Contrasena": form.d.contrasena});
			 
			 mensaje='Datos modificados correctamente'			
			 return render.formulario2(mensaje)


if __name__ == "__main__":
    app.run()
