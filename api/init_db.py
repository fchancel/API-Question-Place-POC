from config import get_settings
from feedbacks.nodes.distinction_node import DistinctionNode
from general.services.utils_services import read_json_file
from questions.nodes.answer_node import AnswerMeta
from questions.nodes.question_node import QuestionMeta

# INIT COUNTER
all_nodes = AnswerMeta.nodes.all()
for a in all_nodes:
    a.delete()
AnswerMeta(counter=0).save()

all_nodes = QuestionMeta.nodes.all()
for a in all_nodes:
    a.delete()
QuestionMeta(counter=0).save()


# INIT DISTINCTION
all_nodes = DistinctionNode.nodes.all()
for a in all_nodes:
    a.delete()
file = get_settings().base_dir + '/initial_data/distinction_feedback.json'
for distinction_feedback in read_json_file(file):
    DistinctionNode(name=distinction_feedback).save()
print("Distinction init done")
