from jwt import JWT, jwk_from_pem
import time


# generate a jwt token for your app
def get_jwt_token(pem, app_id):
    # Open PEM
    with open(pem, 'rb') as pem_file:
        signing_key = jwk_from_pem(pem_file.read())

    payload = {
        # Issued at time
        'iat': int(time.time()),
        # JWT expiration time (10 minutes maximum)
        'exp': int(time.time()) + 600,
        # GitHub App's identifier
        'iss': app_id
    }
    # Create JWT
    jwt_instance = JWT()
    return jwt_instance.encode(payload, signing_key, alg='RS256')


# use the jwt token to get token for your app installation. Note: You require installation id
def get_token(token, installation_id):
    import requests
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    response = requests.post(url, headers=headers)
    # Check if the request was successful
    if response.status_code == 200 or 201:
        # Convert the response to JSON and print it
        data = response.json()
        print(data)
        return data['token']
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None


# pass in the repo name, owner name and access token
def clone_repo(token, owner, repo):
    import subprocess
    # Construct the clone URL with the token
    clone_url = f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"

    # Specify the directory to clone the repo into. Adjust as necessary.
    # For example, './my_repo' will clone the repo into a directory named 'my_repo' in the current working directory.
    target_dir = "./my_repo"

    try:
        # Run the git clone command
        subprocess.run(["git", "clone", clone_url, target_dir], check=True)
        print(f"Repository '{owner}/{repo}' successfully cloned into '{target_dir}'")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")


def get_installation_ids(jwt_token):
    import requests
    url = 'https://api.github.com/app/installations'
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github+json'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        installations = response.json()
        # Extracting the installation IDs
        installation_ids = [installation['id'] for installation in installations]
        return installation_ids
    else:
        print("Failed to retrieve installations")
        print(f"Status Code: {response.status_code}, Response: {response.text}")
        return []


def get_repositories_and_owners(access_token, installation_id):
    import requests
    url = 'https://api.github.com/installation/repositories'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    try:
        # Make a GET request to the GitHub API to get the list of repositories
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX or 5XX
        data = response.json()

        # Extracting repositories and their owner details
        repositories = data.get('repositories', [])
        if len(repositories) > 0:
            return [[repo['html_url'], installation_id] for repo in repositories]
    except:
        pass
    #     for repo in repositories:
    #         print(f"Repository Name: {repo['name']}")
    #         print(f"Owner Login: {repo['owner']['login']}")
    #         print('-' * 60)
    #     if len(repositories) == 0:
    #         print("no repositories found!")
    #     return repositories[0]['owner']['login'], repositories[0]['name']
    # except requests.RequestException as e:
    #     print(f"An error occurred: {e}")
    return []


# replace with armor code GitHub app-id and private_key file path
app_id = "104142" #104142 qa, 89048 dev
private_key = "privatekey.pem"

# Step 1: Get a jwt access token for your app
jwt_token = get_jwt_token(private_key, app_id)
print(jwt_token)
# Step 2: get installation ids for the client.
ids = get_installation_ids(jwt_token)

urls = []
count = 0
for id in ids:
    # Step 3: get an access token for the particular installation.
    app_installation_access_token = get_token(jwt_token, installation_id=id)
    # Step 4: Get owner and repo name you want to clone.
    urls = urls + get_repositories_and_owners(app_installation_access_token, id)
    count += 1
    if count > 0:
        pass

# Step 5: Clone
print(urls)
