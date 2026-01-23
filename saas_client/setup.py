from setuptools import setup, find_packages

setup(
    name="interview-assistant-pro",
    version="1.0.0",
    description="AI-powered interview assistant",
    author="Your Name",
    py_modules=["interview_client"],
    install_requires=[
        "httpx>=0.27.0",
    ],
    entry_points={
        "console_scripts": [
            "interview-assistant=interview_client:main",
        ],
    },
    python_requires=">=3.8",
)
