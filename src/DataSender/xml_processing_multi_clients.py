import sys, os

pyfile = (sys.platform[:3] == 'win' and 'python.exe') or 'python'
pypath = sys.executable     # use sys in newer pys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

numclients = 10

# start('echo-server.py')              # spawn server locally if not yet started

# args = ' '.join(sys.argv[1:])          # pass server name if running remotely
#for i in range(numclients):

# for i in [1, 2, 4, 5, 6, 7, 8, 9]:
#     print(i)
#     print(sys.argv[1:])
#     args_list = sys.argv[1:].append(i)
#     print(args_list)
#     tmp = sys.argv[1:]
#     tmp.append(i)
#     print('tmp', tmp)
#     args = ' '.join(tmp)
#     print(args)
#    

def run(cmdline):
    assert hasattr(os, 'fork')                 
    print("In Fork")
    print(cmdline)
    cmdline = cmdline.split()                  # convert string to list
    if os.fork() == 0:                         # start new child process
        os.execvp(pypath, [pyfile] + cmdline)  # run new program in child

for i in range(10):
    tmp = sys.argv[1:]
    tmp.append(str(i))
    args = ' '.join(tmp)
    print(args)
    run('xml_processing_client.py %s' % args)  # spawn 8? clients to test the server


