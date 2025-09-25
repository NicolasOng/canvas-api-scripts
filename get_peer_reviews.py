import requests
import json
from datetime import datetime
import pytz
import argparse

import pandas as pd

from typing import Any

base_url = "https://canvas.ualberta.ca/"
access_token = "..."

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


def get_all_assessments(course_id: int, rubrics_id: int, rubrics_association_id: int, users_df: pd.DataFrame, submissions_df: pd.DataFrame) -> pd.DataFrame:
    '''
    Gets all assessments for a rubric in a course.
    Then filters the assessments by the rubric_association_id.
    '''
    # get the rubric, along with all the assessments associated with it
    rubric = get_rubric(course_id, rubrics_id)
    assessments = rubric["assessments"]

    # log some stats
    print(f"Found {len(assessments)} total assessments for rubric {rubrics_id} in course {course_id}.")

    num_associated = len([ass for ass in assessments if ass["rubric_association_id"] == rubrics_association_id])
    num_peer_reviews = len([ass for ass in assessments if ass["assessment_type"] == "peer_review"])
    num_submissions = len([ass for ass in assessments if ass["artifact_type"] == "Submission"])

    print(f"Found {num_associated} with the correct association {rubrics_association_id} ({num_associated/len(assessments) if assessments else 0:.2%})")
    print(f"Found {num_peer_reviews} peer reviews ({num_peer_reviews/len(assessments) if assessments else 0:.2%})")
    print(f"Found {num_submissions} assessing submissions ({num_submissions/len(assessments) if assessments else 0:.2%})")

    # filter assessments for the correct association
    assessments = [
        assessment for assessment in assessments 
        if assessment["rubric_association_id"] == rubrics_association_id
    ]

    assessment_ids: list[int] = []
    scores: list[float] = []
    assessed_ids: list[int | None] = []
    assessor_ids: list[int | None] = []
    attempts: list[int] = []
    for assessment in assessments:
        # get the assessment id, score, and attempt number
        assessment_ids.append(assessment["id"])
        scores.append(assessment["score"])
        attempts.append(assessment["artifact_attempt"])
        # convert the assessor id to student id
        assessor_id = assessment["assessor_id"]
        assessor_student_id = get_student_id_by_canvas_id(users_df, assessor_id)
        assessor_ids.append(assessor_student_id)
        if assessor_student_id is None:
            print(f"Warning: Could not find student_id for assessor canvas_id {assessor_id}")
        # convert the artifcact id to student id
        artifact_id = assessment["artifact_id"]
        assessed_student_id = get_student_id_by_submissions_id(submissions_df, artifact_id)
        assessed_ids.append(assessed_student_id)
        if assessed_student_id is None:
            print(f"Warning: Could not find student_id for artifact submission_id {artifact_id}")
    
    # Create DataFrame from the lists
    df = pd.DataFrame({
        'assessment_id': assessment_ids,
        'assessed_student_id': assessed_ids,
        'assessor_student_id': assessor_ids,
        'score': scores,
        'attempt': attempts
    })

    print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns.")
    print(df.head())

    return df

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
    
    # Create DataFrame from the lists
    df = pd.DataFrame({
        'canvas_id': canvas_id,
        'name': names,
        'student_id': student_ids,
        'ccid': ccids
    })
    
    print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns.")
    print(df.head())
    
    return df

def get_student_id_by_canvas_id(users_df: pd.DataFrame, canvas_id: int) -> int | None:
    '''
    Gets the student_id for a given canvas_id from the users DataFrame.
    Returns None if canvas_id is not found.
    '''
    result = users_df[users_df['canvas_id'] == canvas_id]['student_id']
    if len(result) > 0:
        return result.iloc[0]
    else:
        return None

def get_student_id_by_submissions_id(submissions_df: pd.DataFrame, submission_id: int) -> int | None:
    '''
    Gets the student_id for a given submission_id from the submissions DataFrame.
    Returns None if submission_id is not found.
    '''
    result = submissions_df[submissions_df['submission_id'] == submission_id]['student_id']
    if len(result) > 0:
        return result.iloc[0]
    else:
        return None

