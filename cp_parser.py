import sublime
import sublime_plugin
import urllib.request
import os
import re
import json
from bs4 import BeautifulSoup

# Constants
LAST_URL = ''


def get_codeforces_dir(settings):
    parent_dir = settings.get('CODEFORCES_DIR', '.')
    return os.path.join(parent_dir)


def get_codechef_dir(settings):
    parent_dir = settings.get('CODECHEF_DIR', '.')
    return os.path.join(parent_dir)


def get_extension(settings):
    return settings.get('EXTENSION', '')

# Function to create a file based on given parameters


def create_file(parent_dir, title, extension, testcases, contest):
    try:
        # Ensure the given directory exists or create it
        os.makedirs(parent_dir, mode=0o777, exist_ok=True)
        filename = os.path.join(parent_dir, title + contest + '.' + extension)
        open(filename, 'a').close()

        # Write test cases to a separate file
        input_file = filename + ':tests'
        with open(input_file, 'w') as file:
            json.dump(testcases, file, indent=4)
        sublime.status_message('File created successfully: ' + filename)
        return filename
    except Exception as e:
        print('Exception: ', e)
        sublime.error_message('Exception: File not created - ' + str(e))
        return None

# Parse content from Codeforces URL


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
            testcases = [{'test': testcase.get_text(
                separator='\n', strip=True)} for testcase in testcases_elements]
            all_testcases.extend(testcases)
        return [title, all_testcases]
    except Exception as e:
        print(e)
        sublime.error_message('Unable to parse: ' + url)
        return None

# Generate CodeChef API URL


def generate_codechef_api_url(url):
    try:
        parts = url.split('/')
        problem_index = parts.index('problems')
        contest_code = parts[problem_index - 1]
        problem_code = parts[problem_index + 1]
        if (contest_code == 'www.codechef.com'):
            contest_code = 'PRACTICE'
        api_url = 'https://www.codechef.com/api/contests/' + \
            str(contest_code) + '/problems/' + str(problem_code)
        return api_url
    except Exception as e:
        return None

# Parse content from CodeChef URL


def parse_content_codechef(url):
    global LAST_URL
    LAST_URL = url
    try:
        request = urllib.request.Request(
            generate_codechef_api_url(url), headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
        page = response.read()
        json_data = json.loads(page.decode('utf8'))
        sample_test_cases = json_data.get(
            'problemComponents', {}).get('sampleTestCases', [])
        all_testcases = []
        for test_case in sample_test_cases:
            input_data = test_case.get('input').replace("\r\n", "\n")
            all_testcases.append({
                'test': input_data
            })
        title = json_data.get('problem_code')
        return [title, all_testcases]
    except Exception as e:
        print(e)
        sublime.error_message('Unable to parse: ' + url)
        return None

# Main parse function handling URL parsing and file creation


def parse(self, url):
    if url is None or url.strip() == '':
        sublime.error_message('Please enter a URL')
        return
    contest = ''
    content = None
    title = ''
    testcases = []
    parent_dir = ''

    settings = sublime.load_settings('CPParser.sublime-settings')
    extension = get_extension(settings)
    if 'codeforces.com' in url:
        content = parse_content_codeforces(url)
        contest = '_' + str(re.findall(r'\d+', url)
                            [0]) + str(re.findall(r'[A-Z]', url)[0])
        title = content[0]
        testcases = content[1]
        parent_dir = get_codeforces_dir(settings)
        if not parent_dir:
            default_directory = os.path.join(
                sublime.packages_path(),
                'User',
                'CPParser',
                'Codeforces'
            )
            print(default_directory)
            parent_dir = default_directory
    elif 'codechef.com' in url:
        content = parse_content_codechef(url)
        title = content[0]
        testcases = content[1]
        parent_dir = get_codechef_dir(settings)
        if not parent_dir:
            default_directory = os.path.join(
                sublime.packages_path(),
                'User',
                'CPParser',
                'Codechef'
            )
            print(default_directory)
            parent_dir = default_directory
    else:
        sublime.error_message('Unsupported website')
        return

    if content is None:
        return

    file = create_file(parent_dir, title, extension, testcases, contest)
    if file is None:
        return

    snippets_file_name = settings.get('SNIPPETS', None)
    snippets_content = ''
    if snippets_file_name is not None and snippets_file_name.strip() != '':
        try:
            with open(snippets_file_name) as snippets_file:
                snippets_content = snippets_file.readlines()
        except FileNotFoundError as e:
            print('Snippet file not found ', snippets_file_name)
            sublime.error_message('Snippet file not found ' +
                                  snippets_file_name + ' - ' + str(e))
            return

    with open(file, 'w') as newfile:
        newfile.writelines(snippets_content)
    with open(file, 'r') as new_file:
        filedata = new_file.read()
    filedata = filedata.replace('url', LAST_URL)
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
            'Enter program url',
            LAST_URL,
            on_done,
            None,
            None)
