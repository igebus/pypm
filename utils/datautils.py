import struct
import time
from datetime import datetime
import uuid
from utils import binfileutils


CURRENT_VERSION = 0


RECEIVED = -1
LOCAL = 1
CONFLICT = 0


class VersionException(Exception):
    def __init__(self, version):
        super().__init__("Base version " + version + " is not supported.")


def check_version(version):
    if CURRENT_VERSION < version:
        raise VersionException(version)


class EditInfo:
    def __init__(self, version_counter, timestamp, editor):
        self.version_counter = version_counter
        self.timestamp = timestamp
        self.editor = editor
        self.modified = False

    def copy(self):
        return EditInfo(self.version_counter, self.timestamp, self.editor)

    def update(self):
        if not self.modified:
            self.version_counter += 1
            self.modified = True
        self.timestamp = time.time()
        self.editor = "" # TODO set editor

    def check_against(self, received_info):
        if self.modified:
            if self.version_counter > received_info.version_counter:
                return LOCAL
            else:
                return CONFLICT
        else:
            return RECEIVED

    def is_new(self):
        return self.modified and self.version_counter == 1

    def __str__(self):
        return "by " + self.editor + " at " + datetime.fromtimestamp(self.timestamp).strftime("%H:%M %d/%m/%Y")


def create_edit_info():
    edit_info = EditInfo(0, None, None)
    edit_info.update()
    return edit_info


class EntryData:
    def __init__(self, edit_info, username="", password="", url="", comment=""):
        self.username = username
        self.password = password
        self.url = url
        self.comment = comment
        self.edit_info = edit_info

    def copy(self):
        return EntryData(self.edit_info.copy(), self.username, self.password, self.url, self.comment)

    def copy_data(self):
        return EntryData(create_edit_info(), self.username, self.password, self.url, self.comment)

    def merge(self, received):
        check = self.edit_info.check_against(received.edit_info)
        if check == LOCAL:
            return self.copy()
        elif check == RECEIVED:
            return received.copy()
        elif check == CONFLICT:
            # TODO merge
            return None
        else: # should not happen
            raise RuntimeError("Invalid merge code '" + check + "'")


def create_entry_data():
    return EntryData(create_edit_info())


class NodeLocation:
    def __init__(self, edit_info, parent, name, deleted=False):
        self.parent = parent
        self.name = name
        self.deleted = deleted
        self.edit_info = edit_info

    def copy(self):
        return NodeLocation(self.edit_info.copy(), self.parent, self.name, self.deleted)

    def merge(self, received):
        check = self.edit_info.check_against(received.edit_info)
        if check == LOCAL:
            return self.copy()
        elif check == RECEIVED:
            return received.copy()
        elif check == CONFLICT:
            # TODO merge
            return None
        else: # should not happen
            raise RuntimeError("Invalid merge code '" + check + "'")


def create_node_location(parent, name):
    return NodeLocation(create_edit_info(), parent, name)


class Node:
    def __init__(self, node_id, location):
        self.node_id = node_id
        self.location = location
        self.children = {}

    def __getitem__(self, index):
        if type(index) is str:
            index = index.split('/')
        current = self
        for node in index:
            if node == "":
                continue
            if node == "..":
                if current.get_parent() is not None:
                    current = current.get_parent()
            else:
                if node not in current.children.keys():
                    return None
                current = current.children[node]
        return current
    
    def __iter__(self):
        return iter(self.children.values())

    def __len__(self):
        return len(self.children)

    def has_child(self, name):
        return name in self.children.keys()

    def is_ancestor_of(self, other_node):
        check = other_node
        while True:
            if check == self:
                return True
            if check.get_parent() is None:
                return False
            check = check.get_parent()

    def detach(self):
        self.location.parent.children.pop(self.location.name)

    def attach(self):
        self.location.parent.children[self.location.name] = self

    def move(self, parent):
        self.location.edit_info.update()
        self.detach()
        self.location.parent = parent
        self.attach()

    def rename(self, name):
        self.location.edit_info.update()
        self.detach()
        self.location.name = name
        self.attach()

    def move_and_rename(self, parent, name):
        self.location.edit_info.update()
        self.detach()
        self.location.parent = parent
        self.location.name = name
        self.attach()

    def delete(self, trash):
        self.location.edit_info.update()
        self.detach()
        while len(self.children) > 0:
            next(iter(self)).delete(trash)
        self.location.deleted = True
        self.location.parent = None
        self.location.name = None
        self.children = None
        if not self.location.edit_info.is_new():
            trash.append(self)

    def copy(self, group, name):
        self_copy = self.element_copy(group, name)
        for child in self:
            child.copy(self_copy, child.get_name())

    def reset_modified(self):
        self.location.edit_info.modified = False
        for child in self:
            child.reset_modified()

    def get_parent(self):
        return self.location.parent

    def get_name(self):
        return self.location.name

    def get_path(self):
        reverse = []
        current = self
        while True:
            reverse.append(current)
            if current.get_parent() is None:
                break
            current = current.get_parent()
        ret = ""
        while len(reverse) > 0:
            ret += reverse.pop().get_name()+"/"
        return ret


