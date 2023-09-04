import paramiko
import os
import numpy as np

def set_env(name, val):
    os.environ[name] = val

def get_env(name):
    return os.environ.get(name)

class fetch_sim():
    def __init__(self, executable, netlist_file, output_file=None, data_path='./',\
                 command=None, stayalive_command=None,\
                 host = '192.17.223.119', port = 22, counter=0, process_func=None):
        """
        works for simulations that can be invoked by:
        <executable> netlist_file output_file var1 val1 var2 val2 .... varN valN

        <executable>, netlist_file and output_file are set in __init__()
        
        var1 val1 var2 val2 .... varN valN is fed by optim in `Xdict` in sim() to match BO's API
        
        Xdict = {
            'var1': val1,
            'var2': val2,
            ....
            'varN': valN,
        }
        
        process_func    :    user defined function, receives output_file and return output expected by BO
                            called by sim(), after running simulation
        """
        self.counter = counter
        self.CAD_DIR = get_env('CAD_DIR')
        
        if (self.CAD_DIR is None):
            raise Exception("Remote working directory needs to be set to CAD_DIR")
        username = get_env('CAD_USER_NAME')
        password = get_env('CAD_PASSWORD')
        if (username is None) | (password is None):
            raise Exception("For security, user name and password need to be set to CAD_USER_NAME and CAD_PASSWORD. Working directory needs to be set to CAD_DIR")
        self.ssh_client = login(host, port, username, password)
        self.executable = executable#something like run.sh
        self.input_file = netlist_file
        self.output_name = 'output' if output_file is None else output_file
        self.out_ext = '.txt' if output_file is None else output_file.split('.')[-1]#get file extension
        self.process_func = process_func#to process data after simulation
        self.local_data_path = data_path
        self.command=command
        self.stayalive_command=stayalive_command
    
    @staticmethod
    def gen_cmd(var_names_str,var_vals_str,exe):
        """
        all elements in var_vals_str and var_vals_str must be string
        """
        return exe+" "+" ".join([var+" "+val for var,val in zip(var_names_str, var_vals_str)])
        
    def gen_sim_cmd(self,var_names, var_vals):
        
        self.output_file = self.output_name+'_'+str(self.counter)+self.out_ext
        var_name_str = [self.input_file]+var_names
        var_val_str = ["\""+self.output_file+"\""]+[str(val) for val in var_vals]#add " " as part of file name, this goes thru bash to .txt file
        run_cmd = self.gen_cmd(var_name_str, var_val_str, self.executable)
        
        command = "cd "+self.CAD_DIR
        command += " && "
        command += run_cmd
        
        # print(command)
        stayalive_command = "cd "+self.CAD_DIR+" && ls "+self.output_file#try to see if <self.output>_<self.counter>.txt file exists
        
        # print(stayalive_command)
        return command, stayalive_command
        
    def sim_eval(self,**Xdict):
        """
        This function only takes in Xdict as input to be compatible with BO as function evaluation.
        Once get a candidate, BO pass in
        
        Xdict = {
            'var1' : val1,
            'var2' : val2,
            ....
            'varN' : valN,
        }
        Since this class is designed to work with an executable that has signature as
        
        <executable> netlist_file output_file var1 val1 var2 val2 .... varN valN
        
        The netlist_file and out_file will be added manually in this function. This was done in gen_cmd()
        """
        

        var_names = [var for var, _ in Xdict.items()]
        var_vals = np.array([val for _, val in Xdict.items()])
        var_vals = np.around(var_vals,decimals=4)
        
        self.counter += 1
        command__ , stayalive_command__ = self.gen_sim_cmd(var_names,var_vals)
        if self.command is None:
            command = command__
        if self.stayalive_command is None:
            stayalive_command = stayalive_command__
        
        print('Evaluation ', self.counter)
        print('command: ',command)
        print('stayalive_command:',stayalive_command)
        # exit_status = 0#success
        exit_status = ssh_exec(self.ssh_client, command, stayalive_command)
        #get output file to local
        remote_files = [os.path.normpath(self.CAD_DIR+'/'+self.output_file)]
        get_files_from_host(self.ssh_client,remote_files,self.local_data_path)
        BO_output = self.process_func(os.path.normpath(self.local_data_path+'/'+self.output_file))

        return BO_output
    
    def close(self):
        self.ssh_client.close()

