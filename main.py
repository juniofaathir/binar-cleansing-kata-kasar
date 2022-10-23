#This program are copied from PrettyPrinted Github
#I used this for learning purpose

import re, pandas as pd, sqlite3, json
from flask import Flask, jsonify, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app = Flask(__name__)
app.json_encoder = LazyJSONEncoder
conn = sqlite3.connect("data.db", check_same_thread=False)

swagger_template = dict( info = { "title" : LazyString(lambda : "Challenge Gold Chapter 3"),
                                  "version" : LazyString(lambda : "1.0.0"),
                                },
                         host = LazyString(lambda : request.host)
                       )

swagger_config = { "headers" : [],
                   "specs" : [{ "endpoint" : "docs",
                                "route" : "/docs.json"
                              }
                             ],
                   "static_url_path" : "/flasgger_static",
                   "swagger_ui" : True,
                   "specs_route" : "/docs/"
                 }

swagger = Swagger(app, template = swagger_template, config = swagger_config)

abuse = pd.read_sql_query("select * from kasar", conn)
alay = pd.read_sql_query("select * from alay", conn)
alayFix = alay["fix"].to_list()
alayOri = alay["alay"].to_list()
kasar = abuse["abusive"].to_list()

@swag_from("docs/getAll.yml", methods=["GET"]) # =======================================================================
@app.route('/read', methods=['GET'])
def returnAll():
  df = pd.read_sql_query("select * from gold limit 10", conn)
  conn.commit()
  df2 = df.to_dict("records")
  return jsonify(df2)

@swag_from("docs/getSpecified.yml", methods=["GET"]) # =======================================================================
@app.route('/read/<string:id>', methods=['GET'])
def returnOne(id):
  df = pd.read_sql_query("select * from gold where id = '%s'" %(id), conn)
  x = df.to_dict("records")
  conn.commit()
  return jsonify(x)

@swag_from("docs/posting.yml", methods=["POST"]) # =======================================================================
@app.route('/upload', methods=['POST'])
def addOne():
  teks = request.json
  txt = teks["tweet"]
  txt = str(txt).lower()

  txt = re.sub("[,]", " ,", txt)
  txt = re.sub("[.]", " .", txt)
  txt = re.sub("[?]", " ? ", txt)
  txt = re.sub("[!]", " !", txt)
  txt = re.sub("[\"]", " \"", txt)
  txt = re.sub("[\']", "", txt)
  txt = re.sub("[\\n]", " ", txt)
  txt = re.split(" ", txt)

  for word in txt :
    if word in kasar :
        txt[txt.index(word)] = txt[txt.index(word)].replace(word, "***")

  for word in txt :
      if word in alayOri :
          txt[txt.index(word)] = txt[txt.index(word)].replace(word, alayFix[alayOri.index(word)])

  txt = " ".join(txt)
  txt = re.sub(" ,", ",", txt)
  txt = re.sub(" \.", ".", txt)
  txt = re.sub(" \?", "?", txt)
  txt = re.sub(" !", "!", txt)
  txt = re.sub(" \"", "\"", txt)
  
  conn.cursor().execute("insert into gold (tweetOri, tweetClean) values(?, ?)", (teks["tweet"], txt))
  conn.commit()
  return jsonify(teks["tweet"], txt)

@swag_from("docs/postFile.yml", methods=["POST"]) # =======================================================================
@app.route('/upload-file', methods=['POST'])
def addFile():
  file_csv = request.files.get("upfile")
  txt = pd.read_csv(file_csv, usecols = ["Tweet"], encoding='latin-1')
  
  for teks in txt["Tweet"] :
    teks = str(teks).lower()
    teksOri = teks
    teks = re.sub("[,]", " ,", teks)
    teks = re.sub("[.]", " .", teks)
    teks = re.sub("[?]", " ? ", teks)
    teks = re.sub("[!]", " !", teks)
    teks = re.sub("[\"]", " \"", teks)
    teks = re.sub("[\']", "", teks)
    teks = re.sub("[\\n]", " ", teks)
    teks = re.split(" ", teks)
    
    for word in teks :
      if word in kasar :
        teks[teks.index(word)] = teks[teks.index(word)].replace(word, "***")

    for word in teks :
        if word in alayOri :
          teks[teks.index(word)] = teks[teks.index(word)].replace(word, alayFix[alayOri.index(word)])

    teks = " ".join(teks)
    teks = re.sub(" ,", ",", teks)
    teks = re.sub(" \.", ".", teks)
    teks = re.sub(" \?", "?", teks)
    teks = re.sub(" !", "!", teks)
    teks = re.sub(" \"", "\"", teks)
    conn.cursor().execute("insert into gold (tweetOri, tweetClean) values(?, ?)", (teksOri, teks))
    conn.commit()
  return jsonify("OK")

@swag_from("docs/delete.yml", methods=["DELETE"]) # =======================================================================
@app.route('/delete/<string:id>', methods=['DELETE'])
def deleteOne(id):
  conn.cursor().execute("DELETE FROM gold WHERE id = (?)", (id))
  conn.commit()
  return jsonify("dun")

if __name__ == '__main__':
	app.run(debug=True, port=8080) #run app on port 8080 in debug mode