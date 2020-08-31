import cmd
import commands

def parse(args):
    return list(args.split())

class PypmShell(cmd.Cmd):
    intro = 'Welcome into pypm repl v1.0! Type help or ? to get list of commands'
    path = '/'
    prompt = 'pypm / > '

    def gen_prompt(self):
        self.prompt = 'pypm {} > '.format(self.path)

    def do_ls(self, args):
        'Usage: ls [-r] [NODE]...\n' \
        'Lists information about nodes for given NODE(s) (current group by default)\n' \
        '-r option recursively lists NODE(s) which are groups\n'
        args = parse(args)
        if "-r" in args:
            recursive = True
            args.remove('-r')
        else:
            recursive = False
        args = [self.path + node_path if node_path[0] != '/' else node_path for node_path in args]
        if not len(args):
            args.append(self.path)
        result = commands.ls(args, recursive)
        print(result)


    def do_cat(self, args):
        'Usage: cat [-r] [GROUP]...\n' \
        'Prints content of entries included in given GROUP(s) (current group by default)\n'
        args = parse(args)
        if "-r" in args:
            recursive = True
            args.remove('-r')
        else:
            recursive = False
        args = [self.path + node_path if node_path[0] != '/' else node_path for node_path in args]
        if not len(args):
            args.append(self.path)
        result = commands.cat(args, recursive)
        print(result)

    def do_edit(self, args):
        'Usage: edit ENTRY\n' \
        'Edits content of given entry\n'
        args = parse(args)
        if len(args) != 1:
            print("[-] Command edit require exactly one argument\n")
        else:
            result = commands.edit(self.path + args[0])
            print(result)

    def do_cd(self, args):
        'Usage: cd GROUP\n' \
        'Changes current/working group to GROUP\n'
        args = parse(args)
        if len(args) != 1:
            print("[-] Command cd require exactly one argument\n")
        else:
            new_path = args[0]
            if new_path[0] != '/':
                new_path = self.path + new_path
            result = commands.cd(new_path)
            if result is None:
                print("[-] Invalid path, at least one node is entry or does not exist\n")
            else:
                self.path = result
                self.gen_prompt()
    
    def do_mken(self, args):
        'Usage: mken ENTRY...\n' \
        'Creates new empty ENTRY(ies)\n'
        args = parse(args)
        args = [self.path + node_path if node_path[0] != '/' else node_path for node_path in args]
        if not len(args):
            print('[-] Command mken require at least one argument\n')
        else:
            result = commands.mken(args)
            print(result)

    def do_mkgr(self, args):
        'Usage: mkgr GROUP...\n' \
        'Creates new empty GROUP(s)\n'
        args = parse(args)
        args = [self.path + node_path if node_path[0] != '/' else node_path for node_path in args]
        if not len(args):
            print('[-] Command mkgr require at least one argument\n')
        else:
            result = commands.mkgr(args)
            print(result)
    
    def do_rm(self, args):
        'Usage: rm [-r] NODE...\n' \
        'Removes given NODE(s), -r option must be given if at least one\n' \
        'of them is group\n'
        args = parse(args)
        if "-r" in args:
            recursive = True
            args.remove('-r')
        else:
            recursive = False
        args = [self.path + node_path if node_path[0] != '/' else node_path for node_path in args]
        if not len(args):
            args.append(self.path)
        result = commands.rm(args, recursive)
        print(result)

    def do_mv(self, args):
        'Usage: mv SOURCE_NODE NEW_NODE_NAME\n' \
        '   or: mv SOURCE_NODE... DEST_GROUP\n' \
        'Renames SOURCE_NODE to NEW_NODE_NAME, or moves SOURCE_NODE(s) to DEST_GROUP\n'
        args = parse(args)
        args = [self.path + node_path if node_path[0] != '/' else node_path for node_path in args]
        if len(args) < 2:
            print('[-] Command mv require at least two arguments')
        else:
            result = commands.mv(args)
            print(result)
        
    def do_cp(self, args):
        'Usage: cp SOURCE_NODE DEST_NODE\n' \
        '   or: cp SOURCE_NODE... DEST_GROUP\n' \
        'Copies SOURCE_NODE to DEST_NODE or SOURCE_NODE(s) to DEST_GROUP\n'
        args = parse(args)
        args = [self.path + node_path if node_path[0] != '/' else node_path for node_path in args]
        if len(args) < 2:
            print('[-] Command cp require at least two arguments')
        else:
            result = commands.cp(args)
            print(result)

    def do_pull(self, args):
        'Usage: pull HOST PORT DATA_FILE_NAME DOWNLOAD_FILE_PATH\n' \
        'Downloads specified data file from remote server\n'
        pass

    def do_push(self, args):
        'Usage: push HOST PORT DOWNLOAD_FILE_PATH UPLOAD_FILE_PATH\n' \
        'Downloads currently loaded file from remote server, merges modified data\n' \
        'with it and uploads modified and merged data to remote server\n'
        pass

    def do_load(self, args):
        'Usage: load FILE_PATH\n' \
        'Loads data from specified file\n'
        args = parse(args)


    def do_save(self, args):
        'Usage: save [FILE_PATH]\n' \
        'Saves modified data to specified file (overwrites currently loaded by default)\n'
        pass

    def do_exit(self, args):
        'Usage: exit\n' \
        'Does not save any changes, closes pypm repl and exits.\n'
        choice = input('Do you want to exit pypm repl? [Y/n] ')
        if choice == '' or choice.lower()[0] == 'y':
            return True
        else:
            pass

if __name__ == '__main__':
    PypmShell().cmdloop()

