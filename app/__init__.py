from flask import Flask,jsonify,render_template,request,send_file
from app.engine import *
import json, shutil
from flask_compress import Compress
from werkzeug.utils import secure_filename
from io import BytesIO
import keys

app = Flask(__name__)

COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
Compress(app)


@app.route('/cachelist')
def cacheList():
	cache=os.listdir('app/static/desk')
	return jsonify(cache)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/search')
def palette():
	return render_template('search.html')

@app.route('/image')
def image():
	data=json.load(open('app/static/image-init.json'))
	return render_template('image.html',data=data)

@app.route('/imgcache')
def archive():
	data={}
	data['archive']=os.listdir('app/static/desk')
	return render_template('archive.html',data=data)
	
@app.route('/what')
def what():
	return render_template('what.html')

@app.route('/how')
def how():
	return render_template('how.html')

@app.route('/sayhi')
def sayhi():
	return render_template('sayhi.html')

@app.route('/api/img', methods=['POST'])
def img():
	reqType=request.form['type']
	if reqType=='userfile':
		file=request.files['file']
		if file.filename=='':
			print('nofile')
			return 'NOFILE'
		if file and True:
			img=getImage(BytesIO(file.read()),mode='RGB',size_=100)[1]
	else: img=getImage('app/static/img/sample/'+reqType+'.png',mode='RGB',size_=100)[1]
	colorData={}
	colorData['palette']=[getPalette(img,i,mode='HEX') for i in range(3,8)]
	colorData['scatter']=getPlot(img)
	return jsonify(data=colorData)


@app.route('/api/search', methods=['POST'])
def generate():
	search_term=request.json['key']
	_k=4
	_k=request.json['paletteSize']
	_cacheClear=request.json['cacheClear']
	_ip=request.remote_addr

	search_term=search_term.lower()
	if search_term[-1]==' ':
		search_term=search_term[:-1]

	
	try:
		cache=os.listdir('app/static/desk')
	except:
		os.makedirs('app/static/desk')
		cache=[]



	if not search_term.replace(' ','_') in cache:
		link_list=search(search_term,azureKey=keys.azureKey)
		if(len(link_list)==0): 
			print('ERROR',search_term)
			return "SEARCH_ERROR"
		download(link_list,'app/static/desk/'+search_term)
	elif _cacheClear:
		shutil.rmtree('app/static/desk/'+search_term.replace(' ','_'))
		print('clearing cache for',search_term)
		link_list=search(search_term,azureKey=keys.azureKey)
		if(len(link_list)==0): 
			print('ERROR',search_term)
			return "SEARCH_ERROR"
		download(link_list,'app/static/desk/'+search_term)
	else:
		print('using cache for '+search_term)
	colorData=process('app/static/desk/'+search_term,_k)
	if colorData=="ERROR":return "SEARCH_ERROR"
	return jsonify({'data':colorData})

