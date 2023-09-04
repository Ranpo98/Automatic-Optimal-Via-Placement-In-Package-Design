def ant1(linew,slot1_x,slot1_y,slot2_x,slot2_y,icount=[0]):
    """
    to run an antenna config
    command printed to terminal should look like this in order for things to work properly:
    
    ./run.sh linew 1.0 slot1_x 0.01 slot1_y 0.01 slot2_x 0.01 slot2_y 0.01 outfile '"'ant_0.s1p'"'
    """
    cnt = icount[0]
    print('Evaluation ', cnt)
    sfile_name = "'\"'ant_"+str(cnt)+".s1p'\"'"
    #limit decimals for ansys to work
    linew,slot1_x,slot1_y,slot2_x,slot2_y = np.around([linew,slot1_x,slot1_y,slot2_x,slot2_y],decimals=3)
    input_values = "linew="+str(linew)+" slot1_x="+str(slot1_x)+" slot1_y="+str(slot1_y)+" slot2_x=" +str(slot2_x)+" slot2_y="+str(slot2_y)
    print(input_values)
 
    code_dir = os.environ.get('CAD_DIR')
    if (code_dir is None):
        raise Exception("Working directory needs to be set to CAD_DIR")
    global ssh
    command = "cd "+code_dir
    command += " && ./run.sh linew "+str(linew)+" slot1_x "+str(slot1_x)+" slot1_y "+str(slot1_y)+" slot2_x " +str(slot2_x)+" slot2_y "+str(slot2_y)+" outfile "+sfile_name
    print(command)
    try_command = "ls *.s1p"#try to see if there is any s1p file
    
    exit_status = utils.ssh_exec(ssh, command, try_command)
    
	#try to remove any .lock file
    stdin, stdout, stderr = ssh.exec_command("cd "+code_dir+ " && rm *.aedt.lock")
    icount[0] +=1
    
    return exit_status