from datetime import datetime

from general.nodes.base_node import NodeBase
from neomodel import RelationshipFrom, StringProperty, UniqueIdProperty, db
from questions.relations.comment_rel import CreatedRel
from users.nodes.user_node import UserNode


class CommentNode(NodeBase):
    uid = UniqueIdProperty()
    text = StringProperty(required=True)

    created = RelationshipFrom(UserNode, 'CREATED', model=CreatedRel)

    @classmethod
    def create_and_save(cls, text: str):
        comment_node = cls(text=text)
        comment_node.save()
        return comment_node

    @classmethod
    def get_comment_with_uid(cls, uid: str):
        return cls.nodes.first_or_none(uid=uid)

    @classmethod
    def get_all_comments(cls, answer_uid: str, skip: int, limit: int):
        params = {
            'answer_uid': answer_uid,
            'skip': skip,
            'limit': limit, }
        results, meta = db.cypher_query("""
            MATCH (author:UserNode)-[created_rel:CREATED]->(comment:CommentNode)-[:COMMENT]->(answer:AnswerNode)
            WHERE answer.uid = $answer_uid
            WITH author, created_rel, comment
            ORDER BY created_rel.created
            WITH collect({author:author, created_rel:created_rel, comment:comment}) AS comments
            RETURN  comments[$skip..$limit], size(comments)
                                        """, params)
        if len(results) > 0:
            comments_list = results[0][0]
            authors = []
            created_date = []
            comments = []

            for data in comments_list:
                authors.append(UserNode.inflate(data['author']))
                created_date.append(CreatedRel.inflate(data['created_rel']))
                comments.append(cls.inflate(data['comment']))

            total_comments = results[0][1]
            return {
                'authors': authors,
                'created_date': created_date,
                'comments': comments,
                'total_comments': total_comments
            }
        else:
            return None

    def edit_comment(self, username: str, text: str):
        now = datetime.now()
        params = {
            'username': username,
            'text': text,
            'now': datetime.timestamp(now)
        }
        results, meta = db.cypher_query(f"""
            MATCH (author:UserNode)-[created_rel:CREATED]->(comment:CommentNode)
            WHERE comment.uid = "{self.uid}" AND author.username = $username
            SET comment.text = $text
            SET created_rel.edited = $now
            return author, created_rel, comment
            """, params)
        if len(results) > 0:
            author = [UserNode.inflate(row[0]) for row in results]
            created_date = [CreatedRel.inflate(row[1]) for row in results]
            comment = [self.inflate(row[2]) for row in results]

            return {
                'author': author[0],
                'created_date': created_date[0],
                'comment': comment[0],
            }
        else:
            return None

    def delete_comment(self):
        result, meta = db.cypher_query(f"""
                MATCH (comment:CommentNode)-[rel]-()
                WHERE comment.uid = "{self.uid}"
                DETACH DELETE comment, rel""")
