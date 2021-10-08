import os
import unittest
import json

from werkzeug.wrappers import response
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db
from random import randrange


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'kido', '123', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # question mockup
        self.question_mockup = {
            'question': 'How many stars are on the american flag?',
            'answer': '50 stars',
            'difficulty': 3,
            'category': '4'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['currentCategory'])

    def test_delete_question(self):
        ques_id = db.session.query(Question.id).all()
        arrId = [item[0] for item in ques_id]
        randId = randrange(len(arrId))
        q_item = arrId[randId]
        res = self.client().delete('/questions/{}'.format(q_item),
                                   headers={'Content-type': 'application/x-www-form-urlencoded'})
        data = json.loads(res.data)

        # check if q exist
        ques = Question.query.filter(Question.id == q_item).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['id'])
        # error check
        self.assertEqual(ques, None)


    def test_post_questions_handler(self):
        response = self.client().post('/questions',
                                      json={'searchTerm': 'title'})
        data = json.loads(response.data)

        # get created question
        ques = Question.query.filter_by(id=data['id']).one_or_none()

        self.assertEqual(response.status_code, 200)
        # error check
        self.assertIsNotNone(ques)

    def test_get_questions_by_category(self):
        ques_id = db.session.query(Category.id).all()
        arrId = [item[0] for item in ques_id]
        randId = randrange(len(arrId))
        q_item = arrId[randId]
        # print("q_item >>>>>>>>>>>>>>", q_item)

        response = self.client().get('/categories/{}/questions'.format(q_item),
                                     headers={'Content-type': 'application/x-www-form-urlencoded'})
        data = json.loads(response.data)
        # print("data >>>>>>>>>>>>>>>>>> ", data)

        self.assertEqual(response.status_code, 200)

        # error check
        self.assertNotEqual(len(data['questions']), 0)

    def random_questions(self):

        # send post request with category and previous questions
        response = self.client().post('/quizzes',
                                      json={'previous_questions': [13, 14],
                                            'quiz_category': {'type': 'History', 'id': '3'}})

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['question'])
        # error check
        self.assertNotEqual(data['question']['id'], 13)
        self.assertNotEqual(data['question']['id'], 14)

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
