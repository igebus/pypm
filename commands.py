from utils import datautils
from database_example import *

def paths_to_nodes(nodes_paths):
    nodes = []
    for node_path in nodes_paths:
        node = root[node_path]
        nodes.append((node, node_path if node is None else node.get_path()))
    return nodes


def ls(nodes, recursive):
    nodes = paths_to_nodes(nodes)

    def _ls_helper(nodes, recursive, level):
        result = ""
        log = ""
        for node, node_path in nodes:
            if isinstance(node, datautils.Entry):
                result += "{}{}\n".format("  " * level, node.get_name())
            elif isinstance(node, datautils.Group) and not (recursive or level == 0):
                result += "{}\033[94m{}/\033[0m\n".format("  " * level, node.get_name())
            elif isinstance(node, datautils.Group) and (recursive or level == 0):
                result += "{}\033[94m{}/\033[0m\n".format("  " * level, node.get_name())
                for subnode in node:
                    subresult, sublog = _ls_helper([(subnode, subnode.get_path())], recursive, level + 1)
                    result += subresult
                    log += sublog
            else:
                log += "[-] Node {} does not exist\n".format(node_path)
        return result, log

    results, log = _ls_helper(nodes, recursive, 0)

    if not len(log):
        return results
    elif not len(results):
        return log
    else:
        return results + "\n" + log


def cat(nodes_paths, recursive):
    nodes = paths_to_nodes(nodes_paths)

    def _cat_helper(nodes, recursive, level):
        log = ""
        result = ""
        for node, node_path in nodes:
            if isinstance(node, datautils.Entry):
                result += "  " * level + node.get_name() + ":\n"
                result += "  " * level + "  Username: " + node.get_username() + "\n"
                result += "  " * level + "  Password: " + node.get_password() + "\n"
                result += "  " * level + "  Url: " + node.get_url() + "\n"
                result += "  " * level + "  Comment: " + node.get_comment() + "\n"
            elif isinstance(node, datautils.Group) and not (recursive or level == 0):
                result += "{}\033[94m{}/\033[0m\n".format("  " * level, node.get_name())
            elif isinstance(node, datautils.Group) and (recursive or level == 0):
                result += "{}\033[94m{}/\033[0m\n".format("  " * level, node.get_name())
                for subnode in node:
                    subresult, sublog = _cat_helper([(subnode, subnode.get_path())], recursive, level + 1)
                    result += subresult
                    log += sublog
            else:
                log += "[-] Node {} does not exist\n".format(node_path)
        return result, log
    
    results, log = _cat_helper(nodes, recursive, 0)
    if not len(log):
        return results
    elif not len(results):
        return log
    else:
        return results + "\n" + log


def edit(entry_path):
    entry = root[entry_path]
    log = ""

    if not isinstance(entry, datautils.Entry):
        log += "[-] Node {} is not entry or does not exist\n".format(entry_path)
    else:
        print("Leaving line empty will copy current value of given property")
        new_username = str(input("Enter new username (current is '{}'): ".format(entry.get_username())))
        new_username = entry.get_username() if not new_username else new_username
        log += "[+] Username: {} -> {}\n".format(entry.get_username(), new_username)
        new_password = str(input("Enter new password (current is '{}'): ".format(entry.get_password())))
        new_password = entry.get_password() if not new_password else new_password
        log += "[+] Password: {} -> {}\n".format(entry.get_password(), new_password)
        new_url = str(input("Enter new url (current is '{}'): ".format(entry.get_url())))
        new_url = entry.get_url() if not new_url else new_url
        log += "[+] Url: {} -> {}\n".format(entry.get_url(), new_url)
        new_comment = str(input("Enter new comment (current is '{}'): ".format(entry.get_comment())))
        new_comment = entry.get_comment() if not new_comment else new_comment
        log += "[+] Comment: {} -> {}\n".format(entry.get_comment(), new_comment)

        entry.set_username(new_username)
        entry.set_password(new_password)
        entry.set_url(new_url)
        entry.set_comment(new_comment)
        log = '\n' + log
    return log


def cd(new_path):
    new_node = root[new_path]
    if new_node is None or not isinstance(new_node, datautils.Group):
        return None
    else:
        return new_node.get_path()

def mken(nodes_paths):
    nodes = paths_to_nodes(nodes_paths)
    log = ""
    for node, node_path in nodes:
        if isinstance(node, datautils.Node):
            log += "[-] Node {} already exists\n".format(node_path)
        else:
            parent_path = node_path.split('/')[:-1]
            entry_name = node_path.split('/')[-1]
            parent = root[parent_path]
            if not isinstance(parent, datautils.Group):
                log += "[-] Parent of node {} is not group or does not exist\n".format(node_path)
            else:
                parent_path = parent.get_path()
                datautils.create_entry(parent, entry_name)
                log += "[+] Created entry {} in group {}\n".format(entry_name, parent_path)
    return log


def mkgr(nodes_paths):
    nodes = paths_to_nodes(nodes_paths)
    log = ""
    for node, node_path in nodes:
        if isinstance(node, datautils.Node):
            log += "[-] Node {} already exists\n".format(node_path)
        else:
            parent_path = node_path.split('/')[:-1]
            group_name = node_path.split('/')[-1]
            parent = root[parent_path]
            if not isinstance(parent, datautils.Group):
                log += "[-] Parent of node {} is not group or does not exist\n".format(node_path)
            else:
                parent_path = parent.get_path()
                datautils.create_group(parent, group_name)
                log += "[+] Created group {} in group {}\n".format(group_name, parent_path)
    return log


