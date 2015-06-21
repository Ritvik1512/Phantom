#!/usr/bin/python
# -*- coding: utf-8 -*-
          
from sys import platform as OPERATING_SYSTEM
from bs4 import BeautifulSoup
from flask import Flask, request, render_template
from flask import make_response, current_app, abort, jsonify
from datetime import timedelta
from functools import update_wrapper
import os, hashlib, cPickle, requests, smtplib, threading
import task

SITES_LIST = 'sites'

path=''
if OPERATING_SYSTEM == "linux" or OPERATING_SYSTEM == "linux2":
  path = os.path.expandvars('$HOME/.local/share/phantom/')
elif OPERATING_SYSTEM == "darwin":
  path = os.path.expandvars('$HOME/Library/Application Support/phantom/')
elif OPERATING_SYSTEM == "win32":
  path = os.path.expandvars('%APPDATA%/phantom/')


def crossdomain(origin=None, methods=None, headers=None,
        max_age=21600, attach_to_all=True,
        automatic_options=True):
  if methods is not None:
    methods = ', '.join(sorted(x.upper() for x in methods))
  if headers is not None and not isinstance(headers, basestring):
    headers = ', '.join(x.upper() for x in headers)
  if not isinstance(origin, basestring):
    origin = ', '.join(origin)
  if isinstance(max_age, timedelta):
    max_age = max_age.total_seconds()

  def get_methods():
    if methods is not None:
      return methods

    options_resp = current_app.make_default_options_response()
    return options_resp.headers['allow']

  def decorator(f):
    def wrapped_function(*args, **kwargs):
      if automatic_options and request.method == 'OPTIONS':
        resp = current_app.make_default_options_response()
      else:
        resp = make_response(f(*args, **kwargs))
      if not attach_to_all and request.method != 'OPTIONS':
        return resp

      h = resp.headers

      h['Access-Control-Allow-Origin'] = origin
      h['Access-Control-Allow-Methods'] = get_methods()
      h['Access-Control-Max-Age'] = str(max_age)
      if headers is not None:
        h['Access-Control-Allow-Headers'] = headers
      return resp

    f.provide_automatic_options = False
    return update_wrapper(wrapped_function, f)
  return decorator

#------------------------------------------------------------------------------

def if_exists(page_url):
  page_url_md5 = hashlib.sha224(page_url).hexdigest()
  return os.path.isfile(page_url_md5)

def get_dom_tree(page_url):
  old_data = get_saved_data(page_url)
  changes_to_monitor = ''
  for i in old_data:
    changes_to_monitor = i
  return changes_to_monitor

def get_content(page_url, changes_to_monitor):
  html_doc = requests.get(page_url).text
  soup = BeautifulSoup(html_doc)
  content_data = {}

  for element in changes_to_monitor:
    element_md5 = hashlib.sha224(element).hexdigest()
    element_soup = soup
    # for dom_element in element.split('>'):
    #   print element_soup.select(dom_element)
    #   print
    #   print dom_element
    #   element_soup = element_soup.select(dom_element)[0]

    print element_soup.select(element)
    print
    print element
    print
    element_soup = element_soup.select(element)[0]    
    # print element_soup.get_text()
    # print '-----------'
    content_data[element] = element_soup.get_text()
    # print content_data
  return content_data

def save_data(page_url, changes_to_monitor):
  page_url_md5 = hashlib.sha224(page_url).hexdigest()
  content_data = get_content(page_url, changes_to_monitor)

  with open(page_url_md5, 'wb') as f:
    cPickle.dump(content_data, f, cPickle.HIGHEST_PROTOCOL)

  if not os.path.isfile(SITES_LIST):
    websites = {}
  else: 
    with open(SITES_LIST, 'r') as f:
      websites = cPickle.load(f)

  websites[page_url] = True

  with open(SITES_LIST, 'wb') as f:
    cPickle.dump(websites, f, cPickle.HIGHEST_PROTOCOL)


