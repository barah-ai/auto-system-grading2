import sqlite3
import re
import textract
from db import get_db_connection
import os
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch


def extractContent(pathToFile: str) -> list:
    """extract questions
    Parameters
    ----------
    pathToFile : str
        Path of the uploaded questions(.docx) file.

    Returns
    -------
    list
        list of extracted questions from the .docx file.

    """
    # Read the contents of the document file
    questionsFileContent = textract.process(pathToFile).decode('utf-8')

    # Extract questions from the document text
    pattern = r'(\S.*)'  # Regular expression pattern to match questions
    questions = re.findall(pattern, questionsFileContent)
    return questions


def saveContent(contentType: str, pathToFile: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    """ Extracts questions from the uploaded .docx file and saves in the questions table in the sqlite db, method is invoked after file is uploaded
    ----------
    Parameters
    ----------
    contentType : str
        'answers' for when answers need to be saved; 'questions' for questions
    pathToFile : str
        Path of the uploaded questions(.docx) file.

    Returns
    -------
    bool
        True on success;False on failure
    """
    contentList = extractContent(pathToFile)
    if contentType == 'questions':
        try:
            insert_query = "INSERT INTO questions (question_text) VALUES (?)"
            for i in contentList:
                cursor.execute(insert_query, (i,))
                # insert_query2 = "INSERT INTO model (question_id,answer_text) VALUES (?,?)"
                # modelAnswer = generate_response(i)
                # print(modelAnswer)
                # # cursor.execute(insert_query2, (cursor.lastrowid, modelAnswer))
                conn.commit()
            return 'All questions have been saved successfully!'
        except Exception as e:
            return e
    else:
        pattern = r'(\d+)'  # Regular expression pattern to match questions
        studentId = re.findall(pattern, pathToFile)
        try:
            insert_query = "INSERT INTO answers (question_id,student_id,answer_text) VALUES (?,?,?)"
            for x, y in enumerate(contentList):
                cursor.execute(insert_query, (x + 1, int(studentId[0]), y))
                conn.commit()
            return 'All answers have been saved successfully!'
        except Exception as e:
            return e


def getResults():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute a SELECT query and fetch records
    cursor.execute(
        "SELECT question_id, question_text, answer_text FROM  answers JOIN questions  ON questions.id = answers.question_id")
    records = cursor.fetchall()

    # Print the fetched records
    return records

def generateModelAnswers():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute a SELECT query and fetch records
    cursor.execute(
        "SELECT question_id, question_text, answer_text FROM  answers JOIN questions  ON questions.id = answers.question_id")
    records = cursor.fetchall()

    for i in records:
        modelAnswer = generate_response(i[1])
        print(modelAnswer)
        insert_query2 = "INSERT INTO model (question_id,answer_text) VALUES (?,?)"
        cursor.execute(insert_query2, (i[0], modelAnswer))
        conn.commit()
    # Print the fetched records

def clearData(folderPath):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Query the sqlite_master table to get a list of table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = cursor.fetchall()

    # Extract table names from the result
    table_names = [row[0] for row in table_names]

    # Loop through the table names and truncate each table
    for table_name in table_names:
        truncate_sql = f"DELETE FROM {table_name};"
        cursor.execute(truncate_sql)

    # Commit the changes and close the connection
    conn.commit()
    try:
        for filename in os.listdir(folderPath):
            file_path = os.path.join(folderPath, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return "All records have been deleted successfully!"
    except Exception as e:
        return f"Error deleting files: {str(e)}"


def generate_response(prompt):
    model = GPT2LMHeadModel.from_pretrained('./model')
    tokenizer = GPT2Tokenizer.from_pretrained('./model')
    # Create the attention mask and pad token id
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    attention_mask = torch.ones_like(input_ids)
    pad_token_id = tokenizer.eos_token_id

    output = model.generate(
        input_ids,
        max_length=256,
        #fp16=False,
        num_beams=4,
        attention_mask=attention_mask,
        num_return_sequences=1,  # Generate a single sequence
        temperature=0.9,       # Controls randomness (higher for more diversity)
        early_stopping=True,
        top_k=40,
        top_p=0.92
    )
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    if len(response) > 0:
        return re.findall(r'(?<=\[<startoftext>])(.*?)(?=\[<endoftext>])', response)[0]
    else:
        return 'I couldn\'t answer that'
