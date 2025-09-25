import requests
import json

import pandas as pd

from typing import Any

base_url = "https://canvas.ualberta.ca/"
access_token = "..."

course_id = 28424
assignment_id = 646756
rubrics_id = 9732
rubrics_association_id = 21951
user_id = 121189

course_id_800 = 28424
course_id_801 = 28425


def pagination(url: str | None, headers: dict[str, str], params: dict[str, Any]) -> list[dict[str, Any]]:
    '''
    handles pagination for canvas api
    '''
    all_data: list[dict[str, Any]] = []
    while url:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            all_data.extend(data)

            # Get the next page URL from Link header
            link_header = response.headers.get('Link', '')
            url = None
            
            # Parse Link header for 'next' relation
            for link in link_header.split(','):
                if 'rel="next"' in link:
                    url = link.split(';')[0].strip('<> ')
                    # note: need to keep the access token in params for next requests
                    # not sure if the rest of the params need to be kept.
                    # I'll just keep the params for now.
                    break
        else:
            print(f"Error: {response.status_code}")
            break
    
    return all_data

def normal_request_list(url: str, headers: dict[str, str], params: dict[str, Any]) -> list[dict[str, Any]]:
    print(f"Fetching: {url}")
    response = requests.get(url,
                            headers=headers,
                            params=params
                        )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return []

def normal_request_dict(url: str, headers: dict[str, str], params: dict[str, Any]) -> dict[str, Any]:
    print(f"Fetching: {url}")
    response = requests.get(url,
                            headers=headers,
                            params=params
                        )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return {}


def list_your_courses() -> list[dict[str, Any]]:
    '''
    Gets all courses for the user using the Canvas API.
    https://developerdocs.instructure.com/services/canvas/resources/courses#method.courses.index
    '''
    url = f"{base_url}/api/v1/courses"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": access_token}
    return pagination(url, headers, params)

def get_peer_reviews(course_id: int, assignment_id: int) -> list[dict[str, Any]]:
    '''
    Gets all peer reviews for an assignment in a course.
    https://developerdocs.instructure.com/services/canvas/resources/peer_reviews#method.peer_reviews_api.index
    '''
    url = f"{base_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/peer_reviews"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": access_token}
    return normal_request_list(url, headers, params)

def list_rubrics(course_id: int) -> list[dict[str, Any]]:
    '''
    Lists all rubrics in a course.
    Rubrics are the grading criteria objects that can be associated with assignments.
    https://developerdocs.instructure.com/services/canvas/resources/rubrics#method.rubrics_api.index
    '''
    url = f"{base_url}/api/v1/courses/{course_id}/rubrics"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": access_token}
    return pagination(url, headers, params)

def get_rubric(course_id: int, rubrics_id: int) -> dict[str, Any]:
    '''
    Gets a single rubric by its ID.
    In addition, also returns the assessments made with this rubric,
    like the scores and comments made during peer reviews.
    https://developerdocs.instructure.com/services/canvas/resources/rubrics#method.rubrics_api.show
    '''
    url = f"{base_url}/api/v1/courses/{course_id}/rubrics/{rubrics_id}"
    headers = {"Content-Type": "application/json"}
    params: dict[str, Any] = {
        "access_token": access_token,
        "include": ["assessments"],
        #"style": "comments_only"
    }
    response = requests.get(url,
                            headers=headers,
                            params=params
                        )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return {}

def get_user_in_course_by_userid(course_id: int, user_id: int) -> dict[str, Any]:
    '''
    Gets a user in a course by their user_id.
    The Canvas API returns all the users on the same page as the user with the given user_id,
    hence we need to filter the results to get the user we want.
    https://developerdocs.instructure.com/services/canvas/resources/courses#method.courses.users
    '''
    url = f"{base_url}/api/v1/courses/{course_id}/users"
    headers = {"Content-Type": "application/json"}
    params: dict[str, Any] = {
        "access_token": access_token,
        "user_id": user_id
    }
    users = normal_request_list(url, headers, params)
    users = [user for user in users if user["id"] == user_id]
    return users[0] if users else {}

def get_users_in_course(course_id: int) -> list[dict[str, Any]]:
    '''
    Gets all users in a course.
    Users can be seen at https://canvas.ualberta.ca/courses/[course id]/users/[user id]
    https://developerdocs.instructure.com/services/canvas/resources/courses#method.courses.users
    '''
    url = f"{base_url}/api/v1/courses/{course_id}/users"
    headers = {"Content-Type": "application/json"}
    params: dict[str, Any] = {
        "access_token": access_token,
    }
    return pagination(url, headers, params)

def get_assignments_for_user(course_id: int, user_id: int) -> list[dict[str, Any]]:
    '''
    Gets all assignments for a user in a course.
    Basically gets all assignments in a course, not submissions which I was looking for.
    https://developerdocs.instructure.com/services/canvas/resources/assignments#method.assignments_api.user_index
    '''
    url = f"{base_url}/api/v1/users/{user_id}/courses/{course_id}/assignments"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": access_token}
    return normal_request_list(url, headers, params)

