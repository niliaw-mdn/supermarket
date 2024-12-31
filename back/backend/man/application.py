from flask import Flask, request, jsonify
import os
app=Flask(__name__)

UPLOAD_FOLDER='./uploads'
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER

@app.route('/upload',methods=['POST'])
def upload():
    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'],file.filename)
    
    file.save(file_path)
    return jsonify({"s":1})



if __name__=='__main__':
    app.run(debug=True)