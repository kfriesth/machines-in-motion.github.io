#! /usr/bin/python
from os import path, mkdir, walk
import re
import shutil
import treep.treep_git
import treep.files
import rospkg
from bs4 import BeautifulSoup
import re


def get_ros_install_share_path():
    """
    Use rospack to get the path to the installation folder (supposed sourced)
    """
    ros_pack = rospkg.RosPack()
    if "shared_memory" in ros_pack.list():
        return path.dirname(ros_pack.get_path("shared_memory"))
    else:
        raise Exception('The shared_memory is not part of the cloned packages')
    return 


def copy_doc_package(package_name, share_path):
    """
    Copy/Replace the documentation of the ros package in this repository.
    """
    share_path = get_ros_install_share_path()
    local_doc = path.join("code_documentation", package_name)
    local_doc_html = path.join(share_path, package_name, "doc", "html")
    
    if not path.isdir(local_doc_html):
        print ("WARNING: cannot find the documentation for the package [",
               package_name,
               "]. Nothing to be done")
        return

    if path.isdir(local_doc):
        shutil.rmtree(local_doc)
    
    shutil.copytree(local_doc_html, local_doc)
    return


def find_ros_packages(share_path):
    """
    Find the ros packages cloned from the machines-in-motion github organisation
    """
    treep_projects = treep.files.read_configuration_files(share_path)
    repos_names = treep_projects.get_repos_names()

    packages_list = []
    for repos_name in repos_names:
        repos_path = treep_projects.get_repo_path(repos_name)
        repos_url = treep.treep_git.get_url(repos_path)
        if repos_url and "machines-in-motion" in repos_url:
            for root, _, files in walk(repos_path):
                for file in files:
                    if file == "package.xml":
                        packages_list.append(path.basename(root))
    
    return packages_list


def update_index_html(exported_doc_list, exported_code_cov_list):
    """
    Parse the index_template.html and 
    """
    with open("index_template.html") as fp:
        soup = BeautifulSoup(fp, features="lxml")

    pkg_tag_ul = soup.find(id="list_documentation")
    for doc_folder in exported_doc_list:
        string_href = (
          "https://machines-in-motion.github.io/code_documentation/" +
          doc_folder + "/"
        )
        string_displayed = doc_folder

        pkg_tag_li = soup.new_tag("li")
        pkg_tag_ul.append(pkg_tag_li)

        pkg_tag_a = soup.new_tag("a", href=string_href)
        pkg_tag_a.string = string_displayed
        pkg_tag_li.append(pkg_tag_a)

    pkg_tag_ul = soup.find(id="list_code_coverage")
    for code_cov_folder in exported_code_cov_list:
        string_href = (
          "https://machines-in-motion.github.io/code_coverage/" +
          code_cov_folder + "/"
        )
        string_displayed = code_cov_folder

        pkg_tag_li = soup.new_tag("li")
        pkg_tag_ul.append(pkg_tag_li)

        pkg_tag_a = soup.new_tag("a", href=string_href)
        pkg_tag_a.string = string_displayed
        pkg_tag_li.append(pkg_tag_a)
    
    with open("index.html", 'w') as fp:
        fp.write(soup.prettify())


if __name__ == "__main__":
    # First we get the path to the catkin install share folder
    share_path = get_ros_install_share_path()
    print("The path to the installation folder")
    print(share_path)

    # Then we find all the catkin package wich are in the machines-in-motion url
    packages_list = find_ros_packages(share_path)
    print("The list of the cloned catkin package from the machines-in-motion github")
    print (packages_list)

    # We copy the built documentation inside this repository
    for package in packages_list:
        copy_doc_package(package, share_path)

    # We get all the package names form which the documentation is available
    exported_doc_list = []
    (_, exported_doc_list, _) = walk("code_documentation").next()
    print("The list of all the available documentation yet")
    print (exported_doc_list)

    # We get all the code coverage computed from the bamboo agents
    exported_code_cov_list = []
    (_, exported_code_cov_list, _) = walk("code_coverage").next()
    print("The list of all the available documentation yet")
    print (exported_code_cov_list)

    # We update the list in the website
    update_index_html(exported_doc_list, exported_code_cov_list)
