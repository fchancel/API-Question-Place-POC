
import math
import random
import string
from typing import Optional

from users.nodes.user_node import UserNode
from users.services.user_services import create_password_hash


# from schema.user_schema import UserPayloadCreateInDB
def create_dev_user():
    node = UserNode(username="dev1",
                    last_name="dev",
                    password=create_password_hash("dev"),
                    first_name="dev",
                    is_active=True,
                    email_verified=True,
                    is_verified=True,
                    email="dev@tripeerz.com"
                    )
    node.save()
    return node


def random_email(first_name: Optional[str] = None, last_name: Optional[str] = None):

    hosts = ["gmail", "hotmail", "protonmail", "caramail", "gmx", "doudou", "egypt666", "student.le-101", "tripeerz",
             "ghandi", "monomail", "coolmail", "wanadoo", "orange", "free", "sfr"]
    exts = ["com", "net", "org", "fr", "it", "eu"]
    separators = ["-", ".", "_", ""]

    if not last_name and not first_name:
        letters = string.ascii_letters + string.digits
        name_len = random.randint(3, 14)
        name = (''.join(random.choice(letters) for i in range(name_len)))
    else:
        r = random.randint(0, 3)
        if r == 0:
            name = f'{first_name.lower()}{random.choice(separators)}{last_name.lower()}'
        elif r == 1:
            name = f'{first_name}{random.choice(separators)}{last_name}'
        else:
            name = f'{first_name.lower()}{random.choice(separators)}{last_name[0].lower()}'

        if random.randint(0, 3) == 0:
            name += f"{random.choice(separators)}{random.randint(0, 666)}"

    host = random.choice(hosts)

    ext = random.choice(exts)

    return f'{name}@{host}.{ext}'


def random_first_name():
    return random.choice(["Liam", "Olivia", "Noah", "Emma", "Oliver", "Ava", "Kevin", "Florian",
                          "Elijah", "Charlotte", "William", "Sophia", "James", "Amelia",
                          "Benjamin", "Isabella", "Lucas", "Mia", "Henry", "Evelyn",
                          "Alexander", "Harper", "Remi", "Renaud", "Agathe", "Mouhnir", "Angelo",
                          "Gabriel", "Léo", "Raphaël", "Arthur", "Louis", "Emma", "Vincent",
                          "Jade", "Louise", "Lucas", "Adam", "Maël", "Jules", "Hugo", "Alice", "Liam", "Lina", "Chloé",
                          "Noah", "Ethan", "Paul", "Mia", "Inès", "Léa", "Tiago", "Rose", "Mila", "Ambre", "Sacha",
                          "Gabin", "Nathan", "Mohamed", "Anna", "Aaron", "Eden", "Julia", "Léna", "Tom", "Noé", "Théo",
                          "Elena", "Léon", "Zoé", "Juliette", "Manon", "Martin", "Mathis", "Eva", "Timéo", "Nolan",
                          ])


def random_last_name():
    return random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones",
                          "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez",
                          "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor",
                          "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
                          "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis",
                          "Robinson", "Walker", "Young", "Allen", "King",
                          "Wright", "Scott", "Torres", "Nguyen", "Rambonona", "Martin", "Bernard", "Thomas", "Petit",
                          "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefèvre",
                          "Leroy", "Roux", "David", "Bertrand", "Morel", "Fournier", "Girard", "Bonnet", "Dupont",
                          "Lambert", "Fontaine", "Rousseau", "Vincent", "Muller", "Lefevre"])


def random_user() -> UserNode:
    """
    Generate an user following the UserPayloadCreateInDB Schema: api/schema/user_schema.py
    """

    def _create_username(first_name: str, last_name: str) -> str:
        first_name = first_name.translate(str.maketrans('', '', '- '))
        username = first_name.lower() + last_name[0].lower()
        return f"{username}1"

    first_name = random_first_name()
    last_name = random_last_name()

    username = _create_username(first_name, last_name)
    email = random_email(first_name, last_name)
    user = UserNode(first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password="HASHED_PASSWORD",
                    is_active=random.randint(0, 10) != 0,  # 10%
                    email_verified=True,  # Always
                    private_profile=random.randint(0, 3) == 0,  # 25%
                    is_verified=random.randint(0, 2) == 0  # 33%
                    )
    return user


def generate_users(nb: int, verbose: bool = True) -> list[UserNode]:
    """
    Generate a list of users, with username indexes properly
    in case the usernae already exist
    """
    def _increase_username_index(username: str):
        nb = int(username[-1])
        username = username[0:-1]
        return username + str(nb + 1)

    user_list: list[UserNode] = []
    for i in range(nb):
        created = random_user()
        for u in user_list:
            if u.username == created.username:
                created.username = _increase_username_index(created.username)
        try:
            created.save()
            user_list.append(created)
            if verbose:
                print(f"Creating user {created.username} - {created.email}")
        except Exception as e:
            print(f"ERROR: {e}")
    return user_list


def generate_follow_rels(user: UserNode, user_list: list[UserNode], verbose: bool = True):

    other_users = list.copy(user_list)

    # An user can follow a number of users form 0 to 10% of the total number of users.
    nb_followings = random.randint(0, math.trunc(other_users.__len__() / 14))
    max_followings = random.randint(10, 40)
    if nb_followings > max_followings:
        nb_followings = max_followings

    for i in range(nb_followings):
        try:
            o = random.choice(other_users)

            # We don't want an user following himself, or following two time one person
            if o is not user:
                if verbose:
                    print(f'{user.username} follow {o.username}')

                user.follow.connect(o)

                # Users have a small chance that the users they just followed will follow them back:
                if random.randint(0, 5) == 0:
                    if verbose:
                        print(f'{o.username} follow back {user.username}')
                    o.follow.connect(user)

                other_users.remove(o)

        except Exception as e:
            print(f'ERROR: {e}')
