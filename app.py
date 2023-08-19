from flask import Flask, flash, request, redirect, url_for, render_template, jsonify
import extract
import os
import re

app = Flask(__name__)
app.config['UPLOAD_PATH'] = './uploads'
ALLOWED_EXTENSIONS = {'docx'}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/grade')
def grade():
    results = extract.getResults()
    return render_template('grade.html', data=results)


@app.route('/upload')
def upload():
    return render_template('upload.html', appUrl=os.path.dirname(request.base_url))


@app.route('/actions')
def actions():
    actionName = request.args.get('name', 'delete')
    if actionName == 'delete':
        message = extract.clearData(app.config['UPLOAD_PATH'])
    elif actionName == 'generate':
        extract.generateModelAnswers()
    else:
        message = [extract.saveContent('questions', './uploads/questions.docx'),
                   extract.saveContent('answers', './uploads\\answers_856678.docx')]
    return render_template('actions.html', data=message)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file_data']
    if file.filename == '':
        flash('No selected file')
    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_PATH'], str(file.filename))
        file.save(file_path)
        # check if the uploaded file is question or answers by using RE to check for 'questions' or 'answers' keywords in the file name
        pattern = r'([^\\]+)\.docx$'
        fileType = re.findall(pattern, str(file.filename))
        extract.saveContent(fileType[0], str(file_path))
    return jsonify(f"File successfully uploaded! { fileType[0]}")


@app.route('/generate', methods=['POST'])
def generate():
    data = request.form
    generatedResponse = extract.generate_response(data.get('user_input'))
    return generatedResponse


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0',port=5000)
