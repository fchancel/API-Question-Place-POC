from datetime import datetime

from general.nodes.base_node import NodeBase
from general.nodes.meta_node import MetaBase
from neomodel import (RelationshipFrom, RelationshipTo, StringProperty,
                      UniqueIdProperty, db)
from questions.nodes.comment_node import CommentNode
from questions.nodes.question_node import QuestionNode
from questions.relations.answer_rel import (AnswerRel, CommentRel, CreatedRel,
                                            ValidatedRel, VotedRel)
from users.nodes.user_node import UserNode


class AnswerMeta(MetaBase):
    pass


class AnswerNode(NodeBase):
    uid = StringProperty(required=True)
    text = StringProperty(required=True)

    answer = RelationshipTo(QuestionNode, 'ANSWER', model=AnswerRel)
    validated = RelationshipFrom(QuestionNode, 'VALIDATED', model=ValidatedRel)
    voted = RelationshipFrom(UserNode, 'VOTED', model=VotedRel)
    created = RelationshipFrom(UserNode, 'CREATED', model=CreatedRel)
    comment = RelationshipFrom(CommentNode, 'COMMENT', model=CommentRel)

    @classmethod
    def create_and_save(cls, text: str):
        uid_temp = 0
        answer_node = cls(uid=uid_temp, text=text)
        answer_node.save()
        AnswerMeta.create_and_save_uid(answer_node)
        return answer_node

    @classmethod
    def get_answer_with_uid(cls, uid: str):
        return cls.nodes.first_or_none(uid=uid)

    def get_question(self):
        result, meta = db.cypher_query(f"""
                MATCH (question:QuestionNode)<-[:ANSWER]-(answer:AnswerNode)
                WHERE answer.uid = "{self.uid}"
                RETURN question""")
        if len(result) > 0:
            question = QuestionNode.inflate(result[0])
            return question
        else:
            return None

    @classmethod
    def get_all_answers(cls, question_uid: str, skip: int, limit: int, sort_by: str, desc: str):
        params = {
            'question_uid': question_uid,
            'skip': skip,
            'limit': limit, }
        results, meta = db.cypher_query(f"""
            MATCH (author:UserNode)-[created_rel:CREATED]->(answer:AnswerNode)-[:ANSWER]->(question:QuestionNode)
            WHERE question.uid = $question_uid
            OPTIONAL MATCH (answer)<-[:COMMENT]-(comment:CommentNode)
            OPTIONAL MATCH (:UserNode)-[vote_rel:VOTED]->(answer)
            OPTIONAL MATCH (answer)<-[validated_rel:VALIDATED]-(question)
            WITH collect(vote_rel) AS vote_rel, answer, validated_rel, created_rel, author,
                    count(comment) AS `number_comments`
            WITH [x IN vote_rel WHERE x.type_vote = "up"] AS up, [x IN vote_rel WHERE x.type_vote = "down"] AS down,
                     answer, validated_rel, created_rel, author, number_comments
            WITH size(up) - size(down) AS total_vote, answer, validated_rel, created_rel, author, number_comments
            ORDER BY validated_rel, {sort_by} {desc}"""+"""
            WITH collect({author:author, created_rel:created_rel,answer:answer, total_vote:total_vote,
                    validated_rel:validated_rel, number_comments:number_comments }) as answers
            RETURN  answers[$skip..$limit], size(answers)""", params)

        if len(results) > 0:
            answers_list = results[0][0]
            authors = []
            created_date = []
            answers = []
            total_vote = []
            validated = []
            number_comments = []
            for data in answers_list:
                authors.append(UserNode.inflate(data['author']))
                created_date.append(CreatedRel.inflate(data['created_rel']))
                answers.append(cls.inflate(data['answer']))
                total_vote.append(data['total_vote'])
                number_comments.append(data['number_comments'])
                if not data['validated_rel']:
                    validated.append(None)
                else:
                    validated.append(ValidatedRel.inflate(data['validated_rel']))

            total_answers = results[0][1]
            return {
                'authors': authors,
                'created_date': created_date,
                'answers': answers,
                'total_vote': total_vote,
                'validated': validated,
                'number_comments': number_comments,
                'total_answers': total_answers
            }
        else:
            return None

    def edit_answer(self, username: str, text: str):
        now = datetime.now()
        params = {'username': username,
                  'text': text,
                  "now": datetime.timestamp(now)}
        results, meta = db.cypher_query(f"""
            MATCH (author:UserNode)-[created_rel:CREATED]->(answer:AnswerNode)-[:ANSWER]->(question:QuestionNode)
            WHERE answer.uid = "{self.uid}" AND author.username = $username
            SET answer.text = $text
            SET created_rel.edited = $now
            WITH author, answer, created_rel, question
            OPTIONAL MATCH (answer)<-[:COMMENT]-(comment:CommentNode)
            OPTIONAL MATCH (:UserNode)-[vote_rel:VOTED]->(answer)
            OPTIONAL MATCH (answer)<-[validated_rel:VALIDATED]-(question)
            WITH collect(vote_rel) AS vote_rel, question, answer, validated_rel, created_rel, author,
                    count(comment) AS `number_comments`
            WITH [x IN vote_rel WHERE x.type_vote = "up"] AS up, [x IN vote_rel WHERE x.type_vote = "down"] AS down,
                    question, answer, validated_rel, created_rel, author, number_comments
            WITH size(up) - size(down) AS total_vote, question, answer, validated_rel, created_rel,
                    author, number_comments
            RETURN  author, created_rel, answer, total_vote, validated_rel, number_comments
            """, params)

        if len(results) > 0:
            author = [UserNode.inflate(row[0]) for row in results]
            created_date = [CreatedRel.inflate(row[1]) for row in results]
            answer = [self.inflate(row[2]) for row in results]
            total_vote = [(row[3]) for row in results]
            if not results[0][4]:
                validated = [None]
            else:
                validated = [ValidatedRel.inflate(row[4]) for row in results]
            number_comments = [(row[5]) for row in results]
            return {
                'author': author[0],
                'created_date': created_date[0],
                'answer': answer[0],
                'total_vote': total_vote[0],
                'validated': validated[0],
                'number_comments': number_comments[0]
            }
        else:
            return None

    @classmethod
    def get_validated_answer(cls, uid_question: str):
        params = {"uid_question": uid_question}
        results, meta = db.cypher_query("""
                MATCH (question:QuestionNode)-[validated_rel:VALIDATED]->(answer:AnswerNode)
                WHERE question.uid = $uid_question
                RETURN answer, validated_rel""", params)

        if len(results) > 0:
            answer = [cls.inflate(row[0]) for row in results]
            validated = [ValidatedRel.inflate(row[1]) for row in results]
            return {
                'answer': answer[0],
                'validated': validated[0]
            }
        else:
            return None

    def delete_answer(self):
        result, meta = db.cypher_query(f"""
                MATCH (answer:AnswerNode)-[rel]-()
                WHERE answer.uid = "{self.uid}"
                DETACH DELETE answer, rel""")