def get_assignment(course_id: int, assignment_id: int) -> dict[str, Any]:
    '''
    Gets a single assignment by its ID.
    https://developerdocs.instructure.com/services/canvas/resources/assignments#method.assignments_api.show
    '''
    url = f"{base_url}/api/v1/courses/{course_id}/assignments/{assignment_id}"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": access_token}
    return normal_request_dict(url, headers, params)

def list_assignment_submissions(course_id: int, assignment_id: int) -> list[dict[str, Any]]:
    '''
    Gets all submissions for an assignment in a course.
    Submissions can be seen at https://canvas.ualberta.ca/courses/[course id]/assignments/[assignment id]/submissions/[submission id]
    https://developerdocs.instructure.com/services/canvas/resources/submissions#method.submissions_api.index
    '''
    url = f"{base_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions"
    headers = {"Content-Type": "application/json"}
    params = {
        "access_token": access_token,
        #"include": ["rubric_assessment"],
        #"grouped": True
    }
    return pagination(url, headers, params)


# print(response.status_code)
# print(type(response.json()))
# print(len(response.json()))
# #print(json.dumps(response.json(), indent=4))
# print(response.json().keys())
# print(len(response.json()["assessments"]))
# print(json.dumps(response.json()["assessments"][0], indent=4))

def test():
    rubric = get_rubric(course_id, rubrics_id)
    assessments = rubric["assessments"]

    num_total_assessments = len(assessments)

    filtered_assessments = [
        assessment for assessment in assessments 
        if assessment["rubric_association_id"] == rubrics_association_id
    ]

    num_filtered_assessments = len(filtered_assessments)

    print(f"Found {num_filtered_assessments} assessments with rubric_association_id {rubrics_association_id} out of {num_total_assessments} total assessments.")

    score_total = 0
    total = 0
    for assessment in filtered_assessments:
        score_total += assessment["score"]
        total += 1

    print(f"Average score: {score_total/total if total > 0 else 0:.2f} ({score_total}/{total})")

    print(json.dumps(filtered_assessments[:3], indent=4))

def test2():
    a = list_assignment_submissions(course_id, assignment_id)
    print(f"Found {len(a)} submissions for assignment {assignment_id} in course {course_id}.")
    print(json.dumps(a[:1], indent=4))

def get_all_users(course_id: int) -> pd.DataFrame:
    '''
    Gets all users in a course and returns a DataFrame with their name, student_id, canvas_id, and ccid.
    '''
    users = get_users_in_course(course_id)
    print(f"Found {len(users)} users in course {course_id}.")
    #print(json.dumps(users[0], indent=4))

    canvas_id: list[int] = []
    names: list[str] = []
    student_ids: list[int] = []
    ccids: list[str] = []
    for user in users:
        canvas_id.append(user["id"])
        names.append(user["name"])
        student_ids.append(user["sis_user_id"])
        email: str = user["email"]
        ccids.append(email.split("@")[0]) # email is in the format ccid@ualberta.ca
    
    # Create DataFrame from the three lists
    df = pd.DataFrame({
        'canvas_id': canvas_id,
        'name': names,
        'student_id': student_ids,
        'ccid': ccids
    })
    
    print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns.")
    print(df.head())
    
    return df

def get_all_submissions(course_id: int, assignment_id: int, users_df: pd.DataFrame) -> pd.DataFrame:
    '''
    Gets all submissions for the assignment in the course.
    '''
    # get the assignment's due date
    assignment = get_assignment(course_id, assignment_id)
    due_date = assignment["due_at"]
    print(f"Assignment: {assignment['name']} (ID: {assignment['id']})")
    print(f"Due at: {assignment['due_at']}")
    #print(json.dumps(assignment, indent=4))

    # get all submissions for the assignment
    submissions = list_assignment_submissions(course_id, assignment_id)
    print(f"Found {len(submissions)} submissions for assignment {assignment_id} in course {course_id}.")
    #print(json.dumps(submissions[0], indent=4))

    '''
    Interested in:
    id
    submitted_at -> convert to hours late
    user_id -> convert to student_id
    workflow_state
    attempt
    '''

    return

    student_ids: list[int] = []
    submission_ids: list[int] = []
    scores: list[float | None] = []
    for submission in submissions:
        student_ids.append(submission["user_id"])
        submission_ids.append(submission["id"])
        scores.append(submission["score"])
    
    # Create DataFrame from the three lists
    df = pd.DataFrame({
        'student_id': student_ids,
        'submission_id': submission_ids,
        'score': scores
    })
    
    print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns.")
    print(df.head())
    
    return df

get_all_submissions(course_id, assignment_id, None)