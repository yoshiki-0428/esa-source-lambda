import json
import datetime
import os
import hmac
import hashlib

from github import Github
from github import InputGitTreeElement

token = os.environ.get("GITHUB_TOKEN")
repository = os.environ.get("GITHUB_REPOSITORY")
branch_name = os.environ.get("BRANCH_NAME")
commit_dir = os.environ.get("COMMIT_DIR")
esa_secret_key = os.environ.get("ESA_SECRET_KEY").encode('utf-8')


def main(event, context):
    esa_data = json.loads(event['body'])

    # Validation
    if validate_request(event):
        print("Unauthorized request")
        return {
            "statusCode": 401,
            "body": "Unauthorized request"
        }
    elif 'Templates' in esa_data['post']['name']:
        print("Do not need Commit cause type is template")
        return {
            "statusCode": 204,
            "body": "Do not need Commit cause type is template"
        }
    elif bool(esa_data['post']['wip']):
        print("Do not need Commit cause status is wip")
        return {
            "statusCode": 204,
            "body": "Do not need Commit cause status is wip"
        }

    # find file & file commitment
    md_text = esa_data['post']['body_md']
    if esa_data['kind'] == "post_create":
        print("post_create")
        md_name = create_today_filename(esa_data['post']['number'])
        commit_file(md_name, md_text)

    elif esa_data['kind'] == "post_update":
        print("post_update")
        commit_file(find_file_name(esa_data["post"]["number"]), md_text)

    elif esa_data['kind'] == "post_archive":
        print("post_archive")
        # TODO archive

    return {
        "statusCode": 200,
        "body": "Success Git Commit"
    }


# Repository Info
def get_repo():
    repo = Github(token).get_repo(repository)
    refs = repo.get_git_ref(branch_name)
    return {
        "repo": repo,
        "refs": refs
    }


def commit_file(commit_name, commit_file_text):
    if commit_name == "" or commit_file_text == "":
        return
    # Repository Info
    repo_info = get_repo()

    # Commit file (Create)
    element = InputGitTreeElement(commit_dir + "/" + commit_name, '100644', 'base64', commit_file_text)

    # 最新版のCommit情報を取得
    commit = repo_info['repo'].get_commit(repo_info['refs'].object.sha).commit
    base_tree = commit.tree

    # 新しくCommitを作成
    new_tree = repo_info['repo'].create_git_tree([element], base_tree)
    new_commit = repo_info['repo'].create_git_commit("Create Esa Post by Lambda: " + commit_name, new_tree, [commit])
    repo_info['refs'].edit(new_commit.sha)


def find_file_name(esa_number):
    for content in get_repo()['repo'].get_contents(commit_dir + "/"):
        content_name = content.name
        split_content_name = content_name.split("--")
        if str(esa_number) in split_content_name[len(split_content_name) - 1]:
            return content_name
    print("File is None cause create file at today")
    return create_today_filename(esa_number)


def create_today_filename(number):
    return str(datetime.date.today()) + "--" + str(number) + ".md"


# signature check
def validate_request(event):
    payload = event['body']
    size = len(event['headers']['X-Esa-Signature'].split("sha256="))
    esa_signature = event['headers']['X-Esa-Signature'].split("sha256=")[size - 1]
    return not hmac.new(esa_secret_key, payload.encode('utf-8'), hashlib.sha256).hexdigest() == esa_signature
