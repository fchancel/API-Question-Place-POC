import argparse
import time

from neomodel import clear_neo4j_database, config, db

from activity.nodes.activity_type_node import ActivityTypeNode
from config import get_settings
from feedbacks.nodes.distinction_node import DistinctionNode
from general.services.utils_services import read_json_file
from initial_data.generators.profile_gen import generate_profile
from initial_data.generators.statistic_profile_gen import \
    generate_statistic_profile
from initial_data.generators.users_gen import (create_dev_user,
                                               generate_follow_rels,
                                               generate_users)
from users.nodes.user_node import UserNode

"""
    TODO: Generate Statistic and Profile for each users
"""

# CONFIG

config.DATABASE_URL = get_settings().neo4j_url()

# ARGS


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="answer yes to all question (bypass security quesions)")
    parser.add_argument("--clear-database", action="store_true",
                        help="clear the databse before the generation")
    parser.add_argument('--users', type=int, nargs='?', const=50,
                        help='Numbers of users to be created, default 50')
    return parser.parse_args()


args = init_args()

NB_USERS = args.users if args.users is not None else 50

# TIMER
start_time = time.time()


def print_time():
    if not hasattr(print_time, "actual_time"):
        print_time.actual_time = time.time()  # it doesn't exist yet, so initialize it
    print(f'{round(time.time() - print_time.actual_time, 2)}s')
    print_time.actual_time = time.time()


# CLEAR DATABASE

if args.clear_database:
    if args.yes or input("Are you sure you want to clear ALL the databse ? ") in ["y", "Y"]:
        print("=> clear database ...")
        clear_neo4j_database(db)

print_time()

# READ DISTINCTIONS

print("=> read distinctions ...")
file = get_settings().base_dir + '/initial_data/distinction_feedback.json'
for distinction_feedback in read_json_file(file):
    if args.verbose:
        print(f'add "{distinction_feedback}"')
    distinction_feedback = DistinctionNode(name=distinction_feedback).save()

print_time()

# GENERATE USERS
print("=> generate dev user ...")

dev_user = create_dev_user()
generate_profile(dev_user, args.verbose)
generate_statistic_profile(dev_user, args.verbose)
print(f"    username: {dev_user.username}, password: dev, email: {dev_user.email}")

print(f"=> generate {NB_USERS} users ...")
user_node_list = generate_users(NB_USERS, args.verbose)

print_time()

# GENERATE STATISTIC PROFILES

print("=> generate statistic_profile for each users...")

for u in user_node_list:
    generate_statistic_profile(u, args.verbose)

print_time()

# GENERATE PROFILES

print("=> generate profiles for each users...")

for u in user_node_list:
    generate_profile(u, args.verbose)

print_time()


# GENERATE FOLLOW RELATIONS

active_users = [user for user in user_node_list if user.is_active and user.email_verified]
NB_ACTIVE_USERS = active_users.__len__()

print(f'=> generate following relations for {NB_ACTIVE_USERS} active users ...')
if NB_ACTIVE_USERS > 250:
    print("     (Yeah i know, it's slooooooow ....)")


for user in active_users:
    generate_follow_rels(user, active_users, args.verbose)

print_time()

print(f'=> {NB_USERS} users created in {round(time.time() - start_time, 2)} seconds')
