import os
files = [fle for fle in os.listdir('data') if fle.startswith('oai') and fle.endswith('.xml')]
 
for filename in files:
    if not os.path.isdir('data/'+filename[:15]):
        os.mkdir('data/'+filename[:15])
    if not os.path.isdir('data/'+'/'.join((filename[:15], filename[:16]))):
        os.mkdir('data/'+'/'.join((filename[:15], filename[:16])))
    if not os.path.isdir('data/'+'/'.join((filename[:15], filename[:16], filename[:17]))):
        os.mkdir('data/'+'/'.join((filename[:15], filename[:16], filename[:17])))
    if not os.path.isdir('data/'+'/'.join((filename[:15], filename[:16], filename[:17], filename[:18]))):
        os.mkdir('data/'+'/'.join((filename[:15], filename[:16], filename[:17], filename[:18])))
    print('data/'+filename)
    print('data/'+'/'.join((filename[:15], filename[:16], 
                                                  filename[:17], filename[:18],
                                                  filename)))
    os.rename('data/'+filename, 'data/'+'/'.join((filename[:15], filename[:16], 
                                                  filename[:17], filename[:18],
                                                  filename)))