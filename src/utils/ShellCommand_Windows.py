# coding=utf-8
import os
import re
import subprocess


class ShellCommandWindows(object):
    """
    API
    The shell command of Windows.
    """

    def __init__(self):
        pass

    def kill_zombie_proc(self):
        """
        Kill zombie process.
        Avoid system resource crashes.
        nothing now.
        """
        pass

    def kill_other_python(self):
        """
        kill other python before launch this auto test tool.
        maybe some conflict
        """
        pass
        # port = re.findall(r"python.exe.+?(\d+).+", os.popen("tasklist|findstr python").read())
        # for i in [i for i in set(port) if str(os.getpid()) != i]:
        #     os.system("taskkill /f /t /pid %s" % i)

    def find_proc_and_pid_by_port(self, port):
        """
        find process and pid by process port for Windows.
        int -> list
        :return:[(proc1, pid1), (proc2, pid2)] [str, int]
        """
        try:
            int(port)
        except ValueError:
            raise KeyError("key must be port! Is int, but real %s!" % type(port))
        except TypeError:
            raise KeyError("key must be port! Is int, but real %s!" % type(port))
        command = 'netstat -aon|findstr %s' % port  # 判断端口是否被占用
        bind_pid = list(set(re.findall(r".+LISTEN.+?(\d+)", os.popen(command).read())))
        if not bind_pid:
            return bind_pid

        find_pid = []
        for i in bind_pid:
            command = 'tasklist|findstr %s' % i
            find_pid.append(re.findall(r"(.+?) .+?(\d+).+?Console.+", os.popen(command).read()))
        find_pid = sum(find_pid, [])  # 递归列表[[(),()],[()]] → [(),(),()]
        find_pid = [(i[0], int(i[1])) for i in find_pid if i[1] in bind_pid]

        return find_pid

    def find_proc_and_pid_by_pid(self, pid):
        """
        find process and pid by process pid for Windows.
        int -> list
        :return:[(proc1, pid1), (proc2, pid2)] [str, int]
        """
        try:
            int(pid)
        except ValueError:
            raise KeyError("key must be pid! Is int, but real %s!" % type(pid))
        except TypeError:
            raise KeyError("key must be pid! Is int, but real %s!" % type(pid))
        command = 'tasklist|findstr %s' % pid
        find_pid = list(set(re.findall(r"(.+?) .+?(\d+).+?Console.+", os.popen(command).read())))
        find_pid = [(i[0], int(i[1])) for i in find_pid if i[1] == pid]

        return find_pid

    def find_proc_and_pid_by_proc(self, proc):
        """
        find process and pid by process name for Windows.
        str -> list
        :return:[(proc1, pid1), (proc2, pid2)] [str, int]
        """
        if not isinstance(proc, str):
            raise KeyError("key must be process name! Is string, but real %s!" % type(proc))
        command = 'tasklist|findstr %s' % proc
        find_pid = list(set(re.findall(r"(.+?) .+?(\d+).+?Console.+", os.popen(command).read())))
        find_pid = list(map(lambda x: (x[0], int(x[1])), find_pid))

        return find_pid

    def kill_proc_by_proc(self, proc):
        """
        kill process by process name for Windows.
        """
        if not isinstance(proc, str):
            raise KeyError("key must be process name! Is string, but real %s!" % type(proc))
        if ".exe" in proc:
            command = 'taskkill /f /t /im %s' % proc  # 通过进程名杀死进程
        else:
            command = 'taskkill /f /t /im %s.exe' % proc  # 通过进程名杀死进程
        print(subprocess.check_output(command).decode("gbk"))
        if self.find_proc_and_pid_by_proc(proc):
            raise AssertionError("kill %s fail." % proc)
        else:
            print(u"终止 %s 进程。" % proc)

    def kill_proc_by_pid(self, pid):
        """
        kill process by process pid for Windows.
        """
        try:
            int(pid)
        except ValueError:
            raise KeyError("key must be pid! Is int, but real %s!" % type(pid))
        except TypeError:
            raise KeyError("key must be pid! Is int, but real %s!" % type(pid))

        command = 'taskkill /f /t /pid %s' % pid  # 通过pid杀死进程
        print(subprocess.check_output(command).decode("gbk"))
        # os.system(command)
        if self.find_proc_and_pid_by_pid(pid):
            raise AssertionError("kill %s fail." % pid)
        else:
            print(u"终止 PID %s。" % pid)

    def set_appium_log_addr(self):
        """
        set appium server log repository path for Windows.
        """
        # addr = os.getenv("Temp")
        addr = os.getcwd()
        addr = os.path.join(addr, "debug")
        return addr

    def push_appium_app(self, udid):
        """
        代替appium安装三大APP
        """
        command = r"adb -s %s install .\apk\unlock_apk-debug.apk" % udid
        os.system(command)

        command = r"adb -s %s install .\apk\settings_apk-debug.apk" % udid
        os.system(command)

        command = r"adb -s %s install .\apk\UnicodeIME-debug.apk" % udid
        os.system(command)

    def replace_appium_js(self):
        """
        appium每次都会安装setting.apk和unlock.apk，复制已经取消安装的代码至源appium路径
        """
        appium_path = os.popen("where appium").read().split("\n")[0].split(".bin")[0]

        for i in ["android", "android-common", "adb"]:
            if i == "adb":
                tmp = os.path.join(appium_path, r"appium\node_modules\appium-adb\lib")
            else:
                tmp = os.path.join(appium_path, r"appium\lib\devices\android")
            old_path = os.path.join(tmp, "%s.js" % i)
            try:
                os.renames(old_path, os.path.join(tmp, "%s.bak" % i))
            except WindowsError:
                pass

            if not os.path.isfile(old_path):
                print(subprocess.check_output("copy %s %s" % (r".\apk\%s.js" % i, old_path), shell=True).decode("gbk"))
