import subprocess, requests, zipfile, sys, io, os, re

# Based on https://ahmednagi.com/crack-intelephense/

INTELEPHENSE_PATH = "node_modules/intelephense/lib/intelephense.js"


def patch_intelephense():
    with open(INTELEPHENSE_PATH, mode="r", encoding="utf-8") as f:
        content = f.read()
        content = re.sub(r"isActive\(\){.*?}", "isActive(){return true;}", content)
        content = re.sub(r"isRevoked\(\){.*?}", "isRevoked(){return false;}", content)
        content = re.sub(r"isExpired\(\){.*?}", "isExpired(){return false;}", content)
    return content


def get_latest_release():
    with requests.get(
        "https://api.github.com/repos/bmewburn/vscode-intelephense/releases"
    ) as r:
        asset_url: str = r.json()[0]["assets"][0]["browser_download_url"]

    with requests.get(asset_url, stream=True) as r:
        return os.path.basename(asset_url), io.BytesIO(r.content)


def main():
    if os.path.basename(os.getcwd()) == "_patch":
        os.chdir("..")

    subprocess.run(
        "npm install",
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        shell=True,
    )

    subprocess.run(
        "npm run production",
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        shell=True,
    )

    try:
        os.mkdir("dist")
    except FileExistsError:
        pass

    latest_release = get_latest_release()
    with zipfile.ZipFile(
        "dist/" + latest_release[0], "w", zipfile.ZIP_DEFLATED
    ) as z, zipfile.ZipFile(latest_release[1], "r") as base:
        for file in base.namelist():
            if file == "extension/lib/extension.js":
                z.write(
                    "lib/extension.js",
                    "extension/lib/extension.js",
                )
            elif file == "extension/" + INTELEPHENSE_PATH:
                z.writestr(file, patch_intelephense())
            else:
                z.writestr(file, base.open(file).read())


if __name__ == "__main__":
    main()
