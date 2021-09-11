from collections import defaultdict
from pathlib import Path
from warnings import warn

import pymbe.api as pm
from pymbe.client import APIClient


PYMBE_ROOT = Path(pm.__file__).parent
FIXTURES = (PYMBE_ROOT / "../../tests/fixtures").resolve()


def get_latest_by_name(client: APIClient):
    projects = defaultdict(list)

    for id_, data in client.projects.items():
        projects[data["name"]] += [id_]

    for project_name, project_ids in projects.items():
        if len(project_ids) == 1:
            projects[project_name] = project_ids[0]
            continue
        created_map = [
            (client.projects[project_id]["created"], project_id) for project_id in project_ids
        ]
        projects[project_name] = sorted(created_map)[-1][1]
    return dict(projects)


def download_all_projects(url: str, port: int = 9000):
    client = APIClient(host_url=url, host_port=port)

    for project_name, project_id in get_latest_by_name(client).items():
        try:
            print(f"Retrieving '{project_name}'")
            client.selected_project = project_id
            model = client.get_model()

            print(f" > Saving {project_name}")
            model.save_to_file(FIXTURES / project_name)
            print(f" > Successfully Downloaded '{project_name}'")
        except Exception as exc:  # pylint: disable=broad-except
            warn(f">>> Could not download '{project_name}'\n{exc}")


if __name__ == "__main__":
    download_all_projects(url="http://sysml2-sst.intercax.com")