def check_and_make_dir(path):
    if not os.path.exists(path):
        print('Creating ',path)
        os.makedirs(path)

def login(host,port,username,password):
    ssh_client =paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())#1st time log in to server, we have to answer if we trust the server. This takes care of that, otherwise an error shows up
    ssh_client.connect(hostname=host,port=port,username=username,password=password)
    
    return ssh_client

def ssh_exec(ssh_client, cmd, cmd_try, sleeptime=120, moment='', cnt=[0]):
    """
    execute `cmd`, 
    
    if exit_status == 1, there was some errors, keep trying `cmd_try` until successful or user stops
    
    most likely it fails because Ansys couldnt generate .sNp file, this infinity try will give us a chance to intervene, generating sNP file manually and let the program pick up and move on
    
    """
    # cmd = "pwd "
    print('cmd: ', cmd)
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    # stdin.write("input of command if needed")
    exit_status = stdout.channel.recv_exit_status()# Blocking call, wait til finish
    # exit_status = 1
    if exit_status == 0:
        print("Success")
    else:
        print("Error, exit_status = ", exit_status)
        import datetime
        moment = str(datetime.datetime.now()).split('.')[0].replace(" ", "_")#2021-10-13 16:57:55.548014 ==> 2021-10-13_16:57:55
        moment = moment.replace(":", ".")#2021-10-13_16:57:55 ==> 2021-10-13_16.57.55 ==> to be used as folder name (: is not allowed in folder names)
        stdout_file = 'ssh_exec_stdout_'+moment+'.txt'
        stderr_file = 'ssh_exec_stderr_'+moment+'.txt'
        try:
            lines_out = stdout.read().decode('utf-8')
            lines_err = stderr.read().decode('utf-8')
            with open(stdout_file, 'a') as fl:
                fl.write('========================= ATTEMPT '+str(cnt[0])+' =========================\n')
                fl.write('cmd: '+cmd)
                fl.write(lines_out)
                fl.write('\n\n=============================================================\n\n')
            with open(stderr_file, 'a') as fl:
                fl.write('========================= ATTEMPT '+str(cnt[0])+' =========================\n')
                fl.write('cmd: '+cmd)
                fl.write(lines_err)
                fl.write('\n\n=============================================================\n\n')
        except Exception as e:
            # ssh_client.close()
            print('Could not read stdout/stderr as utf-8 ...')
            print('\nstdout:\n',stdout.read())
            print('\nstderr:\n',stderr.read())
            print(str(e))
            # sys.exit()

        #keep trying cmd_try
        exit_status = 1
        import time
        print('Trying to run \n'+cmd_try+'\n... in infinity loop till success ')
        while (exit_status):#keep trying and sleep 2min, waiting for s4p file manually generated
            # print(cmd_try)
            stdin, stdout, stderr = ssh_client.exec_command(cmd_try)
            exit_status = stdout.channel.recv_exit_status()# Blocking call, wait til finish
            # print(exit_status)
            try:
                lines_out = stdout.read().decode('utf-8')
                lines_err = stderr.read().decode('utf-8')
                with open(stdout_file, 'a') as fl:
                    fl.write('------- RETRY -------\n')
                    fl.write('try_cmd: '+cmd)
                    fl.write(lines_out)
                    fl.write('\n-------------------\n')
                with open(stderr_file, 'a') as fl:
                    fl.write('------- RETRY -------\n')
                    fl.write('try_cmd: '+cmd)
                    fl.write(lines_err)
                    fl.write('\n-------------------\n')
            except Exception as e:
                    # ssh_client.close()
                print('Could not read stdout/stderr as utf-8 ...')
                print('\nstdout:\n',stdout.read())
                print('\nstderr:\n',stderr.read())
                print(str(e))
                # sys.exit()
            print(".", end = '', flush=True)#no new line
            #sleep 2 mins
            if exit_status:
                time.sleep(sleeptime)
            else:
                #sleep a bit more one last time, so i have enough time to close Ansys
                print('\nRunning '+cmd_try+' succesfully, resume in '+str(sleeptime)+'sec')
                time.sleep(sleeptime)
                break
        print('\nSucceed recovered. Move on')
        
		
    cnt[0] += 1
    return exit_status

