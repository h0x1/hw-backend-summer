from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest
from aiohttp_apispec import querystring_schema, request_schema, response_schema, json_schema

from app.quiz.models import Answer
from app.quiz.schemes import (
    ListQuestionSchema, QuestionSchema, 
    ThemeIdSchema, ThemeListSchema, ThemeSchema)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        title = self.data["title"]
        exist_theme = await self.store.quizzes.get_theme_by_title(title)

        if exist_theme:
            raise HTTPConflict

        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @response_schema(ThemeListSchema)
    async def get(self):
        list_themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({"themes": list_themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        theme_id = self.data["theme_id"]
        title = self.data["title"]
        answers = self.data["answers"]

        theme = await self.store.quizzes.get_theme_by_id(theme_id)
        if not theme:
            raise HTTPNotFound

        existed_question = await self.store.quizzes.get_question_by_title(title)
        if existed_question:
            raise HTTPConflict

        total_correct_answers = sum(answer["is_correct"] for answer in answers)
        if total_correct_answers != 1 or len(self.data['answers']) <= 1:
            raise HTTPBadRequest

        question = await self.store.quizzes.create_question(
            title=title,
            theme_id=theme_id,
            answers=[
                Answer(
                    title=answer["title"],
                    is_correct=answer["is_correct"]
                ) for answer in answers
            ]
        )

        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        theme_id = self.request.query.get("theme_id")
        questions = await self.store.quizzes.list_questions(theme_id=theme_id)
        return json_response(data=ListQuestionSchema().dump({"questions": questions}))