def rm(nodes_paths, recursive):
    nodes = paths_to_nodes(nodes_paths)
    log = ""
    for node, node_path in nodes:
        if isinstance(node, datautils.Entry):
            node.delete(trash)
            log += "[+] Entry {} deleted\n".format(node_path)
        elif isinstance(node, datautils.Group) and recursive:
            if node == root:
                log += "[-] Root group cannot be removed (how then pypm would work?)"
            else:
                node.delete(trash)
                log += "[+] Group {} deleted\n".format(node_path)
        elif isinstance(node, datautils.Group) and not recursive:
            log += "[-] Group {} not deleted: -r option not specified\n".format(node_path)
        else:
            log += "[-] Node {} not exist\n".format(node_path)
    return log


def mv(nodes_paths):
    nodes = paths_to_nodes(nodes_paths)
    log = ""
    if len(nodes) > 2:
        dest_node, dest_path = nodes[-1]
        if not isinstance(dest_node, datautils.Group):
            log += "[-] Cannot move given nodes, destination node {} is not group or does not exist\n".format(dest_path)
        for node, node_path in nodes[:-1]:
            if not isinstance(node, datautils.Node):
                log += "[-] Cannot move node {}, it does not exist\n".format(node_path)
            else:
                if node == dest_node:
                    log += "[-] Cannot move node {} to itself\n".format(node_path)
                else:
                    if node.get_name() in [subnode.get_name() for subnode in dest_node]:
                        log += "[-] Cannot move node {} to destination {}, node already exists\n".format(node_path, dest_path)
                    else:
                        node.move(dest_node)
                        log += "[+] Node {} moved to destination {}\n".format(node_path, dest_path)
    else:
        source_node, source_path = nodes[0]
        dest_node, dest_path = nodes[1]
        if not isinstance(source_node, datautils.Node):
            log += "[-] Cannot move, source node {} does not exist\n".format(source_path)
        elif isinstance(dest_node, datautils.Entry):
            log += "[-] Cannot move, destination node {} already exist and is not group\n".format(dest_path)
        else:
            if isinstance(dest_node, datautils.Group):
                if source_node == dest_node:
                    log += "[-] Cannot move node {} to itself\n".format(source_path)
                else:
                    if source_node.get_name() in [subnode.get_name() for subnode in dest_node]:
                        log += "[-] Cannot move node {} to destination {}, node already exists\n".format(source_path, dest_path)
                    else:
                        source_node.move(dest_node)
                        log += "[+] Moved node {} to destination {}\n".format(source_path, dest_path)
            else:
                parent_path = dest_path.split('/')[:-1]
                new_name = dest_path.split('/')[-1]
                parent = root[parent_path]
                if not isinstance(parent, datautils.Group):
                    log += "[-] Cannot move, parent of destination node {} is not group or does not exist\n".format(dest_path)
                else:
                    parent_path = parent.get_path()
                    source_node.move_and_rename(parent, new_name)
                    log += "[+] Moved node {} to {}\n".format(source_path, dest_path)
    return log


def cp(nodes_paths):
    nodes = paths_to_nodes(nodes_paths)
    log = ""
    if len(nodes) > 2:
        dest_node, dest_path = nodes[-1]
        if not isinstance(dest_node, datautils.Group):
            log += "[-] Cannot copy given nodes, destination node {} is not group or does not exist\n".format(dest_path)
        for node, node_path in nodes[:-1]:
            if not isinstance(node, datautils.Node):
                log += "[-] Cannot copy node {}, it does not exist\n".format(node_path)
            else:
                if node == dest_node:
                    log += "[-] Cannot copy node {} to itself\n".format(node_path)
                else:
                    if node.get_name() in [subnode.get_name() for subnode in dest_node]:
                        log += "[-] Cannot copy node {} to destination {}, node already exists\n".format(node_path, dest_path)
                    else:
                        node.copy(dest_node, node.get_name())
                        log += "[+] Copied node {} to destination {}\n".format(node_path, dest_path)
    else:
        source_node, source_path = nodes[0]
        dest_node, dest_path = nodes[1]
        if not isinstance(source_node, datautils.Node):
            log += "[-] Cannot copy, source node {} does not exist\n".format(source_path)
        elif isinstance(dest_node, datautils.Entry):
            log += "[-] Cannot copy, destination node {} already exist and is not group\n".format(dest_path)
        else:
            if isinstance(dest_node, datautils.Group):
                if source_node == dest_node:
                    log += "[-] Cannot copy node {} to itself\n".format(source_path)
                else:
                    if source_node.get_name() in [subnode.get_name() for subnode in dest_node]:
                        log += "[-] Cannot copy node {} to destination {}, node already exists\n".format(source_path, dest_path)
                    else:
                        source_node.copy(dest_node)
                        log += "[+] Copied node {} to destination {}\n".format(source_path, dest_path)
            else:
                parent_path = dest_path.split('/')[:-1]
                new_name = dest_path.split('/')[-1]
                parent = root[parent_path]
                if not isinstance(parent, datautils.Group):
                    log += "[-] Cannot copy, parent of destination node {} is not group or does not exist\n".format(dest_path)
                else:
                    parent_path = parent.get_path()
                    source_node.copy(parent, new_name)
                    log += "[+] Copied node {} to {}\n".format(source_path, dest_path)
    return log

