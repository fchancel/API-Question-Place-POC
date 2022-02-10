import random
from datetime import datetime, timedelta

from initial_data.generators.utils import random_datetime
from lorem_text import lorem
from users.nodes.profile_node import ProfileNode
from users.nodes.user_node import UserNode
from users.schema.profile_schema import GenderEnum

MIN_AGE_IN_YEARS = 10
MAX_AGE_IN_YEARS = 90


def random_job():
    return random.choice([
        "Doctor", "Police officer", "Nurse", "Teacher", "Psychologist", "Investigator", "Lawyer",
        "Pilot", "Actor", "Dentist",
        "Social worker", "Specialized educator", "Computer graphics designer", "Mechanic",
        "Pharmacist", "Veterinarian", "Photographer", "Teacher", "Surgeon", "Accountant", "Architect",
        "Journalist", "Video game designer", "Firefighter", "Anesthesiologist", "Fashion designer",
        "Dental hygienist", "Substance abuse worker", "Ambulance driver", "Carpenter",
        "Biologist", "Musician", "Globe trotter", "Interior Designer",
        "Physiotherapist", "Plumber", "Cook", "Computer engineer", "Massage therapist", "Truck driver",
        "Criminologist", "Athlete", "Writer", "Radiation Oncology Technologist", "Hairdresser", "Comedian",
        "Civil engineer", "Actuary", "Pediatrician",
        "Respiratory therapist"
    ])


def generate_profile(user: UserNode, verbose: bool = False):

    gender = random.choices(list(GenderEnum))
    # Birthdate is random between (now - MIN_AGE) years and (now - MIN_AGE - MAX_YEARS)
    date_min = timedelta(days=365 * (MAX_AGE_IN_YEARS - MIN_AGE_IN_YEARS))
    date_max = datetime.now() - timedelta(days=365 * MIN_AGE_IN_YEARS)
    birthdate = random_datetime(date_min, date_max)
    job = random_job()
    biography = f'Hi ! My name is {user.first_name}, im {job.lower()}.\n{lorem.paragraph()}'

    try:
        profile_node = ProfileNode(birthdate=birthdate.date(),
                                   biography=biography,
                                   job=job,
                                   gender=gender
                                   ).save()
        user.profile.connect(profile_node)
    except Exception as e:
        print(f'ERROR: {e}')
    if verbose:
        print(f'-> {user.username}')
        print(f'    gender: {gender}, birthdate: {birthdate}')
        print(f'    bio: {biography.split(chr(10))[0]}')