class Entry(Node):
    def __init__(self, node_id, location, data):
        super().__init__(node_id, location)
        self.data = data

    def merge(self, received):
        merged_location = self.location.merge(received.location)
        if merged_location.deleted:
            return Entry(self.node_id, merged_location)
        merged_data = self.data.merge(received.data)
        return Entry(self.node_id, merged_location, merged_data)

    def get_username(self):
        return self.data.username

    def get_password(self):
        return self.data.password
    
    def get_url(self):
        return self.data.url
    
    def get_comment(self):
        return self.data.comment

    def set_username(self, username):
        self.data.username = username
        self.data.edit_info.update()

    def set_password(self, password):
        self.data.password = password
        self.data.edit_info.update()

    def set_url(self, url):
        self.data.url = url
        self.data.edit_info.update()

    def set_comment(self, comment):
        self.data.comment = comment
        self.data.edit_info.update()

    def delete(self, trash):
        super().delete(trash)
        self.data = None

    def element_copy(self, group, name):
        entry = create_entry(group, name)
        entry.data = self.data.copy_data()
        return entry

    def reset_modified(self):
        super().reset_modified()
        self.data.edit_info.modified = False


def create_entry(group, name):
    entry = Entry(uuid.uuid1(), create_node_location(group, name), create_entry_data())
    entry.attach()
    return entry


class Group(Node):
    def merge(self, received):
        merged_location = self.location.merge(received.location)
        return Group(self.node_id, merged_location)

    def element_copy(self, group, name):
        return create_group(group, name)


def create_group(group, name):
    group = Group(uuid.uuid1(), create_node_location(group, name))
    group.attach()
    return group


class SubtreeIterator:
    def __init__(self, node):
        self.node = node
        self.iterator_stack = [iter(self.node)]

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.iterator_stack) == 0:
            raise StopIteration
        returned = self.node
        while True:
            try:
                x = next(self.iterator_stack[-1])
                self.node = x
                iterator_stack.append(iter(self.node))
                return returned
            except StopIteration:
                self.iterator_stack.pop()
                if len(self.iterator_stack) == 0:
                    return returned


def create_root():
    return Group(None, NodeLocation(None, None, ''))


def read_uuid(reader):
    return UUID(bytes = reader.read(16))


def write_uuid(writer, value):
    writer.write(value.bytes)


def read_edit_info(reader, version, local):
    check_version(version)
    version_counter = reader.read_uint()
    timestamp = reader.read_double()
    editor = reader.read_string()
    edit_info = EditInfo(version_counter, timestamp, editor)
    if local:
        edit_info.modified = reader.read_bool()
    return edit_info


def write_edit_info(writer, local, edit_info):
    writer.write_uint(edit_info.version_counter)
    writer.write_double(edit_info.timestamp)
    writer.write_string(edit_info.editor)
    if local:
        writer.write_bool(edit_info.modified)


def read_node_location(reader, version, local, parent):
    check_version(version)
    edit_info = read_edit_info(reader, version, local)
    name = reader.read_string()
    return NodeLocation(edit_info, parent, name)


def write_node_location(writer, local, location):
    write_edit_info(writer, local, location.edit_info)
    writer.write_string(location.name)


def read_entry_data(reader, version, local):
    check_version(version)
    edit_info = read_edit_info(reader, version, local)
    username = reader.read_string()
    password = reader.read_string()
    url = reader.read_string()
    comment = reader.read_string()
    return EntryData(edit_info, username, password, url, comment)


def write_entry_data(writer, local, data):
    write_edit_info(writer, local, location.edit_info)
    writer.write_string(data.username)
    writer.write_string(data.password)
    writer.write_string(data.url)
    writer.write_string(data.comment)


def read_entry(reader, version, local, parent):
    check_version(version)
    node_id = read_uuid(reader)
    location = read_node_location(reader, version, local, parent)
    entry_data = read_entry_data(reader, version, local)
    entry = Entry(node_id, location, entry_data)
    entry.attach()
    return entry


def write_entry(writer, local, entry):
    write_uuid(writer, entry.node_id)
    write_node_location(writer, local, entry.location)
    write_entry_data(writer, local, entry.data)


def read_deleted_entry(reader, version, local):
    check_version(version)
    node_id = read_uuid(reader)
    edit_info = read_edit_info(reader, version, local)
    location = NodeLocation(edit_info, None, None, True)
    return Entry(node_id, location, None)