def make_executable(ssh_client, file):
    
    cmd = "chmod 750 "+file
    # print(cmd)
    try:
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()# Blocking call, wait til finish
        if exit_status == 0:
            print("Success")
        else:
            print('Error code:', exit_status)
    except Exception as e:
        print(str(e))


def send_files_to_host(ssh_client, local_files, host_destination):
    assert type(local_files)==list, 'local_files must be a list of full path to files needed moving'
    move_files = []
    with ssh_client.open_sftp() as sftp:
        for file in local_files:
            fl_name = os.path.normpath(file).split('/')[-1]
            remote_file = os.path.normpath(host_destination+'/'+fl_name)
            sftp.put(file,remote_file)
            move_files += [remote_file]
    return move_files
    
def get_files_from_host(ssh_client, remote_files, local_destination):
    assert type(remote_files)==list, 'remote_files must be a list of full path to files needed moving'
    check_and_make_dir(local_destination)
    
    move_files = []
    with ssh_client.open_sftp() as sftp:
        for file in remote_files:
            try:
                remote_file = os.path.normpath(file)
                # print('Getting ', remote_file)
                fl_name = file.split('/')[-1]
                # print('fl_name:', fl_name)
                local_file = os.path.normpath(local_destination+'/'+fl_name)
                # print('local_file:',local_file)
                sftp.get(remote_file, local_file)
                # print('Saved to ', local_file)
                sftp.remove(file)
                move_files += [local_file]
            except FileNotFoundError as e:
                print('FileNotFoundError:',remote_file)
    return move_files


"""
Different loss function

"""

cost_code = {1:'mse', 2:'mdiffe', 3:'msgne', 4:'ml1e', 5:'worst', 6:'worst_rel'}

def dispatch_loss(loss_type,fverbose=False):
    if type(loss_type) == int:
        loss_func = cost_code[loss_type]
        if fverbose:
            print('Dispatching', loss_func)
        return globals()[loss_func]
    elif type(loss_type) == str:
        if fverbose:
            print('Dispatching', loss_type)
        return globals()[loss_type]
    else:
        raise Exception("loss_type must be int or str")

def mse(a,b,fmean=True):
    """mean-square error"""
    return ((a-b)**2).mean() if fmean else (a-b)**2

def mdiffe(a,b,fmean=True):
    """
    mean difference error:
    can somewhat to evaluate how well a < b,
    however, this error function is not good when a << b in some ranges and a > b in other ranges.
    
    The compliance magnitude is too large, will cancel out the non-compliance, leading to a very good-looking cost
    but in reality it's not very good. For example, like this
    
    <-non-comp-
       linace  -><-- compliance-->
    \
     \-----------
     ============\================== b
                  \            /
                   \          /
                    \        /
                     \      /
                      \    /
                       \  /
                        \/
    difference in the compilance range is much larger than that in the non-compliance, 
    hence, over all cost looks like it's all good when it's actually not
    """
    return (a-b).mean() if fmean else (a-b)

def msgne(a,b,fmean=True):
    """mean sign error:
    non-zero where a > b
    zero where a <= b
    
    1. evaluate how well a < b
    2. 0 <= msgne <= 1
    3. amount of violation does not matter
    """
    return ((a-b)>0).mean() if fmean else (a-b)>0

def ml1e(a,b,fmean=True):
    """
    mean l1 error - updated on Feb 01, 22 to reflect that true L1-norm of v is | v |
    previous ml1e is mdiffe()
    """
    return np.abs(a-b).mean() if fmean else np.abs(a-b)

def worst(a,b,fmean=True):
    """
    evaluate how well a < b 
    
    """
    return (a-b).max()

def worst_rel(a,b,fmean=True):
    """
    evaluate how well a < b 
    
    """
    
    return ((a-b)/b).max()