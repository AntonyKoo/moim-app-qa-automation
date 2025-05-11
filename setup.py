from setuptools import setup, find_packages

setup(
    name="moim_app_qa_automation",
    version="0.1",
    packages=find_packages(include=['utils', 'utils.*']),
    install_requires=[
        'Appium-Python-Client==2.9.0',
        'pytest==7.3.1',
        'pytest-html==3.2.0',
        'google-api-python-client==2.86.0',
        'google-auth-httplib2==0.1.0',
        'google-auth-oauthlib==1.0.0',
        'pillow==9.4.0',
        'python-dotenv'
    ],
) 