def write_deleted_entry(writer, local, entry):
    write_uuid(writer, entry.node_id)
    write_edit_info(writer, local, entry.location.edit_info)


def read_deleted_group(reader, version, local):
    check_version(version)
    node_id = read_uuid(reader)
    edit_info = read_edit_info(reader, version, local)
    location = NodeLocation(edit_info, None, None, True)
    return Group(node_id, location)


def write_deleted_group(writer, local, group):
    write_uuid(writer, group.node_id)
    write_edit_info(writer, local, group.location.edit_info)


def read_trash(reader, version, local):
    check_version(version)
    trash = []
    trash_entries_size = reader.read_uint()
    for i in range(trash_entries_size):
        trash.append(read_deleted_entry(reader, version, local))
    trash_groups_size = reader.read_uint()
    for i in range(trash_groups_size):
        trash.append(read_deleted_group(reader, version, local))


def write_trash(writer, local, trash):
    check_version(version)
    groups = []
    entries = []
    for node in trash:
        if type(node) is Entry:
            entries.append(node)
        elif type(node) is Group:
            groups.append(node)
    writer.write_uint(len(entries))
    for entry in entries:
        write_deleted_entry(writer, local, entry)
    writer.write_uint(len(groups))
    for group in groups:
        write_deleted_group(writer, local, group)


def read_group(reader, version, local, parent):
    check_version(version)
    node_id = read_uuid(reader)
    location = read_node_location(reader, version, local, parent)
    current = Group(node_id, location)
    current.attach()
    subgroups_amount = reader.read_uint()
    for i in range(subgroups_amount):
        read_group(reader, version, local, current)
    entries_amount = reader.read_uint()
    for i in range(entries_amount):
        read_entry(reader, version, local, current)
    return current


def write_group(writer, local, group):
    write_uuid(writer, group.node_id)
    write_node_location(writer, local, group.location)
    subgroups = []
    entries = []
    for node in group.children.values():
        if type(node) is Entry:
            entries.append(node)
        elif type(node) is Group:
            subgroups.append(node)
    writer.write_uint(len(subgrous))
    for subgroup in subgrous:
        write_group(writer, local, subgroup)
    writer.write_uint(len(entries))
    for entry in entries:
        write_entry(writer, local, entry)


def read_root(reader, version, local):
    root = create_root()
    subgroups_amount = reader.read_uint()
    for i in range(subgroups_amount):
        read_group(reader, version, local, root)
    entries_amount = reader.read_uint()
    for i in range(entries_amount):
        read_entry(reader, version, local, root)
    return root


def write_root(writer, local, root):
    subgroups = []
    entries = []
    for node in root.children.values():
        if type(node) is Entry:
            entries.append(node)
        elif type(node) is Group:
            subgroups.append(node)
    writer.write_uint(len(subgrous))
    for subgroup in subgrous:
        write_group(writer, local, subgroup)
    writer.write_uint(len(entries))
    for entry in entries:
        write_entry(writer, local, entry)


def read_config(reader, version):
    check_version(version)
    config_size = reader.read_uint()
    json_string = reader.read(config_size).decode("utf-8")
    return json.loads(json_string)


def write_config(writer, config):
    json_bytes = json.dumps(config, separators=(',', ':')).encode("utf-8")
    writer.write_uint(len(json_bytes))
    writer.write(json_bytes)


def decrypt(reader, fernet):
    version = reader.read_uint()
    check_version(version)
    local = reader.read_bool()
    config = None
    if local:
        config = read_config(reader, version)
    base_size = reader.read_uint()
    in_bytes = fernet.decrypt(reader.read(base_size))
    bytes_reader = BytesReader(in_bytes)
    root = read_root(bytes_reader, version, local)
    trash = read_trash(bytes_reader, version, local)
    return root, trash, config


def encrypt(writer, fernet, local, root, trash, config=None):
    writer.write_uint(CURRENT_VERSION)
    writer.write_bool(local)
    if local:
        write_config(writer, config)
    out_bytes = []
    bytes_writer = BytesWriter(out_bytes)
    write_root(bytes_writer, local, root)
    write_trash(bytes_writer, local, trash)
    out_bytes = fernet.encrypt(out_bytes)
    writer.write_uint(len(out_bytes))
    writer.write(out_bytes)


def decrypt_file(path, fernet):
    with open(path, "rb") as file:
        return decrypt(file, fernet, local)


def encrypt_file(path, fernet, local, root, trash, config=None):
    with open(path, "wb") as file:
        encrypt(file, fernet, local, root, trash, config)

def create_database():
    return (create_root(), [], {})
