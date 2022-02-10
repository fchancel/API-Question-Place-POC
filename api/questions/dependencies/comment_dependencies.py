from fastapi import Depends, HTTPException, status
from questions.nodes.comment_node import CommentNode
from users.dependencies.user_dependencies import GetCurrentUser
from users.nodes.user_node import UserNode


def get_comment_dependancie(uid: str):
    comment_node = CommentNode.get_comment_with_uid(uid=uid)
    if not comment_node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return comment_node


def owner_comment(comment_node: CommentNode = Depends(get_comment_dependancie),
                  current_user: UserNode = Depends(GetCurrentUser())):
    if not comment_node.created.is_connected(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not owner")
    return {
        'user': current_user,
        'comment': comment_node
    }
