from datetime import datetime

from general.nodes.base_node import NodeBase
from general.nodes.meta_node import MetaBase
from neomodel import (BooleanProperty, IntegerProperty, RelationshipFrom,
                      RelationshipTo, StringProperty, db)
from places.nodes.place_node import PlaceNode
from questions.relations.answer_rel import ValidatedRel
from questions.relations.question_rel import (CreatedRel, FollowRel,
                                              WhereQuestion)
from slugify import slugify
from users.nodes.user_node import UserNode


class QuestionMeta(MetaBase):
    pass


class QuestionNode(NodeBase):
    uid = IntegerProperty(required=True)
    title = StringProperty(required=True)
    text = StringProperty(required=True)
    slug = StringProperty(required=True)
    hidden = BooleanProperty(default=False)

    created = RelationshipFrom(UserNode, 'CREATED', model=CreatedRel)
    follow = RelationshipFrom(UserNode, 'FOLLOW', model=FollowRel)
    place = RelationshipTo(PlaceNode, 'GEO', model=WhereQuestion)

    @classmethod
    def create_and_save(cls, title: str, text: str):
        uid_temp = 0
        slug = slugify(title)
        question_node = cls(uid=uid_temp, title=title, text=text, slug=slug)
        question_node.save()
        QuestionMeta.create_and_save_uid(question_node)
        return question_node

    @classmethod
    def get_question_with_uid(cls, uid: str):
        return cls.nodes.first_or_none(uid=uid)

    @classmethod
    def get_question_complete_response(cls, uid=uid):
        params = {'uid': uid}
        results, meta = db.cypher_query("""
            MATCH (author:UserNode)-[author_rel:CREATED]->(question:QuestionNode)-[:GEO]->(place:PlaceNode)
            WHERE question.uid = $uid
            OPTIONAL MATCH (question)<-[:ANSWER]-(a:AnswerNode)
            OPTIONAL MATCH (question)-[validated_rel:VALIDATED]->(:AnswerNode)
            RETURN author, author_rel, question, place, count(a) as `nb_answer`, validated_rel
            """, params)

        if len(results) > 0:
            authors = [UserNode.inflate(row[0]) for row in results]
            created_date = [CreatedRel.inflate(row[1]) for row in results]
            questions = [cls.inflate(row[2]) for row in results]
            places = [PlaceNode.inflate(row[3]) for row in results]
            number_answers = [row[4] for row in results]
            if not results[0][5]:
                validated = [None]
            else:
                validated = [ValidatedRel.inflate(row[5]) for row in results]
            return {
                'author': authors[0],
                'created_date': created_date[0],
                'question': questions[0],
                'place': places[0],
                'number_answers': number_answers[0],
                'validated': validated[0]
            }
        else:
            return None

    @classmethod
    def get_mine_questions(cls, username: str, skip: int, limit: int, sort_by: str, desc: str):
        params = {'username': username}
        results, meta = db.cypher_query(f"""
            MATCH (creator:UserNode)-[creator_rel:CREATED]->(question:QuestionNode)-[:GEO]->(place:PlaceNode)
            WHERE creator.username = $username
            OPTIONAL MATCH (question)<-[:ANSWER]-(answer:AnswerNode)
            OPTIONAL MATCH (question)-[validated_rel:VALIDATED]->(:AnswerNode)
            WITH count(answer) as nb_answer, creator, place, creator_rel, question,
                COALESCE(validated_rel, 'None') AS validated
            ORDER BY {sort_by} {desc} """ + """
            WITH creator, collect({created_date:creator_rel, question:question, nb_answer:nb_answer,validated:validated, place:place }) as questions""" + f"""
            RETURN creator, questions[{skip}..{limit}], size(questions) AS amountOfQuestions""", params)

        if len(results) > 0:
            questions_list = results[0][1]
            authors = []
            created_date = []
            questions = []
            places = []
            number_answers = []
            validated = []
            for data in questions_list:
                authors.append(UserNode.inflate(results[0][0]))
                created_date.append(CreatedRel.inflate(data['created_date']))
                questions.append(cls.inflate(data['question']))
                places.append(PlaceNode.inflate(data['place']))
                number_answers.append(data['nb_answer'])
                if data['validated'] == 'None':
                    validated.append(None)
                else:
                    validated.append(ValidatedRel.inflate(data['validated']))

            total_question = results[0][2]
            return {
                'authors': authors,
                'created_date': created_date,
                'questions': questions,
                'places': places,
                'number_answers': number_answers,
                'validated': validated,
                'total_question': total_question
            }
        else:
            return None

    @classmethod
    def get_followed_questions(cls, username: str, skip: int, limit: int, desc: str):
        params = {'username': username}
        results, meta = db.cypher_query(f"""
            MATCH (user:UserNode)-[follow_rel:FOLLOW]->(question:QuestionNode)-[:GEO]->(place:PlaceNode)
            WHERE user.username = $username
            MATCH (question)<-[creator_rel:CREATED]-(creator:UserNode)
            OPTIONAL MATCH (question)<-[:ANSWER]-(answer:AnswerNode)
            OPTIONAL MATCH (question)-[validated_rel:VALIDATED]->(:AnswerNode)
            WITH count(answer) as nb_answer,follow_rel, creator, place, creator_rel, question, 
                COALESCE(validated_rel, 'None') AS validated
            ORDER BY follow_rel.created {desc} """ + """
            WITH collect({creator:creator, created_date:creator_rel, question:question, nb_answer:nb_answer,validated:validated, place:place }) as questions""" + f"""
            RETURN questions[{skip}..{limit}], size(questions) AS amountOfQuestions""", params)

        if len(results) > 0:
            questions_list = results[0][0]
            authors = []
            created_date = []
            questions = []
            places = []
            number_answers = []
            validated = []
            for data in questions_list:
                authors.append(UserNode.inflate(data['creator']))
                created_date.append(CreatedRel.inflate(data['created_date']))
                questions.append(cls.inflate(data['question']))
                places.append(PlaceNode.inflate(data['place']))
                number_answers.append(data['nb_answer'])
                if data['validated'] == 'None':
                    validated.append(None)
                else:
                    validated.append(ValidatedRel.inflate(data['validated']))

            total_question = results[0][1]
            return {
                'authors': authors,
                'created_date': created_date,
                'questions': questions,
                'places': places,
                'number_answers': number_answers,
                'validated': validated,
                'total_question': total_question
            }
        else:
            return None

    def edit_question(self, username: str, title: str, text: str, google_place_id: str):
        now = datetime.now()
        params = {
            'uid': self.uid,
            'username': username,
            'slug': slugify(title),
            'title': title,
            'text': text,
            'google_place_id': google_place_id,
            'now': datetime.timestamp(now)
        }
        results, meta = db.cypher_query("""
            MATCH (author:UserNode)-[author_rel:CREATED]->(question:QuestionNode)-[where_rel:GEO]->(place:PlaceNode)
            WHERE question.uid = $uid AND author.username = $username

            DELETE where_rel
            MERGE (new_place:PlaceNode{google_place_id:$google_place_id})
            CREATE (question)-[r:GEO]->(new_place)
            SET question += {title:$title, text:$text, slug:$slug}
            SET author_rel.edited = $now

            WITH author, author_rel, question, new_place, r
            OPTIONAL MATCH (question)<-[:ANSWER]-(a:AnswerNode)
            OPTIONAL MATCH (question)-[validated_rel:VALIDATED]->(:AnswerNode)
            RETURN author, author_rel, question, new_place, count(a) as `nb_answer`, validated_rel
            """, params)
        if len(results) > 0:
            authors = [UserNode.inflate(row[0]) for row in results]
            created_date = [CreatedRel.inflate(row[1]) for row in results]
            questions = [self.inflate(row[2]) for row in results]
            places = [PlaceNode.inflate(row[3]) for row in results]
            number_answers = [row[4] for row in results]
            if not results[0][5]:
                validated = [None]
            else:
                validated = [ValidatedRel.inflate(row[5]) for row in results]
            return {
                'author': authors[0],
                'created_date': created_date[0],
                'question': questions[0],
                'place': places[0],
                'number_answers': number_answers[0],
                'validated': validated[0]
            }
        else:
            return None
