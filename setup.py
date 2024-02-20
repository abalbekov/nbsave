from setuptools import setup

setup(
    name="nbsave",
    version="1.2",
    description='custom nbconvert templates and exporters to save a notebook as either execution evidence or as instructions',
    author='A.Balbekov',
    author_email='albert.y.balbekov@gmail.com',
    packages=['nbsave','custom_exporter'],
    install_requires=["nbconvert","nbformat","traitlets"],
    data_files=[ ( 'share/jupyter/nbconvert/templates/custom_template', ['custom_template/conf.json','custom_template/index.html.j2'] ) ],
    license_file='LICENSE'
)
