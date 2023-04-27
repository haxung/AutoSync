import hashlib
import json
import os
import sys
import time
import zipfile

import paramiko
import scp


def server_info():
    with open("./conf.user.json", "r", encoding="utf-8") as f:
        user_json = json.load(f)
    hostname = user_json["hostname"]
    usr = user_json["user"]
    pwd = user_json["password"]
    up_dir = user_json["upload_dir"]
    down_dir = user_json["download_dir"]
    f.close()
    return hostname, usr, pwd, up_dir, down_dir


def process(filename, size, sent):
    sys.stdout.write("%s progress: %.2f%% \r" % (filename, float(sent)/float(size)*100))
    

def process4(filename, size, sent, peername):
    sys.stdout.write(
        "(%s:%s) %s progress: %.2f%% \r" % (peername[0], peername[1], filename, float(sent) / float(size)*100))
    

def scp_file(hostname, usr, pwd, up_dir, down_dir, flag):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(hostname, 22, usr, pwd)
    scp_connect = scp.SCPClient(ssh.get_transport(), progress4=process4)
    
    if flag:
        up_zip_path, up_sha256_path = zip_dir(up_dir)
        scp_connect.put(up_zip_path, "~/")
        sys.stdout.write("\n")
        scp_connect.put(up_sha256_path, "~/")
        sys.stdout.write("\n")
        os.remove(up_zip_path)
        os.remove(up_sha256_path)
        sys.stdout.write("OK. Upload finished at %s. \n" % time.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        dir_name = os.path.split(up_dir)[-1]
        zip_name = dir_name + ".zip"
        sha256_name = dir_name + ".txt"

        down_zip_path = os.path.join(down_dir, zip_name)
        down_sha256_path = os.path.join(down_dir, sha256_name)
        # print(down_zip_path)
        # print(down_sha256_path)
        
        scp_connect.get("~/{}".format(zip_name), down_zip_path)
        sys.stdout.write("\n")
        scp_connect.get("~/{}".format(sha256_name), down_sha256_path)
        sys.stdout.write("\n")

        f = open(down_sha256_path, "r")
        up_sha256 = f.readline().strip()
        f.close()
        
        down_sha256 = count_sha256(down_zip_path)
        if up_sha256 == down_sha256:
            sys.stdout.write("OK: zip file is right. \n")
        else:
            sys.stdout.write("Error: zip file is incorrect. \n")
            os.remove(down_zip_path)
            os.remove(down_sha256_path)
            
        sys.stdout.write("OK. Download finished at %s. \n" % time.strftime("%Y-%m-%d %H:%M:%S"))
    scp_connect.close()


def zip_dir(dir_path):
    zip_name = dir_path + ".zip"
    sha256_path = dir_path + ".txt"
    
    zip_obj = zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dir_path):
        fpath = path.replace(dir_path, '')
        
        for filename in filenames:
            zip_obj.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip_obj.close()
    
    sha256_val = count_sha256(zip_name)
    f = open(sha256_path, "w")
    f.write(sha256_val + "\n")
    f.close()
    return zip_name, sha256_path


def count_sha256(file_path):
    start_time = time.time()
    size = os.path.getsize(file_path)
    f = open(file_path, "rb")
    sha256_val = hashlib.sha256()
    LENGTH = 1024 * 1024
    while size >= LENGTH:
        sha256_val.update(f.read(LENGTH))
        size -= LENGTH
    sha256_val.update(f.read())
    f.close()
    end_time = time.time()
    
    sys.stdout.write("OK: get sha256 spending %.2fs.\n" % (end_time - start_time))
    return sha256_val.hexdigest()


if __name__ == "__main__":
    flag = int(input("upload or download(1:0)?\t"))
    if flag not in [0, 1]:
        sys.stdout.write("Error: input is not 0 or 1, try again please. \n")
    if flag == 1:
        sys.stdout.write("Wait a moment. Upload start at %s. \n" % time.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        sys.stdout.write("Wait a moment. Download start at %s. \n" % time.strftime("%Y-%m-%d %H:%M:%S"))
        
    hostname, usr, pwd, up_dir, down_dir = server_info()
    scp_file(hostname, usr, pwd, up_dir, down_dir, flag)
