'''
Created on Jul 22, 2014

@author: pi314
'''
from optparse import OptionParser
from pi.mysql.client import mysqlConnection
from csv import DictReader
from pi.ibHelper.barfeed import RealTimeBar
from datetime import datetime, timedelta, date
import traceback
import copy

def get_options():
    parser = OptionParser()
    parser.add_option('-s', '--startdate', dest='startdate', action='store',
                      help='start date')
    parser.add_option('-e', '--enddate', dest='enddate', action='store',
                      help='end date')
    parser.add_option('-f', '--filepath', dest='filepath', action='store',
                      help='file directory')
    parser.add_option('-l', '--log', dest='logFilename', action='store',
                      help='logFilename')
    parser.add_option('-t', '--datetime', dest='datetime', action='store',
                      default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                      help='datetime')
    parser.add_option('-d', '--dailyETL', dest='dailyETL', default=False, action='store_true',
                      help='Dump from Dropbox file to DB')
    parser.add_option('-v', '--dailyViewETL', dest='dailyViewETL', default=False, action='store_true',
                      help='Generate View from DATA Table')
    opts, args = parser.parse_args()
    return opts

def dailyEtl(options):
    try:
        con = mysqlConnection()
        #delete the given day's data first
        deleteTime = datetime.strptime(options.datetime, "%Y-%m-%d") + timedelta(days=1)
        deleteTime = deleteTime.strftime("%Y-%m-%d")
        con.deleteDataFromDate(deleteTime)
        con.addFromCSVFile(options.filepath + options.datetime + ".csv")
        #log status
        if dailyETLSanityCheck(options):
            if options.logFilename is not None:
                f = open(options.logFilename, 'a')
                f.write("\n********************************************\n")
                f.write("dailyETL finished " + options.datetime + "\n at %s" % (datetime.now()))
    except Exception:
        traceback.print_exc()
        if options.logFilename is not None:
            f = open(options.logFilename, 'a')
            f.write("\n********************************************\n")
            f.write("dailyETL failed " + options.datetime + "\n at %s" % (datetime.now()))

def dailyETLSanityCheck(options):
    #symbol count(*) 
    return True

def dailyViewETLSanityCheck(options):
    return True

def dailyViewEtl(options):
    try:
        con = mysqlConnection()
        generateTime = datetime.strptime(options.datetime, "%Y-%m-%d") + timedelta(days=1)
        generateTime = generateTime.strftime("%Y-%m-%d")
        con.dailyupdate(86400, options.logFilename, generateTime)
        con.dailyupdate(1800, options.logFilename, generateTime)
        con.dailyupdate(300, options.logFilename, generateTime)
        if dailyViewETLSanityCheck(options):
            if options.logFilename is not None:
                f = open(options.logFilename, 'a')
                f.write("dailyViewETL finished " + options.datetime + "\n")
    except Exception:
        traceback.print_exc()
        if options.logFilename is not None:
            f = open(options.logFilename, 'a')
            f.write("dailyViewETL failed " + options.datetime + "\n")

def backFill(options):
    try:
        con = mysqlConnection()
        con.backFill(86400, options.logFilename, options.startdate, options.enddate)
        con.backFill(1800, options.logFilename, options.startdate, options.enddate)
        con.backFill(300, options.logFilename, options.startdate, options.enddate)
        if options.logFilename is not None:
            f = open(options.logFilename, 'a')
            f.write("Back fill finished at %s\n" % (datetime.now()))
    except Exception:
        traceback.print_exc()
        if options.logFilename is not None:
            f = open(options.logFilename, 'a')
            f.write("Back fill failed at %s\n" % (datetime.now()))

if __name__ == '__main__':
    options = get_options()
    if options.startdate is not None and options.enddate is not None:
        backFill(options)
    else:
        if options.dailyETL:
            dailyEtl(options)
        if options.dailyViewETL:
            dailyViewEtl(options)
