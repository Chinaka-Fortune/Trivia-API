import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from dotenv import load_dotenv
load_dotenv()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")
        self.database_name = os.getenv("TEST_DB_NAME")
        self.database_path = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT, self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question = {"quetion": "What is your hobby?", "answer": "Football", "category": "Sport", "difficulty": 1}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Two tests for each route, each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))
    
    def test_404_sent_requesting_questions_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000", json={"difficulty": 1})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_get_paginated_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])
        self.assertTrue(len(data["categories"]))
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/categories?page=1000", json={"id": 1})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_delete_question(self):
        res = self.client().delete("/questions/1")
        data = json.loads(res.data)
        
        question = Question.query.filter(Question.id == 1).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(question, None)
        
    def test_422_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["created"], 1)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
    
    def test_422_question_creation_fails(self):
        res = self.client("/questions", json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    
    def test_get_question_search_results(self):
        res = self.client().post("/questions/search", json={"search": "What boxer's original name is Cassius Clay"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["current_category"])
        self.assertTrue(len(data["questions"]))
    
    def test_get_question_search_no_results(self):
        res = self.client().post("/questions/search", json={"search": "football"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(data["questions"], 0)
        self.assertEqual(data["current_category"], 0)
        self.assertEqual(len(data["questions"]), 0)
        self.assertEqual(len(data["message"]), "resourse not found")
    
    def test_get_question_by_category(self):
        res = self.client().post("/categories/<int:categoty_id>/questions", json={"category": 1})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(len(data["questions"]))
    
    def test_404_sent_requesting_question_by_category(self):
        res = self.client().post("/categories/<int:categoty_id>/questions", json={"category": 1000})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
        
    def test_get_quiz_question(self):
        res = self.client().post("/quizzes", json={"search": "What boxer's original name is Cassius Clay"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(len(data["questions"]))
    
    def test_404_sent_requesting_quiz_question(self):
        res = self.client().post("/quizzes", json={"search": "What boxer's original name is Cassius Clay"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()