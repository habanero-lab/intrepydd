from setuptools import setup, find_packages

setup(
    name="intrepydd",                  # Name of the package
    version="0.1.9",                    # Version
    author="Tong Zhou",                 # Your name
    author_email="zt9465@gmail.com", # Your email
    description="An implementation of the Intrepydd compiler", # Short description
    long_description=open("README.md").read(), # Long description from README file
    long_description_content_type="text/markdown", # Type of the long description
    url="https://github.com/habanero-lab/intrepydd", # URL of your project repository
    packages=find_packages(),           # Automatically find the packages in your project
    classifiers=[
        "Programming Language :: Python :: 3",  # Classifiers help users find your project
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',            # Minimum Python version requirement
)