def get_all_submissions(course_id: int, assignment_id: int, users_df: pd.DataFrame) -> pd.DataFrame:
    '''
    Gets all submissions for the assignment in the course.
    '''
    # get the assignment's due date
    assignment = get_assignment(course_id, assignment_id)
    due_date_str = assignment["due_at"]
    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
    print(f"Assignment: {assignment['name']} (ID: {assignment['id']})")
    print(f"Due at: {assignment['due_at']}")
    #print(json.dumps(assignment, indent=4))

    # get all submissions for the assignment
    submissions = list_assignment_submissions(course_id, assignment_id)
    print(f"Found {len(submissions)} submissions for assignment {assignment_id} in course {course_id}.")
    #print(json.dumps(submissions[0], indent=4))

    submission_ids: list[int] = []
    submitted_ats: list[str | None] = []
    hours_late: list[float] = []
    student_ids: list[int | None] = []
    status: list[str] = []
    attempts: list[int] = []
    for submission in submissions:
        # get submission id, status, and attempt number
        submission_ids.append(submission["id"])
        status.append(submission["workflow_state"])
        attempts.append(submission["attempt"])
        # get and convert the submitted_at to a timestamp,
        # and calculate hours late
        submitted_at_str: str | None = submission["submitted_at"]
        if submitted_at_str:
            # get the submit time (in UTC from Canvas)
            submitted_at = datetime.fromisoformat(submitted_at_str.replace('Z', '+00:00'))
            # convert to Mountain Time for display
            mountain_tz = pytz.timezone('America/Edmonton')
            submitted_at_mountain_tz = submitted_at.astimezone(mountain_tz)
            submitted_at_fstr = submitted_at_mountain_tz.strftime("%Y-%m-%d %H:%M:%S %Z")
            submitted_ats.append(submitted_at_fstr)
            hours_late.append((submitted_at - due_date).total_seconds() / 3600.0)
        else:
            submitted_ats.append(None)
            hours_late.append(0.0) # not submitted, so not late
        # get the user id and convert to student_id
        student_id = get_student_id_by_canvas_id(users_df, submission["user_id"])
        student_ids.append(student_id)
        if student_id is None:
            print(f"Warning: Could not find student_id for canvas_id {submission['user_id']}")

    # Create DataFrame from the lists
    df = pd.DataFrame({
        'submission_id': submission_ids,
        'student_id': student_ids,
        'submitted_at': submitted_ats,
        'hours_late': hours_late,
        'status': status,
        'attempt': attempts
    })
    
    print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns.")
    print(df.head())
    
    return df

def get_and_save_peer_review_data(course_id: int, assignment_id: int, rubrics_id: int, rubrics_association_id: int) -> None:
    '''
    Gets all users, submissions, and assessments for the given course and assignment,
    and saves them to CSV files.
    '''
    user_df = get_all_users(course_id)
    submissions_df = get_all_submissions(course_id, assignment_id, user_df)
    assessments_df = get_all_assessments(course_id, rubrics_id, rubrics_association_id, user_df, submissions_df)

    user_df.to_csv('users.csv', index=False)
    submissions_df.to_csv('submissions.csv', index=False)
    assessments_df.to_csv('assessments.csv', index=False)

    print("DataFrames saved to CSV files:")
    print("- users.csv")
    print("- submissions.csv") 
    print("- assessments.csv")

def parse_arguments():
    '''
    Define and parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description="Extract peer review data from Canvas"
    )
    parser.add_argument('-c', '--course-id', type=int, default=28424, help='Canvas course ID')
    parser.add_argument('-a', '--assignment-id', type=int, default=646756, help='Canvas assignment ID')
    parser.add_argument('-r', '--rubrics-id', type=int, default=9732, help='Canvas rubrics ID')
    parser.add_argument('-ra', '--rubrics-association-id', type=int, default=21951, help='Canvas rubrics association ID')
    parser.add_argument('-at', '--access-token', type=str, default=access_token, help='Canvas API access token')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    access_token = args.access_token
    get_and_save_peer_review_data(args.course_id, args.assignment_id, args.rubrics_id, args.rubrics_association_id)
