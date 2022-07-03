import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10 # Number to display per page

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    
    #Set up CORS. Allow '*' for origins.
    setup_db(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})


    #The after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, PUT, PATCH, POST, DELETE, OPTIONS"
        )
        return response

    
    #This endpoint to handles GET requests for all available categories.
    @app.route("/categories")
    def get_categories():
        try:
            categories = Category.query.all()
            categories_list = {category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'categories': categories_list
            })
        except Exception as e:
            print(e)
            abort(404)
            
        # page = request.args.get("page", 1, type=int)
        # start = (page - 1) * 10
        # end = start + 10
        
        # categories = Category.query.all()
        # # print(categories)
        # formatted_categories = [category.format() for category in categories]
        
        # if len(formatted_categories) == 0:
        #     abort(404)
            
        # return jsonify(
        #     {
        #         "success": True,
        #         "categories": formatted_categories[start:end],
        #         "total_categories": len(formatted_categories),
        #     }
        # )


    """
    This endpoint handles GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
    At this point, starting the application loads questions and categories generated, ten questions per page and pagination at the bottom of the screen for three pages. Clicking on the page numbers updates the questions.
    """
    @app.route("/questions")
    def get_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            categories = Category.query.all()
            categories_list = {category.id: category.type for category in categories}
            
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories': categories_list,
                'current_category': None
            })
        except Exception as e:
            print(e)
            abort(404)
        
        # selection = Question.query.order_by(Question.id).all()
        # current_questions = paginate_questions(request, selection)
        # categories = Category.query.order_by(Category.type).all()
        # current_category = [Category.type for category in categories]
        
        # if len(current_questions) == 0:
        #     abort(404)
            
        # if len(categories) == 0:
        #     abort(404)
            
        # return jsonify(
        #     {
        #         "success": True,
        #         "questions": current_questions,
        #         "total_questions": len(current_questions),
        #         #"current_category": categories[]
        #         "categories": current_category,
        #     }
        # )

    """
    This endpoint to DELETEs a question using a question ID.
    On click the trash icon next to a question, the question is removed. This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            
            if question is None:
                abort(404)
                
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            
            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all())
                }
            )
            
        except Exception as e:
            print(e)
            abort(422)

    """
    This endpoint to POSTs a new question, which requires the question and answer text, category, and difficulty score.
    On submiting a question on the "Add" tab, the form will clear and the question will appear at the end of the last page of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        
        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        search = body.get("search", None)
        
        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search)))
                current_questions = paginate_questions(request, selection)
                
                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(selection.all()),
                    }
                )
            
            else:
                questions = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                
                questions.insert()
                
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)
                
                return jsonify(
                    {
                        "success": True,
                        "created": questions.id,
                        "questions": current_questions,
                        "total_questions": len(Question.query.all()),
                    }
                )
        
        except:
            abort(422)

    """
    This Creates a POST endpoint to get questions based on a search term. It returns any questions for whom the search term is a substring of the question.
    You can search by any phrase. The questions list updates and includes only question that include that string within their question. You can try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get("searchTerm", None)
        
        if search_term:
            search_results = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
            categories = Category.query.all()
            categories_list = [category.format() for category in categories]
            return jsonify(
                {
                    "success": True,
                    "questions": [question.format() for question in search_results],
                    "total_questions": len(search_results),
                    "categories": categories_list,
                    "current_category": None
                }
            )
        
        abort(404)

    """
    This creates a GET endpoint to get questions based on category.
    In the "List" tab / main screen, clicking on one of the categories in the left column causes only questions of that category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def get_question_category(category_id):
        categories_new = Category.query.filter(Category.id == category_id).one_or_none()
        if categories_new is None:
            abort(404)
        
        try:
            category = Category.query.get(category_id)
            categories = Category.query.all()
            selection = Question.query.filter(Question.category == category.id).all()
            #selection = Category.query.filter_by(Category.id == category_id).one_or_none()
            current_questions = paginate_questions(request, selection)
            
            return jsonify(
                {
                    "success": True,
                    "questions": [question.format() for question in selection],
                    "total_questions": len(Question.query.all()),
                    "current_categories": [category.format() for category in categories],
                    "categories": [category.format() for category in categories],
                    "current_category": category.type
                }
            )
        
        except Exception as e:
            print(e)
            abort(400)

    """
    This creates a POST endpoint to get questions to play the quiz. This endpoint takes category and previous question parameters and returns a random questions within the given category, if provided, and that is not one of the previous questions.
    In the "Play" tab, after a user selects "All" or a category, one question at a time is displayed, the user is allowed to answer and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def get_quiz():
        try:
            body = request.get_json()
            
            prev_questions = body.get("previous_questions", None)
            #quiz_answer = body.get("quiz_answer")
            quiz_category = body.get("quiz_category", None)
            #quiz_difficulty = body.get("quiz_difficulty")
                
            if quiz_category["id"] == 0:
                #questions = Question.query.filter(Question.id.notin_(prev_questions)).all()
                questions = Question.query.all()
            
            else:
                questions = Question.query.filter(Question.category == quiz_category["id"], Question.id.notin_(prev_questions)).all()
                #questions = Question.query.filter(Question.category == quiz_category["id"]).all()
            
            quiz_questions = []
            
            for question in questions:
                if question.id not in prev_questions:
                    quiz_questions.append(question)
                    
            if len(quiz_questions) == 0:
                return jsonify({
                'success': True,
                'question': None
                #'question': random_question.format()
            })
                
            random_question = random.choice(quiz_questions)
            
            return jsonify({
                'success': True,
                'question': random_question.format()
            })
        except Exception as e:
            print(e)
            abort(422)

    """
    Here are the error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}), 400
        )
        
    @app.errorhandler(500)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "server error"}), 500
        )


    return app

