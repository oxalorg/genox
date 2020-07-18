from setuptools import setup


with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="genox",
    version="0.2",
    description="genox - extremely simple static site generator",
    license="MIT",
    long_description=long_description,
    author="oxalorg",
    author_email="mitesh@oxal.org",
    py_modules=["genox"],
    entry_points="""
        [console_scripts]
        genox=genox:cli
    """,
    install_requires=["markdown2", "pyyaml", "jinja2"],
)