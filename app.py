from flask import Flask, request, render_template
import os
import PyPDF2
import docx
import re
 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
 
# Create the uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
 
# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
    return text
 
# Function to extract text from DOCX
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text
 
# Function to extract skills, education, certifications, and experience
def extract_info(text):
    text = text.lower()
 
    # Extract skills
    skills_match = re.search(r'skills\s*:\s*(.*?)(?=\n|$)', text, re.IGNORECASE)
    skills = skills_match.group(1).split(',') if skills_match else []
    skills = [skill.strip() for skill in skills]
 
    # Extract education
    education_match = re.search(r'education\s*:\s*(.*?)(?=\n\s*\n|$)', text, re.IGNORECASE | re.DOTALL)
    education = education_match.group(1).strip().split('\n') if education_match else []
 
    # Extract certifications
    certifications_match = re.search(r'certifications\s*:\s*(.*?)(?=\n|$)', text, re.IGNORECASE)
    certifications = certifications_match.group(1).strip().split(',') if certifications_match else []
    certifications = [cert.strip() for cert in certifications]
 
    # Extract experience
    experience_match = re.search(r'experience\s*:\s*(.*?)(?=\n\s*\n|$)', text, re.IGNORECASE | re.DOTALL)
    experience = experience_match.group(1).strip().split('\n') if experience_match else []
 
    return {
        'skills': skills,
        'education': education,
        'certifications': certifications,
        'experience': experience,
    }
 
@app.route('/')
def upload_form():
    return render_template('upload.html')
 
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400
 
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
 
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
 
    # Extract text based on file type
    if file.filename.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file.filename.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        return "Unsupported file type", 400
 
    # Extract information
    info = extract_info(text)
 
    return f"Skills: {info['skills']}<br>Education: {info['education']}<br>Certifications: {info['certifications']}<br>Experience: {info['experience']}"
 
if __name__ == '__main__':
    app.run(debug=True,port=8855)