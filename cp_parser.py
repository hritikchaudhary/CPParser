import sublime
import sublime_plugin
import urllib.request
import os
import re
import json
from bs4 import BeautifulSoup

LAST_URL = ''
SUPPORTED_WEBSITES = ['codeforces.com']


def is_supported_website(url):
    for site in SUPPORTED_WEBSITES:
        if site in url:
            return True
    return False


def load_settings():
    return sublime.load_settings('CPParser.sublime-settings')


def get_parent_dir(settings):
    parent_dir = settings.get('PARENT_DIR', '.')
    return os.path.join(parent_dir)


def get_extension(settings):
    return settings.get('EXTENSION', '')


def create_file(parent_dir, title, extension, testcases):
    try:
        os.makedirs(parent_dir, mode=0o777, exist_ok=True)
        filename = os.path.join(parent_dir, title + "_" + str(re.findall(r'\d+', LAST_URL)[
                                0]) + str(re.findall(r'[A-Z]', LAST_URL)[0]) + '.' + extension)
        open(filename, "a").close()
        input_file = filename + ':tests'
        with open(input_file, 'w') as file:
            json.dump(testcases, file, indent=4)
        sublime.status_message("File created successfully: " + filename)
        return filename
    except Exception as e:
        print("Exception: ", e)
        sublime.error_message("Exception: File not created - " + str(e))
        return None


def parse_content_codeforces(url):
    global LAST_URL
    LAST_URL = url
    request = urllib.request.Request(
        url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(request)
        page = response.read()
        parsed_content = BeautifulSoup(page, 'html.parser')

        title = parsed_content.find('div', attrs={
                                    'class': 'problem-statement'}).find('div', attrs={'class': 'title'}).text[2:].strip()
        title = re.sub(r'[^\w]+', '_', title)

        input_parents = parsed_content.find_all('div', class_='input')

        all_testcases = []
        for input_parent in input_parents:
            testcases_elements = input_parent.find_all('pre')
            testcases = [{"test": testcase.get_text(
                separator='\n', strip=True)} for testcase in testcases_elements]
            all_testcases.extend(testcases)
        return [title, all_testcases]
    except Exception as e:
        print(e)
        sublime.error_message("Unable to parse: " + url)
        return None


def parse(self, url):
    if url is None or url.strip() == '':
        return

    if not is_supported_website(url):
        sublime.error_message("Unsupported website")
        return

    content = parse_content_codeforces(url)
    if content is None:
        return

    title = content[0]
    testcases = content[1]
    settings = load_settings()
    parent_dir = get_parent_dir(settings)
    extension = get_extension(settings)
    file = create_file(parent_dir, title, extension, testcases)

    if file is None:
        return

    snippets_file_name = settings.get('SNIPPETS', None)
    snippets_content = ''
    if snippets_file_name is not None:
        try:
            with open(snippets_file_name) as snippets_file:
                snippets_content = snippets_file.readlines()
        except FileNotFoundError as e:
            print("File not found ", snippets_file_name)
            sublime.error_message("File not found " +
                                  snippets_file_name + " - " + str(e))
            return

    with open(file, 'w') as newfile:
        newfile.writelines(snippets_content)
    with open(file, 'r') as new_file:
        filedata = new_file.read()
    filedata = filedata.replace("url", LAST_URL)
    with open(file, 'w') as new_file:
        new_file.write(filedata)
    return file


class CpProblemCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(url):
            result = parse(self, url)
            if result:
                self.view.window().open_file(result)

        sublime.active_window().show_input_panel(
            "Enter program url",
            LAST_URL,
            on_done,
            None,
            None)
