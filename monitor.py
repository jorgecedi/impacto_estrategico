# -*- coding:utf-8 -*-
import requests
import threading
import time
import os
import sys
import csv
import signal
from daemon import Daemon
from urlparse import urlparse


# Importamos django para poder acceder a los modelos
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "impactoestrategico.settings")
django.setup()
from sitios.models import Sitio

DEFAULT_WAIT_TIME = 1
DEFAULT_REQUEST_TIMEOUT = 20
PATH = os.path.dirname(os.path.abspath(__file__))
VERBOSE = False
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
}

class GracefulKiller:
    """ Clase para parar el proceso de forma que no genere errores. """

    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.kill_now = True

class CsvLogger(object):
    """ Clase para registrar los checks en un csv."""

    def __init__(self, file_name, path):
        self.file_name = "%s/%s.csv" % (path, file_name,)

    def write(self, info):
        """ Escribe la información del check en el archivo seleccionado """
        with open(self.file_name, 'ab') as fp:
            wr = csv.writer(fp, quoting=csv.QUOTE_ALL)
            wr.writerow(info)

class Check(object):
    """ Clase para realizar los checks a los sitios. """

    def __init__(self, sitio, path):
        self.url = sitio.url
        self.frecuencia = sitio.frecuencia
        self.id = sitio.id
        self.timeout = sitio.timeout
        self.running = False
        self.check_thread = threading.Thread(target=self.check_site)
        self.configuration_thread = threading.Thread(target=self.reload_site_configuration)
        # self.logger = CsvLogger(self.get_domain_name(), path)
        self.logger = CsvLogger("datos-recopilados", path)
        self.start()

    def reload_site_configuration(self):
        while self.running == True:
            time.sleep(3)
            try:
                sitio = Sitio.objects.get(pk=self.id)
                self.frecuencia = sitio.frecuencia
                self.timeout = sitio.timeout
                self.url = sitio.url
            except Exception, err:
                pass


    def get_domain_name(self):
        """ Método para obtener el nombre de dominio """
        parsed_uri = urlparse(self.url)
        return '{uri.netloc}'.format(uri=parsed_uri)

    def start(self):
        self.running = True
        self.check_thread.start()
        self.configuration_thread.start()

    def stop(self):
        self.running = False

    def check_site(self):
        """
        Método encargado de hacer un request get al sitio y llamar a la
        función que registra en el archivo csv.
        """
        while( self.running == True ):
            time.sleep(self.frecuencia)
            status_code = "DOWN"
            elapsed = 0
            try:
                r = requests.get(self.url, timeout=self.timeout, headers=DEFAULT_HEADERS)
                elapsed = r.elapsed.total_seconds()
                if r.status_code == 200:
                    status_code = "UP"
            except requests.RequestException, err:
                pass
            ts = time.time()
            info =[
                ts,
                status_code,
                self.url
            ]
            self.logger.write(info)
            if VERBOSE == True:
                print "%s\t%s\t%s\t%s\t\t%s" % (self.id,
                                          ts,
                                          status_code,
                                          round(elapsed,5),
                                          self.url,)

class Monitor(object):
    """ Clase para monitorizar y controlar todos los checks """

    checkers = []
    sitios = []
    path = ""
    running = True

    def __init__(self, path):
        self.path = path
        self.get_sites_from_django_orm()
        self.t = threading.Thread(target=self.check_for_changes)
        self.start_all()

    def check_for_changes(self):
        while self.running == True:
            time.sleep(2)

            ids_sitios_cargados = set([c.id for c in self.checkers])
            sitios_en_bd = Sitio.objects.values_list('id', flat=True)

            for id_a_parar in diff(ids_sitios_cargados, sitios_en_bd):
                print "[-] Parando check con id: %s" % (id_a_parar,)
                self.stop_check(id_a_parar)

            for id_a_iniciar in diff(sitios_en_bd, ids_sitios_cargados):
                print "[+] Iniciando check con id: %s" % (id_a_iniciar,)
                sitio_a_iniciar = Sitio.objects.get(pk=id_a_iniciar)
                self.start_check(sitio_a_iniciar)

    def get_sites_from_django_orm(self):
        self.sitios = Sitio.objects.all()

    def stop_check(self, id):
        for check in self.checkers:
            if check.id == id:
                check.stop()
                self.checkers.remove(check)
                break

    def start_check(self, sitio):
        c = Check(sitio, self.path)
        self.checkers.append(c)

    def start_all(self):
        self.running = True
        self.t.start()
        for sitio in self.sitios:
            self.start_check(sitio)

    def stop_all(self):
        self.running = False
        for check in self.checkers:
            check.stop()

def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]

class MonitorDaemon(Daemon):
    """ Clase para demonizar la aplicación """

    def run(self):
        killer = GracefulKiller()
        monitor = Monitor(self.path)
        while True:
            time.sleep(1)
            if killer.kill_now:
                monitor.stop_all()
                break


if __name__ == "__main__":
    daemon = MonitorDaemon('/tmp/monitor.pid',
                           stderr='/tmp/monitor.err',
                           path=PATH)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print "Iniciando demonio."
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'verbose' == sys.argv[1]:
            try:
                monitor = Monitor(PATH)
                VERBOSE = True
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print "Terminando proceso. Esperando a que todos los hilos terminen."
                monitor.stop_all()
                sys.exit(0)
        else:
            print 'Opción desconocida'
            sys.exit(2)
            sys.exit(0)
    else:
        print "Uso: %s start|stop|restart|verbose" % sys.argv[0]
        sys.exit(2)
