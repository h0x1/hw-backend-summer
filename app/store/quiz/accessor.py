from sqlalchemy import select
from sqlalchemy.orm import joinedload, subqueryload, selectinload

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    Answer,
    Question,
    Theme, ThemeModel, AnswerModel, QuestionModel,
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        async with self.app.database.session.begin() as session:
            new_theme = ThemeModel(title=title)
            session.add(new_theme)

        return new_theme.to_dc()

    async def get_theme_by_title(self, title: str) -> Theme | None:
        async with self.app.database.session() as session:
            theme = (await session.execute(
                select(ThemeModel)
                .where(ThemeModel.title == title)
            )).scalar()

        if not theme:
            return

        return theme.to_dc()

    async def get_theme_by_id(self, id_: int) -> Theme | None:
        async with self.app.database.session() as session:
            theme = (await session.execute(
                select(ThemeModel)
                .where(ThemeModel.id == id_)
            )).scalar()

        if not theme:
            return

        return theme.to_dc()

    async def list_themes(self) -> list[Theme]:
        async with self.app.database.session() as session:
            themes_models = (await session.execute(
                select(ThemeModel)
            )).scalars().all()

            themes = [theme_model.to_dc() for theme_model in themes_models]
        return themes

    async def create_answers(self, question_id: int, answers: list[Answer]) -> list[Answer]:
        async with self.app.database.session() as session:
            new_answers = [
                AnswerModel(
                    title=answer.title,
                    is_correct=answer.is_correct,
                    question_id=question_id
                ) for answer in answers
            ]
            session.add_all(new_answers)
            await session.commit()

            answers = [answer.to_dc() for answer in new_answers]
            return answers

    async def create_question(self, title: str, theme_id: int, answers: list[Answer]) -> Question:
        async with self.app.database.session() as session:
            answer_models = [
                AnswerModel(
                    title=answer.title,
                    is_correct=answer.is_correct
                ) for answer in answers
            ]
            new_question = QuestionModel(
                title=title,
                theme_id=theme_id,
                answers=answer_models)

            session.add(new_question)
            await session.commit()

        return new_question.to_dc()

    async def get_question_by_title(self, title: str) -> Question | None:
        async with self.app.database.session() as session:
            question = (await session.execute(
                select(QuestionModel)
                .where(QuestionModel.title == title)
                .options(joinedload(QuestionModel.answers))
            )).scalar()

        if not question:
            return

        return question.to_dc()

    async def list_questions(self, theme_id: int | None = None) -> list[Question]:
        async with self.app.database.session() as session:
            query = select(QuestionModel)

            if theme_id:
                query = query.where(QuestionModel.theme_id == theme_id)

            question_models = (await session.execute(
                query.options(joinedload(QuestionModel.answers))
            )).scalars().unique().all()

            questions = [question_model.to_dc() for question_model in question_models]

        return questions