def get_saved_data(page_url):
  page_url_md5 = hashlib.sha224(page_url).hexdigest()
  with open(page_url_md5, 'r') as f:
    return cPickle.load(f)

def compare_data(page_url):
  # return 'hello'
  # print 'ch',changes_to_monitor
  page_url_md5 = hashlib.sha224(page_url).hexdigest()
  old_data = get_saved_data(page_url)
  changes_to_monitor = [get_dom_tree(page_url)]
  new_data = get_content(page_url, changes_to_monitor)


  old_data_pickle = cPickle.dumps(old_data, cPickle.HIGHEST_PROTOCOL)
  new_data_pickle = cPickle.dumps(new_data, cPickle.HIGHEST_PROTOCOL)
  
  print old_data
  print new_data

  if  old_data_pickle==new_data_pickle:
    return 'No changes'
  
  #TODO: ASSUMES CHANGES_TO_MONITOR NEVER CHANGES. CHANGE IT.
  changes = {}
  for element in old_data:
    try:
      if old_data[element] != new_data[element]:
        changes[element] = (old_data[element],new_data[element])
    except:
      pass
  print 'changes',changes
  if not len(changes):
    return 'No Changes'
  return changes

def main(page_url,changes_to_monitor):
  # page_url = 'http://localhost:8000/'
  # changes_to_monitor = [
  #                        'html > body > #div3 > p',
  #                        'html > body > #div2 > p#id2'
  #                      ]

  # page_url = 'http://localhost:8000/ebay.html'
  # changes_to_monitor = [
  #                        'html > body > div#Body > div#CenterPanelDF > div#CenterPanel > div#CenterPanelInternal > div#LeftSummaryPanel > div#mainContent > form > div.c-std.vi-ds3cont-box-marpad > div.actPanel.vi-noborder > div.u-cb > div.u-flL.w29.vi-price > span#prcIsum_bidPrice'
  #                      ]
  
  #----------------------------------------------------------------------------
  # return True
  if not if_exists(page_url):
    save_data(page_url,changes_to_monitor)
    print 'Data Saved. You will be notified if website changes.'
    return 'Data Saved. You will be notified if website changes.'
  else:
    compared_data = compare_data(page_url,changes_to_monitor)
    if compared_data:
      save_data(page_url,changes_to_monitor)
      return jsonify(compared_data)
    else:
      return 'No Change'


app = Flask(__name__)

@app.route('/')
@crossdomain(origin='*')
def index():
  return app.send_static_file('index.html')

@app.route('/add', methods=['POST'])
@crossdomain(origin='*')
def add():
  # return 'hello'
  # if not request.form or (not 'url' in request.form or not 'data' in request.form):
    # abort(400)
  # print 'form',request.form
  page_url = request.form['url']
  # print page_url
  changes_to_monitor = [request.form['data']]
  save_data(page_url,changes_to_monitor)
  threading.Timer(5, task.scan_for_changes, [page_url]).start()
  print 'Data Saved. You will be notified if website changes.'
  return 'Data Saved. You will be notified if website changes.'
  
@app.route('/check', methods=['POST'])
@crossdomain(origin='*')
def check():
  page_url = request.form['url']
  changes_to_monitor = [get_dom_tree(page_url)]
  if not if_exists(page_url):
    print 'Does not exist'
    return 'Does not exist'
  else:
    compared_data = compare_data(page_url)
    if compared_data!='No Changes':
      save_data(page_url,changes_to_monitor)
      print page_url,'Changes:'
      print jsonify(compared_data)
      return jsonify(compared_data)
    else:
      print page_url,'No Change'
      return 'No Change'

@app.route('/start')
@crossdomain(origin='*')
def start():
  print request.args['url']
  threading.Timer(5, task.scan_for_changes, [request.args['url']]).start()
  # task.scan_for_changes(request.args['url'])
  return 'ok'

# app = Flask(__name__, static_url_path='')
if __name__ == '__main__':
  app.run(debug=True)
