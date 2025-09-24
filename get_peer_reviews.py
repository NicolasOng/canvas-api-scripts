import requests
import json

base_url = "https://canvas.ualberta.ca/"
courses_endpoint = "api/v1/courses"
access_token = ""

course_id = 28424
assignment_id = 646756
peer_reviews_endpoint = f"/api/v1/courses/{course_id}/assignments/{assignment_id}/peer_reviews"


rubrics_id = 9732
rubrics_association_id = 21951

user_id = 121189

headers = {
    "Content-Type": "application/json"
}
params = {
    "access_token": access_token,
    "include": ["assessments"],
    "style": "comments_only"
}

def pagination(url: str, headers: dict, params: dict) -> list:
    '''
    handles pagination for canvas api
    '''
    all_data = []
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

def normal_request_list(url: str, headers: dict, params: dict) -> list:
    response = requests.get(url,
                            headers=headers,
                            params=params
                        )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return []

def normal_request_dict(url: str, headers: dict, params: dict) -> dict:
    response = requests.get(url,
                            headers=headers,
                            params=params
                        )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return {}


def list_rubrics(course_id: int) -> list:
    url = f"{base_url}/api/v1/courses/{course_id}/rubrics"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": access_token}
    return pagination(url, headers, params)

def get_rubric(course_id: int, rubrics_id: int) -> dict:
    url = f"{base_url}/api/v1/courses/{course_id}/rubrics/{rubrics_id}"
    headers = {"Content-Type": "application/json"}
    params = {
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

def get_users_in_course_by_userid(course_id: int, user_id: int) -> list:
    '''
    Gets a users in a course by their user_id.
    The Canvas API returns all the users on the same page as the user with the given user_id,
    hence we need to filter the results to get the user we want.
    '''
    url = f"{base_url}/api/v1/courses/{course_id}/users"
    headers = {"Content-Type": "application/json"}
    params = {
        "access_token": access_token,
        "user_id": user_id
    }
    users = normal_request_list(url, headers, params)
    users = [user for user in users if user["id"] == user_id]
    return users[0] if users else {}

def get_assignments_for_user(course_id: int, user_id: int) -> list:
    url = f"{base_url}/api/v1/users/{user_id}/courses/{course_id}/assignments"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": access_token}
    return normal_request_list(url, headers, params)

def list_assignment_submissions(course_id: int, assignment_id: int) -> list:
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

a = list_assignment_submissions(course_id, assignment_id)
print(f"Found {len(a)} submissions for assignment {assignment_id} in course {course_id}.")
print(json.dumps(a[:1], indent=4))