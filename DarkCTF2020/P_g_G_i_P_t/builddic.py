
yourpath = './P_g_G_i_P_t/10k'

import os

with open('./dic.txt', 'w') as dic:

    for root, dirs, files in os.walk(yourpath, topdown=True):
        files.sort()
        for name in files:
            #print(os.path.join(root, name))
            with open(os.path.join(root, name), 'r') as f1:
                
                str = '{}_mI0\n'.format(f1.readline())
                dic.write(str)
                #if '2766951_mI0\n' == str:
                #    print('found in file: {}'.format(name))
