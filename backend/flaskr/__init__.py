import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_Q(req, select):
    page_number = req.args.get('page', 1, type=int)
    start_P = (page_number - 1) * QUESTIONS_PER_PAGE
    end_P = start_P + QUESTIONS_PER_PAGE

    questions_list = [current_question.format() for current_question in select]
    current_questions = questions_list[start_P:end_P]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS")
        return response

    '''
  @DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

    @app.route("/categories", methods=["GET"])
    def get_categories():
        try:
            load_categories = Category.query.order_by(Category.type).all()
            if len(load_categories) == 0:
                abort(404)
            the_categories = {category.id: category.type for category in Category.query.all()}

            return jsonify({"success": True, "categories": the_categories})
        except Exception:
            abort(404)

    '''
  @DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    @app.route("/questions", methods=["GET"])
    def get_questions():
        load = Question.query.order_by(Question.id).all()
        load_questions = paginate_Q(request, load)
        load_cat = Category.query.order_by(Category.type).all()

        load_categories = {cat.id: cat.type for cat in load_cat}

        try:
            if len(load_questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': load_questions,
                'total_questions': len(load_questions),
                'categories': load_categories,
                'current_category': load_categories
            })
        except Exception:
            abort(404)

    '''
  @DONE: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

    @app.route("/questions/<int:id_D>", methods=["DELETE"])
    def delete_question(id_D):
        try:
            load_Q = Question.query.get(id_D)
            load_Q.delete()

            return jsonify({'success': True,
                            'message': "Question deleted",
                            'id': id_D
                            })

        except Exception:
            abort(422)

    '''
  @DONE: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

    @app.route("/questions", methods=['POST'])
    def post_question():

        try:
            load = request.get_json()
            new_Q = load['question']
            new_A = load['answer']
            new_D = load['difficulty']
            new_C = load['category']
            question = Question(question=new_Q, answer=new_A, category=new_C, difficulty=new_D)
            question.insert()
            return jsonify({
                'success': True,
                'message': 'Question created'
            })

        except Exception:
            abort(422)

    '''
  @DONE: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        load = request.get_json()['searchTerm']
        try:

            search_results = Question.query.filter(
                Question.question.ilike('%' + load + '%')).all()
            list_Q = []
            for each in search_results:
                list_Q.append(each)
            if len(list_Q) == 0:
                abort(422)

            return jsonify({
                'success': True,
                'questions': paginate_Q(request, search_results),
                'total_questions': len(search_results),
                'current_category': None
            })
        except Exception:
            abort(422)

    '''
  @DONE: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.route('/categories/<int:id_c>/questions', methods=['GET'])
    def get_Q_depend_on_C(id_c):
        list_Q = Question.query.filter(Question.category == int(id_c))
        try:
            result_c = paginate_Q(request, list_Q)

            if len(result_c) == 0:
                abort(404)
            else:

                return jsonify({
                    'success': True,
                    'questions': result_c,
                    'current_category': id_c,
                    'total_questions': len(result_c)
                })

        except Exception:
            abort(404)

    '''
  @DONE: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():

        load = request.get_json()
        print(load)
        previous_Q = load.get('previous_questions')
        quiz_C = load.get('quiz_category')


        try:

            quiz_C_id = int(quiz_C['id'])
            list_Q = Question.query.filter(Question.id.notin_(previous_Q))
            if (previous_Q is None) or (quiz_C is None):
                abort(404)

            if quiz_C_id != 0:
                list_Q = list_Q.filter_by(category=quiz_C_id)

            random_Q = list_Q.first().format()



        except Exception:
            abort(404)

        return jsonify({
            'success': True,
            'question': random_Q
        })

    '''
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, "error": 404, "message": "Resource Not Found Error"
        })

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False, "error": 422, "message": "Unprocessable Error"
        })

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False, "error": 405, "message": "Method Not Allowed"
        })

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False, "error": 400, "message": "Bad Request"
        })

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            "success": False, "error": 500, "message": "Internal server error"
        })

    return app
